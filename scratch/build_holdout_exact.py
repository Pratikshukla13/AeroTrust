import json
import math
import os
import sys
from collections import defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import h3
import numpy as np
import pandas as pd
import yaml

root_path = Path(__file__).resolve().parents[1]
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.app.core.config import load_thresholds
from backend.app.detectors.abstention import AbstentionEngine
from backend.app.detectors.spoofing import (
    GeoBaroAltDetector,
    KinematicFeasibilityDetector,
    MultiAircraftConsensusDetector,
    PosVelConsistencyDetector,
)
from backend.app.detectors.trust_score import TrustScoreEngine
from data.synthetic.generator import SyntheticWorldGenerator

def build_holdout_exact():
    print("=== Generating Exact Holdout Table for Seed 2024 ===")
    gen = SyntheticWorldGenerator(config_path="config/synthetic.yaml", seed_mode="holdout")
    start_ts = int(datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc).timestamp())
    n_days = 7
    end_ts = start_ts + (n_days * 86400)

    aircraft_list = gen.generate_aircraft_registry(600)
    gt_events = gen.generate_ground_truth_events(start_ts, end_ts)
    sw_list = gen.generate_space_weather(start_ts, n_days, step_seconds=3600)
    scanner_aircraft, pitch_down_points = gen.generate_pitch_down_test_flight(start_ts)
    aircraft_list.append(scanner_aircraft)

    tracks = gen.generate_flight_tracks(aircraft_list, gt_events, 6000, start_ts, 30)
    tracks.extend(pitch_down_points)
    manifest = gen.flight_manifest

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
                    "flight_id": f"{icao}_{seg_df['ts'].iloc[0]}",
                    "start_ts": int(seg_df["ts"].iloc[0]),
                    "end_ts": int(seg_df["ts"].iloc[-1]),
                    "df": seg_df,
                    "n_points": len(seg_df),
                })

    manifest_by_icao = defaultdict(list)
    for m in manifest:
        manifest_by_icao[m["icao24"]].append(m)

    thresholds = load_thresholds()
    geo_baro = GeoBaroAltDetector(thresholds)
    kinematic = KinematicFeasibilityDetector(thresholds)
    pos_vel = PosVelConsistencyDetector(thresholds)
    consensus = MultiAircraftConsensusDetector(thresholds)
    abstention = AbstentionEngine(thresholds)
    trust_engine = TrustScoreEngine()

    for seg in flight_segments:
        icao = seg["icao24"]
        st = seg["start_ts"]
        et = seg["end_ts"]
        cands = manifest_by_icao.get(icao, [])
        overlaps = [m for m in cands if not (et < m["start_ts"] or st > m["end_ts"])]

        is_spf = any(m["applied"] and m["event_type"] == "spoofing" for m in overlaps)
        is_jam = any(m["applied"] and m["event_type"] == "jamming" for m in overlaps)
        is_clean = not is_spf and not is_jam
        pts_nic = seg["df"]["nic"].values
        pts_nacp = seg["df"]["nacp"].values
        is_silent = bool(np.mean(pts_nic >= 7) > 0.5)

        # Flags-only baseline: NIC < 7 or NACp < 8
        flag_nic_nacp = bool(np.min(pts_nic) < 7 or np.min(pts_nacp) < 8)

        # Detectors
        res_a = geo_baro.evaluate(seg["df"])
        res_b = kinematic.evaluate(seg["df"])
        res_c = pos_vel.evaluate(seg["df"])

        # Consensus stub for holdout
        flag_a = res_a["flag"]
        flag_b = res_b["flag"]
        flag_c = res_c["flag"]
        flag_d = False

        status, reasons, _ = abstention.evaluate_flight_checks(
            {"geo_baro_alt": res_a, "kinematic_feasibility": res_b, "pos_vel_consistency": res_c},
            total_points=seg["n_points"],
        )

        flag_physics_all = (flag_a or flag_b or flag_c or flag_d)
        flag_comp2 = (flag_a or flag_d) and (status != "unknown")
        flag_union = flag_nic_nacp or flag_comp2

        seg["is_spf"] = is_spf
        seg["is_jam"] = is_jam
        seg["is_clean"] = is_clean
        seg["is_silent"] = is_silent
        seg["flags_only"] = flag_nic_nacp
        seg["physics_all"] = flag_physics_all
        seg["composite_v2"] = flag_comp2
        seg["flags_or_composite_v2"] = flag_union

        # Trust tier
        jam_tier = "degraded" if is_jam else "clear"
        eval_tr = trust_engine.evaluate_overall_flight(
            flight_id=seg["flight_id"],
            segment_start=st,
            segment_end=et,
            checks={"geo_baro_alt": res_a, "kinematic_feasibility": res_b, "pos_vel_consistency": res_c},
            total_points=seg["n_points"],
            jamming_status=jam_tier,
            jamming_confidence=0.85 if is_jam else 0.80,
            peer_support_ratio=0.0,  # conservative holdout
        )
        seg["tier"] = eval_tr["status"]

    total_clean = sum(1 for s in flight_segments if s["is_clean"])
    total_spoof = sum(1 for s in flight_segments if s["is_spf"])
    total_jam = sum(1 for s in flight_segments if s["is_jam"])

    print(f"Holdout counts: Clean={total_clean}, Spoof={total_spoof}, Jam={total_jam}")

    # Evaluate each detector row
    rows_data = []
    for row_name, key in [
        ("flags-only baseline (NIC/NACp)", "flags_only"),
        ("physics_all (a OR b OR c OR d)", "physics_all"),
        ("composite_v2 (Corroborated: a OR d)", "composite_v2"),
        ("flags OR composite_v2", "flags_or_composite_v2"),
    ]:
        tp, fp, fn, tn = 0, 0, 0, 0
        tp_sil, fn_sil = 0, 0
        tp_nonsil, fn_nonsil = 0, 0
        fp_jam = 0
        fp_clean = 0

        for seg in flight_segments:
            flag = seg[key]
            if seg["is_spf"]:
                if flag:
                    tp += 1
                    if seg["is_silent"]: tp_sil += 1
                    else: tp_nonsil += 1
                else:
                    fn += 1
                    if seg["is_silent"]: fn_sil += 1
                    else: fn_nonsil += 1
            else:
                if flag:
                    fp += 1
                    if seg["is_jam"]: fp_jam += 1
                    else: fp_clean += 1
                else:
                    tn += 1

        prec = (tp / max(1, tp + fp)) * 100.0
        rec = (tp / max(1, tp + fn)) * 100.0
        f1 = (2 * prec * rec) / max(1e-9, prec + rec)
        rec_sil = (tp_sil / max(1, tp_sil + fn_sil)) * 100.0
        rec_nonsil = (tp_nonsil / max(1, tp_nonsil + fn_nonsil)) * 100.0
        fp_per_1k = (fp_clean / max(1, total_clean)) * 1000.0

        rows_data.append({
            "name": row_name,
            "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "prec": prec, "rec": rec, "f1": f1,
            "rec_sil": rec_sil, "rec_nonsil": rec_nonsil,
            "fp_per_1k": fp_per_1k,
            "fp_jam": fp_jam, "fp_clean": fp_clean,
        })

    # Evidence tiers for holdout
    tier_stats = []
    for t in ["no_alert", "degraded", "assured_clear", "insufficient", "unknown"]:
        t_segs = [s for s in flight_segments if s["tier"] == t]
        cnt = len(t_segs)
        n_spf = sum(1 for s in t_segs if s["is_spf"])
        n_jam = sum(1 for s in t_segs if s["is_jam"])
        n_host = sum(1 for s in t_segs if s["is_spf"] or s["is_jam"])
        host_pct = (n_host / max(1, cnt)) * 100.0
        npv = ((cnt - n_host) / max(1, cnt)) * 100.0
        tier_stats.append({
            "tier": t, "count": cnt,
            "n_spf": n_spf, "n_jam": n_jam, "n_host": n_host,
            "host_pct": host_pct, "npv": npv,
        })

    return rows_data, tier_stats, total_clean, total_spoof, total_jam, len(flight_segments)

if __name__ == "__main__":
    rows, tiers, n_cln, n_spf, n_jam, n_tot = build_holdout_exact()
    print("\n--- Rows ---")
    for r in rows:
        print(r)
    print("\n--- Tiers ---")
    for t in tiers:
        print(t)

