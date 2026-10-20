# Release Notes — Scientific Reports R2 Minor Revision

Release date: 2026-10-19

This release is a documentation/reproducibility alignment update corresponding to the current minor-revision manuscript. It does not add new training runs, alter locked results, reselect thresholds, revisit calibration data, or access the original outer-test cohort again.

## Changes in this release

- Added a publication-version manifest binding the repository to exact manuscript and Supplementary hashes.
- Added an explicit analysis-stage map separating repeated-seed developmental evidence, the locked outer-test analysis, and post-lock exploratory analyses.
- Preserved the conservative interpretation of the physical-space versus native-voxel control: large and directionally consistent, but not conventionally statistically significant with the exact five-block test (`p = 0.0625`).
- Preserved the MONAI RetinaNet3D comparison as a descriptive post-lock external-framework benchmark with no superiority or state-of-the-art claim.
- Updated release metadata and integrity documentation.
- Rebuilt and verified the root SHA-256 file manifest after the documentation update.

No raw DICOM data are included.
