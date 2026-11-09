> **Multi-Seed Stability & Seed Categorization**: Clean FPR & Recall Across Development, Informed, and Clean Estimate Seeds

| Evaluation Role | Seed Label | Seed Val | Flights ($N$) | N_clean | N_spoof | Clean FPs | Clean FPR (%) | Wilson 95% CI | Recall (%) | Silent Share (%) | N Events |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Development/Informed | dev (42) | 42 | 5,256 | 3,088 | 1,558 | 3 | **0.10%** | [0.03%, 0.29%] | **25.7%** | 27.3% | 64 |
| Development/Informed | test (1337) | 1337 | 5,193 | 3,340 | 1,272 | 2 | **0.06%** | [0.02%, 0.22%] | **26.0%** | 25.9% | 64 |
| Development/Informed | holdout (2024) | 2024 | 5,226 | 2,846 | 1,808 | 6 | **0.21%** | [0.10%, 0.46%] | **19.7%** | 25.6% | 64 |
| Development/Informed | fresh (2025) | 2025 | 5,283 | 3,061 | 1,559 | 5 | **0.16%** | [0.07%, 0.38%] | **22.7%** | 27.6% | 64 |
| Development/Informed | fresh (2026) | 2026 | 5,293 | 3,116 | 1,606 | 4 | **0.13%** | [0.05%, 0.33%] | **24.0%** | 26.2% | 64 |
| Development/Informed | fresh (2027) | 2027 | 5,249 | 3,124 | 1,539 | 2 | **0.06%** | [0.02%, 0.23%] | **21.4%** | 27.6% | 64 |
| **Clean Estimate** | fresh_3001 | 3001 | 5,267 | 3,081 | 1,641 | 8 | **0.26%** | [0.13%, 0.51%] | **22.5%** | 25.2% | 64 |
| **Clean Estimate** | fresh_3002 | 3002 | 5,249 | 3,235 | 1,473 | 4 | **0.12%** | [0.05%, 0.32%] | **30.1%** | 25.4% | 64 |
| **Clean Estimate** | fresh_3003 | 3003 | 5,284 | 3,128 | 1,529 | 5 | **0.16%** | [0.07%, 0.37%] | **28.7%** | 25.8% | 64 |
| **Pooled Multi-Seed Total** | **Pooled** | — | — | **28,019** | **13,985** | **39** | **0.139%** | [0.10%, 0.19%] | **24.4%** | — | — |
