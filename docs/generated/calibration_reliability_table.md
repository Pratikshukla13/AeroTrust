> **Dataset Fingerprint**: Seed: 1337 | Flights: 5,225 | N_clean: 3,887 | N_spoof: 913 | N_jam: 427 | Config Hash: b6011043368eca73...

| Probability Bin | Total Flights ($N$) | Mean Predicted Prob | Empirical Positive Rate | Delta ($\Delta$) | Calibration Status (Rule: $|\Delta|>0.1, N\ge 30$) |
|:---|:---:|:---:|:---:|:---:|:---|
| [0.0, 0.1) | 3,745 | 0.000 | 0.068 | +0.068 | **Well-Calibrated** |
| [0.1, 0.2) | 0 | --- | --- | --- | Nominal / Zero Flights |
| [0.2, 0.3) | 1 | 0.263 | 1.000 | +0.737 | Small-N / Insufficient Sample |
| [0.3, 0.4) | 0 | --- | --- | --- | Nominal / Zero Flights |
| [0.4, 0.5) | 0 | --- | --- | --- | Nominal / Zero Flights |
| [0.5, 0.6) | 0 | --- | --- | --- | Nominal / Zero Flights |
| [0.6, 0.7) | 0 | --- | --- | --- | Nominal / Zero Flights |
| [0.7, 0.8) | 1,158 | 0.750 | 0.383 | -0.367 | **Miscalibrated** (Over-prediction) |
| [0.8, 0.9) | 0 | --- | --- | --- | Nominal / Zero Flights |
| [0.9, 1.0) | 321 | 0.992 | 0.660 | -0.332 | **Miscalibrated** (Over-prediction) |

> **Calibration Diagnostics & Brier Skill Assessment**:
> - **Brier Score**: **0.1518** (Reference baseline = **0.1442**).
> - **Brier Skill Score (BSS)**: **-0.0528**. *Assessment: Skill is weak ($BSS < 0$) relative to an optimal constant base-rate predictor.*
> - **Exposition Rule**: Because $BSS < 0$, the AeroTrust API and UI expose only evidence tiers (`assured_clear`, `no_alert`, `degraded`) and deterministic reasons, plus a raw uncalibrated field named `uncalibrated_score`.
