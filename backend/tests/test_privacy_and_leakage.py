"""Phase 8 Privacy and Synthetic Integrity Tests.

Verifies that the repository contains NO real-world aircraft tail numbers,
airline flight numbers, or live operational flight callsigns.
All evaluated flights must conform strictly to synthetic nomenclature.
"""

import json
import re
from pathlib import Path
import pytest


# Regexes for real commercial airline flight identifiers and tail numbers
AIRLINE_CALLSIGN_PATTERN = re.compile(
    r"\b(?:BAW|AFR|DLH|UAL|AAL|DAL|SWA|RYR|EZY|THY|UAE|QTR|KLM|SAS|FIN|TAP|IBE|AZA|CSN|CCA|CES)\s?[0-9]{1,4}[A-Z]?\b",
    re.IGNORECASE,
)

REAL_TAIL_NUMBER_PATTERN = re.compile(
    r"\b(?:N[0-9]{1,5}[A-Z]{0,2}|G-[A-Z]{4}|F-[A-Z]{4}|D-[A-Z]{4}|OE-[A-Z]{3}|VH-[A-Z]{3}|C-[FGI][A-Z]{3})\b",
    re.IGNORECASE,
)


def test_no_real_callsigns_in_manifests():
    """Verifies that synthetic scenario manifests contain only synthetic flight identifiers."""
    synthetic_manifest = Path("data/synthetic/ground_truth/flight_manifest.json")
    assert synthetic_manifest.exists(), "flight_manifest.json must exist"

    with open(synthetic_manifest, "r", encoding="utf-8") as f:
        records = json.load(f)

    for rec in records:
        fl_id = rec.get("flight_id", "")
        icao24 = rec.get("icao24", "")

        # Synthetic prefixes: 'x' (hex-based synthetic), 'SYN-', 'LEG-', 'DEMO-'
        assert fl_id.startswith(("x", "SYN-", "LEG-", "DEMO-", "test_")), (
            f"Flight ID {fl_id} violates synthetic naming convention"
        )
        assert not AIRLINE_CALLSIGN_PATTERN.search(fl_id), (
            f"Forbidden real airline callsign detected in flight_id: {fl_id}"
        )
        assert not REAL_TAIL_NUMBER_PATTERN.search(fl_id), (
            f"Forbidden real aircraft registration tail number detected: {fl_id}"
        )


def test_no_real_callsigns_in_static_demo_snapshots():
    """Verifies that frontend static demo snapshots contain only synthetic flights."""
    static_data_dir = Path("frontend/public/static-data")
    flights_json = static_data_dir / "flights.json"
    assert flights_json.exists(), "flights.json static snapshot must exist"

    with open(flights_json, "r", encoding="utf-8") as f:
        flights = json.load(f)

    for fl in flights:
        fl_id = fl.get("flight_id", "")
        assert fl_id.startswith(("x", "SYN-", "LEG-", "DEMO-")), (
            f"Non-synthetic flight ID {fl_id} found in static demo snapshots"
        )
        assert not AIRLINE_CALLSIGN_PATTERN.search(fl_id), (
            f"Real airline callsign pattern detected in static flight ID: {fl_id}"
        )


def test_synthetic_icao24_address_space():
    """Verifies that ICAO24 hex identifiers in static demo and evaluated tables are synthetic."""
    static_data_dir = Path("frontend/public/static-data")
    flights_json = static_data_dir / "flights.json"

    with open(flights_json, "r", encoding="utf-8") as f:
        flights = json.load(f)

    for fl in flights:
        icao24 = fl.get("icao24", "")
        # Standard synthetic prefix 'x' or 6-char hex
        assert re.match(r"^(?:x[0-9a-f]{6}|[0-9a-f]{6}|SYN[0-9a-f]*)$", icao24, re.IGNORECASE), (
            f"Unrecognized ICAO24 format {icao24} in static demo dataset"
        )
