from datetime import date
from typing import List, Optional
from backend.app.schemas.incident import (
    IncidentCase,
    IncidentCasePreset,
    CalculatorInputs,
    CalculatorOutputs,
    SensitivityRow,
)


def compute_days_event_to_statement(
    event_date_str: Optional[str], statement_date_str: Optional[str]
) -> Optional[int]:
    """Computes elapsed days between event_date and public_statement_date only if both exist."""
    if not event_date_str or not statement_date_str:
        return None
    try:
        d1 = date.fromisoformat(event_date_str)
        d2 = date.fromisoformat(statement_date_str)
        return (d2 - d1).days
    except (ValueError, TypeError):
        return None


# Seed ONLY public facts. Anything not listed is None / unknown.
# Every case is marked "needs verification" per Phase 7 rules.
INCIDENT_CASES: List[IncidentCase] = [
    IncidentCase(
        case_id="A320-SOLAR-2025",
        title="A320 Solar Radiation Single-Event Effect",
        event_date="2025-10-30",
        public_statement_date="2025-11-28",
        directive_date="2025-11-29",
        aircraft_affected_total=6000,
        aircraft_in_service=None,  # unknown / not specified in facts
        aircraft_undelivered=None,  # unknown / not specified in facts
        deliveries_context="Fewer than 100 remaining on 1 Dec 2025.",
        days_event_to_statement=compute_days_event_to_statement("2025-10-30", "2025-11-28"),
        source_url="https://ad.easa.europa.eu/ad/2025-XXXX-E",
        verification_status="needs verification",
    ),
    IncidentCase(
        case_id="A320-PANEL-2025",
        title="A320 Fuselage Panels Production Discrepancy",
        event_date=None,  # event date unknown
        public_statement_date=None,  # unknown
        directive_date="2025-12-17",
        aircraft_affected_total=628,
        aircraft_in_service=177,
        aircraft_undelivered=451,
        deliveries_context=None,
        days_event_to_statement=None,
        source_url="https://ad.easa.europa.eu/ad/US-2025-XXXX",
        verification_status="needs verification",
    ),
    IncidentCase(
        case_id="A330-TOOL-2026",
        title="A330 Stray Assembly Tool Inspection",
        event_date=None,  # event date unknown
        public_statement_date=None,  # unknown
        directive_date=None,  # policy due mid-Nov 2026, no directive date yet
        aircraft_affected_total=None,  # number inspected not disclosed
        aircraft_in_service=None,  # not disclosed
        aircraft_undelivered=None,  # not disclosed
        deliveries_context="Zero deliveries in June and July 2026; nine in March to May 2026. Number of aircraft inspected not disclosed. Policy to the regulator due mid-November 2026.",
        days_event_to_statement=None,
        source_url="https://www.airbus.com/en/investors/commercial-aircraft-deliveries-2026",
        verification_status="needs verification",
    ),
]


# Presets fill ONLY the fields that are sourced; everything else stays None/empty
PRESETS: List[IncidentCasePreset] = [
    IncidentCasePreset(
        case_id="A320-SOLAR-2025",
        title="A320 Solar Radiation (29 Days Scoping)",
        days_to_scope=29.0,  # 30 Oct to 28 Nov 2025 = 29 days
        aircraft_held_in_service=None,  # unsourced
        aircraft_held_undelivered=None,  # unsourced
        baseline_handover_rate_per_month=None,
        share_recovered_later=None,
        value_per_aircraft=None,
        sourced_fields=["days_to_scope"],
    ),
    IncidentCasePreset(
        case_id="A320-PANEL-2025",
        title="A320 Fuselage Panels (177 In-Service, 451 Undelivered)",
        days_to_scope=None,  # unsourced (event date unknown)
        aircraft_held_in_service=177.0,  # sourced
        aircraft_held_undelivered=451.0,  # sourced
        baseline_handover_rate_per_month=None,
        share_recovered_later=None,
        value_per_aircraft=None,
        sourced_fields=["aircraft_held_in_service", "aircraft_held_undelivered"],
    ),
    IncidentCasePreset(
        case_id="A330-TOOL-2026",
        title="A330 Stray Assembly Tool (Deliveries Context Only)",
        days_to_scope=None,  # unsourced
        aircraft_held_in_service=None,  # unsourced
        aircraft_held_undelivered=None,  # unsourced
        baseline_handover_rate_per_month=None,
        share_recovered_later=None,
        value_per_aircraft=None,
        sourced_fields=[],  # All calculator numeric inputs unsourced
    ),
]


def run_calculator(inputs: CalculatorInputs) -> CalculatorOutputs:
    """Executes the Incident Clock scoping calculator without invented constants."""
    days = inputs.days_to_scope
    in_service = inputs.aircraft_held_in_service
    undelivered = inputs.aircraft_held_undelivered
    rate = inputs.baseline_handover_rate_per_month
    share_rec = inputs.share_recovered_later
    val = inputs.value_per_aircraft

    # Compute Total Held Aircraft
    has_held = (in_service is not None) or (undelivered is not None)
    total_held = ((in_service or 0.0) + (undelivered or 0.0)) if has_held else None

    # a. aircraft_days_held = held aircraft x days
    aircraft_days_held: Optional[float] = None
    if total_held is not None and days is not None:
        aircraft_days_held = float(total_held * days)

    formula_a = "aircraft_days_held = (aircraft_held_in_service + aircraft_held_undelivered) × days_to_scope"
    assumption_a = (
        "Assumes all scoped aircraft remain unavailable or paused for the entire scoping duration."
    )

    # b. Model A (line stop): handovers_lost = baseline_rate x days / 30, net of recovered share
    model_a_gross: Optional[float] = None
    model_a_net: Optional[float] = None
    if rate is not None and days is not None:
        model_a_gross = float(rate * (days / 30.0))
        rec_factor = (1.0 - share_rec) if share_rec is not None else 1.0
        model_a_net = float(model_a_gross * rec_factor)

    formula_b = (
        "gross_handovers_lost = baseline_handover_rate_per_month × (days_to_scope / 30); "
        "net_handovers_lost = gross × (1 - share_recovered_later)"
    )
    assumption_b = (
        "Assumes monthly production capacity is evenly distributed over 30 days per month. "
        "Recovery share accounts for post-incident overtime/surge catch-up."
    )

    # c. Model B (hold of finished aircraft): handover delay in aircraft-days only
    # Handover delay specifically measures undelivered finished aircraft delayed from delivery
    model_b_aircraft_days: Optional[float] = None
    if undelivered is not None and days is not None:
        model_b_aircraft_days = float(undelivered * days)
    elif total_held is not None and days is not None and undelivered is None:
        # If undelivered is not broken out, provide total held delay
        model_b_aircraft_days = float(total_held * days)

    formula_c = "handover_delay_aircraft_days = aircraft_held_undelivered × days_to_scope"
    assumption_c = (
        "Measures cumulative delivery delay for finished airframes awaiting inspection or regulatory clearance."
    )

    # One-day cost of delay (aircraft-days per day)
    one_day_aircraft_days: Optional[float] = None
    if total_held is not None:
        one_day_aircraft_days = float(total_held)  # 1 day * total_held aircraft = total_held aircraft-days/day

    # Financial calculations: STRICTLY None if value_per_aircraft is blank
    financial_impact: Optional[float] = None
    one_day_money: Optional[float] = None

    if val is not None and val > 0:
        if model_a_net is not None:
            financial_impact = float(model_a_net * val)
        if rate is not None:
            # Daily net line loss * value
            rec_factor = (1.0 - share_rec) if share_rec is not None else 1.0
            daily_net_lost = (rate / 30.0) * rec_factor
            one_day_money = float(daily_net_lost * val)

    # Sensitivity Table over days (0.5x, 1x, 2x)
    sensitivity_rows: List[SensitivityRow] = []
    multipliers = [("0.5x", 0.5), ("1.0x", 1.0), ("2.0x", 2.0)]
    for label, mult in multipliers:
        sens_days = (days * mult) if days is not None else None
        sens_held_days = (total_held * sens_days) if (total_held is not None and sens_days is not None) else None

        sens_model_a_net: Optional[float] = None
        if rate is not None and sens_days is not None:
            gross = rate * (sens_days / 30.0)
            rec_factor = (1.0 - share_rec) if share_rec is not None else 1.0
            sens_model_a_net = float(gross * rec_factor)

        sens_model_b_days: Optional[float] = None
        if undelivered is not None and sens_days is not None:
            sens_model_b_days = float(undelivered * sens_days)
        elif total_held is not None and sens_days is not None and undelivered is None:
            sens_model_b_days = float(total_held * sens_days)

        sens_money: Optional[float] = None
        if val is not None and val > 0 and sens_model_a_net is not None:
            sens_money = float(sens_model_a_net * val)

        sensitivity_rows.append(
            SensitivityRow(
                multiplier_label=label,
                multiplier=mult,
                days=sens_days,
                aircraft_days_held=sens_held_days,
                model_a_net_handovers_lost=sens_model_a_net,
                model_b_aircraft_days=sens_model_b_days,
                financial_impact=sens_money,
            )
        )

    return CalculatorOutputs(
        total_held_aircraft=total_held,
        aircraft_days_held=aircraft_days_held,
        aircraft_days_held_formula=formula_a,
        aircraft_days_held_assumption=assumption_a,
        model_a_gross_handovers_lost=model_a_gross,
        model_a_net_handovers_lost=model_a_net,
        model_a_formula=formula_b,
        model_a_assumption=assumption_b,
        model_b_aircraft_days=model_b_aircraft_days,
        model_b_formula=formula_c,
        model_b_assumption=assumption_c,
        one_day_cost_aircraft_days=one_day_aircraft_days,
        one_day_cost_money=one_day_money,
        financial_impact_total=financial_impact,
        sensitivity_table=sensitivity_rows,
    )
