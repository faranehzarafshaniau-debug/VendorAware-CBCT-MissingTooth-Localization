# Vendor-Aware 3D Missing-Tooth Localization in Multi-Vendor CBCT

Reproducibility materials for the Scientific Reports revision:

**Leakage-Controlled Evaluation of Vendor-Aware Three-Dimensional Missing-Tooth Localization in Partially Annotated Multi-Vendor Cone-Beam Computed Tomography**

Repository: https://github.com/faranehzarafshaniau-debug/VendorAware-CBCT-MissingTooth-Localization

## Purpose

This repository provides the versioned code, locked configurations, reviewer-driven experiment protocols, and audit summaries used to support the revised manuscript. It is a reproducibility release, not a redistribution of the source CBCT dataset.

## Data

The study uses the public MORPH-CBCT resource described in Scientific Data:

- Feng L, Li Z, Gu Q, et al. *Adults' dental cone beam computed tomography images dataset for detecting and classifying missing teeth*. Scientific Data 13, 828 (2026).
- Article DOI: https://doi.org/10.1038/s41597-026-07156-9
- Dataset repository DOI: https://doi.org/10.57760/sciencedb.26465

Raw DICOM data are **not included** in this repository. Users should obtain the source data from the official repository and follow its licensing and access conditions.

## Repository structure

- `code/` — versioned preprocessing, model, training, validation, inference, baseline, and gate-ablation source snapshots from the locked workflow.
- `reviewer_revision/protocols/` — pre-result protocol locks for the three reviewer-requested experiments.
- `reviewer_revision/exp_c/` — executable MONAI RetinaNet benchmark code and formal configurations.
- `reviewer_revision/results/` — final audit tables and summaries for EXP-A, EXP-B, and EXP-C.
- `evidence/` — SHA-256-verified archive of the full reviewer-driven evidence package.
- `provenance/source_archives/` — original source-package archives retained for provenance.
- `docs/` — release scope and verified environment notes.

## Reviewer-driven revision experiments

Three experiments were locked before formal result inspection:

- **EXP-A — matched GRL isolation:** 50 formal runs / 25 matched pairs. Mean pFROC 0.887033 (GRL off) vs 0.889780 (GRL on); paired mean difference +0.002747; exact two-sided fold-blocked sign-flip p = 0.875.
- **EXP-B — physical-space vs native-voxel processing:** 50 formal runs / 25 matched pairs. Mean pFROC 0.899725 vs 0.430220; paired mean difference +0.469505; all 25 paired runs favored physical-space processing; exact two-sided fold-blocked sign-flip p = 0.0625.
- **EXP-C — external MONAI RetinaNet3D benchmark:** 25 formal runs. Mean best validation pFROC 0.230330 ± 0.121265; median 0.196429; range 0.000000–0.500000.

These analyses are reported as reviewer-driven post-submission evidence and do not replace the originally locked outer-test analysis.

## Integrity

The full reviewer-experiment evidence archive has SHA-256:

`692c2e9699810b51fd33c327a9f174f2a7bb7ced57eea93175d252c0d9a844d8`

Do not alter locked numerical reports in place. Documentation updates should be committed separately and, after publication, preferably associated with a versioned release/tag.

## Privacy and redistribution

No raw CBCT DICOM files are redistributed here. Public materials are limited to code, configurations, de-identified derived experiment outputs, audit summaries, and provenance archives.

## Citation

Citation metadata are provided in `CITATION.cff`. The associated manuscript is currently under revision; update the citation record with the final article DOI after publication.
