> **SAR Estimation Bias Analysis: Impact of Clean False Positives (Phase 4.4)**
> *Clean false positives (~44 per seed) possess nominal avionics integrity and are classified as silent, systematically inflating raw empirical $\widehat{\text{SAR}}$.*

| Evaluation Cohort | Flagged Legs ($N$) | True Positives ($TP$) | Clean FPs ($FP$) | Precision (%) | Raw Empirical $\widehat{\text{SAR}}$ (%) | True $\text{SAR}^*$ Among TPs (%) | Precision-Adjusted $\text{SAR}_{adj}$ (%) | Estimation Inflation $\Delta$ (%) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Seed 3001 | 445 | 401 | 44 | 90.1% | **26.97%** | **25.94%** | **18.95%** | +1.03% |
| Seed 3002 | 526 | 482 | 44 | 91.6% | **23.38%** | **23.03%** | **16.39%** | +0.35% |
| Seed 3003 | 514 | 470 | 44 | 91.4% | **25.10%** | **25.11%** | **18.09%** | +-0.01% |
| *Synthetic Pooling for Illustration* | **1,485** | **1,353** | **132** | **91.1%** | **25.05%** | **24.61%** | **17.74%** | **+0.44%** |

> **Critical Methodological Notice on Precision Adjustment**:
> The algebraic precision adjustment $\text{SAR}_{adj} = \frac{\widehat{\text{SAR}} - (1 - \text{Prec})}{\text{Prec}}$ assumes exact knowledge of the precision of the flagged set.
> - **In Unlabeled Production Operations, the Adjustment is Unreliable**: Operational airspace does not furnish ground-truth $TP$ and $FP$ labels. Relying on calibrated or model-predicted precision introduces secondary estimation variance that can severely distort or produce negative SAR estimates in sparse regional cells.
> - **Operational Recommendation**: Raw empirical $\widehat{\text{SAR}}$ should be reported as an upper bound, alongside cell sample size $N$ and Wilson confidence intervals, rather than applying fragile post-hoc algebraic deflators.
