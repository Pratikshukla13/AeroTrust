> **Silent Acceptance Rate (SAR) Cell-Level Table with Complementary Suppression (Phase 4.1 Task 2)**
> *Primary Privacy Rule: Any cell with fewer than 30 flagged flights ($N < 30$) is primary-suppressed.*
> *Complementary Suppression Rule: To prevent marginal subtraction attacks (recovering a suppressed cell by subtracting published cells from row/column totals), whenever a row or column contains exactly one suppressed cell, the second smallest cell in that row/column is also suppressed (`[COMPLEMENTARY SUPPRESSED]`).*
> *Counts for all suppressed cells are strictly replaced with `suppressed` (no N, no silent count published).*

| Evaluation Cohort | Aircraft Family | Geographic Region | Flagged Legs ($N$) | Silent Count ($N_{sil}$) | Empirical $\widehat{\text{SAR}}$ (%) | 95% Wilson Confidence Interval | Privacy Status |
|:---|:---|:---|:---:|:---:|:---:|:---:|:---|
| Seed 3001 | A320-family | Baltic | 37 | 7 | **18.9%** | [9.5%, 34.2%] | Published (Valid) |
| Seed 3001 | A320-family | Eastern Mediterranean | 87 | 35 | **40.2%** | [30.6%, 50.7%] | Published (Valid) |
| Seed 3001 | A320-family | Black Sea | 66 | 17 | **25.8%** | [16.7%, 37.4%] | Published (Valid) |
| Seed 3001 | A320-family | Middle East | 38 | 11 | **28.9%** | [17.0%, 44.8%] | Published (Valid) |
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
| Seed 3002 | A320-family | Baltic | 32 | 12 | **37.5%** | [22.9%, 54.7%] | Published (Valid) |
| Seed 3002 | A320-family | Eastern Mediterranean | 53 | 19 | **35.8%** | [24.3%, 49.3%] | Published (Valid) |
| Seed 3002 | A320-family | Black Sea | 63 | 18 | **28.6%** | [18.9%, 40.7%] | Published (Valid) |
| Seed 3002 | A320-family | Middle East | 67 | 21 | **31.3%** | [21.5%, 43.2%] | Published (Valid) |
| Seed 3002 | A320-family | Western Europe | suppressed | suppressed | — | — | **COMPLEMENTARY SUPPRESSED (Marginal Protection)** |
| Seed 3002 | A320-family | North Atlantic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3002 | A330 | Baltic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3002 | A330 | Eastern Mediterranean | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3002 | A330 | Black Sea | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3002 | A330 | Middle East | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3002 | A330 | Western Europe | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3002 | A330 | North Atlantic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3002 | A350 | Baltic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3002 | A350 | Eastern Mediterranean | 30 | 5 | **16.7%** | [7.3%, 33.6%] | Published (Valid) |
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
| Seed 3003 | A320-family | Baltic | 34 | 8 | **23.5%** | [12.4%, 40.0%] | Published (Valid) |
| Seed 3003 | A320-family | Eastern Mediterranean | 57 | 15 | **26.3%** | [16.6%, 39.0%] | Published (Valid) |
| Seed 3003 | A320-family | Black Sea | 71 | 23 | **32.4%** | [22.7%, 43.9%] | Published (Valid) |
| Seed 3003 | A320-family | Middle East | 86 | 36 | **41.9%** | [32.0%, 52.4%] | Published (Valid) |
| Seed 3003 | A320-family | Western Europe | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3003 | A320-family | North Atlantic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3003 | A330 | Baltic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3003 | A330 | Eastern Mediterranean | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3003 | A330 | Black Sea | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| Seed 3003 | A330 | Middle East | 32 | 9 | **28.1%** | [15.6%, 45.4%] | Published (Valid) |
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
| *Synthetic Pooling for Illustration* | A320-family | Baltic | 103 | 27 | **26.2%** | [18.7%, 35.5%] | Published (Valid) |
| *Synthetic Pooling for Illustration* | A320-family | Eastern Mediterranean | 197 | 69 | **35.0%** | [28.7%, 41.9%] | Published (Valid) |
| *Synthetic Pooling for Illustration* | A320-family | Black Sea | 200 | 58 | **29.0%** | [23.2%, 35.6%] | Published (Valid) |
| *Synthetic Pooling for Illustration* | A320-family | Middle East | 191 | 68 | **35.6%** | [29.2%, 42.6%] | Published (Valid) |
| *Synthetic Pooling for Illustration* | A320-family | Western Europe | suppressed | suppressed | — | — | **COMPLEMENTARY SUPPRESSED (Marginal Protection)** |
| *Synthetic Pooling for Illustration* | A320-family | North Atlantic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| *Synthetic Pooling for Illustration* | A330 | Baltic | 52 | 10 | **19.2%** | [10.8%, 31.9%] | Published (Valid) |
| *Synthetic Pooling for Illustration* | A330 | Eastern Mediterranean | 80 | 16 | **20.0%** | [12.7%, 30.0%] | Published (Valid) |
| *Synthetic Pooling for Illustration* | A330 | Black Sea | 81 | 12 | **14.8%** | [8.7%, 24.1%] | Published (Valid) |
| *Synthetic Pooling for Illustration* | A330 | Middle East | 71 | 16 | **22.5%** | [14.4%, 33.5%] | Published (Valid) |
| *Synthetic Pooling for Illustration* | A330 | Western Europe | suppressed | suppressed | — | — | **COMPLEMENTARY SUPPRESSED (Marginal Protection)** |
| *Synthetic Pooling for Illustration* | A330 | North Atlantic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| *Synthetic Pooling for Illustration* | A350 | Baltic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| *Synthetic Pooling for Illustration* | A350 | Eastern Mediterranean | 70 | 10 | **14.3%** | [7.9%, 24.3%] | Published (Valid) |
| *Synthetic Pooling for Illustration* | A350 | Black Sea | 46 | 4 | **8.7%** | [3.4%, 20.3%] | Published (Valid) |
| *Synthetic Pooling for Illustration* | A350 | Middle East | 60 | 8 | **13.3%** | [6.9%, 24.2%] | Published (Valid) |
| *Synthetic Pooling for Illustration* | A350 | Western Europe | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| *Synthetic Pooling for Illustration* | A350 | North Atlantic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| *Synthetic Pooling for Illustration* | other | Baltic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| *Synthetic Pooling for Illustration* | other | Eastern Mediterranean | 45 | 13 | **28.9%** | [17.7%, 43.4%] | Published (Valid) |
| *Synthetic Pooling for Illustration* | other | Black Sea | 36 | 10 | **27.8%** | [15.8%, 44.0%] | Published (Valid) |
| *Synthetic Pooling for Illustration* | other | Middle East | 36 | 15 | **41.7%** | [27.1%, 57.8%] | Published (Valid) |
| *Synthetic Pooling for Illustration* | other | Western Europe | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |
| *Synthetic Pooling for Illustration* | other | North Atlantic | suppressed | suppressed | — | — | **SUPPRESSED (< 30)** |

> **Demonstration of Marginal Subtraction Attack & Defense**:
> - **Worked Attack Example (Without Complementary Suppression)**: Suppose the marginal total for `A350` across all regions is published as $N_{\text{total}} = 85$. If 5 regional cells publish counts of $[22, 18, 15, 14, 11]$ (sum = 80) and exactly 1 cell (`North Atlantic`) is primary-suppressed ($N < 30$), an adversary solves: $N_{\text{North Atlantic}} = 85 - 80 = 5$. Thus, primary suppression alone leaks the exact suppressed count.
> - **The Complementary Defense**: By applying complementary suppression to a second cell (e.g. `Western Europe`), the adversary only observes the joint equation $x_1 + x_2 = 85 - 69 = 16$. With two unknown integer counts in one linear equation, the system has 1 degree of freedom and is algebraically underdetermined. Exact counts cannot be recovered.
