"""Unit Tests for AeroTrust Detectors and Abstention Engine.

Tests:
1. Check (a): GeoBaroAltDetector (Geometric vs barometric altitude baseline residual)
2. Check (b): KinematicFeasibilityDetector (Speed, acceleration, turn-rate bounds)
3. Check (c): PosVelConsistencyDetector (Dead reckoning drift over rolling window)
4. Check (d): MultiAircraftConsensusDetector (15-min window, res 5 + k=1 ring)
5. Check (e): ModeSEHSPhysicsDetector (Documented stub returning status='unknown')
6. JammingDetector: NIC/NACp drop ratios and gap evaluation
7. AbstentionEngine: Section 4.3 rule compliance
"""

import math
import numpy as np
import pandas as pd
import pytest

from backend.app.detectors.abstention import AbstentionEngine
from backend.app.detectors.jamming import JammingDetector
from backend.app.detectors.spoofing import (
    GeoBaroAltDetector,
    KinematicFeasibilityDetector,
    ModeSEHSPhysicsDetector,
    MultiAircraftConsensusDetector,
    PosVelConsistencyDetector,
)


@pytest.fixture
def clean_flight_df():
    """Generates 20 clean nominal cruise points at 30-second intervals."""
    records = []
    base_ts = 1793491200
    lat_curr, lon_curr = 48.0, 5.0
    gs = 235.0
    track = 56.3
    dt = 30.0
    rad = math.radians(track)
    dlat = (gs * dt * math.cos(rad)) / 111139.0
    dlon = (gs * dt * math.sin(rad)) / (111139.0 * math.cos(math.radians(48.0)))

    for i in range(20):
        records.append({
            "icao24": "xclean01",
            "ts": base_ts + (i * 30),
            "lat": lat_curr + (i * dlat),
            "lon": lon_curr + (i * dlon),
            "baro_alt_m": 10500.0,
            "geo_alt_m": 10520.0,  # Constant 20m delta
            "gs_mps": gs,
            "track_deg": track,
            "vrate_mps": 0.0,
            "on_ground": False,
            "nic": 10,
            "nacp": 10,
            "sil": 3,
        })
    return pd.DataFrame(records)


@pytest.fixture
def spoofed_alt_df(clean_flight_df):
    """Flight with injected 300m geometric altitude offset."""
    df = clean_flight_df.copy()
    # Inject 300m offset during middle segment
    df.loc[10:18, "geo_alt_m"] += 300.0
    return df


@pytest.fixture
def spoofed_speed_df(clean_flight_df):
    """Flight with impossible hypersonic speed jump (500 m/s)."""
    df = clean_flight_df.copy()
    # Jump coordinate to create implied speed > 400 m/s
    df.loc[10, "lat"] += 0.20  # ~22 km jump in 30s = ~730 m/s
    return df


@pytest.fixture
def spoofed_drift_df(clean_flight_df):
    """Flight with progressive lateral position drift."""
    df = clean_flight_df.copy()
    for i in range(10, 20):
        df.loc[i, "lat"] += (i - 9) * 0.01  # Drifting by ~1.1 km per step
    return df


# -------------------------------------------------------------
# Test Check (a): Geo-Baro Altitude
# -------------------------------------------------------------
def test_geo_baro_clean_flight(clean_flight_df):
    detector = GeoBaroAltDetector()
    res = detector.evaluate(clean_flight_df)
    assert res["status"] == "clear"
    assert res["flag"] is False
    assert res["residual"] < 50.0  # Stable baseline delta


def test_geo_baro_spoofed_flight(spoofed_alt_df):
    detector = GeoBaroAltDetector()
    res = detector.evaluate(spoofed_alt_df)
    assert res["status"] == "flagged"
    assert res["flag"] is True
    assert res["residual"] >= 150.0
    assert res["confidence"] > 0.70
    assert len(res["reasons"]) > 0


def test_geo_baro_abstains_on_few_points():
    detector = GeoBaroAltDetector()
    tiny_df = pd.DataFrame([{"geo_alt_m": 10000.0, "baro_alt_m": 10000.0}])
    res = detector.evaluate(tiny_df)
    assert res["status"] == "unknown"
    assert res["flag"] is False
    assert "insufficient_points" in res["reasons"][0]


# -------------------------------------------------------------
# Test Check (b): Kinematic Feasibility
# -------------------------------------------------------------
def test_kinematic_clean_flight(clean_flight_df):
    detector = KinematicFeasibilityDetector()
    res = detector.evaluate(clean_flight_df)
    assert res["status"] == "clear"
    assert res["flag"] is False
    assert res["residual"] <= 1.0


def test_kinematic_spoofed_speed_jump(spoofed_speed_df):
    detector = KinematicFeasibilityDetector()
    res = detector.evaluate(spoofed_speed_df)
    assert res["status"] == "flagged"
    assert res["flag"] is True
    assert res["residual"] > 1.0
    assert any("implied_speed" in r for r in res["reasons"])


# -------------------------------------------------------------
# Test Check (c): Position-Velocity Consistency
# -------------------------------------------------------------
def test_pos_vel_consistency_clean(clean_flight_df):
    detector = PosVelConsistencyDetector()
    res = detector.evaluate(clean_flight_df)
    assert res["status"] == "clear"
    assert res["flag"] is False


def test_pos_vel_consistency_drift(spoofed_drift_df):
    detector = PosVelConsistencyDetector()
    res = detector.evaluate(spoofed_drift_df)
    assert res["status"] == "flagged"
    assert res["flag"] is True
    assert res["residual"] > 600.0
    assert any("pos_vel_drift" in r for r in res["reasons"])


# -------------------------------------------------------------
# Test Check (d): Multi-Aircraft Consensus
# -------------------------------------------------------------
def test_multi_aircraft_consensus_abstains_on_solo_flight():
    detector = MultiAircraftConsensusDetector()
    # Only 1 aircraft in neighborhood
    res = detector.evaluate(
        target_icao="xsolo01",
        h3_cell="851f1853fffffff",
        window_start_ts=1793491200,
        window_end_ts=1793492100,
        peer_anomalies_in_neighborhood={"xsolo01": False},
    )
    assert res["status"] == "unknown"
    assert res["flag"] is False
    assert any("insufficient_peer_density" in r for r in res["reasons"])


def test_multi_aircraft_consensus_detects_cluster():
    detector = MultiAircraftConsensusDetector()
    # 4 aircraft in cell neighborhood, 3 showing anomalies
    peers = {
        "xac01": True,
        "xac02": True,
        "xac03": True,
        "xac04": False,
    }
    res = detector.evaluate(
        target_icao="xac01",
        h3_cell="851f1853fffffff",
        window_start_ts=1793491200,
        window_end_ts=1793492100,
        peer_anomalies_in_neighborhood=peers,
    )
    assert res["status"] == "flagged"
    assert res["flag"] is True
    assert res["residual"] == 0.75
    assert res["raw_score"] == 0.75
    assert res["calibrated_prob"] > 0.50
    assert res["confidence"] > 0.50


# -------------------------------------------------------------
# Test Check (e): Mode S Physics Stub
# -------------------------------------------------------------
def test_mode_s_ehs_stub_returns_documented_unknown():
    stub = ModeSEHSPhysicsDetector()
    res = stub.evaluate(pd.DataFrame())
    assert res["status"] == "unknown"
    assert res["flag"] is False
    assert res["confidence"] == 0.0
    assert "ehs_registers_unavailable" in res["reasons"]


# -------------------------------------------------------------
# Test Jamming Detector
# -------------------------------------------------------------
def test_jamming_detector_clean(clean_flight_df):
    jam_det = JammingDetector()
    res = jam_det.evaluate_track_window(clean_flight_df)
    assert res["status"] == "clear"
    assert res["flag"] is False
    assert res["residual"] < 0.20


def test_jamming_detector_degraded():
    jam_det = JammingDetector()
    # Degraded NIC/NACp
    rows = []
    for i in range(15):
        rows.append({"nic": 3, "nacp": 4, "sil": 0, "ts": 1000 + i * 30})
    df = pd.DataFrame(rows)
    res = jam_det.evaluate_track_window(df)
    assert res["status"] == "degraded"
    assert res["flag"] is True
    assert res["residual"] > 0.40


def test_jamming_three_tier_clean_single_aircraft_insufficient():
    jam_det = JammingDetector()
    rows = [{"nic": 10, "nacp": 10, "sil": 3, "ts": 1000 + i * 30, "icao24": "ac01"} for i in range(15)]
    df = pd.DataFrame(rows)
    res = jam_det.aggregate_cell("851f1853fffffff", 100, df, mode="v3_three_tier")
    assert res["status"] == "insufficient"
    assert "single_aircraft_clean_evidence_insufficient" in res["reasons"][0]


def test_jamming_three_tier_clean_multi_aircraft_ok():
    jam_det = JammingDetector()
    rows = [{"nic": 10, "nacp": 10, "sil": 3, "ts": 1000 + i * 30, "icao24": "ac01"} for i in range(10)]
    rows += [{"nic": 10, "nacp": 10, "sil": 3, "ts": 1000 + i * 30, "icao24": "ac02"} for i in range(10)]
    df = pd.DataFrame(rows)
    res = jam_det.aggregate_cell("851f1853fffffff", 100, df, mode="v3_three_tier")
    assert res["status"] == "clear"
    assert res["confidence"] >= 0.80


# -------------------------------------------------------------
# Test Abstention Engine
# -------------------------------------------------------------
def test_abstention_engine_insufficient_points():
    engine = AbstentionEngine()
    checks = {
        "geo_baro_alt": {"flag": False, "confidence": 0.8, "status": "clear"},
        "kinematic_feasibility": {"flag": False, "confidence": 0.8, "status": "clear"},
    }
    status, reasons, conf = engine.evaluate_flight_checks(checks, total_points=4)
    assert status == "unknown"
    assert any("insufficient_track_points" in r for r in reasons)


def test_abstention_engine_insufficient_checks():
    engine = AbstentionEngine()
    checks = {
        "geo_baro_alt": {"flag": False, "confidence": 0.8, "status": "clear"},
        "kinematic_feasibility": {"flag": False, "confidence": 0.0, "status": "unknown"},
        "pos_vel_consistency": {"flag": False, "confidence": 0.0, "status": "unknown"},
    }
    status, reasons, conf = engine.evaluate_flight_checks(checks, total_points=25)
    assert status == "unknown"
    assert any("insufficient_independent_checks" in r for r in reasons)
