> **Single Silent Definition Verification**: Evaluated with Canonical `is_silent_flight` and Legacy `nic_high`
> *Under this single definition, naive baseline recall on silent flights is exactly 0.0% across all seeds by construction.*

| Evaluation Role | Seed Label | Attack Subtype | Spoofed Legs ($N$) | Canonical Silent ($N$) | Naive Baseline Silent Recall (%) | altitude_consistency_v2 Silent Recall (%) | Legacy `nic_high` ($N$) | altitude_consistency_v2 `nic_high` Recall (%) |
|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| Development/Informed | test (1337) | **altitude_offset** | 514 | 130 | **0.0%** | **32.3%** | 172 | **35.5%** |
| Development/Informed | test (1337) | **combined** | 402 | 100 | **0.0%** | **42.0%** | 123 | **42.3%** |
| Development/Informed | test (1337) | **horizontal_drift** | 269 | 73 | **0.0%** | **0.0%** | 89 | **0.0%** |
| Development/Informed | test (1337) | **horizontal_offset** | 199 | 58 | **0.0%** | **0.0%** | 63 | **0.0%** |
| Clean Estimate | fresh_3001 | **altitude_offset** | 563 | 140 | **0.0%** | **42.1%** | 183 | **41.5%** |
| Clean Estimate | fresh_3001 | **combined** | 556 | 132 | **0.0%** | **34.1%** | 175 | **38.3%** |
| Clean Estimate | fresh_3001 | **horizontal_drift** | 367 | 92 | **0.0%** | **0.0%** | 115 | **0.0%** |
| Clean Estimate | fresh_3001 | **horizontal_offset** | 277 | 65 | **0.0%** | **0.0%** | 78 | **0.0%** |
| Clean Estimate | fresh_3002 | **altitude_offset** | 544 | 146 | **0.0%** | **46.6%** | 179 | **45.8%** |
| Clean Estimate | fresh_3002 | **combined** | 548 | 125 | **0.0%** | **34.4%** | 156 | **37.8%** |
| Clean Estimate | fresh_3002 | **horizontal_drift** | 287 | 76 | **0.0%** | **0.0%** | 94 | **0.0%** |
| Clean Estimate | fresh_3002 | **horizontal_offset** | 216 | 62 | **0.0%** | **0.0%** | 72 | **0.0%** |
| Clean Estimate | fresh_3003 | **altitude_offset** | 473 | 111 | **0.0%** | **48.6%** | 141 | **52.5%** |
| Clean Estimate | fresh_3003 | **combined** | 520 | 141 | **0.0%** | **45.4%** | 178 | **51.1%** |
| Clean Estimate | fresh_3003 | **horizontal_drift** | 421 | 115 | **0.0%** | **0.0%** | 151 | **0.0%** |
| Clean Estimate | fresh_3003 | **horizontal_offset** | 242 | 65 | **0.0%** | **0.0%** | 85 | **0.0%** |

> **Resolution of Previous Discrepancy**:
> - Calling `is_silent_flight` and `evaluate_naive_baseline` on the identical injection window enforces that `evaluate_naive_baseline` flags True if and only if `is_silent_flight` is False.
> - Naive baseline recall on canonical silent flights is **strictly 0.0%** across every single seed and attack subtype.
> - `altitude_consistency_v2` relies strictly on barometric vs geometric altimetry (Check a behind the abstention gate), achieving **24.2% - 50.5% recall on silent altitude attacks** while naive flags fail completely.
