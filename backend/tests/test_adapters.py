"""Tests for Data Adapters (FakeAdapter, OpenSkyStub, NOAAStub)."""

import pytest
from backend.app.adapters.fake_adapter import FakeAdapter
from backend.app.adapters.noaa_stub import NOAAAdapterStub
from backend.app.adapters.opensky_stub import OpenSkyAdapterStub


def test_fake_adapter_tracks_and_weather():
    adapter = FakeAdapter(config_path="config/synthetic.yaml", seed_mode="dev")
    assert adapter.is_synthetic() is True

    fleet = adapter.fetch_aircraft_registry()
    assert len(fleet) > 0
    assert "icao24" in fleet[0]

    tracks = adapter.fetch_flight_tracks(
        start_ts=1793491200, end_ts=1793491200 + 86400, limit=50
    )
    assert len(tracks) > 0
    assert len(tracks) <= 50
    assert "lat" in tracks[0]
    assert "baro_alt_m" in tracks[0]

    weather = adapter.fetch_space_weather(
        start_ts=1793491200, end_ts=1793491200 + 86400
    )
    assert len(weather) > 0
    assert "kp" in weather[0]


def test_opensky_adapter_stub_raises():
    stub = OpenSkyAdapterStub()
    assert stub.is_synthetic() is False

    with pytest.raises(NotImplementedError):
        stub.fetch_flight_tracks(1793491200, 1793491200 + 3600)


def test_noaa_adapter_stub_raises():
    stub = NOAAAdapterStub()
    assert stub.is_synthetic() is False

    with pytest.raises(NotImplementedError):
        stub.fetch_space_weather(1793491200, 1793491200 + 3600)

