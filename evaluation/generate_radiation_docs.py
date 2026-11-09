"""AeroTrust Radiation Documentation Generator (Phase 3.2).

Single Source of Truth: Reads config/radiation_tables.yaml and generates:
- docs/RADIATION.md
- docs/generated/radiation_sources_table.md

Labels every parameter value as 'illustrative placeholder'.
Marks every scientific source as 'candidate, unverified'.
"""

from pathlib import Path
import yaml


def generate_radiation_docs():
    yaml_path = Path("config") / "radiation_tables.yaml"
    with open(yaml_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    alt_bins = cfg.get("altitude_bins", [])
    geomag_bins = cfg.get("geomag_latitude_bins", []) or cfg.get("geomagnetic_latitude_bins", [])
    sw_tiers = cfg.get("space_weather_tiers", [])
    pole = cfg.get("geomagnetic_pole", {})
    exp_levels = cfg.get("exposure_levels", {})

    # 1. Generate docs/generated/radiation_sources_table.md
    md_table = [
        "| Parameter Category | Altitude / Cutoff / Storm Bin | Relative Multiplier | Operational Status | Candidate Public Source (Unverified) | Description / Physical Mechanism |",
        "|:---|:---|:---:|:---:|:---|:---|",
    ]

    for b in alt_bins:
        md_table.append(
            f"| **Altitude Shielding ($F_{{alt}}$)** | Up to {b['alt_max_m']:,.0f} m | {b['factor']:.2f} | *illustrative placeholder* | **ICRP Publication 132** (candidate, unverified) | Atmospheric column mass depth shielding. |"
        )

    for b in geomag_bins:
        md_table.append(
            f"| **Geomagnetic Cutoff ($F_{{geomag}}$)** | Up to {b['max_geomag_lat_deg']:.0f}° | {b['factor']:.2f} | *illustrative placeholder* | **FAA CARI-7 / EURADOS 2004-01** (candidate, unverified) | Vertical cutoff rigidity dipole deflection. |"
        )

    for b in sw_tiers:
        md_table.append(
            f"| **Space Weather ($M_{{storm}}$)** | `{b['name']}` (Kp≥{b['min_kp']:.1f}, Flux≥{b['min_proton_flux_10mev']:.0f}) | {b['multiplier']:.2f} | *illustrative placeholder* | **Mertens et al. NAIRAS (2013)** (candidate, unverified) | Secondary proton cascade enhancement during GLE. |"
        )

    md_table.append("\n> **Phase 3.2 Single Source of Truth & Disclaimer Notice**:")
    md_table.append("> - **Single Source of Truth**: This table is dynamically rendered directly from `config/radiation_tables.yaml`. Hand-edited edits are strictly forbidden and enforced by CI tests.")
    md_table.append("> - **Placeholder Notice**: Every numerical value above is an **illustrative placeholder**. It must not be used for aircrew occupational dose accounting.")
    md_table.append("> - **Candidate Sources**: All cited scientific sources are **candidate, unverified** literature targets intended for future empirical calibration.")

    out_table = Path("docs") / "generated" / "radiation_sources_table.md"
    out_table.write_text("\n".join(md_table) + "\n", encoding="utf-8")
    print(f"Generated {out_table}")

    # 2. Generate docs/RADIATION.md
    rad_md = f"""# AeroTrust Space Radiation Exposure Model (Axis B)

> **Single Source of Truth**: This document is auto-generated directly from [`config/radiation_tables.yaml`](file:///c:/Users/ASus/Desktop/AeroTrust/config/radiation_tables.yaml).  
> **Operational Status**: All numerical factors are **illustrative placeholders** only.  
> **Literature Status**: All cited sources are **candidate, unverified** references.  
> **Non-Probability Guarantee**: Radiation index represents a relative dimensionless physical exposure multiplier ($R \\ge 0.05$), never an integrity probability or threat confidence.

---

## 1. Physical Factor Multipliers (From `config/radiation_tables.yaml`)

{"\n".join(md_table)}

---

## 2. Model Architecture & Mathematical Synthesis

The instantaneous relative radiation exposure index $R(t)$ for flight segment at timestamp $t$ is computed as:

\\[
R(t) = F_{{\\text{{alt}}}}(h) \\times F_{{\\text{{geomag}}}}(\\lambda_m) \\times M_{{\\text{{space\\_weather}}}}(K_p, \\Phi_p)
\\]

Where:
- $F_{{\\text{{alt}}}}(h)$: Altitude factor from column depth attenuation curve (*illustrative placeholder*).
- $F_{{\\text{{geomag}}}}(\\lambda_m)$: Geomagnetic dipole shielding based on geomagnetic latitude $\\lambda_m$ computed against IGRF-13 dipole pole ({pole.get('north_pole_lat', 80.7)}°N, {pole.get('north_pole_lon', -72.7)}°W) (*illustrative placeholder*).
- $M_{{\\text{{space\\_weather}}}}(K_p, \\Phi_p)$: Solar energetic particle multiplier driven by NOAA SWPC planetary $K_p$ and 10 MeV proton flux $\\Phi_p$ (*illustrative placeholder*).

---

## 3. Discrete Operational Tiers (Axis B)

Radiation index is reported strictly in discrete operational tiers, completely decoupled from Axis A hostile interference:

| Operational Level | Exposure Threshold | Description |
|:---|:---|:---|
| **`low`** | $R < {exp_levels.get('low', {}).get('threshold_max', 2.50):.2f}$ | {exp_levels.get('low', {}).get('description', 'Nominal atmospheric cosmic ray background')} |
| **`moderate`** | ${exp_levels.get('low', {}).get('threshold_max', 2.50):.2f} \\le R < {exp_levels.get('moderate', {}).get('threshold_max', 5.50):.2f}$ | {exp_levels.get('moderate', {}).get('description', 'Elevated high-altitude or polar exposure')} |
| **`elevated`** | $R \\ge {exp_levels.get('moderate', {}).get('threshold_max', 5.50):.2f}$ | {exp_levels.get('elevated', {}).get('description', 'Significant space-weather event or extreme high-altitude polar flight')} |
"""

    out_rad = Path("docs") / "RADIATION.md"
    out_rad.write_text(rad_md, encoding="utf-8")
    print(f"Generated {out_rad}")


if __name__ == "__main__":
    generate_radiation_docs()

