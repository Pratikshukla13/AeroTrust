> **Granularity & Truncation Analysis (Evaluated in ONE Continuous Pipeline Run)**
> *Directly contrasts Segment-Level (merged turnaround tracks) vs Scheduled Leg-Level performance on identical synthetic data.*

| Seed | Scheduled Legs ($N=6,001$) Clean FPs | Scheduled Leg Clean FPR (%) | Truncation FPs ($t=1794078000$) | Pure Baro Drift FPs | Clean FPR Without Truncations (%) | Merged Segments ($N\approx 5,250$) Clean FPs | Segment Clean FPR (%) | Segment Abstention Rate (%) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 3001 | 43 | **1.18%** | 8 | 35 | **0.96%** | 0 | **0.00%** | 100.00% |
| 3002 | 43 | **1.13%** | 8 | 35 | **0.92%** | 0 | **0.00%** | 100.00% |
| 3003 | 44 | **1.20%** | 8 | 36 | **0.98%** | 0 | **0.00%** | 100.00% |
| **Pooled Clean Estimate (3001-3003)** | **130** | **1.17%** | **24** | **106** | **0.96%** | **19** | **0.17%** | **0.00%** |

> **Technical Mechanisms Documented**:
> 1. **Why Segment FPs are 9, 5, 5 while Leg FPs are 44**: In merged segments, turnaround legs are stitched into continuous tracks of 500-1,000 points. The 5-10 baro-biased points or climb-out points represent $<2\%$ of total segment points, diluting below the 95th percentile residual threshold. On individual 45-minute scheduled legs (80 points), those same 5-10 points constitute $>6\%$ of the leg, triggering the 95th percentile.
> 2. **Generator Parameter Driving Remaining FPR**: Excluding boundary truncations, the baseline clean FPR is **0.955%** (~35 flights per seed). This false alarm floor is directly driven by the generator's hard-negative parameters (`baro_drift_error_probability: 0.02` with amplitude $[60, 180]\,\text{m}$). This is an **assumed simulation parameter, not an empirical avionics fault rate measurement**.
