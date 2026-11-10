> **SAR Estimation Bias Analysis: Decomposition with Measured FP Silent Fraction (Phase 4.1 Task 1)**
> *Clean false positives possess nominal ADS-B integrity (high NIC/NACp, no gaps), but random coverage dropouts (p=0.04) cause ~65% to fail silent criteria.*
> *Exact Decomposition: $\text{SAR}^* = \frac{\widehat{\text{SAR}} \cdot N - f \cdot FP}{TP}$, where $f$ is the measured silent fraction of false positives.*
> *Methodological Notice: Because $f$ cannot be directly measured in unlabelled production airspace, this adjustment is illustrative. Raw empirical $\widehat{\text{SAR}}$ is the primary reported operational number.*

| Evaluation Cohort | Flagged Legs ($N$) | True Positives ($TP$) | Clean FPs ($FP$) | Measured FP Silent Fraction $f$ (%) | Raw Empirical $\widehat{\text{SAR}}$ (%) | True $\text{SAR}^*$ Among TPs (%) | Exact Decomposed $\text{SAR}^*$ (%) | Residual Error (%) | Old Invalid $\text{SAR}_{adj}$ (%) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Seed 3001 | 466 | 424 | 42 | **35.71%** (15/42) | **26.39%** | **25.47%** | **25.47%** | **0.0000%** | 19.10% |
| Seed 3002 | 529 | 484 | 45 | **33.33%** (15/45) | **24.20%** | **23.35%** | **23.35%** | **0.0000%** | 17.15% |
| Seed 3003 | 541 | 489 | 52 | **32.69%** (17/52) | **27.36%** | **26.79%** | **26.79%** | **0.0000%** | 19.63% |
| *Synthetic Pooling for Illustration* | **1,536** | **1,397** | **139** | **33.81%** (47/139) | **25.98%** | **25.20%** | **25.20%** | **0.0000%** | 18.61% |

> **Mathematical Reconciliation & Bug Explanation**:
> 1. **Why the Old Formula Failed**: The previous precision-adjusted formula $\text{SAR}_{adj} = \frac{\widehat{\text{SAR}} - (1 - \text{Prec})}{\text{Prec}}$ mathematically assumed that 100% of false positives are silent ($f = 1.0$).
> 2. **Measured Silent Fraction**: The actual measured silent fraction among false positives is **$f \approx 33.8\%$** (Seed 3001: 35.7%, Seed 3002: 33.3%, Seed 3003: 32.7%). Clean false positives suffer random sensor dropouts ($p=0.04$) creating gaps $>60\text{s}$, causing `is_silent_flight` to return False.
> 3. **Exact Residual**: Incorporating $f$ yields exact equality with **zero residual error (0.0000%)** against the empirical ground-truth $\text{SAR}^*$.
> 4. **Unlabeled Airspace Limitation**: In unlabelled operational airspace, $f$ is unobservable without ground truth, making algebraic adjustments unreliable in production operations. Therefore, adjusted estimates are strictly illustrative, and raw empirical $\widehat{\text{SAR}}$ must be reported as the primary metric.
