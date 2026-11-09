> **Coarse SAR Aggregations: Family-Only and Region-Only Rollups (Phase 4.3)**
> *Coarser aggregations pool traffic across sparse cells to overcome single-cell suppression while maintaining privacy.*
> *Generator assumption: The underlying synthetic silent probability is ~26.3% overall (`A320: 0.40, A330: 0.25, A350: 0.15, other: 0.30`).*

### A. Aircraft Family-Only Aggregation

| Aggregation Cohort | Aircraft Family | Flagged Legs ($N$) | Silent Count ($N_{sil}$) | Empirical $\widehat{\text{SAR}}$ (%) | 95% Wilson Confidence Interval | Synthetic Underlying Share (%) |
|:---|:---|:---:|:---:|:---:|:---:|:---:|
| Seed 3001 | **A320-family** | 252 | 83 | **32.9%** | [27.4%, 39.0%] | *40.0% (unvalidated)* |
| Seed 3001 | **A330** | 84 | 15 | **17.9%** | [11.1%, 27.4%] | *25.0% (unvalidated)* |
| Seed 3001 | **A350** | 62 | 9 | **14.5%** | [7.8%, 25.3%] | *15.0% (unvalidated)* |
| Seed 3001 | **other** | 47 | 13 | **27.7%** | [16.9%, 41.8%] | *30.0% (unvalidated)* |
| Seed 3002 | **A320-family** | 247 | 76 | **30.8%** | [25.3%, 36.8%] | *40.0% (unvalidated)* |
| Seed 3002 | **A330** | 119 | 18 | **15.1%** | [9.8%, 22.6%] | *25.0% (unvalidated)* |
| Seed 3002 | **A350** | 103 | 14 | **13.6%** | [8.3%, 21.5%] | *15.0% (unvalidated)* |
| Seed 3002 | **other** | 57 | 15 | **26.3%** | [16.6%, 39.0%] | *30.0% (unvalidated)* |
| Seed 3003 | **A320-family** | 272 | 84 | **30.9%** | [25.7%, 36.6%] | *40.0% (unvalidated)* |
| Seed 3003 | **A330** | 130 | 20 | **15.4%** | [10.2%, 22.6%] | *25.0% (unvalidated)* |
| Seed 3003 | **A350** | 61 | 6 | **9.8%** | [4.6%, 19.8%] | *15.0% (unvalidated)* |
| Seed 3003 | **other** | 51 | 19 | **37.3%** | [25.3%, 51.0%] | *30.0% (unvalidated)* |
| *Synthetic Pooling for Illustration* | **A320-family** | **771** | **243** | **31.5%** | [28.3%, 34.9%] | *40.0% (unvalidated)* |
| *Synthetic Pooling for Illustration* | **A330** | **333** | **53** | **15.9%** | [12.4%, 20.2%] | *25.0% (unvalidated)* |
| *Synthetic Pooling for Illustration* | **A350** | **226** | **29** | **12.8%** | [9.1%, 17.8%] | *15.0% (unvalidated)* |
| *Synthetic Pooling for Illustration* | **other** | **155** | **47** | **30.3%** | [23.6%, 38.0%] | *30.0% (unvalidated)* |

---

### B. Geographic Region-Only Aggregation

| Aggregation Cohort | Geographic Region | Flagged Legs ($N$) | Silent Count ($N_{sil}$) | Empirical $\widehat{\text{SAR}}$ (%) | 95% Wilson Confidence Interval | Regional Threat Profile |
|:---|:---|:---:|:---:|:---:|:---:|:---|
| Seed 3001 | **Baltic** | 57 | 10 | **17.5%** | [9.8%, 29.4%] | Active EW hotspot |
| Seed 3001 | **Eastern Mediterranean** | 143 | 44 | **30.8%** | [23.8%, 38.8%] | Active EW hotspot |
| Seed 3001 | **Black Sea** | 111 | 26 | **23.4%** | [16.5%, 32.1%] | Active EW hotspot |
| Seed 3001 | **Middle East** | 75 | 25 | **33.3%** | [23.7%, 44.6%] | Active EW hotspot |
| Seed 3001 | **Western Europe** | 44 | 15 | **34.1%** | [21.9%, 48.9%] | Active EW hotspot |
| Seed 3001 | **North Atlantic** | 15 | 0 | — | — | Sparse region (< 30 flagged flights) |
| Seed 3002 | **Baltic** | 70 | 21 | **30.0%** | [20.5%, 41.5%] | Active EW hotspot |
| Seed 3002 | **Eastern Mediterranean** | 117 | 25 | **21.4%** | [14.9%, 29.6%] | Active EW hotspot |
| Seed 3002 | **Black Sea** | 133 | 31 | **23.3%** | [16.9%, 31.2%] | Active EW hotspot |
| Seed 3002 | **Middle East** | 131 | 30 | **22.9%** | [16.5%, 30.8%] | Active EW hotspot |
| Seed 3002 | **Western Europe** | 60 | 13 | **21.7%** | [13.1%, 33.6%] | Active EW hotspot |
| Seed 3002 | **North Atlantic** | 15 | 3 | — | — | Sparse region (< 30 flagged flights) |
| Seed 3003 | **Baltic** | 58 | 10 | **17.2%** | [9.6%, 28.9%] | Active EW hotspot |
| Seed 3003 | **Eastern Mediterranean** | 119 | 32 | **26.9%** | [19.7%, 35.5%] | Active EW hotspot |
| Seed 3003 | **Black Sea** | 122 | 27 | **22.1%** | [15.7%, 30.3%] | Active EW hotspot |
| Seed 3003 | **Middle East** | 143 | 42 | **29.4%** | [22.5%, 37.3%] | Active EW hotspot |
| Seed 3003 | **Western Europe** | 48 | 12 | **25.0%** | [14.9%, 38.8%] | Active EW hotspot |
| Seed 3003 | **North Atlantic** | 24 | 6 | — | — | Sparse region (< 30 flagged flights) |
| *Synthetic Pooling for Illustration* | **Baltic** | **185** | **41** | **22.2%** | [16.8%, 28.7%] | Pooled Regional Rollup |
| *Synthetic Pooling for Illustration* | **Eastern Mediterranean** | **379** | **101** | **26.6%** | [22.4%, 31.3%] | Pooled Regional Rollup |
| *Synthetic Pooling for Illustration* | **Black Sea** | **366** | **84** | **23.0%** | [18.9%, 27.5%] | Pooled Regional Rollup |
| *Synthetic Pooling for Illustration* | **Middle East** | **349** | **97** | **27.8%** | [23.4%, 32.7%] | Pooled Regional Rollup |
| *Synthetic Pooling for Illustration* | **Western Europe** | **152** | **40** | **26.3%** | [20.0%, 33.8%] | Pooled Regional Rollup |
| *Synthetic Pooling for Illustration* | **North Atlantic** | **54** | **9** | **16.7%** | [9.0%, 28.7%] | Pooled Regional Rollup |
