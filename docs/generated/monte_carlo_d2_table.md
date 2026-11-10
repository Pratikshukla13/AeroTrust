> **Detector Rule Specification & Monte Carlo Analysis (Phase 4.1 Task 5)**
> *Exact Detector Rule verbatim from `backend/app/detectors/spoofing.py`:*

```python
# Exact Detector Rule (GeoBaroAltDetector):
geo = points_df['geo_alt_m'].values
baro = points_df['baro_alt_m'].values
diff = geo - baro
baseline = np.median(diff)  # Flight's own baseline over scheduled leg
residuals = np.abs(diff - baseline)
max_residual = float(np.percentile(residuals, 95.0))  # 95th percentile statistic
flag = bool(max_residual > 120.0)  # max_residual_meters from config/thresholds.yaml
# Evaluated if: len(points_df) >= 5 (min_points_required)
```

### A. 100,000 Flight Monte Carlo Simulation Results

| Evaluation Level | Simulated Cohort Size ($N$) | Flagged Flights | Flagged Fraction (%) | Empirical Simulation FPR (%) | Discrepancy Factor |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Scheduled Flight Leg** | 100,000 | 13 | **0.013%** | **0.955%** (~35 / 3,650) | 73x higher in generator |
| **Merged Flight Segment** | 50,000 | 0 | **0.000%** | **0.170%** (19 / 11,000) | Diluted to zero in MC |

> **Candidate Reasons for Discrepancy Between Pure Point-Noise Model (0.013%) and Full Generator (0.955%)**:
> 1. **Binomial Concentration in the 95th Percentile**: In an idealized per-point Bernoulli trial ($p=0.02$), a 200-point flight expects only 4 biased points (2.0%). To cross the 95th percentile, at least 5% (10 points) must be biased AND exceed the 120m threshold. By binomial tail probability, $P(\text{Binomial}(200, 0.02) \ge 10) \approx 0.00013$ ($0.013\%$).
> 2. **Short Leg Vulnerability in Full Schedule**: In the actual generator schedule, 15% of legs are short flights ($N \approx 15-30$ points). For an $N=20$ flight, just 1 or 2 biased points constitute $5-10\%$ of the flight, immediately forcing the 95th percentile above the 120m threshold.
> 3. **Non-Linear Vertical Profiles**: The full generator models climb, descent, go-arounds, and atmospheric pressure variation, creating non-stationary geo-baro residuals that interact with the median baseline.
> 4. **Boundary Truncations**: Simulation horizon cutoffs at $t=1794078000$ truncate in-progress flights into short fragments, producing 8 additional false alarms per seed (1.169% FPR with truncations vs 0.955% without).
> 5. **Segment-Level Dilution**: In merged segments (500-1,000 points), the law of large numbers concentrates point-wise bias around 2.0%, diluting residuals below the 95th percentile ($0.17\%$ in generator, $0.00\%$ in MC).
> *Notice: In strict compliance with instructions, detector logic and thresholds stay frozen at v0.3.1-claims.*
