"""AeroTrust Detector Execution Pipeline.

Executes all Section 4.2 detectors:
1. JammingDetector (H3 spatial cell aggregation per 1-hour time bucket)
2. Spoofing Checks (a, b, c, d, e) with AbstentionEngine
Populates database tables: `interference_cells` and `spoof_checks`.
Logs exact execution runtime.
Quarantined from ground truth data.
"""

import io
import json
import os
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import h3
import numpy as np
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

# Ensure project root is on sys.path
root_path = Path(__file__).resolve().parents[3]
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.app.core.config import load_thresholds
from backend.app.detectors.abstention import AbstentionEngine
from backend.app.detectors.jamming import JammingDetector
from backend.app.detectors.spoofing import (
    GeoBaroAltDetector,
    KinematicFeasibilityDetector,
    ModeSEHSPhysicsDetector,
    MultiAircraftConsensusDetector,
    PosVelConsistencyDetector,
)


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", 5432)),
        user=os.getenv("POSTGRES_USER", "aerotrust"),
        password=os.getenv("POSTGRES_PASSWORD", "aerotrust_secret"),
        dbname=os.getenv("POSTGRES_DB", "aerotrust"),
    )


class DetectorPipeline:
    """Batch executor for AeroTrust detector suite."""

    def __init__(self):
        self.thresholds = load_thresholds()
        self.jamming_detector = JammingDetector(self.thresholds)
        self.geo_baro_detector = GeoBaroAltDetector(self.thresholds)
        self.kinematic_detector = KinematicFeasibilityDetector(self.thresholds)
        self.pos_vel_detector = PosVelConsistencyDetector(self.thresholds)
        self.consensus_detector = MultiAircraftConsensusDetector(self.thresholds)
        self.ehs_stub = ModeSEHSPhysicsDetector(self.thresholds)
        self.abstention_engine = AbstentionEngine(self.thresholds)

    def run(self, max_flights: Optional[int] = None) -> Dict[str, Any]:
        t0 = time.time()
        print("=== AeroTrust Batch Detector Pipeline ===")
        conn = get_db_connection()
        cur = conn.cursor()

        print("1. Fetching track points from database...")
        query = """
            SELECT icao24, ts, lat, lon, baro_alt_m, geo_alt_m, gs_mps, track_deg, vrate_mps, on_ground, nic, nacp, sil, h3_cell
            FROM flight_track_points
            ORDER BY icao24, ts;
        """
        cur.execute(query)
        columns = [desc[0] for desc in cur.description]
        raw_rows = cur.fetchall()
        print(f"Loaded {len(raw_rows):,} track points in {time.time() - t0:.2f}s.")

        df = pd.DataFrame(raw_rows, columns=columns)

        # -------------------------------------------------------------
        # Part 1: Jamming & Spatial Cell Aggregation (interference_cells)
        # Phase 2.6: Pooled over k=1 ring and 30-minute windows
        # -------------------------------------------------------------
        t_jam_start = time.time()
        print("\n2. Executing Jamming Detector with k=1 ring pooling & 30-minute buckets...")
        res5_cells = [h3.latlng_to_cell(lat, lon, 5) for lat, lon in zip(df["lat"], df["lon"])]
        df["h3_cell_res5"] = res5_cells
        df["time_bucket_30m"] = (df["ts"] // 1800) * 1800

        # Group indices by (cell_5, time_bucket_30m)
        cell_time_indices = defaultdict(list)
        for idx, (c5, tb) in enumerate(zip(df["h3_cell_res5"], df["time_bucket_30m"])):
            cell_time_indices[(c5, tb)].append(idx)

        active_keys = list(cell_time_indices.keys())
        interference_records = []

        for (cell_5, tb_30m) in active_keys:
            neighbors = h3.grid_disk(cell_5, 1)
            pooled_indices = []
            for nb in neighbors:
                if (nb, tb_30m) in cell_time_indices:
                    pooled_indices.extend(cell_time_indices[(nb, tb_30m)])

            if not pooled_indices:
                continue

            pooled_df = df.iloc[pooled_indices]
            res = self.jamming_detector.aggregate_cell(
                h3_cell=cell_5,
                time_bucket=int(tb_30m),
                cell_points_df=pooled_df,
                mode="v2_pooled",
            )
            interference_records.append((
                res["h3_cell"],
                res["time_bucket"],
                res["jam_score"],
                None,  # spoof_score updated later
                res["n_aircraft"],
                res["n_checks"],
                res["status"],
                json.dumps(res["reasons"]),
            ))

        print(f"Generated {len(interference_records):,} interference cell records in {time.time() - t_jam_start:.2f}s.")

        # Clear and insert interference_cells
        cur.execute("TRUNCATE TABLE interference_cells CASCADE;")
        insert_cells_sql = """
            INSERT INTO interference_cells (
                h3_cell, time_bucket, jam_score, spoof_score, n_aircraft, n_checks, status, reasons
            ) VALUES %s
            ON CONFLICT (h3_cell, time_bucket) DO UPDATE SET
                jam_score = EXCLUDED.jam_score,
                n_aircraft = EXCLUDED.n_aircraft,
                n_checks = EXCLUDED.n_checks,
                status = EXCLUDED.status,
                reasons = EXCLUDED.reasons;
        """
        execute_values(cur, insert_cells_sql, interference_records, page_size=5000)
        conn.commit()

        # -------------------------------------------------------------
        # Part 2: Spoofing Checks (a, b, c, e) per flight
        # -------------------------------------------------------------
        t_spoof_start = time.time()
        print("\n3. Executing Spoofing Detectors (Checks a, b, c, e)...")
        spoof_records = []

        flight_groups = df.groupby("icao24")
        all_icaos = list(flight_groups.groups.keys())
        if max_flights:
            all_icaos = all_icaos[:max_flights]

        # Decompose aircraft histories into individual flights (split on turnaround gaps > 10 min)
        flight_segments: List[pd.DataFrame] = []
        for icao in all_icaos:
            ac_df = flight_groups.get_group(icao).sort_values("ts")
            dts = np.diff(ac_df["ts"].values)
            split_indices = np.where(dts > 600)[0] + 1
            seg_dfs = np.split(ac_df, split_indices)
            for seg in seg_dfs:
                if len(seg) >= 3:
                    flight_segments.append(seg)

        print(f"Segmented {len(all_icaos)} aircraft into {len(flight_segments):,} distinct flights.")

        # First pass: run individual flight checks and record anomalies for consensus
        flight_anomalies_by_window = defaultdict(dict)  # (cell, 15m_bucket) -> {icao24: is_anomalous}
        flight_geo_baro_res_by_window = defaultdict(dict)  # (cell, 15m_bucket) -> {icao24: geo_baro_res}
        flight_check_cache = {}

        for flight_idx, flight_df in enumerate(flight_segments):
            icao = flight_df["icao24"].iloc[0]
            w_start = int(flight_df["ts"].min())
            w_end = int(flight_df["ts"].max())

            # Check a: Geo-Baro Alt
            res_a = self.geo_baro_detector.evaluate(flight_df)
            # Check b: Kinematic Feasibility (with gap & vrate isolation)
            res_b = self.kinematic_detector.evaluate(flight_df)
            # Check c: Position-Velocity Consistency (with gap isolation)
            res_c = self.pos_vel_detector.evaluate(flight_df)
            # Check e: Mode S Stub
            res_e = self.ehs_stub.evaluate(flight_df)

            flight_checks = {
                "geo_baro_alt": res_a,
                "kinematic_feasibility": res_b,
                "pos_vel_consistency": res_c,
                "mode_s_ehs_physics": res_e,
            }
            flight_check_cache[(icao, w_start)] = (w_start, w_end, flight_df, flight_checks)

            # Record if flight exhibited anomaly for consensus check (d)
            is_anom = bool(res_a["flag"] or res_c["flag"])
            rep_cell = flight_df["h3_cell_res5"].iloc[len(flight_df) // 2]
            bucket_15m = w_start // 900
            flight_anomalies_by_window[(rep_cell, bucket_15m)][icao] = is_anom
            flight_geo_baro_res_by_window[(rep_cell, bucket_15m)][icao] = res_a["residual"]

        # Second pass: Check (a) Peer Relativity, Check (d) Consensus & Abstention arbitration
        print("4. Executing Peer Relativity, Check (d) Consensus & Abstention Arbitration...")
        for (icao, w_start), (w_start, w_end, flight_df, f_checks) in flight_check_cache.items():
            rep_cell = flight_df["h3_cell_res5"].iloc[len(flight_df) // 2]
            bucket_15m = w_start // 900

            # Gather peer residuals & peer anomalies in k-ring (k=1)
            neighbors = h3.grid_disk(rep_cell, 1)
            peer_anoms = {}
            peer_geo_baro_residuals = []
            for nb in neighbors:
                if (nb, bucket_15m) in flight_anomalies_by_window:
                    for p_icao, anom_val in flight_anomalies_by_window[(nb, bucket_15m)].items():
                        if p_icao != icao:
                            peer_anoms[p_icao] = anom_val
                if (nb, bucket_15m) in flight_geo_baro_res_by_window:
                    for p_icao, p_res in flight_geo_baro_res_by_window[(nb, bucket_15m)].items():
                        if p_icao != icao:
                            peer_geo_baro_residuals.append(p_res)

            # Refine Check (a) with peer-relative residual feature (Phase 2.6)
            if f_checks["geo_baro_alt"]["flag"] and peer_geo_baro_residuals:
                refined_res_a = self.geo_baro_detector.evaluate(
                    flight_df, peer_residuals=peer_geo_baro_residuals
                )
                f_checks["geo_baro_alt"] = refined_res_a

            # Evaluate consensus
            res_d = self.consensus_detector.evaluate(
                target_icao=icao,
                h3_cell=rep_cell,
                window_start_ts=w_start,
                window_end_ts=w_end,
                peer_anomalies_in_neighborhood=peer_anoms,
            )
            f_checks["multi_aircraft_consensus"] = res_d

            # Apply AbstentionEngine
            final_status, abstention_reasons, comp_conf = self.abstention_engine.evaluate_flight_checks(
                f_checks, total_points=len(flight_df)
            )

            # Record each check in spoof_checks
            for check_name, res in f_checks.items():
                spoof_records.append((
                    icao,
                    w_start,
                    w_end,
                    check_name,
                    res["residual"],
                    res["flag"],
                    res["confidence"],
                    res["n_points"],
                    res["status"],
                    json.dumps(res.get("reasons", [])),
                ))

        print(f"Generated {len(spoof_records):,} spoof_checks rows in {time.time() - t_spoof_start:.2f}s.")

        # Ingest into spoof_checks using execute_values
        print("Ingesting spoof_checks into PostgreSQL...")
        cur.execute("TRUNCATE TABLE spoof_checks CASCADE;")
        insert_spoof_sql = """
            INSERT INTO spoof_checks (
                icao24, ts_window_start, ts_window_end, check_name, residual, flag, confidence, n_points, status, reasons
            ) VALUES %s;
        """
        execute_values(cur, insert_spoof_sql, spoof_records, page_size=5000)
        conn.commit()

        total_runtime = time.time() - t0
        print(f"\nPipeline finished in {total_runtime:.2f} seconds.")
        print(f"Total interference cells populated: {len(interference_records):,}")
        print(f"Total spoof checks populated:       {len(spoof_records):,}")

        # Summary counts
        cur.execute("SELECT status, count(*) FROM spoof_checks GROUP BY status;")
        spoof_summary = dict(cur.fetchall())
        cur.execute("SELECT status, count(*) FROM interference_cells GROUP BY status;")
        jam_summary = dict(cur.fetchall())
        conn.close()

        return {
            "total_runtime_seconds": round(total_runtime, 2),
            "interference_cells_count": len(interference_records),
            "spoof_checks_count": len(spoof_records),
            "spoof_checks_by_status": spoof_summary,
            "interference_cells_by_status": jam_summary,
        }


if __name__ == "__main__":
    pipeline = DetectorPipeline()
    results = pipeline.run()
    print("\nExecution Summary:")
    print(json.dumps(results, indent=2))
