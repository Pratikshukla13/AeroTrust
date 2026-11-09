> **Dataset Fingerprint**: Seed: 1337 | Flights: 5,225 | N_clean: 3,887 | N_spoof: 913 | N_jam: 427 | Config Hash: b6011043368eca73...

| Composite Architecture | Logic / Triggers | Clean FPR | Precision | Recall | F1-Score | Resistance to Turbulence & Dropouts |
|:---|:---|:---:|:---:|:---:|:---:|:---|
| **Composite v1 (Phase 2.5)** | Naive OR (a OR b OR c OR d) | 13.09% | 48.8% | 42.3% | 45.3% | Vulnerable (FPR scales linearly with wind shear & telemetry gaps) |
| **Composite v2 (Pre-Registered)** | Corroborated Primary (a OR d), b/c supporting | **0.87%** | **90.8%** | **24.6%** | **38.8%** | **Resilient (< 0.9% FPR under severe turbulence and dropouts)** |
