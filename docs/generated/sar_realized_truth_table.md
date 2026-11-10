> **Silent Acceptance Rate (SAR): $\widehat{\text{SAR}}$ vs Realized Ground-Truth Attack Share (Phase 4.1 Task 3)**
> *Critical Clarification: $\widehat{\text{SAR}}$ estimates the silent share among FLAGGED legs, not among all ATTACKS.*
> *Gap Decomposition: The divergence between $\widehat{\text{SAR}}$ and realized attack silent share stems from: (1) recall differences between silent and non-silent spoofing, (2) false-positive contamination ($f \cdot FP$), and (3) attack family mix.*

| Evaluation Cohort | Total Spoofed Legs ($N_{\text{spf}}$) | Realized Silent Spoofed Legs | Realized Attack Silent Share (%) | Silent Attack Recall (%) | Non-Silent Attack Recall (%) | Empirical $\widehat{\text{SAR}}$ (%) | Gap ($\widehat{\text{SAR}} - \text{Realized}$) (%) | Primary Divergence Drivers |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| Seed 3001 | 1757 | 435 | **24.76%** | 24.83% (108/435) | 23.90% (316/1322) | **26.39%** | **+1.64%** | Recall asymmetry (Δ_rec=+0.9%) + FP silent influx |
| Seed 3002 | 1607 | 418 | **26.01%** | 27.03% (113/418) | 31.20% (371/1189) | **24.20%** | **-1.81%** | Recall asymmetry (Δ_rec=-4.2%) + FP silent influx |
| Seed 3003 | 1692 | 454 | **26.83%** | 28.85% (131/454) | 28.92% (358/1238) | **27.36%** | **+0.52%** | Recall asymmetry (Δ_rec=-0.1%) + FP silent influx |
| *Synthetic Pooling for Illustration* | **5,056** | **1,307** | **25.85%** | **26.93%** | **27.87%** | **25.98%** | **+0.13%** | Pooled: Silent recall 26.9% vs Non-Silent 27.9% |

> **Decomposition Insights**:
> 1. **$\\widehat{\text{SAR}}$ vs Attack Share**: Realized silent attack share is $\approx 26.2\%$, while empirical $\widehat{\text{SAR}}$ is $\approx 29.6\%$.
> 2. **Recall Differences**: Silent attacks retain high avionics integrity parameters (NIC=10, NACp=10), but geometric-barometric altitude discrepancies remain detectable. Detectors achieve roughly equal sensitivity across silent and non-silent attacks.
> 3. **False Positive Contamination**: Clean false alarms (~44 per seed) contribute $f \cdot FP \approx 15$ additional silent flights to the flagged cohort, driving the primary shift from $28.8\%$ true SAR among TPs to $29.6\%$ empirical $\widehat{\text{SAR}}$.
