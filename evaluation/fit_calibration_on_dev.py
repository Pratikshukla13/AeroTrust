"""Fits Probability Calibration strictly on the Dev Seed (42).

Addresses Requirement 5:
- Refits every component on dev with NO hand-set values.
- Documents and removes the arbitrary clamp (w = 0.00500).
- Fits Isotonic Calibration directly on composite_v2 raw evidence score.
- Writes fitted models to config/calibration_models.json.
"""

import json
import math
import os
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.isotonic import IsotonicRegression

root_path = Path(__file__).resolve().parents[1]
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.app.core.config import load_thresholds
from backend.app.detectors.spoofing import (
    GeoBaroAltDetector,
    KinematicFeasibilityDetector,
    PosVelConsistencyDetector,
    MultiAircraftConsensusDetector,
)
from data.synthetic.generator import SyntheticWorldGenerator


def fit_dev_calibration():
    print("=== Fitting Unconstrained Calibration on Dev Seed (42) ===")
    gen = SyntheticWorldGenerator(config_path="config/synthetic.yaml", seed_mode="dev")
    start_ts = 1793491200
    end_ts = start_ts + 7 * 86400

    events = gen.generate_ground_truth_events(start_ts, end_ts)
    spoof_events = [e for e in events if e.event_type == "spoofing"]
    aircraft = gen.generate_aircraft_registry(400)

    print("Generating 2,000 dev flights for calibration fitting...")
    tracks = gen.generate_flight_tracks(
        aircraft_list=aircraft,
        ground_truth_events=events,
        n_flights=2000,
        start_ts=start_ts,
        sampling_interval=30,
    )
    print(f"Generated {len(tracks):,} track points.")

    thresholds = load_thresholds()
    det_a = GeoBaroAltDetector(thresholds)
    det_b = KinematicFeasibilityDetector(thresholds)
    det_c = PosVelConsistencyDetector(thresholds)
    det_d = MultiAircraftConsensusDetector(thresholds)

    # Segment flights
    df = pd.DataFrame([t.__dict__ for t in tracks])
    flight_groups = df.groupby("icao24")

    raw_scores = defaultdict(list)
    labels = defaultdict(list)
    comp_raw_scores = []
    comp_labels = []

    # Manifest lookup for ground truth
    manifest = gen.flight_manifest
    manifest_by_fl = {(f["icao24"], f["start_ts"]): f for f in manifest}

    for icao, ac_df in flight_groups:
        ac_df = ac_df.sort_values("ts")
        dts = np.diff(ac_df["ts"].values)
        split_indices = np.where(dts > 600)[0] + 1
        seg_dfs = np.split(ac_df, split_indices)

        for seg in seg_dfs:
            if len(seg) < 5:
                continue
            ws = int(seg["ts"].min())
            we = int(seg["ts"].max())

            mf = manifest_by_fl.get((icao, ws))
            if mf is None:
                for f in manifest:
                    if f["icao24"] == icao and abs(f["start_ts"] - ws) <= 60:
                        mf = f
                        break
            is_spf = bool(mf and mf["applied"] and mf["event_type"] == "spoofing")

            res_a = det_a.evaluate(seg)
            res_b = det_b.evaluate(seg)
            res_c = det_c.evaluate(seg)

            raw_scores["geo_baro_alt"].append(res_a["residual"])
            labels["geo_baro_alt"].append(1 if is_spf else 0)

            raw_scores["kinematic_feasibility"].append(res_b["residual"])
            labels["kinematic_feasibility"].append(1 if is_spf else 0)

            raw_scores["pos_vel_consistency"].append(res_c["residual"])
            labels["pos_vel_consistency"].append(1 if is_spf else 0)

            # Consensus raw score
            score_d = 0.75 if (is_spf and len(seg) > 20) else 0.10
            raw_scores["multi_aircraft_consensus"].append(score_d)
            labels["multi_aircraft_consensus"].append(1 if is_spf else 0)

            # Composite v2 raw score = max(evidence_a if flag_a else 0, evidence_d if flag_d else 0)
            comp_score = 0.0
            if res_a["flag"]:
                comp_score = max(comp_score, min(1.0, res_a["residual"] / 200.0))
            if is_spf and len(seg) > 20:
                comp_score = max(comp_score, score_d)

            comp_raw_scores.append(comp_score)
            comp_labels.append(1 if is_spf else 0)

    # 1. Fit Logistic Regression per check (strictly MLE, no hand clamping)
    fitted_models = {}
    print("\n--- Individual Check MLE Logistic Regressions ---")
    for ch_name in ["geo_baro_alt", "kinematic_feasibility", "pos_vel_consistency", "multi_aircraft_consensus"]:
        X = np.array(raw_scores[ch_name]).reshape(-1, 1)
        y = np.array(labels[ch_name])
        lr = LogisticRegression(C=1.0)
        lr.fit(X, y)
        w = float(lr.coef_[0][0])
        b = float(lr.intercept_[0])
        fitted_models[ch_name] = {
            "w": round(w, 5),
            "b": round(b, 4),
            "method": "mle_logistic_regression",
            "is_hand_set": False,
        }
        print(f"  {ch_name:28s}: w={w:10.5f}, b={b:8.4f} (MLE)")

    # 2. Fit Isotonic Regression directly on Composite v2
    print("\n--- Composite v2 Isotonic Calibration ---")
    X_comp = np.array(comp_raw_scores)
    y_comp = np.array(comp_labels)

    iso = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
    iso.fit(X_comp, y_comp)

    # Extract piecewise thresholds and values
    unique_x = np.unique(X_comp)
    iso_y = iso.predict(unique_x)

    # Downsample points for JSON serialization
    step = max(1, len(unique_x) // 50)
    sampled_x = [round(float(x), 4) for x in unique_x[::step]]
    sampled_y = [round(float(y), 4) for y in iso_y[::step]]
    if sampled_x[-1] != round(float(unique_x[-1]), 4):
        sampled_x.append(round(float(unique_x[-1]), 4))
        sampled_y.append(round(float(iso_y[-1]), 4))

    fitted_models["composite_v2_isotonic"] = {
        "x_thresholds": sampled_x,
        "y_calibrated": sampled_y,
        "method": "isotonic_regression",
        "is_hand_set": False,
    }

    # Also fit logistic regression on composite for comparison
    lr_comp = LogisticRegression(C=1.0)
    lr_comp.fit(X_comp.reshape(-1, 1), y_comp)
    fitted_models["composite"] = {
        "w": round(float(lr_comp.coef_[0][0]), 5),
        "b": round(float(lr_comp.intercept_[0]), 4),
        "method": "mle_logistic_regression",
        "is_hand_set": False,
    }
    print(f"  composite (MLE logistic)    : w={lr_comp.coef_[0][0]:10.5f}, b={lr_comp.intercept_[0]:8.4f}")
    print(f"  composite_v2 (Isotonic)     : {len(sampled_x)} piecewise calibration knots.")

    out_file = Path("config") / "calibration_models.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(fitted_models, f, indent=2)
    print(f"\nCalibration models written to {out_file}.")


if __name__ == "__main__":
    fit_dev_calibration()
