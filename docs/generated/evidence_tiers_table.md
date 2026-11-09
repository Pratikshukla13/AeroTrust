> **Dataset Fingerprint**: Seed: 1337 | Flights: 5,225 | N_clean: 3,887 | N_spoof: 913 | N_jam: 427 | Config Hash: b6011043368eca73...

| Evidence Tier | Flights ($N$) | Share (%) | Hostile (Spoofed + Jammed) | Hostile Share (%) | Negative Pred. Value (NPV) | Spoofing-Only ($N$) | Jamming-Only ($N$) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **`no_alert`** | 2,814 | 53.86% | 310 | 11.02% | 88.98% | 238 | 73 |
| **`degraded`** | 1,480 | 28.33% | 1,004 | 67.84% | 32.16% | 655 | 350 |
| **`assured_clear`** | 929 | 17.78% | 22 | 2.37% | 97.63% | 18 | 4 |
| **`insufficient`** | 0 | 0.00% | 0 | 0.00% | 0.00% | 0 | 0 |
| **`unknown`** | 2 | 0.04% | 2 | 100.00% | 0.00% | 2 | 0 |

> **Evidence Tier Verification**:
> - Total Segmented Flights = **5,225**. Sum of tier counts: 5,225.
> - Strictly Clean flights ($N_{clean} = 3,887$) and Hostile flights ($N_{hostile} = 1,338$) reconcile with exact zero discrepancy across tiers.
