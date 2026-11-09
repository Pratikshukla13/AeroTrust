"""AeroTrust Radiation Index Module (Axis B: Natural Exposure).

Calculates relative cosmic and solar radiation exposure along commercial flight paths:
- Altitude factor F_alt (atmospheric column depth shielding)
- Geomagnetic latitude factor F_geomag (dipole cutoff rigidity)
- Relative exposure multiplier M_space_weather (solar protons >10 MeV and Kp index)

NOTICE: All lookup tables and parameters are illustrative placeholders until each TODO-CITE
constant is resolved with published empirical sources.
Strict Rule: Never express as a probability. Relative exposure index only.
Externalized in config/radiation_tables.yaml.
"""

import math
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import yaml


class RadiationCalculator:
    """Calculates relative cosmic radiation exposure index for flight segments."""

    def __init__(self, config_path: str = "config/radiation_tables.yaml"):
        # Resolve config path
        cfg_file = Path(config_path)
        if not cfg_file.is_absolute():
            # Try from repo root
            root = Path(__file__).resolve().parents[3]
            cfg_file = root / config_path
            if not cfg_file.exists():
                cfg_file = Path(config_path)

        with open(cfg_file, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        self.alt_bins = self.config.get("altitude_bins", [])
        self.geomag_bins = self.config.get("geomagnetic_latitude_bins", [])
        self.sw_tiers = self.config.get("space_weather_tiers", [])
        self.levels = self.config.get("exposure_levels", {})

        pole = self.config.get("geomagnetic_pole", {"north_pole_lat": 80.7, "north_pole_lon": -72.7})
        self.pole_lat_rad = math.radians(pole["north_pole_lat"])
        self.pole_lon_rad = math.radians(pole["north_pole_lon"])

    def compute_geomagnetic_latitude(self, lat_deg: float, lon_deg: float) -> float:
        """Computes geomagnetic latitude in degrees using spherical dipole approximation."""
        phi = math.radians(lat_deg)
        lam = math.radians(lon_deg)
        # sin(lambda_m) = sin(phi)*sin(phi_0) + cos(phi)*cos(phi_0)*cos(lam - lam_0)
        sin_geomag = (
            math.sin(phi) * math.sin(self.pole_lat_rad)
            + math.cos(phi) * math.cos(self.pole_lat_rad) * math.cos(lam - self.pole_lon_rad)
        )
        sin_geomag = max(-1.0, min(1.0, sin_geomag))
        return math.degrees(math.asin(sin_geomag))

    def get_altitude_factor(self, alt_m: float) -> float:
        """Looks up altitude shielding factor F_alt (monotonic with altitude)."""
        alt_clamped = max(0.0, float(alt_m))
        for b in self.alt_bins:
            if alt_clamped <= b["alt_max_m"]:
                return float(b["factor"])
        # If higher than highest bin, return highest factor
        return float(self.alt_bins[-1]["factor"]) if self.alt_bins else 4.80

    def get_geomag_factor(self, geomag_lat_deg: float) -> float:
        """Looks up geomagnetic latitude factor F_geomag (monotonic with |geomag_lat|)."""
        abs_lat = abs(float(geomag_lat_deg))
        for b in self.geomag_bins:
            if abs_lat <= b["max_geomag_lat_deg"]:
                return float(b["factor"])
        return float(self.geomag_bins[-1]["factor"]) if self.geomag_bins else 2.10

    def get_space_weather_multiplier(
        self, proton_flux_10mev: float = 0.0, kp: float = 2.0
    ) -> Tuple[float, str]:
        """Looks up space weather multiplier M_space_weather based on proton flux and Kp."""
        # Check from highest severity tier down to quiet
        sorted_tiers = sorted(
            self.sw_tiers,
            key=lambda t: max(t.get("min_proton_flux_10mev", 0.0), t.get("min_kp", 0.0)),
            reverse=True,
        )
        for t in sorted_tiers:
            min_flux = t.get("min_proton_flux_10mev", 0.0)
            min_kp = t.get("min_kp", 0.0)
            if (min_flux > 0 and proton_flux_10mev >= min_flux) or (min_kp > 0 and kp >= min_kp):
                return float(t["multiplier"]), t["name"]

        return 1.00, "quiet"

    def compute_index(
        self,
        alt_m: float,
        lat_deg: float,
        lon_deg: float,
        proton_flux_10mev: float = 0.0,
        kp: float = 2.0,
    ) -> Dict[str, Any]:
        """Computes single-point relative radiation index."""
        geomag_lat = self.compute_geomagnetic_latitude(lat_deg, lon_deg)
        f_alt = self.get_altitude_factor(alt_m)
        f_geomag = self.get_geomag_factor(geomag_lat)
        m_sw, sw_tier = self.get_space_weather_multiplier(proton_flux_10mev, kp)

        relative_index = round(f_alt * f_geomag * m_sw, 3)

        # Categorize into Axis B exposure level
        if relative_index < self.levels.get("low", {}).get("threshold_max", 2.50):
            level = "low"
        elif relative_index < self.levels.get("moderate", {}).get("threshold_max", 5.50):
            level = "moderate"
        else:
            level = "elevated"

        return {
            "relative_index": relative_index,
            "level": level,
            "geomag_lat": round(geomag_lat, 2),
            "components": {
                "altitude_m": round(alt_m, 1),
                "altitude_factor": f_alt,
                "geomag_factor": f_geomag,
                "relative_exposure_multiplier": m_sw,
                "space_weather_multiplier": m_sw,
                "space_weather_tier": sw_tier,
                "placeholder_notice": "Illustrative placeholder pending resolution of TODO-CITE constants",
            },
        }

    def compute_flight_segments(
        self,
        flight_df: pd.DataFrame,
        sw_lookup: Optional[Dict[int, Tuple[float, float]]] = None,
        segment_sec: int = 300,
    ) -> List[Dict[str, Any]]:
        """Segments flight trajectory into 5-minute blocks and computes radiation index."""
        if flight_df.empty:
            return []

        df_sorted = flight_df.sort_values("ts").reset_index(drop=True)
        t_start = int(df_sorted["ts"].min())
        t_end = int(df_sorted["ts"].max())
        icao = str(df_sorted["icao24"].iloc[0])

        results = []
        for seg_start in range(t_start, t_end + 1, segment_sec):
            seg_end = seg_start + segment_sec
            sub_df = df_sorted[(df_sorted["ts"] >= seg_start) & (df_sorted["ts"] < seg_end)]
            if sub_df.empty:
                continue

            # Median telemetry over 5-minute segment
            alt_m = float(sub_df["baro_alt_m"].median())
            lat = float(sub_df["lat"].median())
            lon = float(sub_df["lon"].median())
            mid_ts = int(sub_df["ts"].median())

            # Space weather lookup (hourly bucket)
            flux = 0.0
            kp_val = 2.0
            if sw_lookup:
                bucket_h = (mid_ts // 3600) * 3600
                if bucket_h in sw_lookup:
                    kp_val, flux = sw_lookup[bucket_h]

            res = self.compute_index(alt_m, lat, lon, proton_flux_10mev=flux, kp=kp_val)
            results.append({
                "icao24": icao,
                "ts": mid_ts,
                "segment_start": seg_start,
                "segment_end": seg_end,
                "alt_m": alt_m,
                "geomag_lat": res["geomag_lat"],
                "relative_index": res["relative_index"],
                "level": res["level"],
                "components": res["components"],
            })

        return results

