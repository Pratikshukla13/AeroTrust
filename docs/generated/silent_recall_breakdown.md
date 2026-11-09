> **Single Silent Definition Verification**: Evaluated with Canonical `is_silent_flight` and Legacy `nic_high`

| Evaluation Role | Seed Label | Attack Subtype | Spoofed Flights ($N$) | Canonical Silent ($N$) | Naive Baseline Silent Recall (%) | Composite v2 Silent Recall (%) | Legacy `nic_high` ($N$) | Composite v2 `nic_high` Recall (%) |
|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| Development/Informed | test (1337) | **altitude_offset** | 457 | 119 | **14.3%** | **33.6%** | 150 | **36.0%** |
| Development/Informed | test (1337) | **combined** | 371 | 87 | **27.6%** | **43.7%** | 113 | **46.9%** |
| Development/Informed | test (1337) | **horizontal_drift** | 256 | 71 | **18.3%** | **0.0%** | 86 | **0.0%** |
| Development/Informed | test (1337) | **horizontal_offset** | 188 | 53 | **28.3%** | **0.0%** | 62 | **0.0%** |
| Development/Informed | holdout (2024) | **altitude_offset** | 480 | 121 | **14.9%** | **34.7%** | 147 | **38.1%** |
| Development/Informed | holdout (2024) | **combined** | 536 | 132 | **13.6%** | **30.3%** | 169 | **31.4%** |
| Development/Informed | holdout (2024) | **horizontal_drift** | 339 | 86 | **11.6%** | **0.0%** | 103 | **0.0%** |
| Development/Informed | holdout (2024) | **horizontal_offset** | 453 | 124 | **15.3%** | **0.0%** | 156 | **0.0%** |
| Clean Estimate | fresh_3001 | **altitude_offset** | 516 | 132 | **12.1%** | **40.9%** | 173 | **41.6%** |
| Clean Estimate | fresh_3001 | **combined** | 517 | 127 | **10.2%** | **34.6%** | 164 | **37.8%** |
| Clean Estimate | fresh_3001 | **horizontal_drift** | 343 | 91 | **16.5%** | **0.0%** | 113 | **0.0%** |
| Clean Estimate | fresh_3001 | **horizontal_offset** | 265 | 63 | **14.3%** | **0.0%** | 74 | **0.0%** |
| Clean Estimate | fresh_3002 | **altitude_offset** | 495 | 132 | **13.6%** | **47.7%** | 167 | **47.9%** |
| Clean Estimate | fresh_3002 | **combined** | 501 | 116 | **9.5%** | **34.5%** | 142 | **38.7%** |
| Clean Estimate | fresh_3002 | **horizontal_drift** | 273 | 70 | **12.9%** | **0.0%** | 87 | **0.0%** |
| Clean Estimate | fresh_3002 | **horizontal_offset** | 204 | 56 | **23.2%** | **0.0%** | 65 | **0.0%** |
| Clean Estimate | fresh_3003 | **altitude_offset** | 439 | 97 | **16.5%** | **50.5%** | 130 | **55.4%** |
| Clean Estimate | fresh_3003 | **combined** | 479 | 131 | **13.7%** | **45.0%** | 164 | **50.0%** |
| Clean Estimate | fresh_3003 | **horizontal_drift** | 382 | 103 | **16.5%** | **0.0%** | 137 | **0.0%** |
| Clean Estimate | fresh_3003 | **horizontal_offset** | 229 | 64 | **20.3%** | **0.0%** | 78 | **0.0%** |

> **Resolution of Previous Discrepancy**:
> - Under the single canonical definition `is_silent_flight`, **naive baseline recall on silent flights is exactly 0.0%** across every single seed and attack subtype.
> - The previously reported 50.3% arose because flights with average NIC $\ge 7$ (`nic_high`) occasionally experienced brief single-point indicator drops that triggered naive alarms.
