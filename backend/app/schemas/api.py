"""AeroTrust API Pydantic Schemas (Phase 3.5)."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AxisADetails(BaseModel):
    status: str = Field(description="'clear', 'degraded', or 'unknown'")
    calibrated_prob: Optional[float] = Field(None, description="Calibrated hostile RF probability")
    confidence: Optional[float] = Field(None, description="Metric confidence [0, 1]")
    primary_triggered: Optional[bool] = None
    primary_triggers: List[str] = Field(default_factory=list)
    supporting_reasons: List[str] = Field(default_factory=list)
    jamming_status: Optional[str] = None
    jamming_confidence: Optional[float] = None


class AxisBDetails(BaseModel):
    level: str = Field(description="'low', 'moderate', or 'elevated'")
    relative_index: Optional[float] = Field(None, description="Relative cosmic/solar radiation exposure index (never probability)")
    components: Dict[str, Any] = Field(default_factory=dict)


class TrustScoreResponse(BaseModel):
    flight_id: str
    segment_start: int
    segment_end: int
    score: Optional[float] = Field(None, description="Integrated data integrity score [0, 1]")
    uncalibrated_score: Optional[float] = Field(None, description="Raw uncalibrated composite evidence score [0, 1]")
    uncertainty: Optional[float] = Field(None, description="Assessment uncertainty [0, 1]")
    status: str = Field(description="Evidence tier: 'no_alert', 'assured_clear', 'degraded', 'insufficient', or 'unknown'")
    reasons: List[str] = Field(default_factory=list)
    axis_a: Optional[AxisADetails] = None
    axis_b: Optional[AxisBDetails] = None


class InterferenceCellResponse(BaseModel):
    h3_cell: str
    time_bucket: int
    jam_score: Optional[float] = None
    n_aircraft: int
    n_checks: int
    status: str = Field(description="'clear', 'degraded', 'insufficient', or 'unknown'")
    reasons: List[str] = Field(default_factory=list)


class SpaceWeatherResponse(BaseModel):
    ts: int
    kp: float
    proton_flux_10mev: float
    xray_flux: Optional[float] = None
    raw_payload_ref: Optional[str] = None


class RadiationIndexResponse(BaseModel):
    icao24: str
    ts: int
    alt_m: float
    geomag_lat: float
    relative_index: float = Field(description="Relative cosmic radiation index (never probability)")
    components: Dict[str, Any] = Field(default_factory=dict)

