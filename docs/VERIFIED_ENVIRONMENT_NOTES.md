# Verified environment notes

These are verified core runtime facts recorded during the locked reviewer experiments; this is not presented as a complete historical pip freeze.

- Python: 3.12 series on Ubuntu 24.04 during the revision server runs.
- PyTorch: 2.7.0+cu128.
- CUDA runtime: 12.8.
- GPU: NVIDIA GeForce RTX 3080 Ti.
- MONAI (EXP-C): 1.6.0.
- torchvision (EXP-C): 0.22.0+cu128.
- NumPy (EXP-C final prelaunch freeze): 2.1.3.
- Pillow (EXP-C): 12.3.0.

The retained source packages and audited evidence archive preserve the exact experiment-specific configurations and checksums used in the revised analyses.
