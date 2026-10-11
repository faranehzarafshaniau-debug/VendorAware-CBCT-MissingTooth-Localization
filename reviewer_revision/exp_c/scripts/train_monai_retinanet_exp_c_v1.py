#!/usr/bin/env python3

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import random
import time
from pathlib import Path

import numpy as np
import torch

from monai.apps.detection.networks.retinanet_detector import RetinaNetDetector
from monai.apps.detection.networks.retinanet_network import (
    RetinaNet,
    resnet_fpn_feature_extractor,
)
from monai.apps.detection.utils.anchor_utils import (
    AnchorGeneratorWithAnchorShape,
)
from monai.networks.nets import resnet


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_roles(manifest, fold):
    with open(manifest, newline="", encoding="utf-8") as f:
        rows = [
            r for r in csv.DictReader(f)
            if int(r["outer_test_fold"]) == int(fold)
        ]

    roles = {
        k: [r for r in rows if r["role"] == k]
        for k in ("optimization", "validation", "calibration", "outer_test")
    }

    actual = {k: len(v) for k, v in roles.items()}

    permitted = (
        {"optimization":46,"validation":10,"calibration":10,"outer_test":17},
        {"optimization":47,"validation":10,"calibration":10,"outer_test":16},
    )

    if actual not in permitted:
        raise RuntimeError(f"Fold role mismatch: {actual}")

    return roles


def read_anchor_shapes(anchor_file, fold):
    j = json.loads(Path(anchor_file).read_text())
    xyz = j["folds"][str(fold)]["base_anchor_shapes_xyz_voxel"]

    # Cache tensor order is D,H,W = Z,Y,X.
    # Locked anchors are stored X,Y,Z.
    # This is only a coordinate-order conversion, not retuning.
    zyx = [[int(a[2]), int(a[1]), int(a[0])] for a in xyz]

    return xyz, zyx


def build_detector(cfg, anchor_zyx, device):
    returned_layers = [1, 2, 3]

    feature_map_scales = [
        2 ** l for l in range(len(returned_layers) + 1)
    ]

    anchor_generator = AnchorGeneratorWithAnchorShape(
        feature_map_scales=feature_map_scales,
        base_anchor_shapes=anchor_zyx,
    )

    # ResNet-18 FPN is fixed before any formal performance is observed.
    # It satisfies the locked ResNet-FPN RetinaNet contract while fitting
    # the 12-GB GPU at the locked 128x160x160 patch size.
    backbone = resnet.ResNet(
        block=resnet.ResNetBlock,
        layers=[2, 2, 2, 2],
        block_inplanes=resnet.get_inplanes(),
        n_input_channels=1,
        conv1_t_stride=[2, 2, 2],
        conv1_t_size=[7, 7, 7],
    )

    feature_extractor = resnet_fpn_feature_extractor(
        backbone=backbone,
        spatial_dims=3,
        pretrained_backbone=False,
        trainable_backbone_layers=None,
        returned_layers=returned_layers,
    )

    num_anchors = anchor_generator.num_anchors_per_location()[0]

    size_divisible = [
        int(s) * 2 * 2 ** max(returned_layers)
        for s in feature_extractor.body.conv1.stride
    ]

    net = RetinaNet(
        spatial_dims=3,
        num_classes=4,
        num_anchors=num_anchors,
        feature_extractor=feature_extractor,
        size_divisible=size_divisible,
    )

    detector = RetinaNetDetector(
        network=net,
        anchor_generator=anchor_generator,
    ).to(device)

    detector.set_atss_matcher(
        num_candidates=4,
        center_in_gt=False,
    )

    detector.set_hard_negative_sampler(
        batch_size_per_image=64,
        positive_fraction=0.5,
        pool_size=20,
        min_neg=16,
    )

    detector.set_target_keys(
        box_key="box",
        label_key="label",
    )

    detector.set_box_selector_parameters(
        score_thresh=float(cfg["score_thresh"]),
        topk_candidates_per_level=1000,
        nms_thresh=float(cfg["nms_iou"]),
        detections_per_img=100,
    )

    # Configured according to the locked protocol.
    detector.set_sliding_window_inferer(
        roi_size=cfg["patch_dhw"],
        sw_batch_size=1,
        overlap=0.25,
        mode="constant",
        sw_device=device,
        device="cpu",
    )

    return detector


def choose_case(base, rows, step, rng):
    return base.pick_vendor_balanced(rows, step, rng)


def make_patch(base, inf, cache, row, shape, stats, rng, positive):
    v, meta = base.load_case(cache, row)

    shape = np.asarray(shape, dtype=int)
    vshape = np.asarray(v.shape, dtype=int)
    maxstart = np.maximum(vshape - shape, 0)

    if positive and meta["boxes"]:
        b = rng.choice(meta["boxes"])
        a = np.asarray(b["aabb_xyz_voxel"], dtype=float)

        # XYZ -> ZYX
        center_zyx = ((a[:3] + a[3:]) / 2.0)[::-1]

        jitter = rng.uniform(-0.10, 0.10, size=3) * shape

        start = np.floor(
            center_zyx - shape / 2.0 + jitter
        ).astype(int)

        start = np.minimum(
            np.maximum(start, 0),
            maxstart,
        )
    else:
        start = np.asarray(
            [
                int(rng.integers(0, int(m) + 1))
                if m > 0 else 0
                for m in maxstart
            ],
            dtype=int,
        )

    patch = inf.crop_at(
        v,
        tuple(int(x) for x in start),
        tuple(int(x) for x in shape),
    )

    patch = base.norm(patch, stats)

    start_xyz = start[::-1].astype(float)
    shape_xyz = shape[::-1].astype(float)
    end_xyz = start_xyz + shape_xyz

    boxes_zyx = []
    labels = []

    for b in meta["boxes"]:
        a = np.asarray(b["aabb_xyz_voxel"], dtype=float)

        center_xyz = (a[:3] + a[3:]) / 2.0

        # Only boxes whose centers belong to the sampled patch
        if np.any(center_xyz < start_xyz):
            continue
        if np.any(center_xyz >= end_xyz):
            continue

        local_xyz = a.copy()
        local_xyz[:3] -= start_xyz
        local_xyz[3:] -= start_xyz

        local_xyz[:3] = np.maximum(local_xyz[:3], 0.0)
        local_xyz[3:] = np.minimum(local_xyz[3:], shape_xyz)

        if np.any(local_xyz[3:] - local_xyz[:3] <= 1.0):
            continue

        local_zyx = local_xyz[[2,1,0,5,4,3]]

        boxes_zyx.append(local_zyx.tolist())
        labels.append(int(b["region_code"][1:]) - 1)

    if boxes_zyx:
        box_t = torch.tensor(
            np.asarray(boxes_zyx, dtype=np.float32),
            dtype=torch.float32,
        )
        label_t = torch.tensor(labels, dtype=torch.int64)
    else:
        box_t = torch.zeros((0, 6), dtype=torch.float32)
        label_t = torch.zeros((0,), dtype=torch.int64)

    return patch, box_t, label_t, start, meta


def convert_patch_predictions(
    output,
    detector,
    start_zyx,
    volume_shape_zyx,
):
    boxes = output[detector.target_box_key].detach().cpu().numpy()
    labels = output[detector.target_label_key].detach().cpu().numpy()
    scores = output[detector.pred_score_key].detach().cpu().numpy()

    start_xyz = np.asarray(start_zyx[::-1], dtype=float)
    full_xyz = np.asarray(volume_shape_zyx[::-1], dtype=float)

    preds = []

    for box_zyx, label, score in zip(boxes, labels, scores):
        box_zyx = np.asarray(box_zyx, dtype=float)

        # MONAI spatial-axis standard box -> canonical XYZ
        box_xyz = box_zyx[[2,1,0,5,4,3]]

        box_xyz[:3] += start_xyz
        box_xyz[3:] += start_xyz

        box_xyz[:3] = np.maximum(box_xyz[:3], 0.0)
        box_xyz[3:] = np.minimum(box_xyz[3:], full_xyz)

        if np.any(box_xyz[3:] <= box_xyz[:3]):
            continue

        preds.append(
            {
                "score": float(score),
                "region_index": int(label),
                "box_xyz": box_xyz.tolist(),
            }
        )

    return preds


def validation_froc(
    base,
    inf,
    detector,
    cache,
    rows,
    shape,
    stride,
    stats,
    cfg,
    device,
):
    detector.eval()

    cases = []

    with torch.no_grad():
        for case_no, row in enumerate(rows, 1):
            v, meta = base.load_case(cache, row)

            candidates = []

            for z in inf.starts(v.shape[0], shape[0], stride[0]):
                for y in inf.starts(v.shape[1], shape[1], stride[1]):
                    for x in inf.starts(v.shape[2], shape[2], stride[2]):

                        patch = inf.crop_at(
                            v,
                            (z, y, x),
                            tuple(shape),
                        )

                        patch = base.norm(patch, stats)

                        image = torch.from_numpy(
                            patch[None]
                        ).float().to(device)

                        with torch.autocast(
                            "cuda",
                            dtype=torch.float16,
                        ):
                            outputs = detector([image])

                        candidates.extend(
                            convert_patch_predictions(
                                outputs[0],
                                detector,
                                np.asarray([z, y, x]),
                                v.shape,
                            )
                        )

                        del image, outputs

            preds = inf.nms(
                candidates,
                float(cfg["nms_iou"]),
                int(cfg["maximum_detections_per_case"]),
            )

            affine = np.asarray(
                meta["target_affine_xyz_to_lps"]
            )

            for p in preds:
                box = np.asarray(p["box_xyz"])
                p["center_lps"] = inf.lps(
                    affine,
                    (box[:3] + box[3:]) / 2.0,
                ).tolist()

            gts = []

            for b in meta["boxes"]:
                a = np.asarray(b["aabb_xyz_voxel"])

                gts.append(
                    {
                        "box_xyz": a.tolist(),
                        "center_lps": b["center_lps_mm"],
                        "region_index":
                            int(b["region_code"][1:]) - 1,
                    }
                )

            cases.append(
                {
                    "case_id": row["case_id"],
                    "predictions": preds,
                    "ground_truth": gts,
                }
            )

            print(
                f"VAL_CASE {case_no}/{len(rows)} "
                f"case={row['case_id']} "
                f"pred={len(preds)} gt={len(gts)}",
                flush=True,
            )

    scores = sorted(
        {
            0.0,
            1.0,
            *[
                round(p["score"], 6)
                for c in cases
                for p in c["predictions"]
            ],
        }
    )

    total = sum(
        len(c["ground_truth"])
        for c in cases
    )

    curve = []

    for th in scores:
        tp = fp = fn = 0
        errors = []

        for c in cases:
            a, b, d, e = inf.match_case(
                c["predictions"],
                c["ground_truth"],
                th,
                float(cfg["matching_iou"]),
            )

            tp += a
            fp += b
            fn += d
            errors += e

        curve.append(
            {
                "threshold": float(th),
                "sensitivity": tp / max(total, 1),
                "fp_per_volume": fp / max(len(cases), 1),
                "tp": tp,
                "fp": fp,
                "fn": fn,
                "median_center_error_mm":
                    float(np.median(errors))
                    if errors else None,
            }
        )

    points = []

    for budget in cfg["froc_budgets"]:
        eligible = [
            x for x in curve
            if x["fp_per_volume"] <= float(budget)
        ]

        best = max(
            eligible,
            key=lambda x:
                (x["sensitivity"], -x["fp_per_volume"]),
        )

        points.append(
            {
                "budget": float(budget),
                **best,
            }
        )

    return {
        "partial_froc_score": float(
            np.mean(
                [x["sensitivity"] for x in points]
            )
        ),
        "budget_points": points,
        "ground_truth_objects": total,
        "curve": curve,
        "cases": cases,
    }


def smoke_test(
    base,
    inf,
    detector,
    cache,
    optimization,
    validation,
    shape,
    stats,
    rng,
    device,
    output,
):
    detector.train()

    row = optimization[0]

    patch, boxes, labels, _, _ = make_patch(
        base, inf, cache, row,
        shape, stats, rng, True
    )

    image = torch.from_numpy(
        patch[None]
    ).float().to(device)

    targets = [
        {
            "box": boxes.to(device),
            "label": labels.to(device),
        }
    ]

    optimizer = torch.optim.SGD(
        detector.network.parameters(),
        lr=0.01,
        momentum=0.9,
        nesterov=True,
        weight_decay=3e-5,
    )

    scaler = torch.amp.GradScaler("cuda")

    optimizer.zero_grad(set_to_none=True)

    with torch.autocast("cuda", dtype=torch.float16):
        losses = detector([image], targets)
        loss = (
            losses[detector.cls_key]
            + losses[detector.box_reg_key]
        )

    if not torch.isfinite(loss):
        raise RuntimeError("Smoke positive loss is non-finite")

    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()

    positive_loss = float(loss.detach().cpu())

    # Explicit empty-target compatibility gate.
    detector.train()

    empty_image = torch.zeros_like(image)

    empty_targets = [
        {
            "box": torch.zeros(
                (0, 6),
                dtype=torch.float32,
                device=device,
            ),
            "label": torch.zeros(
                (0,),
                dtype=torch.int64,
                device=device,
            ),
        }
    ]

    optimizer.zero_grad(set_to_none=True)

    with torch.autocast("cuda", dtype=torch.float16):
        empty_losses = detector(
            [empty_image],
            empty_targets,
        )

        empty_loss = (
            empty_losses[detector.cls_key]
            + empty_losses[detector.box_reg_key]
        )

    if not torch.isfinite(empty_loss):
        raise RuntimeError("Smoke empty-target loss is non-finite")

    # Inference-only validation path test; no performance metric.
    detector.eval()

    v, _ = base.load_case(cache, validation[0])

    z = max((v.shape[0] - shape[0]) // 2, 0)
    y = max((v.shape[1] - shape[1]) // 2, 0)
    x = max((v.shape[2] - shape[2]) // 2, 0)

    p = inf.crop_at(
        v,
        (z, y, x),
        tuple(shape),
    )

    p = base.norm(p, stats)

    t = torch.from_numpy(
        p[None]
    ).float().to(device)

    with torch.no_grad(), torch.autocast(
        "cuda",
        dtype=torch.float16,
    ):
        pred = detector([t])

    report = {
        "status": "PASS",
        "test_type": "execution_only_smoke",
        "performance_interpreted": False,
        "positive_training_loss": positive_loss,
        "empty_target_loss":
            float(empty_loss.detach().cpu()),
        "inference_prediction_count":
            int(
                pred[0][detector.pred_score_key]
                .numel()
            ),
        "calibration_accessed": False,
        "outer_test_accessed": False,
        "peak_reserved_gb":
            torch.cuda.max_memory_reserved() / 1024**3,
    }

    Path(output).mkdir(parents=True, exist_ok=True)

    rp = Path(output) / "exp_c_smoke_report.json"

    rp.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(report, indent=2))
    print("EXP_C_SMOKE_PASS=true")


def main():
    ap = argparse.ArgumentParser()

    ap.add_argument("--project-root", required=True)
    ap.add_argument("--config", required=True)
    ap.add_argument("--anchor-contract", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--smoke", action="store_true")

    args = ap.parse_args()

    project = Path(args.project_root).resolve()
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)

    cfg = json.loads(
        Path(args.config).read_text()
    )

    fold = int(cfg["outer_fold"])
    seed = int(cfg["seed"])

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

    torch.backends.cudnn.benchmark = False

    rng = np.random.default_rng(seed)

    device = torch.device("cuda")

    base = load_module(
        "exp_c_base",
        project
        / "revision_helpers"
        / "train_fold0_pilot_dynamic_roles_v1.py",
    )

    inf = load_module(
        "exp_c_inf",
        project
        / "paper2_fold0_inference_package"
        / "scripts"
        / "infer_fold0_outer_test.py",
    )

    manifest = (
        project
        / "manifests"
        / "inner_split_v1"
        / "nested_partitions_v1.csv"
    )

    roles = load_roles(manifest, fold)

    optimization = roles["optimization"]
    validation = roles["validation"]

    cache = project / "outputs" / "preprocessed_v1"

    if not cache.exists():
        raise RuntimeError(
            f"Preprocessed cache missing: {cache}"
        )

    stats_path = output / "normalization_stats_exp_c.json"

    if stats_path.exists():
        stats = json.loads(stats_path.read_text())
    else:
        stats = base.fit_stats(
            cache,
            optimization,
            [],
            cfg,
            rng,
        )

        stats["normalization_scope"] = (
            "labeled_optimization_only"
        )

        stats["optimization_case_ids"] = [
            r["case_id"] for r in optimization
        ]

        stats["unlabeled_case_ids"] = []

        stats_path.write_text(
            json.dumps(stats, indent=2),
            encoding="utf-8",
        )

    if len(stats["optimization_case_ids"]) != len(optimization):
        raise RuntimeError("Normalization scope mismatch")

    anchor_xyz, anchor_zyx = read_anchor_shapes(
        args.anchor_contract,
        fold,
    )

    detector = build_detector(
        cfg,
        anchor_zyx,
        device,
    )

    shape = [
        int(v) for v in cfg["patch_dhw"]
    ]

    stride = [
        int(round(v * 0.75))
        for v in shape
    ]

    if args.smoke:
        smoke_test(
            base,
            inf,
            detector,
            cache,
            optimization,
            validation,
            shape,
            stats,
            rng,
            device,
            output,
        )
        return

    optimizer = torch.optim.SGD(
        detector.network.parameters(),
        lr=float(cfg["learning_rate"]),
        momentum=0.9,
        weight_decay=3e-5,
        nesterov=True,
    )

    scaler = torch.amp.GradScaler("cuda")

    best = -1.0
    history = []
    start_epoch = 0

    last_path = output / "checkpoint_last.pt"
    best_path = output / "checkpoint_best.pt"

    if last_path.exists():
        c = torch.load(
            last_path,
            map_location="cpu",
            weights_only=False,
        )

        detector.network.load_state_dict(c["network"])
        optimizer.load_state_dict(c["optimizer"])
        scaler.load_state_dict(c["scaler"])

        best = float(c["best"])
        history = c["history"]
        start_epoch = int(c["epoch"]) + 1

        print(
            f"RESUME epoch={start_epoch}",
            flush=True,
        )

    for epoch in range(
        start_epoch,
        int(cfg["epochs"]),
    ):
        detector.train()

        epoch_losses = []
        epoch_cls = []
        epoch_box = []

        positive_steps = 0
        random_steps = 0

        t0 = time.time()

        torch.cuda.reset_peak_memory_stats()

        for step in range(
            int(cfg["steps_per_epoch"])
        ):
            row = choose_case(
                base,
                optimization,
                step,
                rng,
            )

            positive = (
                rng.random()
                < float(cfg["positive_fraction"])
            )

            patch, boxes, labels, _, _ = make_patch(
                base,
                inf,
                cache,
                row,
                shape,
                stats,
                rng,
                positive,
            )

            if positive:
                positive_steps += 1
            else:
                random_steps += 1

            image = torch.from_numpy(
                patch[None]
            ).float().to(device)

            targets = [
                {
                    "box": boxes.to(device),
                    "label": labels.to(device),
                }
            ]

            optimizer.zero_grad(set_to_none=True)

            with torch.autocast(
                "cuda",
                dtype=torch.float16,
            ):
                losses = detector(
                    [image],
                    targets,
                )

                loss_cls = losses[
                    detector.cls_key
                ]

                loss_box = losses[
                    detector.box_reg_key
                ]

                loss = loss_cls + loss_box

            if not torch.isfinite(loss):
                raise RuntimeError(
                    f"Non-finite loss "
                    f"epoch={epoch} step={step}"
                )

            scaler.scale(loss).backward()

            scaler.unscale_(optimizer)

            torch.nn.utils.clip_grad_norm_(
                detector.network.parameters(),
                12.0,
            )

            scaler.step(optimizer)
            scaler.update()

            epoch_losses.append(
                float(loss.detach().cpu())
            )

            epoch_cls.append(
                float(loss_cls.detach().cpu())
            )

            epoch_box.append(
                float(loss_box.detach().cpu())
            )

            del image, targets, losses, loss

        do_val = (
            ((epoch + 1)
             % int(cfg["validation_every_epochs"])
             == 0)
            or
            epoch == int(cfg["epochs"]) - 1
        )

        vf = None
        score = None

        if do_val:
            vf = validation_froc(
                base,
                inf,
                detector,
                cache,
                validation,
                shape,
                stride,
                stats,
                cfg,
                device,
            )

            score = float(
                vf["partial_froc_score"]
            )

        rec = {
            "epoch": epoch,
            "mean_training_loss":
                float(np.mean(epoch_losses)),
            "mean_cls_loss":
                float(np.mean(epoch_cls)),
            "mean_box_loss":
                float(np.mean(epoch_box)),
            "positive_steps": positive_steps,
            "random_steps": random_steps,
            "validation_partial_froc": score,
            "validation_budget_points":
                vf["budget_points"]
                if vf else None,
            "seconds": time.time() - t0,
            "peak_reserved_gb":
                torch.cuda.max_memory_reserved()
                / 1024**3,
        }

        history.append(rec)

        print(
            json.dumps(rec),
            flush=True,
        )

        state = {
            "epoch": epoch,
            "network":
                detector.network.state_dict(),
            "optimizer":
                optimizer.state_dict(),
            "scaler":
                scaler.state_dict(),
            "best": best,
            "history": history,
            "config": cfg,
            "manifest_sha256":
                digest(manifest),
            "normalization_sha256":
                digest(stats_path),
            "anchor_contract_sha256":
                digest(args.anchor_contract),
            "anchor_xyz": anchor_xyz,
            "anchor_zyx_runtime":
                anchor_zyx,
        }

        torch.save(
            state,
            last_path,
        )

        if score is not None and score > best:
            best = score
            state["best"] = best

            torch.save(
                state,
                best_path,
            )

        del vf
        torch.cuda.empty_cache()

    if not best_path.exists():
        raise RuntimeError(
            "Best checkpoint was not produced"
        )

    report = {
        "status": "PASS",
        "protocol":
            "PAPER2_REVISION_R1_EXP_C_MONAI_RETINANET3D_V1",
        "implementation":
            "MONAI 1.6.0 RetinaNetDetector",
        "backbone":
            "3D ResNet-18 FPN",
        "backbone_choice_status":
            "fixed before formal performance observation",
        "outer_fold": fold,
        "repeat": int(cfg["repeat"]),
        "seed": seed,
        "epochs_completed": len(history),
        "steps_per_epoch":
            int(cfg["steps_per_epoch"]),
        "optimization_cases":
            len(optimization),
        "validation_cases":
            len(validation),
        "best_validation_partial_froc":
            best,
        "anchor_xyz_locked":
            anchor_xyz,
        "anchor_zyx_runtime":
            anchor_zyx,
        "normalization_scope":
            "labeled_optimization_only",
        "uses_unlabeled_data": False,
        "calibration_accessed": False,
        "outer_test_accessed": False,
        "history": history,
    }

    rp = output / "exp_c_formal_report.json"

    rp.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    files = [
        rp,
        stats_path,
        best_path,
        last_path,
    ]

    with open(
        output / "EXP_C_SHA256SUMS.txt",
        "w",
        encoding="utf-8",
    ) as f:
        for p in files:
            f.write(
                f"{digest(p)}  {p.name}\n"
            )

    print(json.dumps(report, indent=2))
    print("EXP_C_FORMAL_RUN_PASS=true")


if __name__ == "__main__":
    main()
