> **EASA-Style Regional Ranking Importer & Rank Correlation (Pipeline Test Only)**
> *Validates the end-to-end ingestion and statistical rank-consistency check against simulated external regulatory/threat reports.*
> *Notice: Labelled STRICTLY as PIPELINE TEST ONLY. Not a real-world regulatory evaluation.*

> **Spearman Rank Correlation**: $\rho = 0.829$ ($p = 0.0416$)

| External Report Rank | Region Name | Simulated External Threat Index | Detector Flagged Legs ($N$) | Detector-Derived Rank | Alignment Status |
|:---:|:---|:---:|:---:|:---:|:---|
| 1 | **Eastern Mediterranean** | 113.80 | 143 | 1 | Aligned |
| 2 | **Baltic** | 107.69 | 57 | 4 | Displaced (Δ=2) |
| 3 | **Black Sea** | 107.40 | 111 | 2 | Displaced (Δ=-1) |
| 4 | **Middle East** | 94.89 | 75 | 3 | Displaced (Δ=-1) |
| 5 | **Western Europe** | 0.00 | 44 | 5 | Aligned |
| 6 | **North Atlantic** | 0.00 | 15 | 6 | Aligned |
