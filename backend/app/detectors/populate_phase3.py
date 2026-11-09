"""AeroTrust Phase 3 Population Pipeline.

Populates `radiation_index` and `trust_scores` tables in PostgreSQL:
1. Computes 5-minute flight radiation exposures via RadiationCalculator.
2. Computes integrated Two-Axis trust scores via TrustScoreEngine.
3. Ingests all records using high-performance execute_values.
"""

import json
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import h3

root_path = Path(__file__).resolve().parents[3]
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.app.detectors.radiation import RadiationCalculator
from backend.app.detectors.trust_score import TrustScoreEngine


def get_db():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", 5432)),
        user=os.getenv("POSTGRES_USER", "aerotrust"),
        password=os.getenv("POSTGRES_PASSWORD", "aerotrust_secret"),
        dbname=os.getenv("POSTGRES_DB", "aerotrust"),
    )


def populate_phase3():
    t0 = time.time()
    print("=== AeroTrust Phase 3 Database Population Pipeline ===")
    conn = get_db()
    cur = conn.cursor()

    rad_calc = RadiationCalculator()
    trust_engine = TrustScoreEngine()

    # 1. Fetch space weather observations into hourly lookup
    print("1. Fetching space weather observations...")
    cur.execute("SELECT ts, kp, proton_flux_10mev FROM space_weather ORDER BY ts;")
    sw_lookup = {}
    for ts, kp, flux in cur.fetchall():
        sw_lookup[ts] = (kp, flux)
    print(f"Loaded {len(sw_lookup)} space weather hourly observations.")

    # 2. Fetch distinct flight segments from spoof_checks
    print("2. Fetching flight checks from spoof_checks...")
    cur.execute("""
        SELECT icao24, ts_window_start, ts_window_end, check_name, residual, flag, confidence, status, reasons
        FROM spoof_checks;
    """)
    checks_rows = cur.fetchall()
    checks_by_fl = defaultdict(dict)
    flight_windows = {}
    for icao, st, et, chk, res, flag, conf, status, reasons in checks_rows:
        checks_by_fl[(icao, st)][chk] = {
            "residual": res,
            "flag": flag,
            "confidence": conf,
            "status": status,
            "reasons": json.loads(reasons) if isinstance(reasons, str) else (reasons or [])
        }
        flight_windows[(icao, st)] = (et)
    print(f"Loaded checks for {len(checks_by_fl):,} distinct flights.")

    # 3. Fetch flight track points grouped by flight window
    print("3. Fetching track points and computing radiation index in 5-minute segments...")
    cur.execute("""
        SELECT id, icao24, ts, lat, lon, baro_alt_m
        FROM flight_track_points
        ORDER BY icao24, ts;
    """)
    tracks = cur.fetchall()
    df_tracks = pd.DataFrame(tracks, columns=["id", "icao24", "ts", "lat", "lon", "baro_alt_m"])
    tracks_by_icao = {icao: group for icao, group in df_tracks.groupby("icao24")}
    print(f"Indexed {len(df_tracks):,} track points across {len(tracks_by_icao)} aircraft.")

    # Fetch jamming cells to map flights
    cur.execute("SELECT h3_cell, time_bucket, status FROM interference_cells WHERE status = 'degraded';")
    degraded_cells = set((r[0], r[1]) for r in cur.fetchall())

    rad_records = []
    trust_records = []

    for (icao, st), checks in checks_by_fl.items():
        et = flight_windows[(icao, st)]
        ac_tracks = tracks_by_icao.get(icao)
        if ac_tracks is None:
            continue
        fl_df = ac_tracks[(ac_tracks["ts"] >= st) & (ac_tracks["ts"] <= et)]
        if fl_df.empty:
            continue

        flight_id = f"{icao}_{st}"
        n_points = len(fl_df)

        # Radiation calculation (5-minute segments)
        rad_segments = rad_calc.compute_flight_segments(fl_df, sw_lookup=sw_lookup, segment_sec=300)
        max_rad_segment = None
        max_rad_idx = 0.0
        for seg in rad_segments:
            rad_records.append((
                seg["icao24"],
                seg["ts"],
                seg["alt_m"],
                seg["geomag_lat"],
                seg["relative_index"],
                json.dumps(seg["components"]),
            ))
            if seg["relative_index"] > max_rad_idx:
                max_rad_idx = seg["relative_index"]
                max_rad_segment = seg

        # Jamming status check: does this flight overlap any degraded interference cell?
        has_degraded_jamming = False
        sample_pts = fl_df.iloc[::max(1, len(fl_df) // 10)]
        for _, r in sample_pts.iterrows():
            c = h3.latlng_to_cell(r["lat"], r["lon"], 5)
            tb = (int(r["ts"]) // 1800) * 1800
            if (c, tb) in degraded_cells:
                has_degraded_jamming = True
                break

        jam_status = "degraded" if has_degraded_jamming else "clear"
        jam_conf = 0.85 if has_degraded_jamming else 0.80

        # Peer support check: does this flight have peer support across its windows?
        chk_d = checks.get("multi_aircraft_consensus", {})
        has_consensus = (chk_d.get("status") not in ["unknown", "insufficient", None])
        peer_ratio = 1.0 if has_consensus else 0.0

        # Evaluate Trust Score
        eval_result = trust_engine.evaluate_overall_flight(
            flight_id=flight_id,
            segment_start=st,
            segment_end=et,
            checks=checks,
            total_points=n_points,
            jamming_status=jam_status,
            jamming_confidence=jam_conf,
            radiation_summary=max_rad_segment,
            peer_support_ratio=peer_ratio,
        )

        trust_records.append((
            eval_result["flight_id"],
            eval_result["segment_start"],
            eval_result["segment_end"],
            eval_result["score"],
            eval_result["uncertainty"],
            eval_result["status"],
            json.dumps({
                "reasons": eval_result["reasons"],
                "axis_a": eval_result["axis_a"],
                "axis_b": eval_result["axis_b"],
            }),
        ))

    print(f"\nGenerated {len(rad_records):,} radiation_index rows.")
    print(f"Generated {len(trust_records):,} trust_scores rows.")

    # Clear existing and insert
    print("Ingesting radiation_index records...")
    cur.execute("TRUNCATE TABLE radiation_index CASCADE;")
    execute_values(
        cur,
        """
        INSERT INTO radiation_index (icao24, ts, alt_m, geomag_lat, relative_index, components)
        VALUES %s;
        """,
        rad_records,
        page_size=5000,
    )

    print("Ingesting trust_scores records...")
    cur.execute("TRUNCATE TABLE trust_scores CASCADE;")
    execute_values(
        cur,
        """
        INSERT INTO trust_scores (flight_id, segment_start, segment_end, score, uncertainty, status, reasons)
        VALUES %s;
        """,
        trust_records,
        page_size=5000,
    )

    conn.commit()
    conn.close()
    print(f"Phase 3 database population complete in {time.time() - t0:.2f} seconds!")


if __name__ == "__main__":
    populate_phase3()

