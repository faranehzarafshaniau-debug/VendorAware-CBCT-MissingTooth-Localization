# Vendor-Aware 3D Missing-Tooth Localization in Multi-Vendor CBCT

Reproducibility materials for the Scientific Reports manuscript:

**Leakage-Controlled Evaluation of Vendor-Aware Three-Dimensional Missing-Tooth Localization in Partially Annotated Multi-Vendor Cone-Beam Computed Tomography**

Repository: https://github.com/faranehzarafshaniau-debug/VendorAware-CBCT-MissingTooth-Localization

## Release status

This repository snapshot is aligned with the minor-revision manuscript prepared on **2026-10-19**. The revision round introduced terminology/interpretation and reproducibility-documentation updates only; **no new model training, threshold selection, calibration access, or outer-test access was performed**.

The exact manuscript/Supplementary source and PDF hashes for this release are recorded in `PUBLICATION_VERSION_MANIFEST.md`.

## Purpose

This repository provides versioned code, locked configurations, reviewer-driven experiment protocols, audited results, checksums, and provenance material supporting the manuscript. It is a reproducibility release and does not redistribute the source CBCT dataset.

## Data

The study uses the public MORPH-CBCT resource described in Scientific Data:

- Feng L, Li Z, Gu Q, et al. *Adults' dental cone beam computed tomography images dataset for detecting and classifying missing teeth*. Scientific Data 13, 828 (2026).
- Article DOI: https://doi.org/10.1038/s41597-026-07156-9
- Dataset DOI: https://doi.org/10.57760/sciencedb.26465

Raw DICOM data are **not included**. Users should obtain the source data from the official repository and follow its licensing and access conditions.

## Analysis-stage terminology

To prevent protocol layers from being conflated, this release uses the following terminology consistently:

1. **Repeated-seed developmental analysis** — optimization-stability evidence using repeated fold/seed runs. These runs reuse the same cohort and are not treated as independent patient-level samples.
2. **Locked outer-test analysis** — the original calibration-thresholded held-out performance analysis. Fold-specific thresholds were selected using disjoint calibration cases and then applied unchanged to the outer-test cases.
3. **Post-lock exploratory analyses** — analyses initiated after the original outer-test results had been accessed. These include the conventional/Mean-Teacher controls, cumulative gate ablation, strict leave-one-vendor-out analysis, matched GRL isolation, physical-space versus native-voxel control, and the MONAI RetinaNet3D benchmark.

See `docs/ANALYSIS_STAGE_MAP_R2.md` for the complete crosswalk.

## Reviewer-driven experiments

Three direct reviewer-requested controls are preserved under immutable protocol/evidence records:

- **EXP-A — matched GRL isolation:** 50 formal runs / 25 matched pairs. Mean pFROC 0.887033 (GRL off) vs 0.889780 (GRL on); paired mean difference +0.002747; exact two-sided five-fold-block sign-flip p = 0.875. No material GRL-specific localization benefit was established.
- **EXP-B — physical-space vs native-voxel processing:** 50 formal runs / 25 matched pairs. Mean pFROC 0.899725 vs 0.430220; paired mean difference +0.469505; all 25 pairs favored physical-space processing; exact two-sided five-fold-block sign-flip p = 0.0625. This is reported as a **large, directionally consistent observed difference, not a conventionally statistically significant effect**.
- **EXP-C — MONAI RetinaNet3D benchmark:** 25 formal runs. Mean best validation pFROC 0.230330 ± 0.121265; median 0.196429; range 0.000000–0.500000. This is a **descriptive post-lock external-framework benchmark only** and is not used to claim architectural superiority or state-of-the-art performance.

These post-lock analyses do not replace or re-rank the originally locked outer-test analysis.

## Repository structure

- `code/` — retained preprocessing, model, training, validation, inference, baseline, and gate-ablation source snapshots.
- `reviewer_revision/protocols/` — protocol locks for EXP-A, EXP-B, and EXP-C.
- `reviewer_revision/exp_c/` — executable MONAI RetinaNet3D benchmark code and formal configurations.
- `reviewer_revision/results/` — audited result tables and summaries for EXP-A/B/C.
- `evidence/` — SHA-256-verified archive of the full reviewer-driven evidence package.
- `provenance/source_archives/` — retained source-package archives used for provenance.
- `docs/` — environment notes, analysis-stage map, release scope, and final R2 reproducibility audit.
- `PUBLICATION_VERSION_MANIFEST.md` — binding between this public release and the final minor-revision manuscript/Supplementary files.
- `SHA256SUMS.txt` — repository-file checksum manifest for this release snapshot.

## Integrity

Reviewer-experiment evidence archive SHA-256:

`692c2e9699810b51fd33c327a9f174f2a7bb7ced57eea93175d252c0d9a844d8`

Locked numerical outputs must not be edited in place. Documentation changes should be committed separately and associated with a versioned release/tag.

## Privacy and redistribution

No raw CBCT DICOM files are redistributed here. Public materials are limited to code, configurations, de-identified derived experiment outputs, audit summaries, and provenance archives.

## Citation

Citation metadata are provided in `CITATION.cff`. The article DOI should be added after publication.
