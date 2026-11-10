from datetime import date
from typing import List, Optional
from backend.app.schemas.incident import (
    IncidentCase,
    IncidentCasePreset,
    DatedEvent,
    SourceItem,
    FleetBreakdown,
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


# Phase 7.2 Corrected Public Facts.
# Rule 4: Every URL must be either a real URL provided by user or null. All invented/placeholder
# URLs (including ad.easa.europa.eu patterns) are removed (set to None). Cases with null source_url
# show 'primary source missing' in red. url_status is 'unchecked'.
INCIDENT_CASES: List[IncidentCase] = [
    IncidentCase(
        case_id="A320-SOLAR-2025",
        title="A320 Solar Radiation Single-Event Effect",
        event_date="2025-10-30",
        public_statement_date="2025-11-28",
        directive_date="2025-11-28",
        directive_status="issued",  # Issued 28 Nov 2025; effective date to be confirmed from the AD document
        aircraft_affected_total=6000,
        aircraft_in_service=None,  # unknown / not specified in facts
        aircraft_undelivered=None,  # unknown / not specified in facts
        deliveries_context="About 6,000 aircraft, fewer than 100 remaining on 1 Dec 2025.",
        in_service_scope_notes=None,
        days_event_to_statement=compute_days_event_to_statement("2025-10-30", "2025-11-28"),
        source_url=None,  # Placeholder deleted; awaits user-provided URL
        source_type="regulator",
        url_status="unchecked",
        verification_status="needs verification",
        sources=[
            SourceItem(
                url=None,
                title="EASA Emergency Airworthiness Directive",
                source_type="regulator",
                url_status="unchecked",
                fact_referenced="Emergency AD issued 28 Nov 2025 for ~6,000 aircraft; effective date to be confirmed from AD document.",
            ),
            SourceItem(
                url=None,
                title="Airbus Alert Notification to Operators",
                source_type="manufacturer",
                url_status="unchecked",
                fact_referenced="Airbus alert issued 28 Nov 2025; stated intense solar radiation may corrupt data critical to flight controls; <100 remaining on 1 Dec 2025.",
            ),
        ],
        dated_events=[
            DatedEvent(
                date="2025-10-30",
                label="Incident Event",
                description="Data corruption event critical to flight controls occurs at cruise altitude. Airbus stated intense solar radiation may corrupt data; independent experts questioned whether radiation level was unusual. Axis B is exposure context, not a cause.",
                source_url=None,
                source_type="regulator",
                url_status="unchecked",
            ),
            DatedEvent(
                date="2025-11-28",
                label="Airbus Alert & EASA Emergency AD Issued",
                description="Airbus alert and EASA emergency directive issued 28 Nov 2025 (effective date to be confirmed from the AD document).",
                source_url=None,
                source_type="regulator",
                url_status="unchecked",
            ),
            DatedEvent(
                date="2025-12-01",
                label="Rectification Progress",
                description="Fewer than 100 aircraft remaining out of ~6,000 affected.",
                source_url=None,
                source_type="manufacturer",
                url_status="unchecked",
            ),
        ],
        fleet_breakdowns=[],
    ),
    IncidentCase(
        case_id="A320-PANEL-2025",
        title="A320 Fuselage Panels Production Discrepancy",
        event_date=None,  # event date unknown
        public_statement_date="2025-12-02",
        directive_date="2025-12-17",
        directive_status="proposed",  # EASA PROPOSED directive published 17 Dec 2025; later final directive to be confirmed
        aircraft_affected_total=628,
        aircraft_in_service=177,
        aircraft_undelivered=451,
        deliveries_context="2025 delivery target cut 820 to 790 on 3 Dec 2025.",
        in_service_scope_notes=None,
        days_event_to_statement=None,
        source_url=None,  # Placeholder deleted; awaits user-provided URL
        source_type="regulator",
        url_status="unchecked",
        verification_status="needs verification",
        sources=[
            SourceItem(
                url=None,
                title="EASA Proposed Airworthiness Directive (PAD)",
                source_type="regulator",
                url_status="unchecked",
                fact_referenced="EASA PROPOSED directive published 17 Dec 2025 (177 in service, 451 in production); later final directive to be confirmed.",
            ),
            SourceItem(
                url=None,
                title="Airbus Public Statement on Fuselage Panels",
                source_type="manufacturer",
                url_status="unchecked",
                fact_referenced="Airbus public statement 2 Dec 2025 confirming 628 in scope; 2025 delivery target cut 820 to 790 on 3 Dec 2025.",
            ),
            SourceItem(
                url=None,
                title="Reuters Industrial Investigation",
                source_type="wire",
                url_status="unchecked",
                fact_referenced="Reuters breakdown: 168 in service, 245 on assembly lines (about 100 due for delivery in 2025), 215 in earlier production.",
            ),
        ],
        dated_events=[
            DatedEvent(
                date="2025-12-02",
                label="Airbus Public Statement",
                description="Airbus public statement confirming 628 aircraft in scope for fuselage panel discrepancy.",
                source_url=None,
                source_type="manufacturer",
                url_status="unchecked",
            ),
            DatedEvent(
                date="2025-12-03",
                label="Delivery Target Cut",
                description="Airbus officially cuts 2025 delivery target from 820 to 790 aircraft.",
                source_url=None,
                source_type="manufacturer",
                url_status="unchecked",
            ),
            DatedEvent(
                date="2025-12-17",
                label="EASA PROPOSED Directive Published",
                description="EASA publishes PROPOSED directive for 628 aircraft (177 in service, 451 in production); later final directive to be confirmed.",
                source_url=None,
                source_type="regulator",
                url_status="unchecked",
            ),
        ],
        fleet_breakdowns=[
            FleetBreakdown(
                name="EASA Proposed Directive (17 Dec 2025)",
                source_url=None,
                source_type="regulator",
                url_status="unchecked",
                in_service=177,
                undelivered_or_production=451,
                customer_allocated_or_other=None,
                total=628,
                notes="Official EASA Proposed Directive regulatory scope: 177 in service, 451 in production.",
            ),
            FleetBreakdown(
                name="Reuters Sourced Breakdown",
                source_url=None,
                source_type="wire",
                url_status="unchecked",
                in_service=168,
                undelivered_or_production=245,
                customer_allocated_or_other=215,
                total=628,
                notes="168 in service, 245 on assembly lines (about 100 due for delivery in 2025), 215 in earlier production.",
            ),
        ],
    ),
    IncidentCase(
        case_id="A330NEO-TOOL-2026",
        title="A330neo Stray Assembly Tool Inspection",
        event_date=None,  # event date unknown
        public_statement_date=None,  # unknown
        directive_date=None,  # policy due mid-Nov 2026, no directive published
        directive_status="none_published_or_unknown",  # Phase 7.2: none_published_or_unknown (not proposed)
        aircraft_affected_total=None,  # number inspected not disclosed
        aircraft_in_service=None,  # not disclosed
        aircraft_undelivered=None,  # not disclosed
        deliveries_context="Zero deliveries in June and July 2026; 3, 2, 4 in March, April, May; one on 11 Aug 2026; number of aircraft inspected not disclosed; policy to the regulator due mid-November 2026.",
        in_service_scope_notes="Reports conflict: one says no retroactive fix is required for in-service aircraft, another says inspections are recommended for aircraft delivered from early 2021 to end of May 2026, with final requirements under discussion with the regulator. Needs verification.",
        days_event_to_statement=None,
        source_url=None,  # Placeholder deleted; awaits user-provided URL
        source_type="manufacturer",
        url_status="unchecked",
        verification_status="needs verification",
        sources=[
            SourceItem(
                url=None,
                title="Airbus Monthly Orders & Deliveries Files (2026)",
                source_type="manufacturer",
                url_status="unchecked",
                fact_referenced="Official deliveries: March (3), April (2), May (4); June (0), July (0); 11 Aug 2026 (1).",
            ),
            SourceItem(
                url=None,
                title="Regulator Oversight Discussion",
                source_type="regulator",
                url_status="unchecked",
                fact_referenced="Inspection policy to the regulator due mid-November 2026; in-service requirements under discussion.",
            ),
        ],
        dated_events=[
            DatedEvent(
                date="2026-03-31",
                label="March Deliveries",
                description="3 A330neo aircraft delivered.",
                source_url=None,
                source_type="manufacturer",
                url_status="unchecked",
            ),
            DatedEvent(
                date="2026-04-30",
                label="April Deliveries",
                description="2 A330neo aircraft delivered.",
                source_url=None,
                source_type="manufacturer",
                url_status="unchecked",
            ),
            DatedEvent(
                date="2026-05-31",
                label="May Deliveries",
                description="4 A330neo aircraft delivered (total 9 in March–May).",
                source_url=None,
                source_type="manufacturer",
                url_status="unchecked",
            ),
            DatedEvent(
                date="2026-06-30",
                label="June Delivery Pause",
                description="Zero A330neo deliveries in June 2026.",
                source_url=None,
                source_type="manufacturer",
                url_status="unchecked",
            ),
            DatedEvent(
                date="2026-07-31",
                label="July Delivery Pause",
                description="Zero A330neo deliveries in July 2026.",
                source_url=None,
                source_type="manufacturer",
                url_status="unchecked",
            ),
            DatedEvent(
                date="2026-08-11",
                label="Deliveries Resume",
                description="One A330neo delivered on 11 Aug 2026.",
                source_url=None,
                source_type="manufacturer",
                url_status="unchecked",
            ),
            DatedEvent(
                date="2026-11-15",
                label="Regulator Policy Filing Milestone",
                description="Inspection policy to the regulator due mid-November 2026.",
                source_url=None,
                source_type="regulator",
                url_status="unchecked",
            ),
        ],
        fleet_breakdowns=[],
    ),
]


# Presets fill ONLY the fields that are sourced; everything else stays None/empty
PRESETS: List[IncidentCasePreset] = [
    IncidentCasePreset(
        case_id="A320-SOLAR-2025",
        title="A320 Solar Radiation (Public Gap 29 Days)",
        days_to_scope=None,  # Phase 7.2 rule: removed from preset; leaves days_to_scope empty
        aircraft_held_in_service=None,  # unsourced
        aircraft_held_undelivered=None,  # unsourced
        baseline_handover_rate_per_month=None,
        share_recovered_later=None,
        value_per_aircraft=None,
        days_event_to_public_statement=29.0,  # Separate display-only field that cannot feed the calculator
        days_event_to_public_statement_helper="This is the public gap between the incident and Airbus's statement. It is not a hold period and not a scoping time.",
        sourced_fields=[],  # days_to_scope removed, cannot feed calculator
    ),
    IncidentCasePreset(
        case_id="A320-PANEL-2025",
        title="A320 Fuselage Panels (177 In-Service, 451 Undelivered)",
        days_to_scope=None,  # unsourced (event date unknown)
        aircraft_held_in_service=177.0,  # sourced from EASA Proposed Directive
        aircraft_held_undelivered=451.0,  # sourced from EASA Proposed Directive
        baseline_handover_rate_per_month=None,
        share_recovered_later=None,
        value_per_aircraft=None,
        days_event_to_public_statement=None,
        days_event_to_public_statement_helper=None,
        sourced_fields=["aircraft_held_in_service", "aircraft_held_undelivered"],
    ),
    IncidentCasePreset(
        case_id="A330NEO-TOOL-2026",
        title="A330neo Stray Assembly Tool (Deliveries Context Only)",
        days_to_scope=None,  # unsourced
        aircraft_held_in_service=None,  # unsourced
        aircraft_held_undelivered=None,  # unsourced
        baseline_handover_rate_per_month=None,
        share_recovered_later=None,
        value_per_aircraft=None,
        days_event_to_public_statement=None,
        days_event_to_public_statement_helper=None,
        sourced_fields=[],  # All calculator numeric inputs unsourced
    ),
]


def run_calculator(inputs: CalculatorInputs) -> CalculatorOutputs:
    """Executes the Incident Clock scoping calculator without invented constants.
    
    FORMULAS ARE STRICTLY PRESERVED FROM PHASE 7:
    a. aircraft_days_held = held aircraft x days.
    b. Model A (line stop): handovers_lost = baseline_rate x days / 30, net of recovered share if provided.
    c. Model B (hold of finished aircraft): handover delay in aircraft-days only.
    d. If value_per_aircraft is blank, show no money figure.
    """
    days = inputs.days_to_scope
    in_service = inputs.aircraft_held_in_service
    undelivered = inputs.aircraft_held_undelivered
    rate = inputs.baseline_handover_rate_per_month
    share_rec = inputs.share_recovered_later
    val = inputs.value_per_aircraft

    # Compute Total Held Aircraft
    has_held = (in_service is not None) or (undelivered is not None)
    total_held: Optional[float] = None
    if has_held:
        total_held = float((in_service or 0.0) + (undelivered or 0.0))

    # a. Total Aircraft-Days Held
    aircraft_days_held: Optional[float] = None
    if total_held is not None and days is not None:
        aircraft_days_held = float(total_held * days)

    formula_a = "aircraft_days_held = (aircraft_held_in_service + aircraft_held_undelivered) × days_to_scope"

    # b. Model A (line stop): handovers lost = baseline_rate x days / 30, net of recovered share
    model_a_gross: Optional[float] = None
    model_a_net: Optional[float] = None
    if rate is not None and days is not None:
        model_a_gross = float(rate * (days / 30.0))
        rec_factor = (1.0 - share_rec) if share_rec is not None else 1.0
        model_a_net = float(model_a_gross * rec_factor)

    formula_b = (
        "gross_handovers_lost = baseline_handover_rate_per_month × (days_to_scope / 30); "
        "net_handovers_lost = gross_handovers_lost × (1 - share_recovered_later)"
    )

    # c. Model B (hold of finished aircraft): handover delay in aircraft-days only
    model_b_aircraft_days: Optional[float] = None
    if undelivered is not None and days is not None:
        model_b_aircraft_days = float(undelivered * days)
    elif total_held is not None and days is not None and undelivered is None:
        model_b_aircraft_days = float(total_held * days)

    formula_c = "handover_delay_aircraft_days = aircraft_held_undelivered × days_to_scope"

    # One-day cost of delay (aircraft-days per day)
    one_day_aircraft_days: Optional[float] = None
    if total_held is not None:
        one_day_aircraft_days = float(total_held)

    # Financial calculations: STRICTLY None if value_per_aircraft is blank
    financial_impact: Optional[float] = None
    one_day_money: Optional[float] = None
    if val is not None:
        if model_a_net is not None:
            financial_impact = float(model_a_net * val)
        if rate is not None:
            rec_factor = (1.0 - share_rec) if share_rec is not None else 1.0
            daily_net_lost = (rate / 30.0) * rec_factor
            one_day_money = float(daily_net_lost * val)

    # Sensitivity matrix over duration multipliers: 0.5x, 1.0x, 2.0x
    sensitivity_table: List[SensitivityRow] = []
    if days is not None and days > 0:
        for mult in [0.5, 1.0, 2.0]:
            d = days * mult
            adh = (total_held * d) if total_held is not None else 0.0

            m_a_net: Optional[float] = None
            if rate is not None:
                m_a_gross = rate * (d / 30.0)
                rec = (1.0 - share_rec) if share_rec is not None else 1.0
                m_a_net = m_a_gross * rec

            m_b: Optional[float] = None
            if undelivered is not None:
                m_b = undelivered * d
            elif total_held is not None and undelivered is None:
                m_b = total_held * d

            f_impact: Optional[float] = None
            if val is not None and m_a_net is not None:
                f_impact = m_a_net * val

            sensitivity_table.append(
                SensitivityRow(
                    multiplier=mult,
                    duration_days=d,
                    aircraft_days_held=adh,
                    model_a_net_handovers_lost=m_a_net,
                    model_b_aircraft_days=m_b,
                    financial_impact=f_impact,
                )
            )

    assumptions = [
        "Aircraft held count applies uniformly across the scoping duration.",
        "Model A assumes uniform monthly delivery rate across standard 30-day calendar months.",
        "Model B measures holding duration of finished aircraft exclusively in aircraft-days.",
        "Financial figures are withheld unless value per aircraft is explicitly specified.",
        "Scenario calculations reflect user inputs and public disclosures only, not internal manufacturer records.",
    ]

    return CalculatorOutputs(
        total_held_aircraft=total_held,
        aircraft_days_held=aircraft_days_held,
        model_a_gross_handovers_lost=model_a_gross,
        model_a_net_handovers_lost=model_a_net,
        model_b_aircraft_days=model_b_aircraft_days,
        financial_impact_total=financial_impact,
        one_day_cost_aircraft_days=one_day_aircraft_days,
        one_day_cost_money=one_day_money,
        formula_a_aircraft_days=formula_a,
        formula_b_model_a=formula_b,
        formula_c_model_b=formula_c,
        assumptions_applied=assumptions,
        sensitivity_table=sensitivity_table,
    )
