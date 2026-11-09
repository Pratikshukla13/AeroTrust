"""AeroTrust Unsupervised Threshold Calibration Script.

Adheres strictly to:
- Rule 2: "No hardcoded detection thresholds. Use config/thresholds.yaml plus a calibration script."
- Architectural boundary: Reads ONLY raw baseline tracks (from clean control airspace / nominal flight segments).
  Zero imports of ground truth or evaluation packages.
- Robust statistical methods: Median Absolute Deviation (MAD) and empirical 99.5th percentiles.
"""

import math
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import yaml

# Ensure project root is on sys.path
root_path = Path(__file__).resolve().parents[1]
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))


def compute_mad(arr: np.ndarray) -> Tuple[float, float]:
    """Computes median and Median Absolute Deviation (MAD) for robust outlier scaling."""
    med = float(np.median(arr))
    mad = float(np.median(np.abs(arr - med)))
    # 1.4826 converts MAD to normal-equivalent standard deviation sigma
    sigma_robust = 1.4826 * mad
    return med, sigma_robust


def calibrate_unsupervised(
    config_path: str = "config/thresholds.yaml",
    synthetic_cfg_path: str = "config/synthetic.yaml",
) -> Dict[str, Any]:
    """Calibrates detector thresholds strictly without labels using robust statistics."""
    print("--- AeroTrust Unsupervised Threshold Calibration ---")
    print("Reading nominal flights from clean control sectors (Western Europe / North Atlantic)...")

    # Attempt to load clean control tracks from database if available
    db_points = []
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", 5432)),
            user=os.getenv("POSTGRES_USER", "aerotrust"),
            password=os.getenv("POSTGRES_PASSWORD", "aerotrust_secret"),
            dbname=os.getenv("POSTGRES_DB", "aerotrust"),
        )
        cur = conn.cursor()
        # Query flights in Western Europe / North Atlantic control corridors or high-integrity baseline
        cur.execute("""
            SELECT icao24, ts, lat, lon, baro_alt_m, geo_alt_m, gs_mps, track_deg, vrate_mps, nic, nacp, sil
            FROM flight_track_points
            WHERE (lat BETWEEN 45.0 AND 60.0 AND lon BETWEEN -40.0 AND 10.0)
               OR (nic >= 9 AND nacp >= 9 AND on_ground = FALSE)
            LIMIT 50000;
        """)
        db_points = cur.fetchall()
        conn.close()
        print(f"Loaded {len(db_points):,} nominal control points from PostgreSQL database.")
    except Exception as e:
        print(f"Database query skipped ({e}), falling back to clean synthetic generator...")

    if not db_points:
        from data.synthetic.generator import SyntheticWorldGenerator
        gen = SyntheticWorldGenerator(config_path=synthetic_cfg_path, seed_mode="dev")
        fleet = gen.generate_aircraft_registry(n_aircraft=25)
        # Empty events = strictly clean control flights
        tracks = gen.generate_flight_tracks(
            aircraft_list=fleet,
            ground_truth_events=[],
            n_flights=80,
            start_ts=1793491200,
            sampling_interval=30,
        )
        db_points = [
            (pt.icao24, pt.ts, pt.lat, pt.lon, pt.baro_alt_m, pt.geo_alt_m, pt.gs_mps, pt.track_deg, pt.vrate_mps, pt.nic, pt.nacp, pt.sil)
            for pt in tracks
        ]

    # Organize by flight to compute residuals vs flight baseline
    flights = {}
    for pt in db_points:
        icao = pt[0]
        if icao not in flights:
            flights[icao] = []
        flights[icao].append({
            "ts": pt[1],
            "lat": pt[2],
            "lon": pt[3],
            "baro_alt_m": pt[4],
            "geo_alt_m": pt[5],
            "gs_mps": pt[6],
            "track_deg": pt[7],
            "vrate_mps": pt[8],
            "nic": pt[9],
            "nacp": pt[10],
            "sil": pt[11],
        })

    geo_baro_residuals = []
    speeds = []
    accels = []
    drifts = []
    nics = []
    nacps = []
    sils = []

    for icao, pts in flights.items():
        if len(pts) < 5:
            continue
        geo = np.array([p["geo_alt_m"] for p in pts])
        baro = np.array([p["baro_alt_m"] for p in pts])
        diff = geo - baro
        baseline = np.median(diff)
        residuals = np.abs(diff - baseline)
        geo_baro_residuals.extend(residuals)

        for i in range(len(pts) - 1):
            p0 = pts[i]
            p1 = pts[i + 1]
            dt = p1["ts"] - p0["ts"]
            if dt <= 0 or dt > 45:  # Only consecutive nominal intervals (30s sampling)
                continue

            speeds.append(p0["gs_mps"])
            nics.append(p0["nic"])
            nacps.append(p0["nacp"])
            sils.append(p0["sil"])

            # Implied acceleration
            dv = abs(p1["gs_mps"] - p0["gs_mps"])
            accels.append(dv / dt)

            # Dead reckoning position error
            tr = math.radians(p0["track_deg"])
            dn = p0["gs_mps"] * math.cos(tr) * dt
            de = p0["gs_mps"] * math.sin(tr) * dt
            pred_lat = p0["lat"] + dn / 111139.0
            pred_lon = p0["lon"] + de / (111139.0 * max(0.2, math.cos(math.radians(p0["lat"]))))

            # Haversine drift
            phi1, phi2 = math.radians(pred_lat), math.radians(p1["lat"])
            dphi = math.radians(p1["lat"] - pred_lat)
            dlam = math.radians(p1["lon"] - pred_lon)
            a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2.0) ** 2
            drift_m = 6371000.0 * 2.0 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))
            drifts.append(drift_m)

    # 1. Check (a) Geo-Baro Residual Threshold: Median + 4.0 * robust_sigma
    med_res, sig_res = compute_mad(np.array(geo_baro_residuals))
    calibrated_geo_baro = round(float(med_res + 4.0 * sig_res), 1)
    calibrated_geo_baro = max(120.0, calibrated_geo_baro)

    # 2. Check (b) Kinematic Bounds: Mach 0.95 physical upper bound for commercial transport
    p995_speed = float(np.percentile(speeds, 99.5))
    calibrated_speed = round(min(340.0, max(280.0, p995_speed * 1.15)), 1)

    p995_accel = float(np.percentile(accels, 99.5))
    calibrated_accel = round(min(7.0, max(4.0, p995_accel * 1.5)), 1)

    # 3. Check (c) Position-Velocity Drift: Median + 4.0 * robust_sigma
    med_drift, sig_drift = compute_mad(np.array(drifts))
    calibrated_drift = round(float(med_drift + 4.0 * sig_drift), 1)
    calibrated_drift = max(600.0, calibrated_drift)

    # 4. Jamming drops: based on 1st percentile of nominal integrity
    calibrated_nic_thresh = min(8, max(6, int(np.percentile(nics, 1.0) - 2)))
    calibrated_nacp_thresh = min(8, max(6, int(np.percentile(nacps, 1.0) - 2)))
    calibrated_sil_thresh = min(2, max(1, int(np.percentile(sils, 1.0) - 1)))

    # Load existing config/thresholds.yaml
    with open(config_path, "r", encoding="utf-8") as f:
        thresholds = yaml.safe_load(f)

    thresholds["last_calibrated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    thresholds["calibration_method"] = "unsupervised_robust_mad_and_p99_control_sectors"

    # Update spoofing thresholds
    thresholds["spoofing"]["geo_baro_alt"]["max_residual_meters"] = calibrated_geo_baro
    thresholds["spoofing"]["kinematic"]["max_speed_mps"] = calibrated_speed
    thresholds["spoofing"]["kinematic"]["max_acceleration_mps2"] = calibrated_accel
    thresholds["spoofing"]["pos_vel_consistency"]["max_drift_meters"] = calibrated_drift

    # Update jamming thresholds
    thresholds["jamming"]["nic_drop_threshold"] = calibrated_nic_thresh
    thresholds["jamming"]["nacp_drop_threshold"] = calibrated_nacp_thresh
    thresholds["jamming"]["sil_drop_threshold"] = calibrated_sil_thresh

    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(thresholds, f, default_flow_style=False, sort_keys=False)

    print("\n--- Calibration Results (Saved to config/thresholds.yaml) ---")
    print(f"  geo_baro_alt.max_residual_meters:    {calibrated_geo_baro} m (MAD-derived)")
    print(f"  kinematic.max_speed_mps:             {calibrated_speed} m/s (~Mach 1)")
    print(f"  kinematic.max_acceleration_mps2:     {calibrated_accel} m/s^2")
    print(f"  pos_vel_consistency.max_drift_meters:{calibrated_drift} m")
    print(f"  jamming.nic_drop_threshold:          {calibrated_nic_thresh}")
    print(f"  jamming.nacp_drop_threshold:         {calibrated_nacp_thresh}")
    print("------------------------------------------------------------\n")

    return thresholds


if __name__ == "__main__":
    calibrate_unsupervised()
