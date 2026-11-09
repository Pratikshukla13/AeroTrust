import sys
import os
import random
import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, ".")
from data.synthetic.generator import SyntheticWorldGenerator
from backend.app.detectors.spoofing import (
    GeoBaroAltDetector,
    KinematicFeasibilityDetector,
    PosVelConsistencyDetector,
    MultiAircraftConsensusDetector,
)

def run():
    print("Generating pristine clean control flights...")
    # Use dev seed for controlled experiment calibration
    gen = SyntheticDataGenerator(seed=42)
    
    # We want 100 long flights with 0 noise/perturbations
    # Let's see how generator creates flights
    # Generate flights on Western Europe corridor
    corr = [c for c in gen.corridors if c["id"] == "CORR-WE-01"][0]
    
    det_a = GeoBaroAltDetector()
    det_b = KinematicFeasibilityDetector()
    det_c = PosVelConsistencyDetector()
    det_d = MultiAircraftConsensusDetector()
    
    def eval_df(df):
        res_a = det_a.evaluate(df)
        res_b = det_b.evaluate(df)
        res_c = det_c.evaluate(df)
        res_d = det_d.evaluate(
            target_icao=str(df["icao24"].iloc[0]),
            h3_cell="851f1853fffffff",
            window_start_ts=int(df["ts"].min()),
            window_end_ts=int(df["ts"].max()),
            peer_anomalies_in_neighborhood={str(df["icao24"].iloc[0]): False}
        )
        flag = res_a["flag"] or res_b["flag"] or res_c["flag"] or res_d["flag"]
        return {
            "flag": flag,
            "flag_a": res_a["flag"],
            "flag_b": res_b["flag"],
            "flag_c": res_c["flag"],
            "flag_d": res_d["flag"],
        }

    # Generate 100 clean flights
    pristine_flights = []
    for i in range(100):
        ac = gen.aircraft[i % len(gen.aircraft)]
        # generate 120 points (1 hour flight)
        pts = gen._generate_corridor_track(
            corridor=corr,
            aircraft=ac,
            flight_start=1793491200 + i * 1800,
            duration_points=120,
            sampling_interval=30,
            events=[], # No spoofing or jamming
        )
        df = pd.DataFrame(pts)
        pristine_flights.append(df)
        
    print(f"Generated {len(pristine_flights)} pristine flights.")
    base_res = [eval_df(df) for df in pristine_flights]
    print(f"Pristine Baseline FPR: {sum(r['flag'] for r in base_res)/len(base_res)*100:.1f}% (a: {sum(r['flag_a'] for r in base_res):.0f}, b: {sum(r['flag_b'] for r in base_res):.0f}, c: {sum(r['flag_c'] for r in base_res):.0f})")

    # (a) Controlled Experiment: Inject each ALONE at stated severity
    # 1. Turbulence alone: vertical rate spikes (+-14 m/s)
    turb_res = []
    for df_orig in pristine_flights:
        df = df_orig.copy()
        n = len(df)
        for idx in range(int(0.2*n), int(0.8*n)):
            if idx % 4 == 0:
                df.loc[idx, "vrate_mps"] += 14.0
        turb_res.append(eval_df(df))

    # 2. Baro bias alone: +120m bias step midway
    baro_res = []
    for df_orig in pristine_flights:
        df = df_orig.copy()
        n = len(df)
        # step bias of +120m in second half
        for idx in range(int(0.4*n), n):
            df.loc[idx, "baro_alt_m"] += 120.0
        baro_res.append(eval_df(df))

    # 3. Go-around alone: missed approach climb maneuver
    ga_res = []
    for df_orig in pristine_flights:
        df = df_orig.copy()
        n = len(df)
        for idx in range(int(0.88*n), int(0.95*n)):
            df.loc[idx, "baro_alt_m"] += 500.0
            df.loc[idx, "geo_alt_m"] += 500.0
            df.loc[idx, "vrate_mps"] = 14.0
        ga_res.append(eval_df(df))

    # 4. Dropouts alone: dt = 90s gap
    drop_res = []
    for df_orig in pristine_flights:
        df = df_orig.copy()
        n = len(df)
        mid = int(0.5*n)
        df_dropped = df.drop(index=[mid, mid+1]).reset_index(drop=True)
        drop_res.append(eval_df(df_dropped))

    print("\n--- Controlled Hard Negative Experiment (Isolated at Stated Severity) ---")
    exps = [
        ("Clean Control Baseline (No Injections)", base_res),
        ("Turbulence Alone (vrate spikes +-14 m/s)", turb_res),
        ("Baro Bias Alone (+120m altimeter step)", baro_res),
        ("Go-Around Alone (Missed approach climb)", ga_res),
        ("Dropouts Alone (dt = 90s telemetry gap)", drop_res),
    ]
    for name, rlist in exps:
        cFPR = sum(r["flag"] for r in rlist) / len(rlist) * 100
        fA = sum(r["flag_a"] for r in rlist) / len(rlist) * 100
        fB = sum(r["flag_b"] for r in rlist) / len(rlist) * 100
        fC = sum(r["flag_c"] for r in rlist) / len(rlist) * 100
        print(f"{name:45} | Comp FPR: {cFPR:5.1f}% | Check a: {fA:5.1f}% | Check b: {fB:5.1f}% | Check c: {fC:5.1f}%")

    # (b) Prevalence sweep for turbulence and dropouts (1%, 5%, 20%, 50%, 90%)
    print("\n--- Prevalence Sweep for Turbulence & Dropouts ---")
    sweep = [0.01, 0.05, 0.20, 0.50, 0.90]
    n_pos = 1449
    n_clean = 3820
    tp = 478 # Fixed recall ~33.0%
    base_fpr_val = sum(r["flag"] for r in base_res) / len(base_res)
    turb_fpr = sum(r["flag"] for r in turb_res) / len(turb_res)
    drop_fpr = sum(r["flag"] for r in drop_res) / len(drop_res)
    hn_isolated_fpr = (turb_fpr + drop_fpr) / 2.0
    
    print(f"Prevalence (%) | Clean FPR (%) | Clean FPs | Precision (%) | F1-Score (%)")
    for p in sweep:
        eff_fpr = (1.0 - p) * base_fpr_val + p * hn_isolated_fpr
        fps = int(n_clean * eff_fpr)
        prec = tp / (tp + fps) * 100
        f1 = 2 * (prec/100) * 0.330 / ((prec/100) + 0.330) * 100
        print(f"{p*100:14.1f}% | {eff_fpr*100:13.2f}% | {fps:9d} | {prec:13.2f}% | {f1:12.2f}%")

if __name__ == "__main__":
    run()
