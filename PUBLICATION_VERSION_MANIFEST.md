# Publication Version Manifest — R2 Minor Revision

Repository: `https://github.com/faranehzarafshaniau-debug/VendorAware-CBCT-MissingTooth-Localization`  
Journal: Scientific Reports  
Manuscript: *Leakage-Controlled Evaluation of Vendor-Aware Three-Dimensional Missing-Tooth Localization in Partially Annotated Multi-Vendor Cone-Beam Computed Tomography*  
Release alignment date: `2026-10-19`

## Purpose

This manifest binds the public reproducibility release to the manuscript and Supplementary Information prepared for the current minor revision. It introduces no new experiment and changes no locked numerical result.

## Manuscript lineage

- Previously submitted portal-generated manuscript PDF SHA-256: `e2bbc1ade210fa53c98b2318e9b71c6f25fe91a81ea3b4bd94b1f40e16de7467`
- Previously submitted clean LaTeX source SHA-256: `1a548ebd82f1439dde3d88d6e8226110363516ee9c27a97b7c5454b6db100cf9`
- Previously submitted Supplementary LaTeX source SHA-256: `5169c790cb469545ffc2f9c55f33dcc884b9063a5ee3f34f3632d9673cf01d39`
- Current R2 clean LaTeX source SHA-256: `c671d6c0d29e787b17c3e130f6ad93de88b48235cb41aa052063c4d1e57dd7c1`
- Current R2 manuscript PDF SHA-256: `d60423aecefbadafe250ec9adafd9e15b3c0abe79c481896f0637cb19c2a6acf`
- Current R2 Supplementary LaTeX source SHA-256: `a2d62933e4fe9e80fe31aa586d709896860f49ca979109300b22ec8fd7f375ef`
- Current R2 Supplementary PDF SHA-256: `b78201e76c71825216dd17c4bbed4b6071cfc4e0c92d02339b90e3c39864713b`

The R2 manuscript changes terminology/interpretation and reproducibility documentation only. No new model training, threshold selection, calibration access, or outer-test access was performed.

## Evidence integrity

- Reviewer-experiment evidence archive SHA-256: `692c2e9699810b51fd33c327a9f174f2a7bb7ced57eea93175d252c0d9a844d8`
- EXP-A final audit: `PASS`, 50 reports / 25 paired comparisons; GRL-on minus GRL-off mean paired difference `+0.002747`, exact five-block p = `0.875`.
- EXP-B final audit: `PASS`, 50 reports / 25 paired comparisons; physical minus native-voxel mean paired difference `+0.469505`, `25/25` positive pairs, exact five-block p = `0.0625`.
- EXP-C final audit: `PASS`, `25/25` formal runs; mean best validation pFROC `0.230330 ± 0.121265`, median `0.196429`, range `0.000000–0.500000`.

## Interpretation lock

- The original calibration-thresholded outer-test evaluation remains the locked held-out performance analysis.
- Repeated-seed results are developmental stability analyses and are not independent patient-level evidence.
- Analyses initiated after original outer-test access are labelled post-lock exploratory.
- EXP-B is described as a large, directionally consistent observed difference, not a conventionally statistically significant effect (`p = 0.0625`).
- EXP-C is descriptive only and is not used to claim superiority or state-of-the-art performance.
- R2 contains no new experiment and does not alter the original result hierarchy.

## Repository release audit

- Root `SHA256SUMS.txt` snapshot: `202` entries verified, `0` mismatches.
- The root checksum manifest intentionally excludes itself; it covers the release files listed therein.

## Repository crosswalk

- Core workflow snapshots: `code/`
- EXP-A/B/C protocol locks: `reviewer_revision/protocols/`
- EXP-A/B/C audited outputs: `reviewer_revision/results/`
- MONAI executable/configurations: `reviewer_revision/exp_c/`
- Full revision evidence archive: `evidence/PAPER2_REVISION_EXPERIMENTS_FINAL_20261011.tar.gz`
- Analysis-stage terminology: `docs/ANALYSIS_STAGE_MAP_R2.md`
- Final release audit: `docs/FINAL_R2_REPRODUCIBILITY_AUDIT.txt`
