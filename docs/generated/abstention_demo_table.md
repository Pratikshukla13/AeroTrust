> **Rule-Trigger Demo, Not an Accuracy Result: Telemetry Degradation and Abstention Protocol Audit (Phase 4.2 Task 5)**
> *Validates README Section 4.3 Abstention Protocol under degraded operational scenarios. This artifact demonstrates rule triggering under stress conditions and is not an accuracy benchmark.*
> **Dataset Fingerprint**: Scenario: RULE_TRIGGER_DEMO | Seed: 9999 | Flights: 200 | N_clean: 175 | N_spoof: 25 | N_jam: 0 | Config Hash: `b6011043` | Primary Unit: Demo Flights (Never mixed with benchmark seeds)

### A. Abstention Trigger Rates by Operational Scenario & v0.3 Tier Distribution

| Operational Scenario / Rule Case | Evaluated Flights | no_alert (Clear) | flagged_altitude_inconsistency (Flagged) | jamming_degraded | insufficient (Abstained) | Abstention Rate (%) | Primary Triggered Rule |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **Short Track Fragment (3-6 pts)** | 25 | 0 | 0 | 0 | **25** | **100.0%** | `insufficient_track_points: N < 10` |
| **Oceanic Telemetry Dropout (25-min gap, 6 pts)** | 25 | 0 | 0 | 0 | **25** | **100.0%** | `insufficient_track_points: N < 10` |
| **Single Usable Check Available (< 2 independent checks)** | 25 | 0 | 0 | 0 | **25** | **100.0%** | `insufficient_independent_checks: 1 < 2` |
| **Low Confidence Checks (mean check conf < 0.35)** | 25 | 0 | 0 | 0 | **25** | **100.0%** | `low_mean_confidence: < 0.35` |
| **Conflicting Sensor Evidence (disagreement std > 0.45)** | 25 | 0 | 0 | 0 | **25** | **100.0%** | `conflicting_evidence: disagreement std > 0.45` |
| **Nominal Commercial Flight (Dual Checks, High Conf)** | 50 | 50 | 0 | 0 | **0** | **0.0%** | `None (Dual Checks Valid, Conf >= 0.80)` |
| **Genuine Altitude Inconsistency (Altitude Offset 150m)** | 25 | 0 | 25 | 0 | **0** | **0.0%** | `geo_baro_residual_exceeded > 120m` |
| **Overall Rule-Trigger Demo Suite** | **200** | **50 (25.0%)** | **25 (12.5%)** | **0 (0.0%)** | **125 (62.5%)** | **62.5%** | All 4 Section 4.3 Abstention Rules Validated |

> **Abstention Protocol Audit & Benchmark Findings**:
> 1. **Why Benchmark Seeds Showed 0.0% Abstention**: In benchmark seeds (42, 1337, 2024, 3001-3003), 100% of flight tracks represent dense commercial airway operations where:
>    - Track points per leg range from 68 to 1,010 (median 140, mean 289), exceeding the 10-point starvation threshold.
>    - Both geometric-barometric consistency and kinematic climb consistency checks are populated and valid.
>    - Mean detector confidence exceeds 0.80 across nominal and attacked flights.
>    - Sensors do not exhibit unresolvable inter-check conflict.
> 2. **Benchmark Leg Share Hitting Each Rule**: Across all 5,225 scheduled legs in the frozen benchmark dataset:
>    - `insufficient_track_points` ($N < 10$): **0.0%** (0 / 5,225 legs)
>    - `insufficient_independent_checks` (< 2 checks): **0.0%** (0 / 5,225 legs)
>    - `low_mean_confidence` ($< 0.35$): **0.0%** (0 / 5,225 legs)
>    - `conflicting_evidence` (disagreement std $> 0.45$): **0.0%** (0 / 5,225 legs)
>    - Total benchmark abstention rate: **0.0%**.
> 3. **Rule-Trigger Demo Verification**: Under simulated telemetry stress (track starvation, sensor dropouts, low SNR, and conflicting avionics), the AbstentionEngine reliably triggers **62.5% abstention (125/200)** without generating false alarms.
