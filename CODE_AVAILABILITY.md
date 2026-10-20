# Code availability

The versioned code, configurations, protocol locks, de-identified reproducibility materials, and checksum-audited reviewer-driven evidence supporting the current Scientific Reports minor revision are publicly available at:

https://github.com/faranehzarafshaniau-debug/VendorAware-CBCT-MissingTooth-Localization

`PUBLICATION_VERSION_MANIFEST.md` records the exact SHA-256 hashes of the manuscript and Supplementary files associated with this repository snapshot. `SHA256SUMS.txt` provides file-level integrity verification for the public release.

The analysis layers are intentionally separated: the original calibration-thresholded outer-test analysis remains the locked held-out performance analysis; repeated-seed runs are developmental stability evidence; and analyses initiated after outer-test access are labelled post-lock exploratory. In particular, the physical-space versus native-voxel experiment is not described as conventionally statistically significant (five-block p = 0.0625), and the MONAI RetinaNet3D comparison is descriptive only and is not used to claim superiority.

Raw MORPH-CBCT DICOM data are not redistributed and should be obtained from the official dataset repository under its applicable terms:

https://doi.org/10.57760/sciencedb.26465
