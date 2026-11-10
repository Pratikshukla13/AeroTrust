from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class DatedEvent(BaseModel):
    date: str  # e.g., "2025-10-30", "2025-11-28", "2025-12-02"
    label: str  # e.g., "Airbus Alert & EASA Emergency AD Issued"
    description: str  # Detailed factual context
    source_url: Optional[str] = None
    source_type: Optional[str] = None  # "regulator", "manufacturer", "wire", "media"


class SourceItem(BaseModel):
    url: str
    title: str
    source_type: str  # "regulator", "manufacturer", "wire", "media"
    fact_referenced: str


class FleetBreakdown(BaseModel):
    name: str  # e.g., "EASA Proposed AD (17 Dec 2025)" or "Reuters Market Reporting (Dec 2025)"
    source_url: str
    source_type: str  # "regulator", "wire"
    in_service: Optional[int] = None
    undelivered_or_production: Optional[int] = None
    customer_allocated_or_other: Optional[int] = None
    total: int
    notes: Optional[str] = None


class IncidentCase(BaseModel):
    case_id: str
    title: str
    event_date: Optional[str] = None
    public_statement_date: Optional[str] = None
    directive_date: Optional[str] = None
    directive_status: Optional[Literal["issued", "effective", "proposed", "final"]] = None
    aircraft_affected_total: Optional[int] = None
    aircraft_in_service: Optional[int] = None
    aircraft_undelivered: Optional[int] = None
    deliveries_context: Optional[str] = None
    in_service_scope_notes: Optional[str] = None
    days_event_to_statement: Optional[int] = None
    source_url: str  # Primary URL
    source_type: str = "regulator"  # Primary source type
    sources: List[SourceItem] = Field(default_factory=list)  # Primary + secondary URLs per fact
    dated_events: List[DatedEvent] = Field(default_factory=list)  # Dated timeline milestones
    fleet_breakdowns: List[FleetBreakdown] = Field(default_factory=list)  # Alternate breakdowns
    verification_status: Literal["sourced", "needs verification", "unknown field"] = "needs verification"


class IncidentCasePreset(BaseModel):
    case_id: str
    title: str
    days_to_scope: Optional[float] = None
    aircraft_held_in_service: Optional[float] = None
    aircraft_held_undelivered: Optional[float] = None
    baseline_handover_rate_per_month: Optional[float] = None
    share_recovered_later: Optional[float] = None
    value_per_aircraft: Optional[float] = None
    sourced_fields: List[str] = Field(default_factory=list)


class CalculatorInputs(BaseModel):
    days_to_scope: Optional[float] = None
    aircraft_held_in_service: Optional[float] = None
    aircraft_held_undelivered: Optional[float] = None
    baseline_handover_rate_per_month: Optional[float] = None
    share_recovered_later: Optional[float] = None
    value_per_aircraft: Optional[float] = None


class SensitivityRow(BaseModel):
    multiplier_label: str  # "0.5x", "1.0x", "2.0x"
    multiplier: float
    days: Optional[float] = None
    aircraft_days_held: Optional[float] = None
    model_a_net_handovers_lost: Optional[float] = None
    model_b_aircraft_days: Optional[float] = None
    financial_impact: Optional[float] = None


class CalculatorOutputs(BaseModel):
    total_held_aircraft: Optional[float] = None
    aircraft_days_held: Optional[float] = None
    aircraft_days_held_formula: str
    aircraft_days_held_assumption: str

    model_a_gross_handovers_lost: Optional[float] = None
    model_a_net_handovers_lost: Optional[float] = None
    model_a_formula: str
    model_a_assumption: str

    model_b_aircraft_days: Optional[float] = None
    model_b_formula: str
    model_b_assumption: str

    one_day_cost_aircraft_days: Optional[float] = None
    one_day_cost_money: Optional[float] = None
    financial_impact_total: Optional[float] = None

    sensitivity_table: List[SensitivityRow] = Field(default_factory=list)
