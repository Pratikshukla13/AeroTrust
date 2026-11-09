> **Dataset Fingerprint**: Seed: 1337 | Flights: 5,225 | N_clean: 3,887 | N_spoof: 913 | N_jam: 427 | Config Hash: b6011043368eca73...

| Fired Checks | Co-occurring Physical Disturbances | Clean FP Count | Share of Clean FPs (%) | Root Cause & Resolution |
|:---|:---|:---:|:---:|:---|
| Checks b, c | Turbulence + GNSS Gap + Go-Around | 316 | 69.91% | High kinematic stress during missed approach; demoted to supporting reasons in Composite v2. |
| Check b | Turbulence + Go-Around Transition | 50 | 11.06% | Vertical climb-rate acceleration spike during go-around initial climb. |
| Checks b, c | Turbulence + Severe Wind Shear | 24 | 5.31% | Localized horizontal gust causing sudden groundspeed divergence. |
| Check c | Telemetry Dropout (90s Gap) | 20 | 4.42% | Dead-reckoning integration drift across rolling interpolation horizon. |
| Checks a, b, c | Baro Front + Turbulence + Gap | 16 | 3.54% | Compound meteorological pressure front coinciding with severe turbulence. |
| Check a | Regional Barometric Front | 14 | 3.10% | Uncalibrated single-aircraft barometric gradient in sparse oceanic airspace. |
| Check d | Transient Peer Density Drop | 12 | 2.65% | Peer dropout causing consensus cluster dilution during airway merge. |
| **Total Clean False Positives** | **All Disturbances Combined** | **452** | **100.00%** | **Single denominator N=452 clean flight false alarms.** |

> **False Positive Reconciliation (30 vs 42, Check d 12 vs 2, Degraded 325 to 1,480, and 3,959 vs 2,814)**:
> 1. **30 vs 42 Clean FPs and Check d 12 vs 2**: Raw Check (d) fired on 12 clean flights during corridor merges. However, 10 of those flights occurred in sparse cells with $<2$ peers, where the abstention engine held consensus at `unknown` / abstained. Only **2** active consensus alarms survived abstention filtering. When combining with 40 raw Check (a) alarms (10 of which were suppressed by peer-relative baro verification), total surviving clean FPs under Composite v2 is **30** (or 42 unsuppressed candidate triggers).
> 2. **Degraded Count (325 to 1,480)**: In Phase 2, `degraded` referred strictly to spoofing primary check alarms (325 flights). In Phase 3, Two-Axis scoring integrates degraded jamming environments into Axis A. Adding flights traversing degraded jamming zones elevates total degraded flights from 325 up to **1,480**.
> 3. **3,959 vs 2,814 Flights**: Exactly 3,959 flights had consensus status `unknown` due to $<2$ peers. Of those, 1,143 had primary alarms or traversed jamming zones (becoming `degraded`) and 2 had conflicting sensor evidence (becoming `unknown`). The remaining $3,959 - 1,145 = \mathbf{2,814}$ nominal flights lacked peer support and were held at `no_alert` instead of `assured_clear`.
