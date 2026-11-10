"""Phase 4.1 Experiments: Monte Carlo (D2), Seed Variance (4001-4012), and Abstention Demo."""

import sys
import math
import random
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import asdict
from collections import Counter
import numpy as np
import pandas as pd

root_path = Path(__file__).resolve().parents[1]
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.app.core.config import load_thresholds
from backend.app.detectors.spoofing import GeoBaroAltDetector
from backend.app.detectors.abstention import AbstentionEngine
from backend.app.detectors.silent_check import is_silent_flight
from data.synthetic.generator import SyntheticWorldGenerator

def run_monte_carlo_d2(n_flights: int = 100_000):
    print(f"=== TASK 5: MONTE CARLO D2 ({n_flights:,} flights) ===")
    np.random.seed(42)
    threshold = 120.0
    noise_sigma = 15.0
    baro_drift_p = 0.02
    min_points = 5

    # Duration profile from config:
    # 15% short [35, 55] min
    # 65% med [60, 180] min
    # 20% long [180, 330] min
    # At 30s interval:
    # short: [70, 110] pts
    # med: [120, 360] pts
    # long: [360, 660] pts
    leg_flags = 0
    seg_flags = 0

    # Simulate legs
    flight_lens = []
    dur_choices = np.random.choice([0, 1, 2], size=n_flights, p=[0.15, 0.65, 0.20])
    for choice in dur_choices:
        if choice == 0:
            pts = np.random.randint(70, 111)
        elif choice == 1:
            pts = np.random.randint(120, 361)
        else:
            pts = np.random.randint(360, 661)
        flight_lens.append(pts)

    for pts in flight_lens:
        # Differential noise: geo_noise - baro_noise ~ N(0, 2 * 15^2)
        diff_noise = np.random.normal(0, np.sqrt(2) * noise_sigma, size=pts)
        # Baro bias: with p=0.02, uniform in [60, 180]
        mask = np.random.random(size=pts) < baro_drift_p
        biases = np.zeros(pts)
        if np.any(mask):
            biases[mask] = np.random.uniform(60.0, 180.0, size=np.sum(mask))

        diff = diff_noise - biases
        baseline = np.median(diff)
        residuals = np.abs(diff - baseline)
        stat = np.percentile(residuals, 95.0)

        if stat > threshold:
            leg_flags += 1

    leg_rate = (leg_flags / n_flights) * 100.0
    print(f"Monte Carlo Leg-Level Flagged: {leg_flags}/{n_flights:,} = {leg_rate:.3f}% (compare to ~0.955% pure baro drift)")

    # Simulate merged segments (merging 2-3 legs: 250 to 1200 pts)
    n_segs = n_flights // 2
    seg_flag_cnt = 0
    for _ in range(n_segs):
        pts = np.random.randint(300, 1000)
        diff_noise = np.random.normal(0, np.sqrt(2) * noise_sigma, size=pts)
        mask = np.random.random(size=pts) < baro_drift_p
        biases = np.zeros(pts)
        if np.any(mask):
            biases[mask] = np.random.uniform(60.0, 180.0, size=np.sum(mask))
        diff = diff_noise - biases
        baseline = np.median(diff)
        residuals = np.abs(diff - baseline)
        stat = np.percentile(residuals, 95.0)
        if stat > threshold:
            seg_flag_cnt += 1

    seg_rate = (seg_flag_cnt / n_segs) * 100.0
    print(f"Monte Carlo Segment-Level Flagged: {seg_flag_cnt}/{n_segs:,} = {seg_rate:.3f}% (compare to ~0.17% segment FPR)")

    return leg_rate, seg_rate

def run_seed_variance_tasks():
    print("\n=== TASK 6: SEED VARIANCE (Seeds 4001 to 4012) ===")
    thresholds = load_thresholds()
    geo_baro = GeoBaroAltDetector(thresholds)

    clean_fp_counts = []
    trunc_counts = []
    baro_counts = []

    for s in range(4001, 4013):
        t0 = datetime.now()
        gen = SyntheticWorldGenerator(config_path="config/synthetic.yaml", seed_mode=s)
        start_ts = int(datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc).timestamp())
        n_days = 7
        end_ts = start_ts + (n_days * 86400)

        aircraft_list = gen.generate_aircraft_registry(600)
        gt_events = gen.generate_ground_truth_events(start_ts, end_ts)
        scanner_aircraft, pitch_down_points = gen.generate_pitch_down_test_flight(start_ts)
        aircraft_list.append(scanner_aircraft)

        tracks = gen.generate_flight_tracks(
            aircraft_list=aircraft_list,
            ground_truth_events=gt_events,
            n_flights=6000,
            start_ts=start_ts,
            sampling_interval=30,
        )
        manifest = list(gen.flight_manifest)

        df_tracks = pd.DataFrame([asdict(t) for t in tracks])
        tracks_by_icao = {icao: grp.sort_values("ts") for icao, grp in df_tracks.groupby("icao24")}

        c_fps = 0
        t_fps = 0
        b_fps = 0

        for m in manifest:
            is_spf = bool(m["applied"] and m["event_type"] == "spoofing")
            is_jam = bool(m["applied"] and m["event_type"] == "jamming")
            if not is_spf and not is_jam:
                icao = m["icao24"]
                l_st = m["start_ts"]
                l_et = m["end_ts"]
                icao_grp = tracks_by_icao.get(icao, None)
                if icao_grp is not None and not icao_grp.empty:
                    leg_df = icao_grp[(icao_grp["ts"] >= l_st) & (icao_grp["ts"] <= l_et)]
                else:
                    leg_df = pd.DataFrame()

                res_a = geo_baro.evaluate(leg_df) if not leg_df.empty else {"flag": False}
                if res_a.get("flag", False):
                    c_fps += 1
                    if l_st == 1794078000:
                        t_fps += 1
                    else:
                        b_fps += 1

        clean_fp_counts.append(c_fps)
        trunc_counts.append(t_fps)
        baro_counts.append(b_fps)
        print(f"Seed {s}: Total Clean FP={c_fps} (Trunc={t_fps}, Pure Baro={b_fps}) in {(datetime.now()-t0).total_seconds():.1f}s")

    mean_baro = np.mean(baro_counts)
    std_baro = np.std(baro_counts, ddof=1)
    min_baro = np.min(baro_counts)
    max_baro = np.max(baro_counts)
    print(f"Baro FP Stats across 12 seeds: Mean={mean_baro:.2f}, Std={std_baro:.2f}, Min={min_baro}, Max={max_baro}")
    print(f"Theoretical Binomial SD (N=3650, p=0.0096) = {np.sqrt(3650 * 0.0096 * 0.9904):.2f}")

    return {
        "seeds": list(range(4001, 4013)),
        "clean_fps": clean_fp_counts,
        "trunc_fps": trunc_counts,
        "baro_fps": baro_counts,
        "mean_baro": mean_baro,
        "std_baro": std_baro,
        "min_baro": min_baro,
        "max_baro": max_baro,
    }

if __name__ == "__main__":
    run_monte_carlo_d2(100_000)
    run_seed_variance_tasks()
