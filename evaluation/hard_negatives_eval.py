"""Controlled Hard Negative Experiment and Prevalence Sweep.

Addresses Requirement 10:
(a) Controlled experiment: take matched clean control flights, inject each hard negative
    ALONE at stated severity, report FPR per type (turbulence, baro bias, go-around, dropouts).
(b) Prevalence sweep for turbulence and dropouts (1%, 5%, 20%, 50%, 90%) showing composite
    FPR and precision. Explicitly state default prevalence as an unvalidated assumption.
"""

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

def run_hard_negatives_analysis():
    # Use dev seed 42 to avoid test seed contamination
    gen = SyntheticWorldGenerator(config_path="config/synthetic.yaml", seed_mode="dev")
    reg_list = gen.generate_aircraft_registry(n_aircraft=200)
    
    det_a = GeoBaroAltDetector()
    det_b = KinematicFeasibilityDetector()
    det_c = PosVelConsistencyDetector()
    det_d = MultiAircraftConsensusDetector()

    def eval_flight_track(df: pd.DataFrame):
        res_a = det_a.evaluate(df)
        res_b = det_b.evaluate(df)
        res_c = det_c.evaluate(df)
        res_d = det_d.evaluate(
            target_icao=str(df["icao24"].iloc[0]),
            h3_cell=str(df["h3_cell"].iloc[0]) if "h3_cell" in df.columns else "851f1853fffffff",
            window_start_ts=int(df["ts"].min()),
            window_end_ts=int(df["ts"].max()),
            peer_anomalies_in_neighborhood={str(df["icao24"].iloc[0]): False}
        )
        flag = res_a["flag"] or res_b["flag"] or res_c["flag"] or res_d["flag"]
        return {
            "composite": flag,
            "check_a": res_a["flag"],
            "check_b": res_b["flag"],
            "check_c": res_c["flag"],
            "check_d": res_d["flag"],
        }

    # Generate 150 pristine clean control flights (no turbulence, no baro drift, no go-around, no dropout)
    # Temporarily override difficulty knobs to pure zero
    orig_diff = dict(gen.difficulty)
    gen.difficulty["noise_level_sigma_meters"] = 10.0
    gen.difficulty["coverage_dropout_probability"] = 0.0
    gen.difficulty["turbulence_spike_probability"] = 0.0
    gen.difficulty["baro_drift_error_probability"] = 0.0
    gen.difficulty["go_around_probability"] = 0.0

    print("Generating pristine clean control flights...")
    raw_points = gen.generate_flight_tracks(
        aircraft_list=reg_list,
        ground_truth_events=[], # Zero attacks
        n_flights=150,
        start_ts=1793491200,
        sampling_interval=30,
    )
    # Restore original difficulty
    gen.difficulty = orig_diff

    # Group into flights
    pts_dict = [p.__dict__ if hasattr(p, "__dict__") else p for p in raw_points]
    df_all = pd.DataFrame(pts_dict)
    
    # Identify flight segments (continuous points per icao24)
    flight_dfs = []
    for icao, group in df_all.groupby("icao24"):
        group = group.sort_values("ts").reset_index(drop=True)
        # Split on large ts gaps if any
        dt = np.diff(group["ts"].values)
        split_indices = np.where(dt > 120)[0] + 1
        splits = np.split(group, split_indices)
        for s in splits:
            if len(s) >= 40:
                flight_dfs.append(s.reset_index(drop=True))
                if len(flight_dfs) >= 100:
                    break
        if len(flight_dfs) >= 100:
            break

    print(f"Curated {len(flight_dfs)} matched pristine clean control flights.")

    # 1. Clean Baseline (Zero hard negatives)
    baseline_res = [eval_flight_track(f) for f in flight_dfs]
    base_fpr = sum(r["composite"] for r in baseline_res) / len(flight_dfs)

    # 2. Turbulence ALONE: vertical rate spikes (+-14 m/s) in cruise
    turb_dfs = []
    for f in flight_dfs:
        df = f.copy()
        n = len(df)
        for i in range(int(0.2 * n), int(0.8 * n)):
            if i % 3 == 0:
                df.loc[i, "vrate_mps"] += 14.0
        turb_dfs.append(df)
    turb_res = [eval_flight_track(df) for df in turb_dfs]
    turb_fpr = sum(r["composite"] for r in turb_res) / len(flight_dfs)

    # 3. Baro Bias ALONE: +120m bias step in cruise
    baro_dfs = []
    for f in flight_dfs:
        df = f.copy()
        n = len(df)
        for i in range(int(0.3 * n), n):
            df.loc[i, "baro_alt_m"] += 120.0
        baro_dfs.append(df)
    baro_res = [eval_flight_track(df) for df in baro_dfs]
    baro_fpr = sum(r["composite"] for r in baro_res) / len(flight_dfs)

    # 4. Go-Around ALONE: Missed approach climb maneuver
    ga_dfs = []
    for f in flight_dfs:
        df = f.copy()
        n = len(df)
        s_idx, e_idx = int(0.88 * n), min(n - 1, int(0.95 * n))
        for i in range(s_idx, e_idx):
            df.loc[i, "baro_alt_m"] += 600.0
            df.loc[i, "geo_alt_m"] += 600.0
            df.loc[i, "vrate_mps"] = 14.0
        ga_dfs.append(df)
    ga_res = [eval_flight_track(df) for df in ga_dfs]
    ga_fpr = sum(r["composite"] for r in ga_res) / len(flight_dfs)

    # 5. Dropouts ALONE: dt = 90s telemetry gap
    drop_dfs = []
    for f in flight_dfs:
        df = f.copy()
        n = len(df)
        mid = int(0.5 * n)
        df_dropped = df.drop(index=[mid, mid + 1]).reset_index(drop=True)
        drop_dfs.append(df_dropped)
    drop_res = [eval_flight_track(df) for df in drop_dfs]
    drop_fpr = sum(r["composite"] for r in drop_res) / len(flight_dfs)

    results = {
        "baseline": (base_fpr, baseline_res),
        "turbulence": (turb_fpr, turb_res),
        "baro_bias": (baro_fpr, baro_res),
        "go_around": (ga_fpr, ga_res),
        "dropouts": (drop_fpr, drop_res),
    }

    print("\n================== (a) CONTROLLED HARD NEGATIVE EXPERIMENT ==================")
    print(f"{'Condition':45} | {'Comp FPR':8} | {'Check a':8} | {'Check b':8} | {'Check c':8}")
    print("-" * 85)
    for name, (fpr, r_list) in [
        ("Pristine Clean Baseline (No Hard Negatives)", results["baseline"]),
        ("Turbulence Alone (vrate spikes +-14 m/s)", results["turbulence"]),
        ("Baro Bias Alone (+120m step in cruise)", results["baro_bias"]),
        ("Go-Around Alone (Missed approach climb)", results["go_around"]),
        ("Dropouts Alone (dt = 90s telemetry gap)", results["dropouts"]),
    ]:
        fa = sum(r["check_a"] for r in r_list) / len(r_list) * 100
        fb = sum(r["check_b"] for r in r_list) / len(r_list) * 100
        fc = sum(r["check_c"] for r in r_list) / len(r_list) * 100
        print(f"{name:45} | {fpr*100:6.1f}%  | {fa:6.1f}%  | {fb:6.1f}%  | {fc:6.1f}%")

    # (b) Prevalence sweep for turbulence & dropouts
    print("\n================== (b) PREVALENCE SWEEP (TURBULENCE & DROPOUTS) ==================")
    print(f"{'Prevalence':12} | {'Clean FPR':10} | {'Clean FPs':10} | {'Precision':10} | {'F1-Score':10}")
    print("-" * 60)
    
    # Combined turbulence and dropout isolated FPR
    combined_hn_fpr = (turb_fpr + drop_fpr) / 2.0
    n_pos = 1449
    n_clean = 3820
    recall = 0.330
    tp = 478

    sweep_table = []
    for p in [0.01, 0.05, 0.20, 0.50, 0.90]:
        eff_fpr = (1.0 - p) * base_fpr + p * combined_hn_fpr
        expected_fp = int(n_clean * eff_fpr)
        expected_prec = tp / (tp + expected_fp) * 100 if (tp + expected_fp) > 0 else 0.0
        expected_f1 = 2 * (expected_prec/100) * recall / ((expected_prec/100) + recall) * 100 if (expected_prec + recall) > 0 else 0.0
        sweep_table.append((p, eff_fpr, expected_fp, expected_prec, expected_f1))
        print(f"{p*100:8.1f}%    | {eff_fpr*100:7.2f}%   | {expected_fp:8d}   | {expected_prec:7.2f}%   | {expected_f1:7.2f}%")

    return results, sweep_table

if __name__ == "__main__":
    run_hard_negatives_analysis()

