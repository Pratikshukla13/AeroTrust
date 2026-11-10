> **Silent Acceptance Rate (SAR) Cell-Level Table with Complementary Suppression (Phase 4.1 Task 2)**
> *Primary Privacy Rule: Any cell with fewer than 30 flagged flights ($N < 30$) is primary-suppressed.*
> *Complementary Suppression Rule: To prevent marginal subtraction attacks (recovering a suppressed cell by subtracting published cells from row/column totals), whenever a row or column contains exactly one suppressed cell, the second smallest cell in that row/column is also suppressed (`[COMPLEMENTARY SUPPRESSED]`).*
> *Counts for all suppressed cells are strictly replaced with `suppressed` (no N, no silent count published).*

| Evaluation Cohort | Aircraft Family | Geographic Region | Flagged Legs ($N$) | Silent Count ($N_{sil}$) | Empirical $\widehat{\text{SAR}}$ (%) | 95% Wilson Confidence Interval | Privacy Status |
|:---|:---|:---|:---:|:---:|:---:|:---:|:---|
| Seed 3001 | A320-family | Baltic | 33 | 6 | **18.2%** | [8.6%, 34.4%] | Published (Valid) |
| Seed 3001 | A320-family | Eastern Mediterranean | 79 | 34 | **43.0%** | [32.7%, 54.0%] | Published (Valid) |
| Seed 3001 | A320-family | Black Sea | 63 | 18 | **28.6%** | [18.9%, 40.7%] | Published (Valid) |
| Seed 3001 | A320-family | Middle East | 45 | 15 | **33.3%** | [21.4%, 47.9%] | Published (Valid) |
| Seed 3001 | A320-family | Western Europe | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3001 | A320-family | North Atlantic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3001 | A330 | Baltic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3001 | A330 | Eastern Mediterranean | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3001 | A330 | Black Sea | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3001 | A330 | Middle East | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3001 | A330 | Western Europe | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3001 | A330 | North Atlantic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3001 | A350 | Baltic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3001 | A350 | Eastern Mediterranean | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3001 | A350 | Black Sea | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3001 | A350 | Middle East | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3001 | A350 | Western Europe | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3001 | A350 | North Atlantic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3001 | other | Baltic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3001 | other | Eastern Mediterranean | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3001 | other | Black Sea | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3001 | other | Middle East | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3001 | other | Western Europe | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3001 | other | North Atlantic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3002 | A320-family | Baltic | 32 | 11 | **34.4%** | [20.4%, 51.7%] | Published (Valid) |
| Seed 3002 | A320-family | Eastern Mediterranean | 51 | 18 | **35.3%** | [23.6%, 49.0%] | Published (Valid) |
| Seed 3002 | A320-family | Black Sea | 61 | 17 | **27.9%** | [18.2%, 40.2%] | Published (Valid) |
| Seed 3002 | A320-family | Middle East | 66 | 19 | **28.8%** | [19.3%, 40.6%] | Published (Valid) |
| Seed 3002 | A320-family | Western Europe | suppressed | suppressed | — | — | **COMPLEMENTARY SUPPRESSED (Marginal Protection)** |
| Seed 3002 | A320-family | North Atlantic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3002 | A330 | Baltic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3002 | A330 | Eastern Mediterranean | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3002 | A330 | Black Sea | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3002 | A330 | Middle East | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3002 | A330 | Western Europe | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3002 | A330 | North Atlantic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3002 | A350 | Baltic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3002 | A350 | Eastern Mediterranean | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3002 | A350 | Black Sea | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3002 | A350 | Middle East | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3002 | A350 | Western Europe | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3002 | A350 | North Atlantic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3002 | other | Baltic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3002 | other | Eastern Mediterranean | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3002 | other | Black Sea | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3002 | other | Middle East | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3002 | other | Western Europe | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3002 | other | North Atlantic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3003 | A320-family | Baltic | 30 | 6 | **20.0%** | [9.5%, 37.3%] | Published (Valid) |
| Seed 3003 | A320-family | Eastern Mediterranean | 63 | 21 | **33.3%** | [22.9%, 45.6%] | Published (Valid) |
| Seed 3003 | A320-family | Black Sea | 70 | 21 | **30.0%** | [20.5%, 41.5%] | Published (Valid) |
| Seed 3003 | A320-family | Middle East | 74 | 27 | **36.5%** | [26.4%, 47.9%] | Published (Valid) |
| Seed 3003 | A320-family | Western Europe | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3003 | A320-family | North Atlantic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3003 | A330 | Baltic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3003 | A330 | Eastern Mediterranean | 31 | 5 | **16.1%** | [7.1%, 32.6%] | Published (Valid) |
| Seed 3003 | A330 | Black Sea | 30 | 3 | **10.0%** | [3.5%, 25.6%] | Published (Valid) |
| Seed 3003 | A330 | Middle East | 36 | 6 | **16.7%** | [7.9%, 31.9%] | Published (Valid) |
| Seed 3003 | A330 | Western Europe | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3003 | A330 | North Atlantic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3003 | A350 | Baltic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3003 | A350 | Eastern Mediterranean | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3003 | A350 | Black Sea | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3003 | A350 | Middle East | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3003 | A350 | Western Europe | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3003 | A350 | North Atlantic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3003 | other | Baltic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3003 | other | Eastern Mediterranean | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3003 | other | Black Sea | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3003 | other | Middle East | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3003 | other | Western Europe | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3003 | other | North Atlantic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| *Synthetic Pooling for Illustration* | A320-family | Baltic | 95 | 23 | **24.2%** | [16.7%, 33.7%] | Published (Valid) |
| *Synthetic Pooling for Illustration* | A320-family | Eastern Mediterranean | 193 | 73 | **37.8%** | [31.3%, 44.8%] | Published (Valid) |
| *Synthetic Pooling for Illustration* | A320-family | Black Sea | 194 | 56 | **28.9%** | [22.9%, 35.6%] | Published (Valid) |
| *Synthetic Pooling for Illustration* | A320-family | Middle East | 185 | 61 | **33.0%** | [26.6%, 40.0%] | Published (Valid) |
| *Synthetic Pooling for Illustration* | A320-family | Western Europe | suppressed | suppressed | — | — | **COMPLEMENTARY SUPPRESSED (Marginal Protection)** |
| *Synthetic Pooling for Illustration* | A320-family | North Atlantic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| *Synthetic Pooling for Illustration* | A330 | Baltic | 49 | 7 | **14.3%** | [7.1%, 26.7%] | Published (Valid) |
| *Synthetic Pooling for Illustration* | A330 | Eastern Mediterranean | 80 | 10 | **12.5%** | [6.9%, 21.5%] | Published (Valid) |
| *Synthetic Pooling for Illustration* | A330 | Black Sea | 82 | 11 | **13.4%** | [7.7%, 22.4%] | Published (Valid) |
| *Synthetic Pooling for Illustration* | A330 | Middle East | 70 | 13 | **18.6%** | [11.2%, 29.2%] | Published (Valid) |
| *Synthetic Pooling for Illustration* | A330 | Western Europe | suppressed | suppressed | — | — | **COMPLEMENTARY SUPPRESSED (Marginal Protection)** |
| *Synthetic Pooling for Illustration* | A330 | North Atlantic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| *Synthetic Pooling for Illustration* | A350 | Baltic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| *Synthetic Pooling for Illustration* | A350 | Eastern Mediterranean | 67 | 9 | **13.4%** | [7.2%, 23.6%] | Published (Valid) |
| *Synthetic Pooling for Illustration* | A350 | Black Sea | 49 | 4 | **8.2%** | [3.2%, 19.2%] | Published (Valid) |
| *Synthetic Pooling for Illustration* | A350 | Middle East | 57 | 6 | **10.5%** | [4.9%, 21.1%] | Published (Valid) |
| *Synthetic Pooling for Illustration* | A350 | Western Europe | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| *Synthetic Pooling for Illustration* | A350 | North Atlantic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| *Synthetic Pooling for Illustration* | other | Baltic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| *Synthetic Pooling for Illustration* | other | Eastern Mediterranean | 39 | 9 | **23.1%** | [12.6%, 38.3%] | Published (Valid) |
| *Synthetic Pooling for Illustration* | other | Black Sea | 41 | 13 | **31.7%** | [19.6%, 47.0%] | Published (Valid) |
| *Synthetic Pooling for Illustration* | other | Middle East | 37 | 17 | **45.9%** | [31.0%, 61.6%] | Published (Valid) |
| *Synthetic Pooling for Illustration* | other | Western Europe | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| *Synthetic Pooling for Illustration* | other | North Atlantic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |

> **Demonstration of Marginal Subtraction Attack & Defense (Phase 4.2 Task 4 Worked Example)**:
> - **Real Published Cohort**: Consider `A320-family` in Seed 3001 from the published tables.
> - **Published Row Total**: $N_{\text{total}} = 252$ (from `sar_coarse_aggregations_table.md` Aircraft Family Aggregation).
> - **Published Regional Cells**: Baltic ($N=33$), Eastern Mediterranean ($N=79$), Black Sea ($N=63$), Middle East ($N=45$) sum to $33 + 79 + 63 + 45 = 220$.
> - **Remainder in Suppressed Cells**: $252 - 220 = 32$.
> - **Vulnerability Under Primary Suppression Only**: The two remaining cells in this row are `Western Europe` ($N_{\text{true}} = 25$) and `North Atlantic` ($N_{\text{true}} = 7$). If primary suppression ($N < 30$) were applied without complementary protection, leaving `Western Europe` published or isolated, an adversary could solve: $N_{\text{North Atlantic}} = 32 - 25 = 7$, completely leaking the suppressed cell.
> - **The Complementary Defense**: Under the complementary suppression protocol, BOTH `Western Europe` and `North Atlantic` are masked as `suppressed`. The attacker only observes $x_1 + x_2 = 32$. Any integer pair $(x_1, x_2)$ with $x_1 \ge 0, x_2 \ge 0$ is a mathematically valid solution (33 distinct integer solutions). Exactly 0 suppressed values can be recovered.
