> **Dataset Fingerprint**: Seed: 1337 | Flights: 5,225 | N_clean: 3,887 | N_spoof: 913 | N_jam: 427 | Config Hash: b6011043368eca73...

| Attribute / Knob | Value / Specification | Definition & Operational Scope |
|:---|:---|:---|
| **Active Test Seed** | `test` = **1337** | Held-out test evaluation seed (frozen). |
| **Development Seed** | `dev` = **42** | Parameter tuning & calibration seed only. |
| **Final Holdout Seed** | `holdout` = **2024** | Clean, un-tuned confirmation seed. |
| **Config SHA256 Hash** | `b6011043368eca73...` | Deterministic SHA256 fingerprint of `config/synthetic.yaml`. |
| **Total Segmented Flights ($N$)** | **5,225** | Continuous aircraft routes evaluated by detectors. |
| **Planned Timetable Flights** | **6,001** | Raw schedule rows before turnaround stitching. |
| **Strictly Clean Flights ($N_{clean}$)** | **3,887** (74.39%) | Flights experiencing neither spoofing nor jamming. |
| **Spoofing Positives ($N_{spoof}$)** | **913** (17.47%) | Verified trajectory displacement (`applied=True`, `event_type='spoofing'`). |
| **Jamming Positives ($N_{jam}$)** | **427** (8.17%) | Flights traversing degraded interference cells (2 overlap spoofing). |
| **Total Hostile Flights ($N_{hostile}$)** | **1,338** (25.61%) | Flights experiencing either spoofing OR jamming. |
| **Calibration Base Rate ($p_{base}$)** | **0.1747** (17.47%) | Exact empirical base rate ($N_{spoof} / N = 913 / 5,225$). |
| **`attack_share` Knob** | **0.1747** (17.47%) | Fraction of flights experiencing spoofing attacks (planned timetable: 0.23). |
| **`disturbance_prevalence` Knobs** | **0.20** turb, **0.15** gap, **0.02** baro | Background atmospheric turbulence, dropouts, and barometric bias. |

> **Operational Population Definitions & Denominators (Pooled Seeds 3001-3003, Scheduled Legs $N = 18,000$)**:
> 1. **Population Definitions**:
>    - `clean`: neither spoofed nor jammed ($N_{\text{clean-only}} = 11,123$ legs across pooled seeds 3001–3003).
>    - `non-spoofed`: clean + jam-only ($N_{\text{non-spoofed}} = 12,986$ legs, of which clean-only legs: 11,123, jam-only legs: 1,863).
>    - `spoofed`: verified trajectory spoofing applied ($N_{\text{spoof}} = 5,014$ legs).
> 2. **Denominator for 1.17% False-Positive Rate**:
>    - Evaluated over the **11,123 clean-only legs** (neither spoofed nor jammed). With 130 clean false positives pooled (43 + 43 + 44), Clean $\text{FPR} = 130 / 11,123 = 1.1687\% \approx \mathbf{1.17\%}$.
>    - Over all 12,986 non-spoofed legs (including 2 jamming-zone false positives), non-spoofed $\text{FPR} = 132 / 12,986 = 1.0165\% \approx 1.02\%$.
> 3. **Denominator for Per-Seed Precision Tables**:
>    - The denominator is total flagged legs ($\text{TP} + \text{FP}$, where $\text{FP} = 44$ non-spoofed legs flagged per seed):
>      - Seed 3001: $401 / (401 + 44) = 401 / 445 = \mathbf{90.1\%}$
>      - Seed 3002: $482 / (482 + 44) = 482 / 526 = \mathbf{91.6\%}$
>      - Seed 3003: $470 / (470 + 44) = 470 / 514 = \mathbf{91.4\%}$

> **Class Definitions & Count Reconciliation (1,449 $\to$ 1,205 $\to$ 913)**:
> 1. **Exact Definition of 'Positive'**: A flight is defined as a *Spoofing Positive* if and only if its flight window intersects an active spoofing event interval where the offset was actually applied (`applied == True` and `event_type == 'spoofing'`). On the held-out test seed, exactly **913** flights meet this criterion, establishing the exact calibration base rate of **0.1747**.
> 2. **Exact Definition of 'Hostile'**: A flight is defined as *Hostile* if it experiences either spoofing OR jamming. In our test world, 913 spoofed flights and 427 jammed flights have 2 overlapping flights, yielding exactly **1,338 distinct hostile flights** (Hostile Share = 25.61%). Clean flights ($N_{clean} = 3,887$) experience neither threat.
> 3. **Consistent Reconciliation of 1,449 $\to$ 1,205 $\to$ 913**:
>    - **1,449**: In Phase 2.5/2.6, target flights were estimated via a coarse geographic bounding box. That heuristic counted all flights traversing the broad regional boundary during the event window.
>    - **1,205**: The corridor filter narrowed this to flights actually scheduled on affected airways where the injector pulse was active, matching 1,205 planned schedule legs.
>    - **913**: When consecutive timetable legs by the same airframe with turnaround under 10 minutes were stitched into continuous operational flight tracks ($N=5,225$), those 1,205 legs mapped to exactly **913 continuous segmented spoofed flights**.
