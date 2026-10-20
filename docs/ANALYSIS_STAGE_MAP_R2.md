# Analysis-stage map for the R2 manuscript

This document records the terminology used in the manuscript, Supplementary Information, and repository so that different protocol stages are not conflated.

## 1. Repeated-seed developmental analysis

Purpose: quantify optimization stability across repeated fold/seed runs during development.

Key manuscript values:
- Pure supervised: mean pFROC `0.890 ± 0.087`
- Vendor-adversarial: `0.899 ± 0.086`
- Reliability-gated VR-SSL3D: `0.872 ± 0.106`

Interpretation: these repeated fold/seed outcomes reuse the same underlying cohort and are not independent patient-level clinical samples.

## 2. Locked outer-test analysis

Purpose: provide the original held-out localization evaluation after fold-specific operating-point calibration.

Key locked operating point:
- Vendor-adversarial sensitivity `0.793` (95% CI `0.697–0.880`)
- False positives per volume `0.458` (95% CI `0.301–0.639`)

Interpretation: this remains the locked held-out performance analysis. Post-lock experiments do not replace or re-rank it as a confirmatory comparison.

## 3. Post-lock exploratory analyses

The following analyses were initiated after original outer-test access and are therefore exploratory:

- conventional 3D versus confidence-only Mean-Teacher benchmark;
- cumulative gate-component ablation;
- strict leave-one-vendor-out evaluation;
- matched GRL-off versus GRL-on isolation (EXP-A);
- physical-space versus native-voxel control (EXP-B);
- MONAI RetinaNet3D external-framework benchmark (EXP-C).

### EXP-A interpretation
GRL-on minus GRL-off mean paired difference: `+0.002747`; exact five-block p = `0.875`. No material localization advantage attributable specifically to the GRL branch was established.

### EXP-B interpretation
Physical minus native-voxel mean paired difference: `+0.469505`; all `25/25` pairs favored physical processing; exact five-block p = `0.0625`. This is a large and directionally consistent observed difference, **not** a conventionally statistically significant effect.

### EXP-C interpretation
MONAI RetinaNet3D mean best validation pFROC: `0.230330 ± 0.121265`; median `0.196429`; range `0.000000–0.500000`. This is a descriptive external-framework reference only; it is not used to claim that the study framework is superior or state of the art.

## R2 change control

The R2 minor revision contains terminology/interpretation and reproducibility-documentation changes only. No new training, threshold selection, calibration access, or outer-test access was performed.
