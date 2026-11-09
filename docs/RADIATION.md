# AeroTrust Space Radiation Exposure Model (Axis B)

> **Single Source of Truth**: This document is auto-generated directly from [`config/radiation_tables.yaml`](file:///c:/Users/ASus/Desktop/AeroTrust/config/radiation_tables.yaml).  
> **Operational Status**: All numerical factors are **illustrative placeholders** only.  
> **Literature Status**: All cited sources are **candidate, unverified** references.  
> **Non-Probability Guarantee**: Radiation index represents a relative dimensionless physical exposure multiplier ($R \ge 0.05$), never an integrity probability or threat confidence.

---

## 1. Physical Factor Multipliers (From `config/radiation_tables.yaml`)

| Parameter Category | Altitude / Cutoff / Storm Bin | Relative Multiplier | Operational Status | Candidate Public Source (Unverified) | Description / Physical Mechanism |
|:---|:---|:---:|:---:|:---|:---|
| **Altitude Shielding ($F_{alt}$)** | Up to 1,000 m | 0.05 | *illustrative placeholder* | **ICRP Publication 132** (candidate, unverified) | Atmospheric column mass depth shielding. |
| **Altitude Shielding ($F_{alt}$)** | Up to 4,000 m | 0.25 | *illustrative placeholder* | **ICRP Publication 132** (candidate, unverified) | Atmospheric column mass depth shielding. |
| **Altitude Shielding ($F_{alt}$)** | Up to 7,500 m | 0.75 | *illustrative placeholder* | **ICRP Publication 132** (candidate, unverified) | Atmospheric column mass depth shielding. |
| **Altitude Shielding ($F_{alt}$)** | Up to 9,500 m | 1.60 | *illustrative placeholder* | **ICRP Publication 132** (candidate, unverified) | Atmospheric column mass depth shielding. |
| **Altitude Shielding ($F_{alt}$)** | Up to 11,000 m | 2.40 | *illustrative placeholder* | **ICRP Publication 132** (candidate, unverified) | Atmospheric column mass depth shielding. |
| **Altitude Shielding ($F_{alt}$)** | Up to 12,500 m | 3.50 | *illustrative placeholder* | **ICRP Publication 132** (candidate, unverified) | Atmospheric column mass depth shielding. |
| **Altitude Shielding ($F_{alt}$)** | Up to 15,000 m | 4.80 | *illustrative placeholder* | **ICRP Publication 132** (candidate, unverified) | Atmospheric column mass depth shielding. |
| **Geomagnetic Cutoff ($F_{geomag}$)** | Up to 20° | 0.60 | *illustrative placeholder* | **FAA CARI-7 / EURADOS 2004-01** (candidate, unverified) | Vertical cutoff rigidity dipole deflection. |
| **Geomagnetic Cutoff ($F_{geomag}$)** | Up to 40° | 0.85 | *illustrative placeholder* | **FAA CARI-7 / EURADOS 2004-01** (candidate, unverified) | Vertical cutoff rigidity dipole deflection. |
| **Geomagnetic Cutoff ($F_{geomag}$)** | Up to 60° | 1.35 | *illustrative placeholder* | **FAA CARI-7 / EURADOS 2004-01** (candidate, unverified) | Vertical cutoff rigidity dipole deflection. |
| **Geomagnetic Cutoff ($F_{geomag}$)** | Up to 90° | 2.10 | *illustrative placeholder* | **FAA CARI-7 / EURADOS 2004-01** (candidate, unverified) | Vertical cutoff rigidity dipole deflection. |
| **Space Weather ($M_{storm}$)** | `quiet` (Kp≥0.0, Flux≥0) | 1.00 | *illustrative placeholder* | **Mertens et al. NAIRAS (2013)** (candidate, unverified) | Secondary proton cascade enhancement during GLE. |
| **Space Weather ($M_{storm}$)** | `minor_storm` (Kp≥5.0, Flux≥10) | 1.30 | *illustrative placeholder* | **Mertens et al. NAIRAS (2013)** (candidate, unverified) | Secondary proton cascade enhancement during GLE. |
| **Space Weather ($M_{storm}$)** | `moderate_storm` (Kp≥6.0, Flux≥100) | 1.85 | *illustrative placeholder* | **Mertens et al. NAIRAS (2013)** (candidate, unverified) | Secondary proton cascade enhancement during GLE. |
| **Space Weather ($M_{storm}$)** | `strong_storm` (Kp≥7.0, Flux≥1000) | 2.90 | *illustrative placeholder* | **Mertens et al. NAIRAS (2013)** (candidate, unverified) | Secondary proton cascade enhancement during GLE. |
| **Space Weather ($M_{storm}$)** | `severe_storm` (Kp≥8.0, Flux≥10000) | 4.50 | *illustrative placeholder* | **Mertens et al. NAIRAS (2013)** (candidate, unverified) | Secondary proton cascade enhancement during GLE. |

> **Phase 3.2 Single Source of Truth & Disclaimer Notice**:
> - **Single Source of Truth**: This table is dynamically rendered directly from `config/radiation_tables.yaml`. Hand-edited edits are strictly forbidden and enforced by CI tests.
> - **Placeholder Notice**: Every numerical value above is an **illustrative placeholder**. It must not be used for aircrew occupational dose accounting.
> - **Candidate Sources**: All cited scientific sources are **candidate, unverified** literature targets intended for future empirical calibration.

---

## 2. Model Architecture & Mathematical Synthesis

The instantaneous relative radiation exposure index $R(t)$ for flight segment at timestamp $t$ is computed as:

\[
R(t) = F_{\text{alt}}(h) \times F_{\text{geomag}}(\lambda_m) \times M_{\text{space\_weather}}(K_p, \Phi_p)
\]

Where:
- $F_{\text{alt}}(h)$: Altitude factor from column depth attenuation curve (*illustrative placeholder*).
- $F_{\text{geomag}}(\lambda_m)$: Geomagnetic dipole shielding based on geomagnetic latitude $\lambda_m$ computed against IGRF-13 dipole pole (80.7°N, -72.7°W) (*illustrative placeholder*).
- $M_{\text{space\_weather}}(K_p, \Phi_p)$: Solar energetic particle multiplier driven by NOAA SWPC planetary $K_p$ and 10 MeV proton flux $\Phi_p$ (*illustrative placeholder*).

---

## 3. Discrete Operational Tiers (Axis B)

Radiation index is reported strictly in discrete operational tiers, completely decoupled from Axis A hostile interference:

| Operational Level | Exposure Threshold | Description |
|:---|:---|:---|
| **`low`** | $R < 2.50$ | Nominal atmospheric cosmic ray background |
| **`moderate`** | $2.50 \le R < 5.50$ | Elevated high-altitude or polar exposure |
| **`elevated`** | $R \ge 5.50$ | Significant space-weather event or extreme high-altitude polar flight |
