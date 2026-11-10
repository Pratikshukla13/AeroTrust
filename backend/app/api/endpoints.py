"""AeroTrust Read-Only API Endpoints (Phase 3.5).

Provides high-performance, read-only queries into PostgreSQL:
- Trust scores (Two-Axis: Hostile RF & Natural Radiation)
- Interference cells (H3 spatial aggregation)
- Space weather telemetry
- Radiation index segments
"""

import json
import os
from typing import Any, Dict, List, Optional

import psycopg2
from fastapi import APIRouter, HTTPException, Query

from backend.app.schemas.api import (
    AxisADetails,
    AxisBDetails,
    InterferenceCellResponse,
    RadiationIndexResponse,
    SARAggregateResponse,
    SpaceWeatherResponse,
    TrustScoreResponse,
)

router = APIRouter(prefix="/api", tags=["observatory"])


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", 5432)),
        user=os.getenv("POSTGRES_USER", "aerotrust"),
        password=os.getenv("POSTGRES_PASSWORD", "aerotrust_secret"),
        dbname=os.getenv("POSTGRES_DB", "aerotrust"),
    )


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


