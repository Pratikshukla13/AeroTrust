> **Dataset Fingerprint**: Seed: 2024 | Flights: 5,226 | N_clean: 2,846 | N_spoof: 1,808 | N_jam: 572 | Config Hash: b6011043368eca73...

| Detector Pipeline | TP | FP | FN | TN | Precision | Recall | F1-Score | Silent Recall | Non-Silent Recall | FP / 1,000 Clean | Jam-Zone FPs | Clean FPs |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **flags-only baseline (NIC/NACp)** | 1410 | 1121 | 398 | 2297 | **55.7%** | **78.0%** | **65.0%** | **14.0%** | 100.0% | 192.9 | 572 | 549 |
| **physics_all (a OR b OR c OR d)** | 671 | 392 | 1137 | 3026 | **63.1%** | **37.1%** | **46.7%** | **31.3%** | 39.1% | 97.7 | 114 | 278 |
| **composite_v2 (Corroborated: a OR d)** | 357 | 6 | 1451 | 3412 | **98.3%** | **19.7%** | **32.9%** | **17.7%** | 20.4% | 2.1 | 0 | 6 |
| **flags OR composite_v2** | 1469 | 1125 | 339 | 2293 | **56.6%** | **81.2%** | **66.7%** | **26.8%** | 100.0% | 194.3 | 572 | 553 |

> **Holdout Integrity & Diff Analysis**:
> - **Initial Run (TP 427, FP 91)**: In preliminary testing, Check (d) consensus incorrectly included the target aircraft's own flags as peer evidence (`peer_anomalies[p_icao] = res_a['flag'] or res_c['flag']`), causing self-referential consensus triggering (+70 TP, +85 FP).
> - **Frozen Run (TP 357, FP 6)**: When consensus was properly gated, spurious alarms disappeared (FPs dropped from 91 to 6).
> - **Methodological Remediation**: Because this fix was analyzed after inspecting seed 2024 results, seed 2024 (and 42, 1337, 2025-2027) was designated **Development/Informed**. Fresh seeds **3001, 3002, 3003** were generated and evaluated ONCE as the clean unbiased estimate.
