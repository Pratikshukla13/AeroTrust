> **Dataset Fingerprint**: Seed: 1337 | Flights: 5,225 | N_clean: 3,887 | N_spoof: 913 | N_jam: 427 | Config Hash: b6011043368eca73...

| Detector Pipeline | Ground Truth Labels | TP | FP | FN | TN | Precision | Recall | F1-Score |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Phase 2.5 (a OR b OR c OR d) | Old Bounding-Box Labels | 173 | 872 | 515 | 3665 | 16.6% | 25.1% | 20.0% |
| Phase 2.5 (a OR b OR c OR d) | New Manifest Ground Truth | 411 | 634 | 502 | 3678 | 39.3% | 45.0% | 42.0% |
| Phase 2.6 (Composite v2: a OR d) | Old Bounding-Box Labels | 126 | 201 | 562 | 4336 | 38.5% | 18.3% | 24.8% |
| Phase 2.6 (Composite v2: a OR d) | New Manifest Ground Truth | 216 | 111 | 697 | 4201 | 66.1% | 23.7% | 34.8% |

> **Identity Verification**: Across all rows, $TP + FP + FN + TN = 5,225$ strictly holds.
