> **Operational Evidence Tiers v0.3 (Pooled Clean Seeds 3001-3003, Scheduled Legs $N = 18,000$)**
> *Decoupled from Check (d) multi-aircraft consensus. Does not use `assured_clear`.*

| Evidence Tier | Scheduled Legs ($N$) | Share (%) | Hostile (Spoofed + Jammed) | Hostile Share (%) | Negative Pred. Value (NPV) | Primary Operational Role |
|:---|:---:|:---:|:---:|:---:|:---:|:---|
| **`no_alert`** | 14,654 | 81.41% | 3,661 | 24.98% | **75.02%** | Nominal trajectory; clear RF and consistent barometric altimetry. |
| **`flagged_altitude_inconsistency`** | 1,485 | 8.25% | 1,355 | 91.25% | **8.75%** | Check (a) altitude discrepancy exceeded; immediate cockpit avoidance advisory. |
| **`jamming_degraded`** | 1,861 | 10.34% | 1,861 | 100.00% | **0.00%** | Degraded GPS interference environment; caution advisory for position drift. |
| **`insufficient`** | 0 | 0.00% | 0 | 0.00% | **0.00%** | Insufficient telemetry (<5 points); system abstains. |
