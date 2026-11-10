from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class IncidentCase(BaseModel):
    case_id: str
    title: str
    event_date: Optional[str] = None
    public_statement_date: Optional[str] = None
    directive_date: Optional[str] = None
    aircraft_affected_total: Optional[int] = None
    aircraft_in_service: Optional[int] = None
    aircraft_undelivered: Optional[int] = None
    deliveries_context: Optional[str] = None
    days_event_to_statement: Optional[int] = None
    source_url: str
    verification_status: Literal["sourced", "needs verification", "unknown field"]


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
