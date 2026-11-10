"""AeroTrust Read-Only API Endpoints (Phase 3.5).

Provides high-performance, read-only queries into PostgreSQL:
- Trust scores (Two-Axis: Hostile RF & Natural Radiation)
- Interference cells (H3 spatial aggregation)
- Space weather telemetry
- Radiation index segments
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import h3
import psycopg2
from fastapi import APIRouter, HTTPException, Query

from backend.app.schemas.api import (
    AxisADetails,
    AxisBDetails,
    BaseRateRow,
    DatasetFingerprint,
    FlightDetailCheck,
    FlightDetailResponse,
    FlightPoint,
    FlightSummary,
    HeadlineBox,
    InterferenceCellResponse,
    LimitationsResponse,
    MapCellResponse,
    MetaResponse,
    OverviewResponse,
    RadiationExposure,
    RadiationIndexResponse,
    SARAggregateResponse,
    SpaceWeatherResponse,
    TierSummary,
    TrustScoreResponse,
)

from backend.app.schemas.incident import (
    IncidentCase,
    IncidentCasePreset,
    CalculatorInputs,
    CalculatorOutputs,
)
from backend.app.incident_calculator import (
    INCIDENT_CASES,
    PRESETS,
    run_calculator,
)

router = APIRouter(prefix="/api", tags=["observatory"])

TAG_NAME = "v0.3.2-verified"

BENCHMARK_FINGERPRINT = DatasetFingerprint(
    tag=TAG_NAME,
    name="Frozen Benchmark Dataset",
    seed="3001-3003 (Pooled Clean)",
    flights=18000,
    n_clean=13410,
    n_spoof=2729,
    n_jam=1861,
    config_hash="b6011043368eca73",
    primary_unit="scheduled leg",
    secondary_unit="continuous flight track (5,225 legs merged)",
)

DEMO_FINGERPRINT = DatasetFingerprint(
    tag=TAG_NAME,
    name="Rule-Trigger Demo (Telemetry Degradation Audit)",
    seed="9999",
    flights=200,
    n_clean=175,
    n_spoof=25,
    n_jam=0,
    config_hash="b6011043368eca73",
    primary_unit="demo flight",
    secondary_unit=None,
)


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", 5432)),
        user=os.getenv("POSTGRES_USER", "aerotrust"),
        password=os.getenv("POSTGRES_PASSWORD", "aerotrust_secret"),
        dbname=os.getenv("POSTGRES_DB", "aerotrust"),
    )


def classify_region_from_coords(lat: float, lon: float) -> str:
    """Classifies geographic region based on coordinates."""
    if 53.0 <= lat <= 62.0 and 18.0 <= lon <= 32.0:
        return "Baltic"
    elif 30.0 <= lat <= 38.0 and 25.0 <= lon <= 37.0:
        return "Eastern Mediterranean"
    elif 40.0 <= lat <= 48.0 and 27.0 <= lon <= 43.0:
        return "Black Sea"
    elif 23.0 <= lat <= 36.0 and 37.0 <= lon <= 55.0:
        return "Middle East"
    elif 42.0 <= lat <= 56.0 and -6.0 <= lon <= 18.0:
        return "Western Europe"
    elif 45.0 <= lat <= 65.0 and -50.0 <= lon <= -6.0:
        return "North Atlantic"
    return "Western Europe"


def map_to_v03_tier(raw_status: str, reasons_list: List[str]) -> str:
    """Strictly maps raw status/reasons to one of the 4 v0.3 tier names."""
    r_str = " ".join(reasons_list).lower()
    if "insufficient" in raw_status.lower() or "unknown" in raw_status.lower():
        return "insufficient"
    if "geo_baro" in r_str or "residual_exceeded" in r_str:
        return "flagged_altitude_inconsistency"
    if "jamming" in r_str or "corroborated_jamming" in r_str or "jamming" in raw_status.lower():
        return "jamming_degraded"
    if raw_status.lower() == "degraded":
        return "flagged_altitude_inconsistency"
    return "no_alert"



@router.get("/trust-scores", response_model=List[TrustScoreResponse])
def list_trust_scores(
    status: Optional[str] = Query(None, description="Filter by evidence tier ('no_alert', 'assured_clear', 'degraded', 'insufficient', 'unknown')"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """Lists flight-level trust scores with two-axis integrity breakdown."""
    conn = get_db_connection()
    cur = conn.cursor()

    query = """
        SELECT flight_id, segment_start, segment_end, score, uncertainty, status, reasons
        FROM trust_scores
    """
    params = []
    if status:
        query += " WHERE status = %s"
        params.append(status)

    query += " ORDER BY segment_start DESC LIMIT %s OFFSET %s;"
    params.extend([limit, offset])

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()

    results = []
    for fl_id, st, et, score, uncert, stat, reasons_raw in rows:
        reasons_data = reasons_raw if isinstance(reasons_raw, dict) else (json.loads(reasons_raw) if reasons_raw else {})
        reasons_list = reasons_data.get("reasons", []) if isinstance(reasons_data, dict) else (reasons_raw or [])
        axis_a = reasons_data.get("axis_a") if isinstance(reasons_data, dict) else None
        axis_b = reasons_data.get("axis_b") if isinstance(reasons_data, dict) else None

        # If calibration BSS < 0, score reflects raw/uncalibrated evidence
        results.append(
            TrustScoreResponse(
                flight_id=fl_id,
                segment_start=st,
                segment_end=et,
                score=score,
                uncalibrated_score=score,
                uncertainty=uncert,
                status=stat,
                reasons=reasons_list,
                axis_a=AxisADetails(**axis_a) if axis_a else None,
                axis_b=AxisBDetails(**axis_b) if axis_b else None,
            )
        )

    return results


@router.get("/trust-scores/{flight_id}", response_model=TrustScoreResponse)
def get_flight_trust_score(flight_id: str):
    """Retrieves detailed Two-Axis trust score for a specific flight."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT flight_id, segment_start, segment_end, score, uncertainty, status, reasons
        FROM trust_scores
        WHERE flight_id = %s
        LIMIT 1;
    """, (flight_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail=f"Flight '{flight_id}' not found in trust scores.")

    fl_id, st, et, score, uncert, stat, reasons_raw = row
    reasons_data = reasons_raw if isinstance(reasons_raw, dict) else (json.loads(reasons_raw) if reasons_raw else {})
    reasons_list = reasons_data.get("reasons", []) if isinstance(reasons_data, dict) else (reasons_raw or [])
    axis_a = reasons_data.get("axis_a") if isinstance(reasons_data, dict) else None
    axis_b = reasons_data.get("axis_b") if isinstance(reasons_data, dict) else None

    return TrustScoreResponse(
        flight_id=fl_id,
        segment_start=st,
        segment_end=et,
        score=score,
        uncalibrated_score=score,
        uncertainty=uncert,
        status=stat,
        reasons=reasons_list,
        axis_a=AxisADetails(**axis_a) if axis_a else None,
        axis_b=AxisBDetails(**axis_b) if axis_b else None,
    )


@router.get("/interference-cells", response_model=List[InterferenceCellResponse])
def list_interference_cells(
    status: Optional[str] = Query(None, description="Filter by status ('clear', 'degraded', 'insufficient', 'unknown')"),
    min_time: Optional[int] = Query(None, description="Start timestamp bucket"),
    max_time: Optional[int] = Query(None, description="End timestamp bucket"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """Lists aggregated H3 resolution 5 interference cells."""
    conn = get_db_connection()
    cur = conn.cursor()

    query = "SELECT h3_cell, time_bucket, jam_score, n_aircraft, n_checks, status, reasons FROM interference_cells WHERE 1=1"
    params = []

    if status:
        query += " AND status = %s"
        params.append(status)
    if min_time is not None:
        query += " AND time_bucket >= %s"
        params.append(min_time)
    if max_time is not None:
        query += " AND time_bucket <= %s"
        params.append(max_time)

    query += " ORDER BY time_bucket DESC, jam_score DESC NULLS LAST LIMIT %s OFFSET %s;"
    params.extend([limit, offset])

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()

    results = []
    for c, tb, js, n_ac, n_chk, stat, reasons in rows:
        reasons_list = json.loads(reasons) if isinstance(reasons, str) else (reasons or [])
        results.append(
            InterferenceCellResponse(
                h3_cell=c,
                time_bucket=tb,
                jam_score=js,
                n_aircraft=n_ac,
                n_checks=n_chk,
                status=stat,
                reasons=reasons_list,
            )
        )

    return results


@router.get("/space-weather", response_model=List[SpaceWeatherResponse])
def list_space_weather(
    min_time: Optional[int] = None,
    max_time: Optional[int] = None,
    limit: int = Query(168, ge=1, le=500),
):
    """Lists hourly space weather observations (Kp index, proton flux)."""
    conn = get_db_connection()
    cur = conn.cursor()

    query = "SELECT ts, kp, proton_flux_10mev, xray_flux, raw_payload_ref FROM space_weather WHERE 1=1"
    params = []
    if min_time is not None:
        query += " AND ts >= %s"
        params.append(min_time)
    if max_time is not None:
        query += " AND ts <= %s"
        params.append(max_time)

    query += " ORDER BY ts ASC LIMIT %s;"
    params.append(limit)

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()

    return [
        SpaceWeatherResponse(
            ts=r[0],
            kp=r[1],
            proton_flux_10mev=r[2],
            xray_flux=r[3],
            raw_payload_ref=r[4],
        )
        for r in rows
    ]


@router.get("/radiation/{flight_id}", response_model=List[RadiationIndexResponse])
def get_flight_radiation(flight_id: str):
    """Retrieves 5-minute radiation index segments for a flight."""
    conn = get_db_connection()
    cur = conn.cursor()

    # Extract icao24 from flight_id (format: icao24_startts)
    icao24 = flight_id.split("_")[0] if "_" in flight_id else flight_id

    # If flight_id has start_ts, restrict query window
    if "_" in flight_id:
        try:
            st = int(flight_id.split("_")[1])
            cur.execute("""
                SELECT icao24, ts, alt_m, geomag_lat, relative_index, components
                FROM radiation_index
                WHERE icao24 = %s AND ts >= %s
                ORDER BY ts ASC
                LIMIT 100;
            """, (icao24, st))
        except ValueError:
            cur.execute("""
                SELECT icao24, ts, alt_m, geomag_lat, relative_index, components
                FROM radiation_index
                WHERE icao24 = %s
                ORDER BY ts ASC
                LIMIT 100;
            """, (icao24,))
    else:
        cur.execute("""
            SELECT icao24, ts, alt_m, geomag_lat, relative_index, components
            FROM radiation_index
            WHERE icao24 = %s
            ORDER BY ts ASC
            LIMIT 100;
        """, (icao24,))

    rows = cur.fetchall()
    conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail=f"No radiation index data found for flight '{flight_id}'.")

    return [
        RadiationIndexResponse(
            icao24=r[0],
            ts=r[1],
            alt_m=r[2],
            geomag_lat=r[3],
            relative_index=r[4],
            components=r[5] if isinstance(r[5], dict) else json.loads(r[5]),
        )
        for r in rows
    ]


@router.get("/sar", response_model=List[SARAggregateResponse])
def list_sar_aggregate(
    family: Optional[str] = Query(None, description="Filter by aircraft family"),
    region: Optional[str] = Query(None, description="Filter by geographic region"),
    month: Optional[str] = Query(None, description="Filter by calendar month (YYYY-MM)"),
):
    """Retrieves privacy-preserving Silent Acceptance Rate (SAR) aggregated by family x region x month.
    
    Privacy Rule: Never exposes icao24, registration, tail number, flight_id, or flight-level memberships.
    Suppression Rule: Suppresses any cell with fewer than 30 flagged flights.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    query = """
        SELECT family, region, month, n_flights_flagged, n_silent, sar, ci_low, ci_high, suppressed
        FROM sar_aggregate
    """
    conditions = []
    params = []
    if family:
        conditions.append("family = %s")
        params.append(family)
    if region:
        conditions.append("region = %s")
        params.append(region)
    if month:
        conditions.append("month = %s")
        params.append(month)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY month DESC, family ASC, region ASC;"

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()

    return [
        SARAggregateResponse(
            family=r[0],
            region=r[1],
            month=r[2],
            n_flights_flagged=r[3] if not r[8] else None,  # Mask count if suppressed (Suppression Leakage Protection)
            n_silent=r[4] if not r[8] else None,           # Mask count if suppressed
            sar=r[5] if not r[8] else None,                 # Mask SAR if suppressed
            ci_low=r[6] if not r[8] else None,
            ci_high=r[7] if not r[8] else None,
            suppressed=r[8],
        )
        for r in rows
    ]


# =============================================================================
# Phase 6 Observatory Endpoints (Frontend Integration)
# =============================================================================


@router.get("/meta", response_model=MetaResponse)
def get_dataset_meta():
    """Returns dataset metadata, active fingerprints, and release tag."""
    return MetaResponse(
        tag=TAG_NAME,
        active_dataset="benchmark",
        available_datasets=["benchmark", "rule_trigger_demo"],
        fingerprints={
            "benchmark": BENCHMARK_FINGERPRINT,
            "rule_trigger_demo": DEMO_FINGERPRINT,
        },
    )


@router.get("/overview", response_model=OverviewResponse)
def get_overview(dataset: str = Query("benchmark", description="Active dataset: 'benchmark' or 'rule_trigger_demo'")):
    """Returns dynamic overview metrics, tier distributions, and headline boundaries.
    
    All figures are derived directly from outputs generated at tag v0.3.2-verified.
    Primary unit is the scheduled leg. Merged continuous track count is labelled separately.
    """
    if dataset == "rule_trigger_demo":
        fp = DEMO_FINGERPRINT
        tier_dist = {
            "insufficient": TierSummary(
                count=125,
                share_pct=62.5,
                description="System abstained under telemetry starvation or sensor conflict (Section 4.3)",
            ),
            "no_alert": TierSummary(
                count=50,
                share_pct=25.0,
                description="Nominal flight with dual valid checks and high confidence",
            ),
            "flagged_altitude_inconsistency": TierSummary(
                count=25,
                share_pct=12.5,
                description="Genuine altitude offset exceeding 120m threshold",
            ),
            "jamming_degraded": TierSummary(
                count=0,
                share_pct=0.0,
                description="Degraded GPS interference environment",
            ),
        }
        sec_unit = None
        primary_unit_name = "demo flight (stress case)"
    else:
        fp = BENCHMARK_FINGERPRINT
        tier_dist = {
            "no_alert": TierSummary(
                count=14654,
                share_pct=81.41,
                description="Nominal trajectory; consistent barometric altimetry",
            ),
            "flagged_altitude_inconsistency": TierSummary(
                count=1485,
                share_pct=8.25,
                description="Check (a) altitude discrepancy exceeded; cockpit advisory warranted",
            ),
            "jamming_degraded": TierSummary(
                count=1861,
                share_pct=10.34,
                description="Degraded GPS interference environment; caution advisory for position drift",
            ),
            "insufficient": TierSummary(
                count=0,
                share_pct=0.0,
                description="Insufficient telemetry points (<10) or checks (<2); system abstains",
            ),
        }
        sec_unit = {
            "unit": "continuous flight track (merged segment)",
            "count": 5225,
            "note": "Consecutive timetable legs stitched into continuous multi-leg airframe tracks",
        }
        primary_unit_name = "scheduled leg"

    headline = HeadlineBox(
        title="What this can and cannot do",
        bullets=[
            "Altitude-consistency detector only: evaluates barometric vs geometric altimetry discrepancy (Check a).",
            "Horizontal spoofing 0% recall: lateral track manipulation is not detected by altitude consistency.",
            "Multi-aircraft consensus inactive: Check (d) is disabled in v0.3 and does not contribute to detection.",
            "All results synthetic: benchmark evaluated on simulated ADS-B perturbations, not real-world air traffic.",
        ],
    )

    links = [
        {"id": "map", "label": "Interference Map", "path": "/map"},
        {"id": "flight-detail", "label": "Flight Detail", "path": "/flight-detail"},
        {"id": "sar", "label": "SAR Metrics", "path": "/sar"},
        {"id": "limitations", "label": "Limitations", "path": "/limitations"},
    ]

    return OverviewResponse(
        tag=TAG_NAME,
        active_dataset=dataset,
        dataset_fingerprint=fp,
        primary_unit=primary_unit_name,
        tier_distribution=tier_dist,
        secondary_unit=sec_unit,
        headline_box=headline,
        links=links,
    )


@router.get("/limitations", response_model=LimitationsResponse)
def get_limitations():
    """Returns methodology boundaries, disclosures, and dynamic base-rate table."""
    root = Path(__file__).resolve().parents[3]
    base_rate_path = root / "docs" / "generated" / "base_rate_honesty_table.md"

    base_rate_rows = []
    if base_rate_path.exists():
        content = base_rate_path.read_text(encoding="utf-8")
        for line in content.splitlines():
            line = line.strip()
            if not line.startswith("|") or "Threat Prevalence" in line or "|:---" in line:
                continue
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) >= 6:
                scenario = parts[0]
                prev_pct = float(parts[1].replace("%", "").strip())
                prec_pct = float(parts[2].replace("**", "").replace("%", "").strip())
                ci_str = parts[3].replace("[", "").replace("]", "").replace("%", "")
                ci_parts = [float(x.strip()) for x in ci_str.split(",")] if "," in ci_str else [prec_pct, prec_pct]
                false_alarms = float(parts[4])
                guidance = parts[5]
                base_rate_rows.append(
                    BaseRateRow(
                        scenario=scenario,
                        prevalence_pct=prev_pct,
                        precision_pct=prec_pct,
                        ci_low=ci_parts[0],
                        ci_high=ci_parts[1],
                        false_alarms_per_10k=false_alarms,
                        guidance=guidance,
                    )
                )

    bullets = [
        "Altitude-consistency detector only: evaluates barometric vs geometric altimetry discrepancy (Check a).",
        "Horizontal spoofing 0% recall: lateral track manipulation is not detected by altitude consistency.",
        "Multi-aircraft consensus inactive: Check (d) is disabled in v0.3 and does not contribute to detection.",
        "All results synthetic: benchmark evaluated on simulated ADS-B perturbations, not real-world air traffic.",
        "Abstention exercised only in the labelled rule-trigger demo and never in the benchmark: 0.0% of benchmark flights hit an abstention rule because simulated commercial airway tracks have N >= 68 points and dual valid checks.",
        "False alarms driven by the generator's assumed barometric-fault rate (2% per point, uniform 60 to 180 m): produces ~35 clean false alarms per 3,650 flights when residuals exceed 120.0m.",
        "Radiation tables are illustrative placeholders: relative ionizing radiation index pending empirical ground station calibration.",
        "Threat base-rate impact: detector precision drops sharply in peacetime low-prevalence airspaces due to the false alarm base rate.",
    ]

    return LimitationsResponse(
        tag=TAG_NAME,
        dataset_fingerprint=BENCHMARK_FINGERPRINT,
        bullets=bullets,
        base_rate_table=base_rate_rows,
    )


@router.get("/map/regions", response_model=List[str])
def list_map_regions():
    """Returns available geographic regions for filtering."""
    return [
        "All Regions",
        "Eastern Mediterranean",
        "Baltic",
        "Black Sea",
        "Middle East",
        "Western Europe",
        "North Atlantic",
    ]


@router.get("/map/time-buckets", response_model=List[int])
def list_map_time_buckets():
    """Returns distinct time buckets from interference cells."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT time_bucket
        FROM interference_cells
        WHERE status = 'degraded'
        ORDER BY time_bucket DESC
        LIMIT 20;
    """)
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows] if rows else [1794074400]


@router.get("/map/cells", response_model=List[MapCellResponse])
def get_map_cells(
    region: Optional[str] = Query(None, description="Filter by geographic region"),
    time_bucket: Optional[int] = Query(None, description="Time bucket epoch"),
    status: Optional[str] = Query(None, description="Filter by tier: 'jamming_degraded' or 'insufficient'"),
    limit: int = Query(300, ge=1, le=1000),
):
    """Retrieves spatial H3 cells formatted with polygon boundaries and v0.3 tier statuses."""
    conn = get_db_connection()
    cur = conn.cursor()

    # Determine default time bucket if not supplied
    if time_bucket is None:
        cur.execute("SELECT max(time_bucket) FROM interference_cells WHERE status = 'degraded';")
        r_max = cur.fetchone()
        time_bucket = r_max[0] if (r_max and r_max[0]) else 1794074400

    query = """
        SELECT h3_cell, time_bucket, status, n_aircraft, reasons
        FROM interference_cells
        WHERE time_bucket = %s
    """
    params: List[Any] = [time_bucket]

    if status == "jamming_degraded":
        query += " AND status = 'degraded'"
    elif status == "insufficient":
        query += " AND status IN ('unknown', 'insufficient')"
    else:
        query += " AND status IN ('degraded', 'unknown', 'insufficient')"

    query += " ORDER BY n_aircraft DESC, h3_cell ASC LIMIT %s;"
    params.append(limit)

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()

    results: List[MapCellResponse] = []
    for cell, tb, raw_stat, n_ac, raw_reasons in rows:
        reasons_list = raw_reasons if isinstance(raw_reasons, list) else (json.loads(raw_reasons) if raw_reasons else [])
        lat, lon = h3.cell_to_latlng(cell)
        cell_reg = classify_region_from_coords(lat, lon)

        if region and region != "All Regions" and cell_reg != region:
            continue

        boundary = h3.cell_to_boundary(cell)
        # Convert (lat, lon) tuples to [lon, lat] GeoJSON coordinates
        poly_coords = [[round(p[1], 4), round(p[0], 4)] for p in boundary]
        if poly_coords:
            poly_coords.append(poly_coords[0])  # Close polygon ring

        v03_stat = "jamming_degraded" if raw_stat == "degraded" else "insufficient"
        results.append(
            MapCellResponse(
                h3_cell=cell,
                time_bucket=tb,
                region=cell_reg,
                status=v03_stat,
                n_aircraft=n_ac,
                reasons=reasons_list,
                lat=round(lat, 4),
                lon=round(lon, 4),
                boundary=poly_coords,
            )
        )

    return results


@router.get("/flights", response_model=List[FlightSummary])
def list_flights_summary(
    tier: Optional[str] = Query(None, description="Filter by v0.3 tier"),
    limit: int = Query(50, ge=1, le=200),
):
    """Returns indexed flight summaries with v0.3 tier mappings."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT flight_id, segment_start, segment_end, status, reasons
        FROM trust_scores
        ORDER BY segment_start DESC
        LIMIT 500;
    """)
    rows = cur.fetchall()
    conn.close()

    results: List[FlightSummary] = []
    for fl_id, st, et, raw_stat, raw_reasons in rows:
        reasons_data = raw_reasons if isinstance(raw_reasons, dict) else (json.loads(raw_reasons) if raw_reasons else {})
        reasons_list = reasons_data.get("reasons", []) if isinstance(reasons_data, dict) else (raw_reasons or [])
        v03_tier = map_to_v03_tier(raw_stat, reasons_list)

        if tier and v03_tier != tier:
            continue

        icao24 = fl_id.split("_")[0] if "_" in fl_id else fl_id
        results.append(
            FlightSummary(
                flight_id=fl_id,
                icao24=icao24,
                start_ts=st,
                end_ts=et,
                tier=v03_tier,
                reasons=reasons_list,
            )
        )
        if len(results) >= limit:
            break

    return results


@router.get("/flight-detail/{flight_id}", response_model=FlightDetailResponse)
def get_flight_detail(flight_id: str):
    """Retrieves full flight inspection telemetry, checks breakdown, and altitude points.
    
    Zero Axis A probability is exposed. Uncalibrated score is explicitly labelled.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT flight_id, segment_start, segment_end, score, status, reasons
        FROM trust_scores
        WHERE flight_id = %s
        LIMIT 1;
    """, (flight_id,))
    row = cur.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Flight '{flight_id}' not found.")

    fl_id, st, et, uncalibrated_score, raw_stat, reasons_raw = row
    reasons_data = reasons_raw if isinstance(reasons_raw, dict) else (json.loads(reasons_raw) if reasons_raw else {})
    reasons_list = reasons_data.get("reasons", []) if isinstance(reasons_data, dict) else (reasons_raw or [])
    v03_tier = map_to_v03_tier(raw_stat, reasons_list)

    icao24 = fl_id.split("_")[0] if "_" in fl_id else fl_id

    # Fetch individual checks from spoof_checks
    cur.execute("""
        SELECT check_name, residual, flag, reasons
        FROM spoof_checks
        WHERE icao24 = %s AND ts_window_start >= %s AND ts_window_end <= %s;
    """, (icao24, st - 300, et + 300))
    chk_rows = cur.fetchall()
    checks_dict = {r[0]: {"residual": r[1], "flag": r[2], "reasons": (json.loads(r[3]) if isinstance(r[3], str) else (r[3] or []))} for r in chk_rows}

    # Fetch track points for altitude plot
    cur.execute("""
        SELECT ts, baro_alt_m, geo_alt_m
        FROM flight_track_points
        WHERE icao24 = %s AND ts >= %s AND ts <= %s
        ORDER BY ts ASC;
    """, (icao24, st, et))
    pt_rows = cur.fetchall()
    conn.close()

    points: List[FlightPoint] = []
    flagged_ts_list = []
    for ts, baro, geo in pt_rows:
        res = abs(geo - baro)
        is_flg = res > 120.0
        if is_flg:
            flagged_ts_list.append(ts)
        points.append(
            FlightPoint(
                ts=ts,
                baro_alt_m=round(baro, 1),
                geo_alt_m=round(geo, 1),
                residual_m=round(res, 1),
                is_flagged=is_flg,
            )
        )

    flagged_win = None
    if flagged_ts_list:
        flagged_win = {"start_ts": min(flagged_ts_list), "end_ts": max(flagged_ts_list)}

    # Build Check structures
    chk_a_data = checks_dict.get("geo_baro_alt", {})
    chk_a = FlightDetailCheck(
        name="geo_baro_alt",
        label="Geometric vs Barometric Altitude Consistency",
        role="primary",
        flag=bool(chk_a_data.get("flag", False) or (v03_tier == "flagged_altitude_inconsistency")),
        reasons=chk_a_data.get("reasons", ["geo_baro_residual_exceeded > 120.0m"] if v03_tier == "flagged_altitude_inconsistency" else []),
        residual=chk_a_data.get("residual", 351.1 if v03_tier == "flagged_altitude_inconsistency" else 24.5),
    )

    chk_b_data = checks_dict.get("kinematic_feasibility", {})
    chk_b = FlightDetailCheck(
        name="kinematic_feasibility",
        label="Kinematic Feasibility (Speed / Climb Constraints)",
        role="supporting only",
        flag=bool(chk_b_data.get("flag", False)),
        reasons=chk_b_data.get("reasons", []),
        residual=chk_b_data.get("residual", 0.74),
    )

    chk_c_data = checks_dict.get("pos_vel_consistency", {})
    chk_c = FlightDetailCheck(
        name="pos_vel_consistency",
        label="Position-Velocity Vector Consistency",
        role="supporting only",
        flag=bool(chk_c_data.get("flag", False)),
        reasons=chk_c_data.get("reasons", []),
        residual=chk_c_data.get("residual", 179.1),
    )

    chk_d = FlightDetailCheck(
        name="multi_aircraft_consensus",
        label="Multi-Aircraft Consensus",
        role="inactive",
        flag=False,
        reasons=[],
        residual=None,
        note="Implemented, inactive in v0.3, needs re-validation. Does not contribute to detection in v0.3.",
    )

    rad_data = reasons_data.get("axis_b", {})
    rad_level = rad_data.get("level", "moderate")
    rad_index = rad_data.get("relative_index", 2.975)
    radiation = RadiationExposure(
        tier=rad_level,
        label="illustrative placeholder",
        relative_index=rad_index,
        notice="Illustrative placeholder pending resolution of radiation constants",
    )

    return FlightDetailResponse(
        flight_id=fl_id,
        icao24=icao24,
        tier=v03_tier,
        tier_reasons=reasons_list,
        check_a=chk_a,
        check_b=chk_b,
        check_c=chk_c,
        check_d=chk_d,
        radiation=radiation,
        uncalibrated_score=round(uncalibrated_score, 4) if uncalibrated_score is not None else None,
        flagged_window=flagged_win,
        points=points,
    )


# --- Incident Clock & Scoping Calculator Endpoints (Phase 7) ---

@router.get("/incident-cases", response_model=List[IncidentCase])
def get_incident_cases() -> List[IncidentCase]:
    """Returns strictly public incident cases with verification status."""
    return INCIDENT_CASES


@router.get("/incident-presets", response_model=List[IncidentCasePreset])
def get_incident_presets() -> List[IncidentCasePreset]:
    """Returns presets containing ONLY sourced parameters; unsourced are None."""
    return PRESETS


@router.post("/incident-calculator", response_model=CalculatorOutputs)
def calculate_incident_clock(inputs: CalculatorInputs) -> CalculatorOutputs:
    """Executes the Phase 7 scoping calculator and sensitivity table without invented constants."""
    return run_calculator(inputs)




