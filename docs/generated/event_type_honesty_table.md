> **Event-Type Honesty**: Attack Subtype Recall Breakdown Across All Seeds (Dev, Test, Holdout, Informed, and Clean Estimates)

| Seed Split | Seed Val | Pipeline | Altitude Offset Recall (%) | Combined Recall (%) | Horizontal Drift Recall (%) | Horizontal Offset Recall (%) | Total Recall (%) |
|:---|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| Development/Informed (dev (42)) | 42 | **flags-only** | **74.1%** | **74.6%** | **81.7%** | **77.2%** | **76.4%** |
| Development/Informed (dev (42)) | 42 | **physics_all** | **56.5%** | **44.7%** | **36.6%** | **27.3%** | **43.2%** |
| Development/Informed (dev (42)) | 42 | **composite_v2** | **48.4%** | **37.2%** | **0.3%** | **0.0%** | **25.7%** |
| Development/Informed (test (1337)) | 1337 | **flags-only** | **77.7%** | **83.0%** | **77.3%** | **79.8%** | **79.5%** |
| Development/Informed (test (1337)) | 1337 | **physics_all** | **48.4%** | **55.5%** | **44.9%** | **20.2%** | **45.6%** |
| Development/Informed (test (1337)) | 1337 | **composite_v2** | **37.4%** | **43.1%** | **0.0%** | **0.0%** | **26.0%** |
| Development/Informed (holdout (2024)) | 2024 | **flags-only** | **78.5%** | **78.7%** | **77.6%** | **76.8%** | **78.0%** |
| Development/Informed (holdout (2024)) | 2024 | **physics_all** | **39.0%** | **47.9%** | **39.5%** | **20.5%** | **37.1%** |
| Development/Informed (holdout (2024)) | 2024 | **composite_v2** | **34.8%** | **35.4%** | **0.0%** | **0.0%** | **19.7%** |
| Development/Informed (fresh (2025)) | 2025 | **flags-only** | **77.2%** | **76.6%** | **73.5%** | **77.3%** | **76.3%** |
| Development/Informed (fresh (2025)) | 2025 | **physics_all** | **44.3%** | **58.3%** | **40.8%** | **18.8%** | **40.3%** |
| Development/Informed (fresh (2025)) | 2025 | **composite_v2** | **38.7%** | **47.0%** | **0.3%** | **0.0%** | **22.7%** |
| Development/Informed (fresh (2026)) | 2026 | **flags-only** | **78.2%** | **78.7%** | **76.3%** | **73.9%** | **77.0%** |
| Development/Informed (fresh (2026)) | 2026 | **physics_all** | **44.5%** | **48.9%** | **41.0%** | **16.2%** | **38.5%** |
| Development/Informed (fresh (2026)) | 2026 | **composite_v2** | **38.6%** | **40.7%** | **0.0%** | **0.0%** | **24.0%** |
| Development/Informed (fresh (2027)) | 2027 | **flags-only** | **75.1%** | **74.6%** | **76.4%** | **78.0%** | **75.9%** |
| Development/Informed (fresh (2027)) | 2027 | **physics_all** | **43.1%** | **50.7%** | **35.0%** | **20.1%** | **38.2%** |
| Development/Informed (fresh (2027)) | 2027 | **composite_v2** | **34.8%** | **39.4%** | **0.0%** | **0.0%** | **21.4%** |
| Clean Estimate (fresh_3001) | 3001 | **flags-only** | **77.5%** | **77.9%** | **77.8%** | **79.6%** | **78.1%** |
| Clean Estimate (fresh_3001) | 3001 | **physics_all** | **42.8%** | **43.5%** | **38.8%** | **18.9%** | **38.3%** |
| Clean Estimate (fresh_3001) | 3001 | **composite_v2** | **37.6%** | **34.0%** | **0.0%** | **0.0%** | **22.5%** |
| Clean Estimate (fresh_3002) | 3002 | **flags-only** | **77.0%** | **79.0%** | **77.7%** | **78.9%** | **78.1%** |
| Clean Estimate (fresh_3002) | 3002 | **physics_all** | **53.9%** | **51.3%** | **34.8%** | **21.6%** | **45.0%** |
| Clean Estimate (fresh_3002) | 3002 | **composite_v2** | **47.3%** | **41.9%** | **0.0%** | **0.0%** | **30.1%** |
| Clean Estimate (fresh_3003) | 3003 | **flags-only** | **81.5%** | **76.4%** | **77.5%** | **77.7%** | **78.4%** |
| Clean Estimate (fresh_3003) | 3003 | **physics_all** | **54.7%** | **51.6%** | **38.2%** | **21.8%** | **44.7%** |
| Clean Estimate (fresh_3003) | 3003 | **composite_v2** | **51.7%** | **44.3%** | **0.0%** | **0.0%** | **28.7%** |

> **Critical Disclosure on Composite v2 Capability Scope**:
> Notice that **`composite_v2` exhibits strictly 0.0% recall on `horizontal_drift` and `horizontal_offset` across every single seed**.
> Because `composite_v2` is corroborated by barometric vs geometric altimetry (Check a), attacks that displace only latitude/longitude without modifying vertical altitude produce zero vertical anomaly.
> Cross-checks for horizontal spoofing (TDoA multilateration, Mode S EHS roll angle, on-board INS fusion) are documented as **FUTURE WORK ONLY** and are not present in this release.
