"""AeroTrust Database & Synthetic Data Management CLI.

Provides one-command operations:
- Apply schema migrations for all README Section 3 tables.
- Generate full synthetic world (500 aircraft, 3000 flights, 7 days).
- Ingest and populate PostgreSQL/PostGIS.
- Report exact row counts per table.
"""

import argparse
from dataclasses import asdict
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import h3
import numpy as np
import psycopg2
from psycopg2.extras import execute_batch, execute_values

# Ensure project root is on sys.path
root_path = Path(__file__).resolve().parents[2]
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from backend.app.core.config import settings
from data.synthetic.generator import SyntheticWorldGenerator
from data.synthetic.schemas import (
    SyntheticAircraft,
    SyntheticIncidentCase,
    SyntheticSpaceWeatherPoint,
    SyntheticTrackPoint,
)

ALL_TABLES = [
    "aircraft",
    "flight_track_points",
    "spoof_checks",
    "interference_cells",
    "space_weather",
    "radiation_index",
    "trust_scores",
    "sar_aggregate",
    "incident_cases",
    "precursor_candidates",
]


def get_db_connection():
    """Connects to PostgreSQL using configured environment parameters."""
    host = os.getenv("DB_HOST", "localhost")
    port = int(os.getenv("DB_PORT", "5432"))
    user = os.getenv("DB_USER", "aerotrust")
    password = os.getenv("DB_PASSWORD", "aerotrust_secret")
    dbname = os.getenv("DB_NAME", "aerotrust")

    return psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        dbname=dbname,
        connect_timeout=10,
    )


def apply_migrations(conn):
    """Applies SQL migrations for all tables in README Section 3."""
    migration_path = Path(__file__).resolve().parents[1] / "migrations" / "001_initial_schema.sql"
    with open(migration_path, "r", encoding="utf-8") as f:
        sql = f.read()

    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    print("Successfully applied migration 001_initial_schema.sql (PostGIS & all Section 3 tables).")


def load_dataset(
    conn,
    n_aircraft: int = 500,
    n_flights: int = 3000,
    n_days: int = 7,
    sampling_sec: int = 30,
    seed_mode: str = "dev",
):
    """Generates synthetic dataset and loads it into PostgreSQL in batches."""
    print(f"\n--- Generating synthetic world (Scale: {n_aircraft} aircraft, {n_flights} flights, {n_days} days) ---")
    gen = SyntheticWorldGenerator(config_path="config/synthetic.yaml", seed_mode=seed_mode)

    start_ts = 1793491200  # Epoch Nov 2026
    end_ts = start_ts + (n_days * 86400)

    # 1. Aircraft
    aircraft_list = gen.generate_aircraft_registry(n_aircraft)
    print(f"Generated {len(aircraft_list)} aircraft.")

    # 2. Ground truth events (KEPT SEPARATE ON DISK ONLY, NEVER IN DATABASE)
    gt_events = gen.generate_ground_truth_events(start_ts, end_ts)
    gt_dir = os.path.join("data", "synthetic", "ground_truth")
    os.makedirs(gt_dir, exist_ok=True)
    with open(os.path.join(gt_dir, "ground_truth_events.json"), "w", encoding="utf-8") as f:
        json.dump([asdict(e) for e in gt_events], f, indent=2)

    # 3. Space Weather
    sw_list = gen.generate_space_weather(start_ts, n_days, step_seconds=3600)
    print(f"Generated {len(sw_list)} space weather observations.")

    # 4. Incident Cases
    incidents = gen.generate_incident_cases()
    print(f"Loaded {len(incidents)} public incident cases from README Section 4.6.")

    # 5. Precursor flight
    scanner_aircraft, pitch_down_points = gen.generate_pitch_down_test_flight(start_ts)
    aircraft_list.append(scanner_aircraft)

    # 6. Flight Tracks
    print("Generating trajectories (this includes climbs, cruises, descents, and hard negatives)...")
    tracks = gen.generate_flight_tracks(
        aircraft_list=aircraft_list,
        ground_truth_events=gt_events,
        n_flights=n_flights,
        start_ts=start_ts,
        sampling_interval=sampling_sec,
    )
    # Append pitch down flight points
    tracks.extend(pitch_down_points)
    gen.flight_manifest.append({
        "flight_id": f"{scanner_aircraft.icao24}_{start_ts}",
        "icao24": scanner_aircraft.icao24,
        "start_ts": start_ts,
        "end_ts": start_ts + len(pitch_down_points) * sampling_sec,
        "event_id": None,
        "event_type": None,
        "applied": False,
        "inj_start": None,
        "inj_end": None,
    })

    # Save Flight Manifest in ground-truth folder
    manifest_file = os.path.join(gt_dir, "flight_manifest.json")
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(gen.flight_manifest, f, indent=2)
    print(f"Generated ground-truth flight manifest ({len(gen.flight_manifest)} flights) saved to {manifest_file}.")
    print(f"Generated total of {len(tracks):,} track points across {n_flights + 1} flights.")

    durations = gen.last_flight_durations_minutes
    if durations:
        d_min = float(np.min(durations))
        d_med = float(np.median(durations))
        d_mean = float(np.mean(durations))
        d_max = float(np.max(durations))
        print("\n--- Flight Duration Distribution (Realistic Airline Operations) ---")
        print(f"  Min:    {d_min:6.1f} min ({d_min/60.0:4.2f} h)")
        print(f"  Median: {d_med:6.1f} min ({d_med/60.0:4.2f} h)")
        print(f"  Mean:   {d_mean:6.1f} min ({d_mean/60.0:4.2f} h)")
        print(f"  Max:    {d_max:6.1f} min ({d_max/60.0:4.2f} h)")

    print("\n--- Ingesting into PostgreSQL + PostGIS ---")
    cur = conn.cursor()

    # Clear existing data
    for table in reversed(ALL_TABLES):
        cur.execute(f"TRUNCATE TABLE {table} CASCADE;")

    # Ingest Aircraft
    aircraft_tuples = [
        (a.icao24, a.registration, a.type_code, a.family, a.operator)
        for a in aircraft_list
    ]
    execute_values(
        cur,
        """
        INSERT INTO aircraft (icao24, registration, type_code, family, operator)
        VALUES %s
        ON CONFLICT (icao24) DO NOTHING;
        """,
        aircraft_tuples,
    )

    # Ingest Space Weather
    sw_tuples = [
        (sw.ts, sw.kp, sw.proton_flux_10mev, sw.xray_flux, sw.raw_payload_ref)
        for sw in sw_list
    ]
    execute_values(
        cur,
        """
        INSERT INTO space_weather (ts, kp, proton_flux_10mev, xray_flux, raw_payload_ref)
        VALUES %s
        ON CONFLICT (ts) DO NOTHING;
        """,
        sw_tuples,
    )

    # Ingest Incident Cases
    incident_tuples = [
        (
            inc.case_id,
            inc.name,
            inc.trigger_date,
            inc.public_statement_date,
            inc.directive_date,
            inc.aircraft_held_in_service,
            inc.aircraft_held_undelivered,
            inc.days_to_scope,
            inc.source_urls,
        )
        for inc in incidents
    ]
    execute_values(
        cur,
        """
        INSERT INTO incident_cases (
            case_id, name, trigger_date, public_statement_date, directive_date,
            aircraft_held_in_service, aircraft_held_undelivered, days_to_scope, source_urls
        )
        VALUES %s
        ON CONFLICT (case_id) DO NOTHING;
        """,
        incident_tuples,
    )

    # Note: Per Phase 0.5 rules, precursor_candidates table is NOT pre-seeded.
    # Only the precursor scanner module may write to that table.

    # Ingest Track Points using high-performance streaming COPY
    print("Ingesting flight track points with H3 spatial indexing and PostGIS geometries...")
    import io
    chunk_size = 100000
    copy_sql = """
    COPY flight_track_points (
        icao24, ts, lat, lon, baro_alt_m, geo_alt_m, gs_mps, track_deg, vrate_mps,
        on_ground, nic, nacp, sil, source_note, h3_cell, geom
    ) FROM STDIN WITH (FORMAT csv, DELIMITER '\t');
    """

    for chunk_start in range(0, len(tracks), chunk_size):
        chunk = tracks[chunk_start : chunk_start + chunk_size]
        sio = io.StringIO()
        for pt in chunk:
            cell = h3.latlng_to_cell(pt.lat, pt.lon, 7)
            geom_str = f"SRID=4326;POINT({pt.lon} {pt.lat})"
            on_ground_str = "TRUE" if pt.on_ground else "FALSE"
            sio.write(
                f"{pt.icao24}\t{pt.ts}\t{pt.lat}\t{pt.lon}\t{pt.baro_alt_m}\t{pt.geo_alt_m}\t"
                f"{pt.gs_mps}\t{pt.track_deg}\t{pt.vrate_mps}\t{on_ground_str}\t{pt.nic}\t{pt.nacp}\t"
                f"{pt.sil}\t{pt.source_note}\t{cell}\t{geom_str}\n"
            )
        sio.seek(0)
        cur.copy_expert(copy_sql, sio)

    conn.commit()
    print("Ingestion complete!")


def get_table_counts(conn) -> Dict[str, int]:
    """Retrieves exact row counts for EVERY table in README Section 3."""
    counts = {}
    with conn.cursor() as cur:
        for table in ALL_TABLES:
            cur.execute(f"SELECT count(*) FROM {table};")
            counts[table] = cur.fetchone()[0]
    return counts


def report_counts(counts: Dict[str, int]):
    """Prints a formatted markdown-like table of row counts."""
    print("\n=======================================================")
    print("       AEROTRUST DATABASE STATUS & ROW COUNTS          ")
    print("=======================================================")
    print(f"{'Table Name':<28} | {'Row Count':>14}")
    print("-" * 46)
    for table in ALL_TABLES:
        print(f"{table:<28} | {counts.get(table, 0):>14,}")
    print("=======================================================\n")


def main():
    parser = argparse.ArgumentParser(description="AeroTrust Data & Database CLI")
    parser.add_argument("--migrate", action="store_true", help="Apply SQL migrations")
    parser.add_argument("--generate-and-load", action="store_true", help="Generate dataset and load to Postgres")
    parser.add_argument("--scale", choices=["default", "quick"], default="default",
                        help="Scale: default (600 aircraft, 6000 flights) or quick (50 aircraft, 150 flights)")
    parser.add_argument("--seed-mode", choices=["dev", "test"], default="test",
                        help="Seed mode: dev (42) or test (1337)")
    parser.add_argument("--counts", action="store_true", help="Print table row counts")

    args = parser.parse_args()

    try:
        conn = get_db_connection()
    except Exception as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        print("Ensure PostgreSQL/PostGIS container is running (`docker compose up -d`).")
        sys.exit(1)

    if args.migrate or args.generate_and_load:
        apply_migrations(conn)

    if args.generate_and_load:
        if args.scale == "default":
            load_dataset(conn, n_aircraft=600, n_flights=6000, n_days=7, sampling_sec=30, seed_mode=args.seed_mode)
        else:
            load_dataset(conn, n_aircraft=50, n_flights=150, n_days=7, sampling_sec=30, seed_mode=args.seed_mode)

    counts = get_table_counts(conn)
    report_counts(counts)
    conn.close()


if __name__ == "__main__":
    main()
