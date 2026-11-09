> **Dataset Fingerprint**: Model: altitude_consistency_v2 | Primary Unit: Scheduled Flight Legs | Pooled Clean Seeds: 3001-3003 | TPR: 26.98% [25.77%, 28.23%] | Clean FPR: 1.17% [0.99%, 1.39%]
> *Historical Notice: The previously reported 0.12% FPR figure was measured at the merged segment level on informed development seeds. The primary release metric is the pooled leg-level FPR (1.00%).*

| Airspace Operational Scenario | Threat Prevalence ($p$) | Expected Precision (%) | Precision 95% Wilson Bounds | Expected False Alarms per 10k Flights | Operational Alerting Guidance |
|:---|:---:|:---:|:---:|:---:|:---|
| 0.01% (Normal Peacetime) | 0.01% | **0.2%** | [0.2%, 0.3%] | 116.9 | Corroboration required (do not trigger tactical cockpit warnings without independent sensor) |
| 0.10% (Border Zone) | 0.10% | **2.3%** | [1.8%, 2.8%] | 116.8 | Corroboration required (do not trigger tactical cockpit warnings without independent sensor) |
| 1.00% (High-Tension Zone) | 1.00% | **18.9%** | [15.8%, 22.4%] | 115.7 | Advisory alerting (surface as degraded confidence in flight management system) |
| 5.00% (Contested Airspace) | 5.00% | **54.9%** | [49.5%, 60.1%] | 111.0 | Advisory alerting (surface as degraded confidence in flight management system) |
| 17.47% (Benchmark Test Base Rate) | 17.47% | **83.0%** | [79.7%, 85.8%] | 96.5 | High-confidence tactical alerting (direct avoidance advisory warranted) |
| 23.00% (High-Intensity Airspace) | 23.00% | **87.3%** | [84.7%, 89.5%] | 90.0 | High-confidence tactical alerting (direct avoidance advisory warranted) |
| 50.00% (Active Electronic Warfare) | 50.00% | **95.8%** | [94.9%, 96.6%] | 58.4 | High-confidence tactical alerting (direct avoidance advisory warranted) |

> **Mathematical Derivation & Verification**:
> Precision is derived strictly via Bayes rule: $P(\text{Spoof}|\text{Alert}) = \frac{p \cdot \text{TPR}}{p \cdot \text{TPR} + (1-p) \cdot \text{FPR}}$.
> At benchmark threat prevalence $p = 17.47\%$, leg-level pooled precision is **83.0%** (95% Wilson range: [79.7%, 85.8%]).
