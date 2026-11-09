import sys
import os
import random
import psycopg2
import numpy as np
import pandas as pd

sys.path.insert(0, ".")
from backend.app.detectors.spoofing import (
    GeoBaroAltDetector,
    KinematicFeasibilityDetector,
    PosVelConsistencyDetector,
    MultiAircraftConsensusDetector,
)

def get_connection():
    return psycopg2.connect(
        dbname="aerotrust",
        user="aerotrust",
        password="aerotrust_secret",
        host="localhost",
        port=5432,
    )

def run_experiment():
    print("Selecting individual clean control flights from Western Europe / North Atlantic...")
    conn = get_connection()
    cur = conn.cursor()
    
    # Select individual flights from control corridors (lon between -10 and 5, lat 45-55)
    cur.execute("""
        SELECT sc.icao24, sc.ts_window_start, sc.ts_window_end, count(p.id) as pt_count
        FROM (SELECT DISTINCT icao24, ts_window_start, ts_window_end FROM spoof_checks) sc
        JOIN flight_track_points p ON p.icao24 = sc.icao24 AND p.ts BETWEEN sc.ts_window_start AND sc.ts_window_end
        WHERE p.lat BETWEEN 46.0 AND 54.0 AND p.lon BETWEEN -8.0 AND 5.0
        GROUP BY sc.icao24, sc.ts_window_start, sc.ts_window_end
        HAVING count(p.id) BETWEEN 60 AND 300
        LIMIT 100;
    """)
    flight_windows = cur.fetchall()
    print(f"Found {len(flight_windows)} candidate clean control flight windows.")
    
    det_a = GeoBaroAltDetector()
    det_b = KinematicFeasibilityDetector()
    det_c = PosVelConsistencyDetector()
    det_d = MultiAircraftConsensusDetector()
    
    def eval_flight(fdf):
        res_a = det_a.evaluate(fdf)
        res_b = det_b.evaluate(fdf)
        res_c = det_c.evaluate(fdf)
        res_d = det_d.evaluate(
            target_icao=str(fdf["icao24"].iloc[0]),
            h3_cell="851f1853fffffff",
            window_start_ts=int(fdf["ts"].min()),
            window_end_ts=int(fdf["ts"].max()),
            peer_anomalies_in_neighborhood={str(fdf["icao24"].iloc[0]): False}
        )
        flag = res_a["flag"] or res_b["flag"] or res_c["flag"] or res_d["flag"]
        return {
            "flag": flag,
            "flag_a": res_a["flag"],
            "flag_b": res_b["flag"],
            "flag_c": res_c["flag"],
            "flag_d": res_d["flag"],
        }

    # Fetch track points per individual flight window
    clean_dfs = []
    for icao, ws, we, pt_cnt in flight_windows[:50]:
        cur.execute("""
            SELECT icao24, ts, lat, lon, baro_alt_m, geo_alt_m, gs_mps, track_deg, vrate_mps, nic, nacp, sil, on_ground
            FROM flight_track_points
            WHERE icao24 = %s AND ts BETWEEN %s AND %s
            ORDER BY ts ASC;
        """, (icao, ws, we))
        rows = cur.fetchall()
        if len(rows) >= 30:
            cols = ["icao24", "ts", "lat", "lon", "baro_alt_m", "geo_alt_m", "gs_mps", "track_deg", "vrate_mps", "nic", "nacp", "sil", "on_ground"]
            fdf = pd.DataFrame(rows, columns=cols)
            clean_dfs.append(fdf)
            if len(clean_dfs) >= 40:
                break
                
    print(f"Loaded {len(clean_dfs)} distinct individual clean flights.")
    
    # 0. Clean Baseline
    base_res = [eval_flight(df) for df in clean_dfs]
    base_fpr = sum(r["flag"] for r in base_res) / len(clean_dfs)
    print(f"Clean Baseline FPR: {base_fpr*100:.2f}% (a: {sum(r['flag_a'] for r in base_res)/len(clean_dfs)*100:.1f}%, b: {sum(r['flag_b'] for r in base_res)/len(clean_dfs)*100:.1f}%, c: {sum(r['flag_c'] for r in base_res)/len(clean_dfs)*100:.1f}%)")
    
    # 1. Turbulence ALONE: vertical rate spikes (+-14 m/s) during cruise (fraction 0.2 to 0.8)
    turb_res = []
    for df_orig in clean_dfs:
        df = df_orig.copy()
        n = len(df)
        s, e = int(0.20 * n), int(0.80 * n)
        for i in range(s, e):
            if i % 2 == 0:
                df.loc[i, "vrate_mps"] += 14.0
        turb_res.append(eval_flight(df))
        
    # 2. Baro Bias ALONE: +120m bias across entire flight
    baro_res = []
    for df_orig in clean_dfs:
        df = df_orig.copy()
        df["baro_alt_m"] += 120.0
        baro_res.append(eval_flight(df))
        
    # 3. Go-Around ALONE: Missed approach climb maneuver (+14 m/s climb to 1000m)
    ga_res = []
    for df_orig in clean_dfs:
        df = df_orig.copy()
        n = len(df)
        s, e = int(0.88 * n), min(n - 1, int(0.95 * n))
        for i in range(s, e):
            df.loc[i, "baro_alt_m"] += 600.0
            df.loc[i, "geo_alt_m"] += 600.0
            df.loc[i, "vrate_mps"] = 14.0
        ga_res.append(eval_flight(df))
        
    # 4. Dropouts ALONE: dt = 90s gap in telemetry (drop 2 consecutive points at 30s sampling)
    drop_res = []
    for df_orig in clean_dfs:
        df = df_orig.copy()
        n = len(df)
        mid = int(0.5 * n)
        df_dropped = df.drop(index=[mid, mid + 1]).reset_index(drop=True)
        drop_res.append(eval_flight(df_dropped))
        
    print("\n--- Controlled Hard Negative Experiment (Isolated at Stated Severity) ---")
    exps = [
        ("Clean Control Baseline (No Injections)", base_res),
        ("Turbulence Alone (vrate spikes +-14 m/s)", turb_res),
        ("Baro Bias Alone (+120m altimeter bias)", baro_res),
        ("Go-Around Alone (Missed approach climb)", ga_res),
        ("Dropouts Alone (dt = 90s telemetry gap)", drop_res),
    ]
    for name, rlist in exps:
        cFPR = sum(r["flag"] for r in rlist) / len(rlist) * 100
        fA = sum(r["flag_a"] for r in rlist) / len(rlist) * 100
        fB = sum(r["flag_b"] for r in rlist) / len(rlist) * 100
        fC = sum(r["flag_c"] for r in rlist) / len(rlist) * 100
        print(f"{name:45} | Comp FPR: {cFPR:5.1f}% | Check a: {fA:5.1f}% | Check b: {fB:5.1f}% | Check c: {fC:5.1f}%")
        
    # Prevalence Sweep for Turbulence and Dropouts
    print("\n--- Prevalence Sweep for Turbulence & Dropouts ---")
    sweep = [0.01, 0.05, 0.20, 0.50, 0.90]
    n_pos = 1449
    n_clean = 3820
    tp = 478 # Fixed recall ~33.0%
    turb_fpr = sum(r["flag"] for r in turb_res) / len(turb_res)
    drop_fpr = sum(r["flag"] for r in drop_res) / len(drop_res)
    # Average hard-negative response
    hn_fpr = (turb_fpr + drop_fpr) / 2.0
    
    for p in sweep:
        eff_fpr = (1.0 - p) * base_fpr + p * hn_fpr
        fps = int(n_clean * eff_fpr)
        prec = tp / (tp + fps) * 100
        f1 = 2 * (prec/100) * 0.330 / ((prec/100) + 0.330) * 100
        print(f"Prevalence: {p*100:4.1f}% | Composite FPR: {eff_fpr*100:5.2f}% | Expected FPs: {fps:4d} | Precision: {prec:5.2f}% | F1: {f1:5.2f}%")

if __name__ == "__main__":
    run_experiment()
