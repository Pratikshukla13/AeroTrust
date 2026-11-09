"""AeroTrust Synthetic Data Schemas.

All data structures in this module represent purely synthetic entities.
No real flight numbers, tail numbers, or real-world passenger identifiers.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class SyntheticAircraft:
    """Aircraft registry entry."""
    icao24: str  # Fake hex string, e.g. "x0a1b2c"
    registration: str  # Fake registration, e.g. "SYN-A320-001"
    type_code: str  # e.g. "A20N", "A339", "A359"
    family: str  # "A320-family", "A330", "A350", "other"
    operator: str  # Fake operator name, e.g. "Synthetic Aero 01"


@dataclass
class SyntheticTrackPoint:
    """Track point matching README Section 3 schema."""
    icao24: str
    ts: int  # Unix timestamp in seconds
    lat: float
    lon: float
    baro_alt_m: float
    geo_alt_m: float
    gs_mps: float
    track_deg: float
    vrate_mps: float
    on_ground: bool
    nic: int  # Navigation Integrity Category (0-11)
    nacp: int  # Navigation Accuracy Category for Position (0-11)
    sil: int  # Surveillance/Source Integrity Level (0-3)
    source_note: str = "SYNTHETIC_GENERATOR"


@dataclass
class GroundTruthEvent:
    """Ground truth event table.

    STRICT ARCHITECTURAL ISOLATION:
    Kept separate from flight tracks. Detectors and scoring algorithms must NEVER
    import or inspect ground-truth events directly.
    """
    event_id: str
    event_type: str  # "jamming", "spoofing"
    region: str
    start_ts: int
    end_ts: int
    intensity: float  # 0.0 to 1.0
    spoof_type: Optional[str] = None  # "offset", "drift", "convergence", None
    affected_icao24: Optional[str] = None  # Specific aircraft or None for wide-area
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SyntheticSpaceWeatherPoint:
    """Space weather observation point."""
    ts: int
    kp: float  # Kp planetary magnetic index (0.0 to 9.0)
    proton_flux_10mev: float  # pfu (>10 MeV)
    xray_flux: float  # W/m^2
    raw_payload_ref: str = "SYNTHETIC_SWPC_SERIES"


@dataclass
class SyntheticIncidentCase:
    """Incident Case strictly seeded from public numbers (README Section 4.6)."""
    case_id: str
    name: str
    trigger_date: str
    public_statement_date: str
    directive_date: str
    aircraft_held_in_service: int
    aircraft_held_undelivered: int
    days_to_scope: int
    source_urls: str

