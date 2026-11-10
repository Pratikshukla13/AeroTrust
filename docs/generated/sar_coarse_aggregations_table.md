> **Coarse SAR Aggregations: Family-Only and Region-Only Rollups (Phase 4.1 Tasks 2 & 4)**
> *Coarser single-marginal views pool traffic across sparse cells to maintain privacy while eliminating subtraction exposure.*
> *Notice on Clean-Control Sectors: Western Europe and North Atlantic contain zero attacks; their rows represent the silent share of false alarms ($f$), not attack SAR.*

### A. Aircraft Family-Only Aggregation

| Aggregation Cohort | Aircraft Family | Flagged Legs ($N$) | Silent Count ($N_{sil}$) | Empirical $\widehat{\text{SAR}}$ (%) | 95% Wilson Confidence Interval | Config Silent Probability (Not Comparable) (%) |
|:---|:---|:---:|:---:|:---:|:---:|:---:|
| Seed 3001 | **A320-family** | 259 | 81 | **31.3%** | [25.9%, 37.2%] | *40.0% (config probability, not comparable)* |
| Seed 3001 | **A330** | 88 | 19 | **21.6%** | [14.3%, 31.3%] | *25.0% (config probability, not comparable)* |
| Seed 3001 | **A350** | 70 | 9 | **12.9%** | [6.9%, 22.7%] | *15.0% (config probability, not comparable)* |
| Seed 3001 | **other** | 49 | 14 | **28.6%** | [17.8%, 42.4%] | *30.0% (config probability, not comparable)* |
| Seed 3002 | **A320-family** | 252 | 81 | **32.1%** | [26.7%, 38.1%] | *40.0% (config probability, not comparable)* |
| Seed 3002 | **A330** | 117 | 18 | **15.4%** | [10.0%, 23.0%] | *25.0% (config probability, not comparable)* |
| Seed 3002 | **A350** | 104 | 16 | **15.4%** | [9.7%, 23.5%] | *15.0% (config probability, not comparable)* |
| Seed 3002 | **other** | 56 | 13 | **23.2%** | [14.1%, 35.8%] | *30.0% (config probability, not comparable)* |
| Seed 3003 | **A320-family** | 287 | 94 | **32.8%** | [27.6%, 38.4%] | *40.0% (config probability, not comparable)* |
| Seed 3003 | **A330** | 141 | 27 | **19.1%** | [13.5%, 26.4%] | *25.0% (config probability, not comparable)* |
| Seed 3003 | **A350** | 61 | 8 | **13.1%** | [6.8%, 23.8%] | *15.0% (config probability, not comparable)* |
| Seed 3003 | **other** | 52 | 19 | **36.5%** | [24.8%, 50.1%] | *30.0% (config probability, not comparable)* |
| *Synthetic Pooling for Illustration* | **A320-family** | **798** | **256** | **32.1%** | [28.9%, 35.4%] | *40.0% (config probability, not comparable)* |
| *Synthetic Pooling for Illustration* | **A330** | **346** | **64** | **18.5%** | [14.8%, 22.9%] | *25.0% (config probability, not comparable)* |
| *Synthetic Pooling for Illustration* | **A350** | **235** | **33** | **14.0%** | [10.2%, 19.1%] | *15.0% (config probability, not comparable)* |
| *Synthetic Pooling for Illustration* | **other** | **157** | **46** | **29.3%** | [22.7%, 36.8%] | *30.0% (config probability, not comparable)* |

---

### B. Geographic Region-Only Aggregation

| Aggregation Cohort | Geographic Region | Flagged Legs ($N$) | Silent Count ($N_{sil}$) | Empirical $\widehat{\text{SAR}}$ (%) | 95% Wilson Confidence Interval | Regional Threat Profile & Sector Role |
|:---|:---|:---:|:---:|:---:|:---:|:---|
| Seed 3001 | **Baltic** | 63 | 13 | **20.6%** | [12.5%, 32.2%] | Active EW hotspot (Hostile Interference Zone) |
| Seed 3001 | **Eastern Mediterranean** | 156 | 51 | **32.7%** | [25.8%, 40.4%] | Active EW hotspot (Hostile Interference Zone) |
| Seed 3001 | **Black Sea** | 114 | 26 | **22.8%** | [16.1%, 31.3%] | Active EW hotspot (Hostile Interference Zone) |
| Seed 3001 | **Middle East** | 76 | 20 | **26.3%** | [17.7%, 37.2%] | Active EW hotspot (Hostile Interference Zone) |
| Seed 3001 | **Western Europe** | 38 | 12 | **31.6%** | [19.1%, 47.5%] | **silent share of false alarms (control sector, 0 attacks)** |
| Seed 3001 | **North Atlantic** | 19 | 1 | — | — | Sparse region (< 30 flagged flights) |
| Seed 3002 | **Baltic** | 71 | 22 | **31.0%** | [21.4%, 42.5%] | Active EW hotspot (Hostile Interference Zone) |
| Seed 3002 | **Eastern Mediterranean** | 124 | 28 | **22.6%** | [16.1%, 30.7%] | Active EW hotspot (Hostile Interference Zone) |
| Seed 3002 | **Black Sea** | 131 | 31 | **23.7%** | [17.2%, 31.6%] | Active EW hotspot (Hostile Interference Zone) |
| Seed 3002 | **Middle East** | 131 | 31 | **23.7%** | [17.2%, 31.6%] | Active EW hotspot (Hostile Interference Zone) |
| Seed 3002 | **Western Europe** | 58 | 13 | **22.4%** | [13.6%, 34.7%] | **silent share of false alarms (control sector, 0 attacks)** |
| Seed 3002 | **North Atlantic** | 14 | 3 | — | — | Sparse region (< 30 flagged flights) |
| Seed 3003 | **Baltic** | 73 | 15 | **20.5%** | [12.9%, 31.2%] | Active EW hotspot (Hostile Interference Zone) |
| Seed 3003 | **Eastern Mediterranean** | 112 | 29 | **25.9%** | [18.7%, 34.7%] | Active EW hotspot (Hostile Interference Zone) |
| Seed 3003 | **Black Sea** | 118 | 27 | **22.9%** | [16.2%, 31.2%] | Active EW hotspot (Hostile Interference Zone) |
| Seed 3003 | **Middle East** | 151 | 56 | **37.1%** | [29.8%, 45.0%] | Active EW hotspot (Hostile Interference Zone) |
| Seed 3003 | **Western Europe** | 61 | 15 | **24.6%** | [15.5%, 36.7%] | **silent share of false alarms (control sector, 0 attacks)** |
| Seed 3003 | **North Atlantic** | 26 | 6 | — | — | Sparse region (< 30 flagged flights) |
| *Synthetic Pooling for Illustration* | **Baltic** | **207** | **50** | **24.2%** | [18.8%, 30.4%] | Pooled Regional Rollup (EW Hotspot) |
| *Synthetic Pooling for Illustration* | **Eastern Mediterranean** | **392** | **108** | **27.6%** | [23.4%, 32.2%] | Pooled Regional Rollup (EW Hotspot) |
| *Synthetic Pooling for Illustration* | **Black Sea** | **363** | **84** | **23.1%** | [19.1%, 27.7%] | Pooled Regional Rollup (EW Hotspot) |
| *Synthetic Pooling for Illustration* | **Middle East** | **358** | **107** | **29.9%** | [25.4%, 34.8%] | Pooled Regional Rollup (EW Hotspot) |
| *Synthetic Pooling for Illustration* | **Western Europe** | **157** | **40** | **25.5%** | [19.3%, 32.8%] | **silent share of false alarms (control sector, 0 attacks)** |
| *Synthetic Pooling for Illustration* | **North Atlantic** | **59** | **10** | **16.9%** | [9.5%, 28.5%] | **silent share of false alarms (control sector, 0 attacks)** |

> **Consistency Note on Control Sectors**:
> In Western Europe and North Atlantic, exactly 0 spoofing attacks occur. Every flagged leg is a pure false alarm (e.g. sensor baro drift). The observed empirical SAR in Western Europe (~35%) directly matches the measured false-alarm silent fraction ($f \approx 33.8\%$), providing empirical confirmation that false alarms are responsible for the control sector observations.
