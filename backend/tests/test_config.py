"""Configuration and Threshold Tests."""

import os
from pathlib import Path
import yaml
from backend.app.core.config import load_synthetic_config, load_thresholds


def test_thresholds_yaml_structure():
    """Ensures config/thresholds.yaml exists and defines all required sections."""
    cfg = load_thresholds("config/thresholds.yaml")
    assert "version" in cfg
    assert "spoofing" in cfg
    assert "jamming" in cfg
    assert "abstention" in cfg
    assert "sar" in cfg
    assert "radiation" in cfg

    # Verify Rule 2 & Section 4 specifics
    assert "geo_baro_alt" in cfg["spoofing"]
    assert "kinematic" in cfg["spoofing"]
    assert "pos_vel_consistency" in cfg["spoofing"]
    assert "multi_aircraft" in cfg["spoofing"]
    assert cfg["sar"]["suppression_min_flagged_flights"] == 30
    assert cfg["abstention"]["min_independent_checks_available"] >= 2


def test_synthetic_yaml_structure():
    """Ensures config/synthetic.yaml defines determinism seeds, difficulty knobs, and fleet."""
    cfg = load_synthetic_config("config/synthetic.yaml")
    assert "seeds" in cfg
    assert "dev" in cfg["seeds"]
    assert "test" in cfg["seeds"]
    assert "difficulty_knobs" in cfg
    assert "noise_level_sigma_meters" in cfg["difficulty_knobs"]
    assert "silent_acceptance_probability" in cfg
    assert "A320-family" in cfg["silent_acceptance_probability"]
    assert "incident_seed_cases" in cfg
    assert len(cfg["incident_seed_cases"]) == 3

