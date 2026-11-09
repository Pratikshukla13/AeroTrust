"""Tests for the AeroTrust Deterministic Synthetic World Generator."""

import os
from data.synthetic.generator import SyntheticWorldGenerator, generate_full_synthetic_world


def test_generator_determinism():
    """Verifies that identical seeds produce bit-identical synthetic worlds."""
    gen1 = SyntheticWorldGenerator(config_path="config/synthetic.yaml", seed_mode="dev")
    gen2 = SyntheticWorldGenerator(config_path="config/synthetic.yaml", seed_mode="dev")

    fleet1 = gen1.generate_aircraft_registry(10)
    fleet2 = gen2.generate_aircraft_registry(10)
    assert fleet1 == fleet2

    gen_test = SyntheticWorldGenerator(config_path="config/synthetic.yaml", seed_mode="test")
    fleet_test = gen_test.generate_aircraft_registry(10)
    assert fleet1 != fleet_test


def test_aircraft_registry_guardrails():
    """Verifies fake icao24 formatting and aircraft families."""
    gen = SyntheticWorldGenerator(config_path="config/synthetic.yaml", seed_mode="dev")
    fleet = gen.generate_aircraft_registry(30)

    families = {a.family for a in fleet}
    assert "A320-family" in families
    assert "A330" in families
    assert "A350" in families

    for ac in fleet:
        # Must be fake hex starting with 'x' (non-standard 24-bit ICAO)
        assert ac.icao24.startswith("x")
        assert len(ac.icao24) == 7
        assert "Synthetic" in ac.operator
        assert ac.registration.startswith("SYN-")


def test_space_weather_generation():
    """Verifies baseline space weather and injected storm episodes."""
    gen = SyntheticWorldGenerator(config_path="config/synthetic.yaml", seed_mode="dev")
    sw_points = gen.generate_space_weather(start_ts=1793491200, n_days=3, step_seconds=3600)

    assert len(sw_points) == 72
    max_kp = max(p.kp for p in sw_points)
    max_proton = max(p.proton_flux_10mev for p in sw_points)

    # Injected storms must elevate Kp and proton flux
    assert max_kp >= 5.0
    assert max_proton >= 10.0  # S1 storm threshold


def test_ground_truth_events_isolation():
    """Verifies ground truth events generation and separate structure."""
    gen = SyntheticWorldGenerator(config_path="config/synthetic.yaml", seed_mode="dev")
    events = gen.generate_ground_truth_events(1793491200, 1793491200 + 86400 * 2)

    assert len(events) >= 4
    event_types = {e.event_type for e in events}
    assert "jamming" in event_types
    assert "spoofing" in event_types


def test_flight_tracks_and_silent_acceptance():
    """Verifies track generation, noise, hard negatives, and silent acceptance instances."""
    gen = SyntheticWorldGenerator(config_path="config/synthetic.yaml", seed_mode="dev")
    fleet = gen.generate_aircraft_registry(15)
    gt_events = gen.generate_ground_truth_events(1793491200, 1793491200 + 86400)

    tracks = gen.generate_flight_tracks(
        aircraft_list=fleet,
        ground_truth_events=gt_events,
        n_flights=20,
        start_ts=1793491200,
        sampling_interval=30,
    )

    assert len(tracks) > 0
    for pt in tracks:
        assert pt.icao24.startswith("x")
        assert pt.source_note == "SYNTHETIC_GENERATOR"
        assert 0 <= pt.nic <= 11
        assert 0 <= pt.nacp <= 11
        assert 0 <= pt.sil <= 3
        assert pt.baro_alt_m >= 0.0
        assert pt.geo_alt_m >= 0.0

    # Check that both degraded and high integrity points exist (showing silent acceptance is occurring)
    high_integrity_count = sum(1 for pt in tracks if pt.nic >= 9)
    degraded_integrity_count = sum(1 for pt in tracks if pt.nic < 8)
    assert high_integrity_count > 0
    assert degraded_integrity_count > 0


def test_go_around_hard_negative_generation():
    """Verifies that go-around profiles are generated during final approaches."""
    gen = SyntheticWorldGenerator(config_path="config/synthetic.yaml", seed_mode="dev")
    # Boost go_around_probability to 1.0 to guarantee triggering on test flights
    gen.difficulty["go_around_probability"] = 1.0
    fleet = gen.generate_aircraft_registry(5)
    tracks = gen.generate_flight_tracks(
        aircraft_list=fleet,
        ground_truth_events=[],
        n_flights=5,
        start_ts=1793491200,
        sampling_interval=30,
    )
    # Check that in descent phase there are positive vrate climb spikes (+14 m/s) representing aborted landings
    climb_in_descent = [p for p in tracks if p.vrate_mps > 10.0 and p.baro_alt_m < 1500.0]
    assert len(climb_in_descent) > 0, "Go-around climb maneuver must be generated"


def test_incident_cases_seeded_from_readme():
    """Verifies that incident cases seed strictly the public numbers from README 4.6."""
    gen = SyntheticWorldGenerator(config_path="config/synthetic.yaml", seed_mode="dev")
    incidents = gen.generate_incident_cases()

    case_ids = {c.case_id for c in incidents}
    assert case_ids == {"A320-SOLAR-2025", "A320-PANEL-2025", "A330-TOOL-2026"}

    for c in incidents:
        assert c.source_urls.startswith("verify:")
        assert c.days_to_scope > 0


def test_pitch_down_precursor_test_flight():
    """Verifies the synthetic flight generated for pitch-down scanner testing."""
    gen = SyntheticWorldGenerator(config_path="config/synthetic.yaml", seed_mode="dev")
    aircraft, points = gen.generate_pitch_down_test_flight(1793491200)

    assert aircraft.family == "A320-family"
    assert "Real" not in aircraft.operator
    assert points[0].source_note == "SYNTHETIC_PRECURSOR_PITCH_DOWN_FLIGHT"

    # Profile check: sharp vertical rate dip should be present
    min_vrate = min(p.vrate_mps for p in points)
    assert min_vrate <= -20.0  # Significant dip


def test_full_synthetic_world_orchestration(tmp_path):
    """Verifies end-to-end synthetic world generation and ranking CSV export."""
    out_dir = str(tmp_path / "synthetic_out")
    result = generate_full_synthetic_world(
        config_path="config/synthetic.yaml",
        seed_mode="dev",
        output_dir=out_dir,
    )

    assert "aircraft" in result
    assert "tracks" in result
    assert "space_weather" in result
    assert "region_rankings_csv" in result
    assert os.path.exists(result["region_rankings_csv"])

