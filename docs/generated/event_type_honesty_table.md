> **Event-Type Honesty**: Attack Subtype Recall Breakdown Across All Seeds (Dev, Test, Holdout, Informed, and Clean Estimates)

| Seed Split | Seed Val | Pipeline | Altitude Offset Recall (%) | Combined Recall (%) | Horizontal Drift Recall (%) | Horizontal Offset Recall (%) | Total Recall (%) |
|:---|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| Development/Informed (dev (42)) | 42 | **flags-only** | **73.3%** | **72.4%** | **76.7%** | **73.7%** | **73.8%** |
| Development/Informed (dev (42)) | 42 | **physics_all** | **58.8%** | **46.9%** | **40.2%** | **33.1%** | **46.4%** |
| Development/Informed (dev (42)) | 42 | **altitude_consistency_v2** | **47.6%** | **37.2%** | **0.3%** | **0.0%** | **25.5%** |
| Development/Informed (test (1337)) | 1337 | **flags-only** | **74.7%** | **75.1%** | **72.9%** | **70.9%** | **73.9%** |
| Development/Informed (test (1337)) | 1337 | **physics_all** | **53.3%** | **58.2%** | **47.2%** | **22.1%** | **49.1%** |
| Development/Informed (test (1337)) | 1337 | **altitude_consistency_v2** | **37.0%** | **41.5%** | **0.0%** | **0.0%** | **25.8%** |
| Development/Informed (holdout (2024)) | 2024 | **flags-only** | **75.6%** | **77.2%** | **74.4%** | **72.6%** | **75.1%** |
| Development/Informed (holdout (2024)) | 2024 | **physics_all** | **43.6%** | **52.6%** | **41.8%** | **26.6%** | **41.8%** |
| Development/Informed (holdout (2024)) | 2024 | **altitude_consistency_v2** | **35.3%** | **35.3%** | **0.0%** | **0.0%** | **20.2%** |
| Development/Informed (fresh (2025)) | 2025 | **flags-only** | **73.6%** | **73.5%** | **70.2%** | **74.0%** | **72.9%** |
| Development/Informed (fresh (2025)) | 2025 | **physics_all** | **46.0%** | **61.2%** | **44.4%** | **22.0%** | **43.3%** |
| Development/Informed (fresh (2025)) | 2025 | **altitude_consistency_v2** | **37.3%** | **46.8%** | **0.3%** | **0.0%** | **22.5%** |
| Development/Informed (fresh (2026)) | 2026 | **flags-only** | **76.5%** | **76.4%** | **71.8%** | **71.0%** | **74.5%** |
| Development/Informed (fresh (2026)) | 2026 | **physics_all** | **49.2%** | **51.5%** | **42.4%** | **19.1%** | **41.9%** |
| Development/Informed (fresh (2026)) | 2026 | **altitude_consistency_v2** | **39.9%** | **40.4%** | **0.0%** | **0.0%** | **24.9%** |
| Development/Informed (fresh (2027)) | 2027 | **flags-only** | **72.6%** | **70.8%** | **74.2%** | **73.4%** | **72.6%** |
| Development/Informed (fresh (2027)) | 2027 | **physics_all** | **48.5%** | **53.0%** | **37.1%** | **25.9%** | **42.4%** |
| Development/Informed (fresh (2027)) | 2027 | **altitude_consistency_v2** | **36.2%** | **38.7%** | **0.0%** | **0.0%** | **22.0%** |
| Clean Estimate (fresh_3001) | 3001 | **flags-only** | **75.1%** | **76.3%** | **74.9%** | **76.5%** | **75.7%** |
| Clean Estimate (fresh_3001) | 3001 | **physics_all** | **45.6%** | **46.2%** | **42.2%** | **21.7%** | **41.3%** |
| Clean Estimate (fresh_3001) | 3001 | **altitude_consistency_v2** | **37.7%** | **34.0%** | **0.0%** | **0.0%** | **22.7%** |
| Clean Estimate (fresh_3002) | 3002 | **flags-only** | **73.2%** | **77.2%** | **73.5%** | **71.3%** | **74.4%** |
| Clean Estimate (fresh_3002) | 3002 | **physics_all** | **56.4%** | **54.4%** | **38.0%** | **25.0%** | **48.2%** |
| Clean Estimate (fresh_3002) | 3002 | **altitude_consistency_v2** | **47.2%** | **41.1%** | **0.0%** | **0.0%** | **30.2%** |
| Clean Estimate (fresh_3003) | 3003 | **flags-only** | **76.5%** | **72.9%** | **72.7%** | **73.1%** | **73.9%** |
| Clean Estimate (fresh_3003) | 3003 | **physics_all** | **56.7%** | **52.9%** | **42.5%** | **25.6%** | **47.3%** |
| Clean Estimate (fresh_3003) | 3003 | **altitude_consistency_v2** | **51.6%** | **43.5%** | **0.0%** | **0.0%** | **28.4%** |

> **Critical Disclosure on altitude_consistency_v2 Capability Scope**:
> Notice that **`altitude_consistency_v2` exhibits strictly 0.0% recall on `horizontal_drift` and `horizontal_offset` across every single seed**.
> Because `altitude_consistency_v2` relies strictly on barometric vs geometric altimetry (Check a behind the abstention gate), attacks that displace only latitude/longitude without modifying vertical altitude produce zero vertical anomaly.
> Multi-aircraft consensus (Check d) is implemented, inactive, needs re-validation. Cross-checks for horizontal spoofing (TDoA multilateration, Mode S EHS roll angle, on-board INS fusion) are documented as **FUTURE WORK ONLY**.
