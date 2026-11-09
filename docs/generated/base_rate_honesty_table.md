> **Dataset Fingerprint**: Model: Composite v2 | TPR: 24.64% | Test FPR: 0.87% | Pooled FPR: 0.12% | Exact Bayes Formula

| Airspace Operational Scenario | Threat Prevalence ($p$) | Expected Precision (Single-Seed FPR = 0.87%) | Expected Precision (Pooled Multi-Seed FPR = 0.12%) | Expected False Alarms per 10k Flights | Operational Alerting Guidance |
|:---|:---:|:---:|:---:|:---:|:---|
| 0.01% (Normal Peacetime) | 0.01% | **0.3%** | **1.7%** | 13.9 | Corroboration required (do not trigger tactical cockpit warnings without independent sensor) |
| 0.10% (Border Zone) | 0.10% | **2.8%** | **15.1%** | 13.9 | Corroboration required (do not trigger tactical cockpit warnings without independent sensor) |
| 1.00% (High-Tension Zone) | 1.00% | **22.2%** | **64.1%** | 13.8 | Advisory alerting (surface as degraded confidence in flight management system) |
| 5.00% (Contested Airspace) | 5.00% | **59.8%** | **90.3%** | 13.2 | Advisory alerting (surface as degraded confidence in flight management system) |
| 17.47% (Benchmark Test Base Rate) | 17.47% | **85.7%** | **97.4%** | 11.5 | High-confidence tactical alerting (direct avoidance advisory warranted) |
| 23.00% (High-Intensity Airspace) | 23.00% | **89.4%** | **98.1%** | 10.7 | High-confidence tactical alerting (direct avoidance advisory warranted) |
| 50.00% (Active Electronic Warfare) | 50.00% | **96.6%** | **99.4%** | 7.0 | High-confidence tactical alerting (direct avoidance advisory warranted) |

> **Mathematical Derivation & Reconciled Verification**:
> Precision is derived strictly via Bayes rule: $P(\text{Spoof}|\text{Alert}) = \frac{p \cdot \text{TPR}}{p \cdot \text{TPR} + (1-p) \cdot \text{FPR} chefs}$.
> At the benchmark base rate $p = 17.47\%$, single-seed FPR = $0.87\%$, precision is **85.7%** (correcting previous typographical error of 71.2%).
> Under multi-seed pooled FPR = 0.14%, operational precision reaches **97.4%**.
