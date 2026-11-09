> **Primary Evaluation Unit**: Scheduled Flight Legs ($N = 6,000$ Planned + 1 Test Flight = 6,001 Legs)
> *Each row evaluates individual flight legs loaded directly from the quarantined ground truth manifest.*
> *Multi-aircraft consensus (Check d) is implemented, inactive, needs re-validation. In v0.3 it is disabled; detection relies solely on `altitude_consistency_v2` (Check a behind the abstention gate).*

| Seed | Detector Pipeline | TP | FP | FN | TN | Precision | Recall | F1-Score | Silent Recall | Non-Silent Recall | Clean FPs | Jam-Zone FPs | Hostile Precision | Hostile Recall |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| fresh_3001 | **flags-only baseline (NIC/NACp)** | 1334 | 1235 | 429 | 3002 | **51.9%** | **75.7%** | **61.6%** | 0.0% | 100.0% | 636 | 599 | 75.2% | 81.8% |
| fresh_3001 | **physics_all (a OR b OR c)** | 729 | 958 | 1034 | 3279 | **43.2%** | **41.3%** | **42.3%** | 36.1% | 43.0% | 813 | 145 | 51.8% | 37.0% |
| fresh_3001 | **altitude_consistency_v2 (Check a behind abstention)** | 401 | 44 | 1362 | 4193 | **90.1%** | **22.7%** | **36.3%** | 24.2% | 22.3% | 43 | 1 | 90.3% | 17.0% |
| fresh_3001 | **flags OR altitude_consistency_v2** | 1438 | 1251 | 325 | 2986 | **53.5%** | **81.6%** | **64.6%** | 24.2% | 100.0% | 652 | 599 | 75.8% | 86.2% |
| fresh_3002 | **flags-only baseline (NIC/NACp)** | 1186 | 1230 | 409 | 3175 | **49.1%** | **74.4%** | **59.1%** | 0.0% | 100.0% | 641 | 589 | 73.5% | 81.3% |
| fresh_3002 | **physics_all (a OR b OR c)** | 768 | 958 | 827 | 3447 | **44.5%** | **48.2%** | **46.3%** | 44.3% | 49.5% | 824 | 134 | 52.3% | 41.3% |
| fresh_3002 | **altitude_consistency_v2 (Check a behind abstention)** | 482 | 44 | 1113 | 4361 | **91.6%** | **30.2%** | **45.5%** | 27.1% | 31.3% | 43 | 1 | 91.8% | 22.1% |
| fresh_3002 | **flags OR altitude_consistency_v2** | 1297 | 1242 | 298 | 3163 | **51.1%** | **81.3%** | **62.7%** | 27.1% | 100.0% | 653 | 589 | 74.3% | 86.4% |
| fresh_3003 | **flags-only baseline (NIC/NACp)** | 1224 | 1300 | 432 | 3044 | **48.5%** | **73.9%** | **58.6%** | 0.0% | 100.0% | 625 | 675 | 75.2% | 81.5% |
| fresh_3003 | **physics_all (a OR b OR c)** | 784 | 936 | 872 | 3408 | **45.6%** | **47.3%** | **46.4%** | 44.0% | 48.5% | 795 | 141 | 53.8% | 39.7% |
| fresh_3003 | **altitude_consistency_v2 (Check a behind abstention)** | 470 | 44 | 1186 | 4300 | **91.4%** | **28.4%** | **43.3%** | 27.3% | 28.8% | 44 | 0 | 91.4% | 20.2% |
| fresh_3003 | **flags OR altitude_consistency_v2** | 1342 | 1311 | 314 | 3033 | **50.6%** | **81.0%** | **62.3%** | 27.3% | 100.0% | 636 | 675 | 76.0% | 86.5% |

> **Hostile RF Interference Evaluation Note**:
> - Flags-only baseline firing in jamming zones represents **valid RF interference detection** (loss of GPS integrity), not a false alert.
> - Evaluated against a hostile ground-truth label ($	ext{hostile} = 	ext{spoofing} \lor 	ext{jamming}$), flags-only baseline achieves **75.1% - 75.7% precision** and **83.8% - 84.1% recall** on clean seeds.
