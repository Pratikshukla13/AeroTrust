> [!WARNING]
> **Segment-Level Metric Warning (Inflated)**: Segment-level metrics ($N \approx 5,225$) merge turnaround legs ($\le 15$ min) into continuous tracks. A segment is labelled spoofed if ANY leg is, so a flag on a clean leg inside it counts as a true positive.

> **Analysis D1 (Clean-Leg True Positive Inflation)**:
> - Seed `fresh_3001`: 370 segment TPs total; **0** (0.00%) produced solely by flags on non-spoofed legs.
> - Seed `fresh_3002`: 444 segment TPs total; **1** (0.23%) produced solely by flags on non-spoofed legs.
> - Seed `fresh_3003`: 439 segment TPs total; **2** (0.46%) produced solely by flags on non-spoofed legs.

| Seed | Detector Pipeline | TP | FP | FN | TN | Precision | Recall | F1-Score | Silent Recall | Non-Silent Recall | FP / 1,000 Clean | Jam-Zone FPs | Clean FPs |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| fresh_3001 | **flags-only baseline (NIC/NACp)** | 1228 | 1122 | 413 | 2504 | **52.3%** | **74.8%** | **61.5%** | 0.0% | 100.0% | 187.3 | 545 | 577 |
| fresh_3001 | **physics_all (a OR b OR c)** | 629 | 418 | 1012 | 3208 | **60.1%** | **38.3%** | **46.8%** | 35.1% | 39.4% | 105.2 | 94 | 324 |
| fresh_3001 | **altitude_consistency_v2 (Check a behind abstention)** | 370 | 9 | 1271 | 3617 | **97.6%** | **22.5%** | **36.6%** | 23.7% | 22.1% | 2.6 | 1 | 8 |
| fresh_3001 | **flags OR altitude_consistency_v2** | 1326 | 1128 | 315 | 2498 | **54.0%** | **80.8%** | **64.8%** | 23.7% | 100.0% | 189.2 | 545 | 583 |
| fresh_3002 | **flags-only baseline (NIC/NACp)** | 1099 | 1109 | 374 | 2667 | **49.8%** | **74.6%** | **59.7%** | 0.0% | 100.0% | 175.6 | 541 | 568 |
| fresh_3002 | **physics_all (a OR b OR c)** | 663 | 417 | 810 | 3359 | **61.4%** | **45.0%** | **51.9%** | 42.0% | 46.0% | 100.2 | 93 | 324 |
| fresh_3002 | **altitude_consistency_v2 (Check a behind abstention)** | 444 | 5 | 1029 | 3771 | **98.9%** | **30.1%** | **46.2%** | 27.5% | 31.0% | 1.2 | 1 | 4 |
| fresh_3002 | **flags OR altitude_consistency_v2** | 1202 | 1112 | 271 | 2664 | **51.9%** | **81.6%** | **63.5%** | 27.5% | 100.0% | 176.5 | 541 | 571 |
| fresh_3003 | **flags-only baseline (NIC/NACp)** | 1134 | 1176 | 395 | 2579 | **49.1%** | **74.2%** | **59.1%** | 0.0% | 100.0% | 175.5 | 627 | 549 |
| fresh_3003 | **physics_all (a OR b OR c)** | 683 | 419 | 846 | 3336 | **62.0%** | **44.7%** | **51.9%** | 41.3% | 45.9% | 102.3 | 99 | 320 |
| fresh_3003 | **altitude_consistency_v2 (Check a behind abstention)** | 439 | 5 | 1090 | 3750 | **98.9%** | **28.7%** | **44.5%** | 27.3% | 29.2% | 1.6 | 0 | 5 |
| fresh_3003 | **flags OR altitude_consistency_v2** | 1242 | 1179 | 287 | 2576 | **51.3%** | **81.2%** | **62.9%** | 27.3% | 100.0% | 176.5 | 627 | 552 |
