> **Dataset Fingerprint**: Seed: 1337 | Flights: 5,225 | N_clean: 3,887 | N_spoof: 913 | N_jam: 427 | Config Hash: b6011043368eca73...

| Jamming Evaluation Mode | Jamming TP | Jamming FP | Jamming FN | Precision | Recall | F1-Score | Coverage / Notes |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **Coverage-Conditioned Recall** (Evaluated Cells Only) | 5,997 | 8,628 | 21,366 | **41.0%** | **21.9%** | **28.6%** | Conditioned on evaluated cell-time buckets (excludes unknown). |
| **Fixed-Denominator Recall** (All Ground-Truth Jammed Airspace) | 5,997 | 8,628 | 21,911 | **41.0%** | **21.5%** | **28.2%** | Fixed denominator across all 27,908 jammed cell-time observations. |
