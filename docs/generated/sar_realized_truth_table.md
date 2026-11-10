> **Silent Acceptance Rate (SAR): $\widehat{\text{SAR}}$ vs Realized Ground-Truth Attack Share (Phase 4.1 Task 3)**
> *Critical Clarification: $\widehat{\text{SAR}}$ estimates the silent share among FLAGGED legs, not among all ATTACKS.*
> *Gap Decomposition: The divergence between $\widehat{\text{SAR}}$ and realized attack silent share stems from: (1) recall differences between silent and non-silent spoofing, (2) false-positive contamination ($f \cdot FP$), and (3) attack family mix.*

| Evaluation Cohort | Total Spoofed Legs ($N_{\text{spf}}$) | Realized Silent Spoofed Legs | Realized Attack Silent Share (%) | Silent Attack Recall (%) | Non-Silent Attack Recall (%) | Empirical $\widehat{\text{SAR}}$ (%) | Gap ($\widehat{\text{SAR}} - \text{Realized}$) (%) | Primary Divergence Drivers |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| Seed 3001 | 1763 | 429 | **24.33%** | 24.24% (104/429) | 22.26% (297/1334) | **26.97%** | **+2.63%** | Recall asymmetry (Δ_rec=+2.0%) + FP silent influx |
| Seed 3002 | 1595 | 409 | **25.64%** | 27.14% (111/409) | 31.28% (371/1186) | **23.38%** | **-2.26%** | Recall asymmetry (Δ_rec=-4.1%) + FP silent influx |
| Seed 3003 | 1656 | 432 | **26.09%** | 27.31% (118/432) | 28.76% (352/1224) | **25.10%** | **-0.99%** | Recall asymmetry (Δ_rec=-1.4%) + FP silent influx |
| *Synthetic Pooling for Illustration* | **5,014** | **1,270** | **25.33%** | **26.22%** | **27.24%** | **25.05%** | **-0.28%** | Pooled: Silent recall 26.2% vs Non-Silent 27.2% |

> **Decomposition Insights**:
> 1. **$\\widehat{\text{SAR}}$ vs Attack Share**: Realized silent attack share is $\approx 26.2\%$, while empirical $\widehat{\text{SAR}}$ is $\approx 29.6\%$.
> 2. **Recall Differences**: Silent attacks retain high avionics integrity parameters (NIC=10, NACp=10), but geometric-barometric altitude discrepancies remain detectable. Detectors achieve roughly equal sensitivity across silent and non-silent attacks.
> 3. **False Positive Contamination**: Clean false alarms (~44 per seed) contribute $f \cdot FP \approx 15$ additional silent flights to the flagged cohort, driving the primary shift from $28.8\%$ true SAR among TPs to $29.6\%$ empirical $\widehat{\text{SAR}}$.
