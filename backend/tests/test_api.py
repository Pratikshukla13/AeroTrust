"""Unit tests for AeroTrust Read-Only API Endpoints (Phase 3.5).

Verifies:
1. Root / health endpoints
2. Trust scores listing and single flight lookup
3. Two-axis schema validation (Axis A hostile RF, Axis B natural radiation)
4. Interference cells spatial query
5. Space weather observation series
6. 5-minute radiation index query
7. Error handling (404 on missing flight)
"""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_api_root_and_health():
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["project"] == "AeroTrust"
    assert data["synthetic_banner_required"] is True

    res_h = client.get("/health")
    assert res_h.status_code == 200
    assert res_h.json()["status"] == "healthy"


def test_list_trust_scores():
    res = client.get("/api/trust-scores?limit=5")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) > 0
    first = data[0]
    assert "flight_id" in first
    assert "status" in first
    assert first["status"] in ["no_alert", "assured_clear", "degraded", "insufficient", "unknown"]
    assert "axis_a" in first
    assert "axis_b" in first


def test_get_single_flight_trust_score():
    # First get a valid flight_id from listing
    res_list = client.get("/api/trust-scores?limit=1")
    assert res_list.status_code == 200
    flight_id = res_list.json()[0]["flight_id"]

    res = client.get(f"/api/trust-scores/{flight_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["flight_id"] == flight_id
    assert "axis_a" in data
    assert "axis_b" in data
    if data["axis_a"]:
        assert data["axis_a"]["status"] in ["clear", "degraded", "unknown"]
    if data["axis_b"]:
        assert data["axis_b"]["level"] in ["low", "moderate", "elevated"]
        # Never express radiation index as probability
        assert data["axis_b"]["relative_index"] is not None


def test_get_nonexistent_flight_trust_score():
    res = client.get("/api/trust-scores/nonexistent_flight_999999")
    assert res.status_code == 404


def test_list_interference_cells():
    res = client.get("/api/interference-cells?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) > 0
    first = data[0]
    assert "h3_cell" in first
    assert "time_bucket" in first
    assert "status" in first


def test_list_space_weather():
    res = client.get("/api/space-weather?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) > 0
    first = data[0]
    assert "kp" in first
    assert "proton_flux_10mev" in first


def test_get_flight_radiation():
    res_list = client.get("/api/trust-scores?limit=1")
    assert res_list.status_code == 200
    flight_id = res_list.json()[0]["flight_id"]

    res = client.get(f"/api/radiation/{flight_id}")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) > 0
    first = data[0]
    assert "relative_index" in first
    assert "geomag_lat" in first
    assert "components" in first


def test_incident_cases_api():
    """Phase 7: verifies /api/incident-cases, /api/incident-presets, and /api/incident-calculator."""
    res = client.get("/api/incident-cases")
    assert res.status_code == 200
    cases = res.json()
    assert len(cases) == 3
    for c in cases:
        assert c["verification_status"] == "needs verification"
        assert "case_id" in c
        assert "source_url" in c

    res_p = client.get("/api/incident-presets")
    assert res_p.status_code == 200
    presets = res_p.json()
    assert len(presets) == 3

    # Test calculator API endpoint
    payload = {
        "days_to_scope": 30.0,
        "aircraft_held_in_service": 100.0,
        "aircraft_held_undelivered": 50.0,
        "baseline_handover_rate_per_month": 60.0,
        "share_recovered_later": 0.25,
        "value_per_aircraft": None,
    }
    res_c = client.post("/api/incident-calculator", json=payload)
    assert res_c.status_code == 200
    out = res_c.json()
    assert out["aircraft_days_held"] == 4500.0
    assert out["model_a_net_handovers_lost"] == 45.0
    assert out["financial_impact_total"] is None
    assert len(out["sensitivity_table"]) == 3


