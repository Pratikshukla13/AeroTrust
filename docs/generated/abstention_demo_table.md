> **Sparse-Coverage Abstention Protocol Demonstration (Phase 4.1 Task 7)**
> *Validates README Section 4.3 Abstention Protocol under operational telemetry degradation.*
> **Dataset Fingerprint**: Scenario: SPARSE_COVERAGE_DEMO | Seed: 9999 | Flights: 200 | N_clean: 200 | N_spoof: 0 | N_jam: 0 | Config Hash: `b6011043` | Primary Unit: Demo Flights (Never mixed with benchmark seeds)

### A. Abstention Trigger Rates & Tier Distribution

| Operational Archetype | Evaluated Flights | Tier 1 (Clear) | Tier 2 (Hostile / Flagged) | Tier 3 (Abstained / Unknown) | Abstention Rate (%) | Primary Abstention Trigger |
|:---|:---:|:---:|:---:|:---:|:---:|:---|
| **Short Fragments (3-6 points)** | 50 | 0 | 0 | **50** | **100.0%** | `insufficient_track_points: N < 10` |
| **Sparse Low-Point Tracks (5-8 points)** | 50 | 0 | 0 | **50** | **100.0%** | `insufficient_track_points: N < 10` |
| **Oceanic Telemetry Dropout (25-min gap, 6 pts)** | 50 | 0 | 0 | **50** | **100.0%** | `insufficient_track_points: N < 10` |
| **Nominal ADS-B Flight (30 consecutive points)** | 50 | 50 | 0 | **0** | **0.0%** | `None (Sufficient Points & Dual Checks)` |
| **Overall Sparse Demo Dataset** | **200** | **50 (25.0%)** | **0 (0.0%)** | **150 (75.0%)** | **75.0%** | Condition 1: Track Point Starvation |

> **Abstention Protocol Audit Findings**:
> 1. **Why Benchmark Seeds Showed 0.0% Abstention**: Benchmark seeds (42, 1337, 2024, 3001-3003) simulate dense commercial radar corridors where 100% of flights exceed the 10-point threshold.
> 2. **Demonstrated Triggering**: When evaluated against sparse oceanic dropouts, short radar fragments, and data starvation, AbstentionEngine reliably triggers **75.0% abstention (150/200)** without generating false alarms.
