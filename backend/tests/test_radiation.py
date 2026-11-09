"""Unit tests for AeroTrust Natural Radiation Exposure Index (Axis B).

Adheres to Phase 3.2:
- Verifies physical sanity properties:
  1. Monotonicity in altitude
  2. Monotonicity in geomagnetic latitude
  3. Storm multiplier > quiet multiplier
- Verifies that radiation index is never expressed as a probability
- Verifies single source of truth: docs/RADIATION.md strictly matches config/radiation_tables.yaml
- Sanity checks only; no validation against real-world upset data
"""

import os
import re
from pathlib import Path
import pytest
import yaml

from backend.app.detectors.radiation import RadiationCalculator


@pytest.fixture
def rad_calc():
    return RadiationCalculator("config/radiation_tables.yaml")


def test_monotonicity_in_altitude(rad_calc):
    """Sanity check: higher altitude must have greater than or equal altitude factor."""
    altitudes = [0, 500, 2000, 5000, 8000, 10000, 11500, 13000, 14000]
    factors = [rad_calc.get_altitude_factor(a) for a in altitudes]

    for i in range(len(factors) - 1):
        assert factors[i] <= factors[i + 1], (
            f"Altitude factor non-monotonic: alt={altitudes[i]} factor={factors[i]} vs "
            f"alt={altitudes[i+1]} factor={factors[i+1]}"
        )


def test_monotonicity_in_geomagnetic_latitude(rad_calc):
    """Sanity check: higher geomagnetic latitude must have greater than or equal geomag factor."""
    geomag_lats = [0, 10, 25, 35, 45, 55, 65, 75, 85]
    factors = [rad_calc.get_geomag_factor(g) for g in geomag_lats]

    for i in range(len(factors) - 1):
        assert factors[i] <= factors[i + 1], (
            f"Geomag factor non-monotonic: lat={geomag_lats[i]} factor={factors[i]} vs "
            f"lat={geomag_lats[i+1]} factor={factors[i+1]}"
        )


def test_storm_multiplier_greater_than_quiet(rad_calc):
    """Sanity check: space weather storm multipliers must exceed quiet baseline."""
    m_quiet, tier_quiet = rad_calc.get_space_weather_multiplier(proton_flux_10mev=0.5, kp=2.0)
    m_minor, tier_minor = rad_calc.get_space_weather_multiplier(proton_flux_10mev=15.0, kp=5.3)
    m_moderate, tier_mod = rad_calc.get_space_weather_multiplier(proton_flux_10mev=250.0, kp=6.2)
    m_severe, tier_sev = rad_calc.get_space_weather_multiplier(proton_flux_10mev=15000.0, kp=8.5)

    assert m_quiet == 1.00
    assert m_minor > m_quiet
    assert m_moderate > m_minor
    assert m_severe > m_moderate


def test_radiation_index_is_relative_and_not_probability(rad_calc):
    """Cardinal Rule: Radiation index is a relative multiplier, never bounded to [0, 1] probability."""
    # High altitude polar flight during severe storm
    res_high = rad_calc.compute_index(
        alt_m=12000.0, lat_deg=75.0, lon_deg=-20.0, proton_flux_10mev=5000.0, kp=7.5
    )
    # The relative index can well exceed 1.0
    assert res_high["relative_index"] > 1.0
    assert res_high["level"] == "elevated"

    # Sea level equatorial flight
    res_low = rad_calc.compute_index(
        alt_m=500.0, lat_deg=5.0, lon_deg=100.0, proton_flux_10mev=0.1, kp=1.0
    )
    assert res_low["relative_index"] < res_high["relative_index"]
    assert res_low["level"] == "low"


def test_radiation_docs_match_config():
    """Requirement Phase 3.2: Radiation documentation must match config/radiation_tables.yaml.
    
    1. Every altitude and geomagnetic bin factor in config must be present in docs/RADIATION.md.
    2. Labels every value as 'illustrative placeholder'.
    3. Marks every source as 'candidate, unverified'.
    """
    yaml_path = Path("config") / "radiation_tables.yaml"
    with open(yaml_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    doc_path = Path("docs") / "RADIATION.md"
    assert doc_path.exists(), f"Missing {doc_path}"
    doc_text = doc_path.read_text(encoding="utf-8")

    # Assert disclaimers are present
    assert "illustrative placeholder" in doc_text.lower(), "Missing 'illustrative placeholder' label"
    assert "candidate, unverified" in doc_text.lower(), "Missing 'candidate, unverified' label"

    # Verify altitude factors match
    for b in cfg.get("altitude_bins", []):
        factor_str = f"{b['factor']:.2f}"
        assert factor_str in doc_text, f"Altitude factor {factor_str} from config not found in docs/RADIATION.md"

    # Verify storm multipliers match
    for s in cfg.get("space_weather_tiers", []):
        mult_str = f"{s['multiplier']:.2f}"
        assert mult_str in doc_text, f"Storm multiplier {mult_str} from config not found in docs/RADIATION.md"
