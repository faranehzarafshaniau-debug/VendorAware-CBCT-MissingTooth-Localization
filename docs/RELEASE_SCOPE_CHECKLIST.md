# Public release checklist — R2 final alignment

## Included and verified

- [x] Reviewer-driven EXP-A/EXP-B/EXP-C evidence archive and SHA-256 checksum.
- [x] Retained preprocessing source package.
- [x] Retained core model/smoke source package.
- [x] Retained validation-localization source package.
- [x] Retained fold-0 inference source package.
- [x] Retained pure-supervised five-fold source package.
- [x] Retained reliability-gated VR-SSL3D source/configuration package.
- [x] Retained conventional/Mean-Teacher benchmark package.
- [x] Retained gate-component ablation package.
- [x] EXP-A/B/C protocol locks and audited outputs.
- [x] Verified core runtime environment notes.
- [x] Publication-version manifest with exact R2 manuscript/Supplementary hashes.
- [x] Analysis-stage map separating developmental, locked outer-test, and post-lock exploratory evidence.
- [x] Conservative EXP-B interpretation retained (`p = 0.0625`; not conventionally statistically significant).
- [x] MONAI benchmark retained as descriptive only; no superiority/SOTA claim.
- [x] No raw DICOM data or directly identifying metadata included.
- [x] Root SHA-256 manifest rebuilt for the final R2 repository snapshot.

## Publication-stage follow-up

- [ ] After article acceptance/publication, add the final article DOI to `CITATION.cff` and README.
- [ ] Prefer creating an immutable GitHub release/tag for the publication snapshot.
