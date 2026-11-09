import sys
sys.path.insert(0, ".")
import json
from collections import defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
import h3
import numpy as np
import pandas as pd

from backend.app.core.config import load_thresholds
from backend.app.detectors.abstention import AbstentionEngine
from backend.app.detectors.spoofing import (
    GeoBaroAltDetector,
    KinematicFeasibilityDetector,
    PosVelConsistencyDetector,
    MultiAircraftConsensusDetector,
)
from data.synthetic.generator import SyntheticWorldGenerator

def analyze_seed(seed_name):
    gen = SyntheticWorldGenerator(config_path="config/synthetic.yaml", seed_mode=seed_name)
    start_ts = int(datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc).timestamp())
    n_days = 7
    end_ts = start_ts + (n_days * 86400)

    aircraft_list = gen.generate_aircraft_registry(600)
    gt_events = gen.generate_ground_truth_events(start_ts, end_ts)
    event_type_map = {e.event_id: e.spoof_type for e in gt_events if e.event_type == "spoofing"}

    sw_list = gen.generate_space_weather(start_ts, n_days, step_seconds=3600)
    scanner_aircraft, pitch_down_points = gen.generate_pitch_down_test_flight(start_ts)
    aircraft_list.append(scanner_aircraft)

    tracks = gen.generate_flight_tracks(aircraft_list, gt_events, 6000, start_ts, 30)
    tracks.extend(pitch_down_points)

    df_tracks = pd.DataFrame([asdict(t) for t in tracks])
    df_tracks["h3_cell_res5"] = [h3.latlng_to_cell(lat, lon, 5) for lat, lon in zip(df_tracks["lat"], df_tracks["lon"])]
    df_tracks["time_bucket_30m"] = (df_tracks["ts"] // 1800) * 1800

    tracks_by_icao = {icao: grp.sort_values("ts") for icao, grp in df_tracks.groupby("icao24")}
    flight_segments = []
    for icao, grp in tracks_by_icao.items():
        ts_arr = grp["ts"].values
        diffs = np.diff(ts_arr)
        split_indices = np.where(diffs > 900)[0] + 1
        starts = np.insert(split_indices, 0, 0)
        ends = np.append(split_indices, len(grp))
        for s_idx, e_idx in zip(starts, ends):
            seg_df = grp.iloc[s_idx:e_idx]
            if len(seg_df) >= 5:
                flight_segments.append({
                    "icao24": icao,
                    "start_ts": int(seg_df["ts"].iloc[0]),
                    "end_ts": int(seg_df["ts"].iloc[-1]),
                    "df": seg_df,
                    "n_points": len(seg_df),
                })

    manifest_by_icao = defaultdict(list)
    for m in gen.flight_manifest:
        manifest_by_icao[m["icao24"]].append(m)

    thresholds = load_thresholds()
    geo_baro = GeoBaroAltDetector(thresholds)
    abstention = AbstentionEngine(thresholds)

    stats = defaultdict(lambda: {"total": 0, "tp": 0})
    for seg in flight_segments:
        icao = seg["icao24"]
        st = seg["start_ts"]
        et = seg["end_ts"]
        cands = manifest_by_icao.get(icao, [])
        overlaps = [m for m in cands if not (et < m["start_ts"] or st > m["end_ts"]) and m["applied"] and m["event_type"] == "spoofing"]
        if not overlaps:
            continue
        m = overlaps[0]
        ev_type = event_type_map.get(m["event_id"], "unknown")
        pts_nic = seg["df"]["nic"].values
        is_silent = bool(np.mean(pts_nic >= 7) > 0.5)

        res_a = geo_baro.evaluate(seg["df"])
        is_flagged = res_a["flag"]

        key = (ev_type, "silent" if is_silent else "non-silent")
        stats[key]["total"] += 1
        if is_flagged:
            stats[key]["tp"] += 1

    print(f"=== SEED {seed_name} Recall by event_type x silent ===")
    for k, v in sorted(stats.items()):
        r = (v["tp"] / v["total"]) * 100 if v["total"] > 0 else 0
        print(f"{k[0]:22s} | {k[1]:10s}: TP={v['tp']:3d} / {v['total']:3d} ({r:5.1f}%)")

if __name__ == "__main__":
    analyze_seed("holdout")
