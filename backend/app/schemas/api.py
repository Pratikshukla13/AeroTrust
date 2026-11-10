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


class SARAggregateResponse(BaseModel):
    family: str = Field(description="Aircraft family (e.g. 'A320-family', 'A330', 'A350', 'other')")
    region: str = Field(description="Geographic region")
    month: str = Field(description="Calendar month (YYYY-MM)")
    n_flights_flagged: Optional[int] = Field(None, description="Total flagged legs evaluated (None if suppressed)")
    n_silent: Optional[int] = Field(None, description="Count of flagged legs accepting spoofing silently (None if suppressed)")
    sar: Optional[float] = Field(None, description="Silent Acceptance Rate [0, 1] (None if suppressed)")
    ci_low: Optional[float] = Field(None, description="Wilson 95% CI lower bound")
    ci_high: Optional[float] = Field(None, description="Wilson 95% CI upper bound")
    suppressed: bool = Field(description="True if cell has fewer than 30 flagged flights (privacy rule)")


class DatasetFingerprint(BaseModel):
    tag: str
    name: str
    seed: str
    flights: int
    n_clean: int
    n_spoof: int
    n_jam: int
    config_hash: str
    primary_unit: str
    secondary_unit: Optional[str] = None


class MetaResponse(BaseModel):
    tag: str
    active_dataset: str
    available_datasets: List[str]
    fingerprints: Dict[str, DatasetFingerprint]


class TierSummary(BaseModel):
    count: int
    share_pct: float
    description: str


class HeadlineBox(BaseModel):
    title: str
    bullets: List[str]


class OverviewResponse(BaseModel):
    tag: str
    active_dataset: str
    dataset_fingerprint: DatasetFingerprint
    primary_unit: str
    tier_distribution: Dict[str, TierSummary]
    secondary_unit: Optional[Dict[str, Any]] = None
    headline_box: HeadlineBox
    links: List[Dict[str, str]]


class MapCellResponse(BaseModel):
    h3_cell: str
    time_bucket: int
    region: str
    status: str
    n_aircraft: int
    reasons: List[str]
    lat: float
    lon: float
    boundary: List[List[float]]


class FlightSummary(BaseModel):
    flight_id: str
    icao24: str
    start_ts: int
    end_ts: int
    tier: str
    reasons: List[str]


class FlightPoint(BaseModel):
    ts: int
    baro_alt_m: float
    geo_alt_m: float
    residual_m: float
    is_flagged: bool


class FlightDetailCheck(BaseModel):
    name: str
    label: str
    role: str
    flag: bool
    reasons: List[str] = Field(default_factory=list)
    residual: Optional[float] = None
    note: Optional[str] = None


class RadiationExposure(BaseModel):
    tier: str
    label: str = "illustrative placeholder"
    relative_index: Optional[float] = None
    notice: str = "Illustrative placeholder pending resolution of radiation constants"


class FlightDetailResponse(BaseModel):
    flight_id: str
    icao24: str
    tier: str
    tier_reasons: List[str]
    check_a: FlightDetailCheck
    check_b: FlightDetailCheck
    check_c: FlightDetailCheck
    check_d: FlightDetailCheck
    radiation: RadiationExposure
    uncalibrated_score: Optional[float] = None
    flagged_window: Optional[Dict[str, int]] = None
    points: List[FlightPoint] = Field(default_factory=list)


class BaseRateRow(BaseModel):
    scenario: str
    prevalence_pct: float
    precision_pct: float
    ci_low: float
    ci_high: float
    false_alarms_per_10k: float
    guidance: str


class LimitationsResponse(BaseModel):
    tag: str
    dataset_fingerprint: DatasetFingerprint
    bullets: List[str]
    base_rate_table: List[BaseRateRow]



