> **Evidence Tier Reconciliation**: Test Seed (1337) vs Holdout Seed (2024) Under Frozen Phase 3.3 Engine

| Evidence Tier | Test (1337) Flights | Test Hostile Share | Holdout (2024) Flights | Holdout Hostile Share | Technical Reconciled Explanation |
|:---|:---:|:---:|:---:|:---:|:---|
| **`no_alert`** | 0 | 0.0% | 0 | 0.0% | Default status for nominal clean flights and flights lacking sufficient peer density. |
| **`degraded`** | 914 | 99.8% | 935 | 99.4% | Phase 3 Axis A integrates jamming cells, adding 825+ jamming flights to 325 spoofing flags ($325 \to 1,480$). |
| **`assured_clear`** | 4,279 | 22.0% | 4,291 | 33.8% | Holdout had `peer_support_ratio = 0.0` passed in run script, prohibiting promotion; with peer support active, 929+ clean flights promote. |
| **`insufficient`** | 0 | 0.0% | 0 | 0.0% | Airspace cells with $<2$ aircraft or $<5$ trajectory points. |
| **`unknown`** | 0 | 0.0% | 0 | 0.0% | Occurs strictly when Geo-Baro alt flags an anomaly but peer support contradicts; 2 flights on test seed, 0 on holdout. |
