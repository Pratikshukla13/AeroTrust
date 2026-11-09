> **Scheduled Flight Leg Granularity ($N = 6,001$)**: Evaluated Across Clean Estimate Seeds (3001, 3002, 3003)
> *Constituent segments merge 632 multi-leg trajectories into continuous tracks.*

| Seed | Detector Pipeline | TP | FP | FN | TN | Precision | Recall | F1-Score | Silent Recall | Non-Silent Recall | Clean FPs | Jam-Zone FPs |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| fresh_3001 | **flags-only baseline (NIC/NACp)** | 1387 | 1235 | 376 | 3002 | **52.9%** | **78.7%** | **63.3%** | 12.4% | 100.0% | 636 | 599 |
| fresh_3001 | **physics_all (a OR b OR c OR d)** | 729 | 958 | 1034 | 3279 | **43.2%** | **41.3%** | **42.3%** | 36.1% | 43.0% | 813 | 145 |
| fresh_3001 | **composite_v2 (Corroborated: a OR d)** | 401 | 44 | 1362 | 4193 | **90.1%** | **22.7%** | **36.3%** | 24.2% | 22.3% | 43 | 1 |
| fresh_3001 | **flags OR composite_v2** | 1470 | 1251 | 293 | 2986 | **54.0%** | **83.4%** | **65.6%** | 31.7% | 100.0% | 652 | 599 |
| fresh_3002 | **flags-only baseline (NIC/NACp)** | 1233 | 1230 | 362 | 3175 | **50.1%** | **77.3%** | **60.8%** | 11.5% | 100.0% | 641 | 589 |
| fresh_3002 | **physics_all (a OR b OR c OR d)** | 768 | 958 | 827 | 3447 | **44.5%** | **48.2%** | **46.3%** | 44.3% | 49.5% | 824 | 134 |
| fresh_3002 | **composite_v2 (Corroborated: a OR d)** | 482 | 44 | 1113 | 4361 | **91.6%** | **30.2%** | **45.5%** | 27.1% | 31.3% | 43 | 1 |
| fresh_3002 | **flags OR composite_v2** | 1325 | 1242 | 270 | 3163 | **51.6%** | **83.1%** | **63.7%** | 34.0% | 100.0% | 653 | 589 |
| fresh_3003 | **flags-only baseline (NIC/NACp)** | 1286 | 1300 | 370 | 3044 | **49.7%** | **77.7%** | **60.6%** | 14.4% | 100.0% | 625 | 675 |
| fresh_3003 | **physics_all (a OR b OR c OR d)** | 784 | 936 | 872 | 3408 | **45.6%** | **47.3%** | **46.4%** | 44.0% | 48.5% | 795 | 141 |
| fresh_3003 | **composite_v2 (Corroborated: a OR d)** | 470 | 44 | 1186 | 4300 | **91.4%** | **28.4%** | **43.3%** | 27.3% | 28.8% | 44 | 0 |
| fresh_3003 | **flags OR composite_v2** | 1380 | 1311 | 276 | 3033 | **51.3%** | **83.3%** | **63.5%** | 36.1% | 100.0% | 636 | 675 |
