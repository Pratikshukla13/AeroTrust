import pytest
from backend.app.schemas.incident import CalculatorInputs
from backend.app.incident_calculator import (
    INCIDENT_CASES,
    PRESETS,
    compute_days_event_to_statement,
    run_calculator,
)


def test_days_event_to_statement_computation():
    """Verifies that days between event and public statement are computed only when both dates exist."""
    # A320 Solar: 30 Oct 2025 to 28 Nov 2025 -> exactly 29 days
    days = compute_days_event_to_statement("2025-10-30", "2025-11-28")
    assert days == 29

    # Gaps with unknown event date must yield None
    assert compute_days_event_to_statement(None, "2025-12-17") is None
    assert compute_days_event_to_statement("2025-10-30", None) is None
    assert compute_days_event_to_statement(None, None) is None


def test_all_cases_marked_needs_verification():
    """Phase 7 rule: Mark every case 'needs verification' until user replaces URL and sets sourced."""
    assert len(INCIDENT_CASES) == 3
    for case in INCIDENT_CASES:
        assert case.verification_status == "needs verification"
        assert case.source_url.startswith("http")


def test_incident_cases_public_facts_integrity():
    """Verifies that only specified public facts are seeded, leaving gaps as None/unknown."""
    solar = next(c for c in INCIDENT_CASES if c.case_id == "A320-SOLAR-2025")
    assert solar.event_date == "2025-10-30"
    assert solar.public_statement_date == "2025-11-28"
    assert solar.directive_date == "2025-11-29"
    assert solar.aircraft_affected_total == 6000
    assert solar.aircraft_in_service is None  # Not specified in prompt facts -> must be None
    assert solar.aircraft_undelivered is None  # Not specified in prompt facts -> must be None
    assert solar.days_event_to_statement == 29
    assert "Fewer than 100 remaining on 1 Dec 2025" in (solar.deliveries_context or "")

    panel = next(c for c in INCIDENT_CASES if c.case_id == "A320-PANEL-2025")
    assert panel.event_date is None  # Event date unknown
    assert panel.public_statement_date is None
    assert panel.directive_date == "2025-12-17"
    assert panel.aircraft_affected_total == 628
    assert panel.aircraft_in_service == 177
    assert panel.aircraft_undelivered == 451
    assert panel.days_event_to_statement is None

    tool = next(c for c in INCIDENT_CASES if c.case_id == "A330-TOOL-2026")
    assert tool.event_date is None
    assert tool.public_statement_date is None
    assert tool.directive_date is None
    assert tool.aircraft_affected_total is None
    assert tool.aircraft_in_service is None
    assert tool.aircraft_undelivered is None
    assert tool.days_event_to_statement is None
    assert "Zero deliveries in June and July 2026" in (tool.deliveries_context or "")
    assert "nine in March to May 2026" in (tool.deliveries_context or "")


def test_no_preset_contains_unsourced_number():
    """Phase 7 rule: Presets fill only the fields that are sourced; everything else stays empty/None."""
    assert len(PRESETS) == 3

    # Preset 1: Solar
    solar_preset = next(p for p in PRESETS if p.case_id == "A320-SOLAR-2025")
    assert solar_preset.days_to_scope == 29.0
    assert solar_preset.aircraft_held_in_service is None
    assert solar_preset.aircraft_held_undelivered is None
    assert solar_preset.baseline_handover_rate_per_month is None
    assert solar_preset.share_recovered_later is None
    assert solar_preset.value_per_aircraft is None
    assert solar_preset.sourced_fields == ["days_to_scope"]

    # Preset 2: Panels
    panel_preset = next(p for p in PRESETS if p.case_id == "A320-PANEL-2025")
    assert panel_preset.days_to_scope is None  # event date unknown -> unsourced
    assert panel_preset.aircraft_held_in_service == 177.0
    assert panel_preset.aircraft_held_undelivered == 451.0
    assert panel_preset.baseline_handover_rate_per_month is None
    assert panel_preset.share_recovered_later is None
    assert panel_preset.value_per_aircraft is None
    assert set(panel_preset.sourced_fields) == {"aircraft_held_in_service", "aircraft_held_undelivered"}

    # Preset 3: Stray Tool
    tool_preset = next(p for p in PRESETS if p.case_id == "A330-TOOL-2026")
    assert tool_preset.days_to_scope is None
    assert tool_preset.aircraft_held_in_service is None
    assert tool_preset.aircraft_held_undelivered is None
    assert tool_preset.baseline_handover_rate_per_month is None
    assert tool_preset.share_recovered_later is None
    assert tool_preset.value_per_aircraft is None
    assert tool_preset.sourced_fields == []


def test_formula_hand_computed_values():
    """Unit tests for every formula with hand-computed values.
    
    Hand-computed Scenario:
    - days_to_scope = 30
    - aircraft_held_in_service = 100
    - aircraft_held_undelivered = 50
    Total held = 150 aircraft.
    a. aircraft_days_held = 150 * 30 = 4,500.0 aircraft-days.

    b. Model A (line stop):
    - baseline_handover_rate_per_month = 60
    - days_to_scope = 30 -> gross_handovers_lost = 60 * (30/30) = 60.0
    - share_recovered_later = 0.25 (25%) -> net_handovers_lost = 60.0 * (1 - 0.25) = 45.0 handovers.

    c. Model B (hold of finished aircraft):
    - aircraft_held_undelivered = 50
    - days_to_scope = 30 -> 50 * 30 = 1,500.0 aircraft-days.

    One-day cost:
    - aircraft-days per day = 150.0 aircraft-days / day.
    """
    inputs = CalculatorInputs(
        days_to_scope=30.0,
        aircraft_held_in_service=100.0,
        aircraft_held_undelivered=50.0,
        baseline_handover_rate_per_month=60.0,
        share_recovered_later=0.25,
        value_per_aircraft=None,  # Blank
    )
    res = run_calculator(inputs)

    assert res.total_held_aircraft == 150.0
    assert res.aircraft_days_held == 4500.0
    assert res.model_a_gross_handovers_lost == 60.0
    assert res.model_a_net_handovers_lost == 45.0
    assert res.model_b_aircraft_days == 1500.0
    assert res.one_day_cost_aircraft_days == 150.0

    # Sensitivity table hand-computed checks:
    # 0.5x -> days = 15
    row_05 = next(r for r in res.sensitivity_table if r.multiplier_label == "0.5x")
    assert row_05.days == 15.0
    assert row_05.aircraft_days_held == 150.0 * 15.0  # 2250.0
    assert row_05.model_a_net_handovers_lost == (60.0 * (15.0 / 30.0)) * 0.75  # 22.5
    assert row_05.model_b_aircraft_days == 50.0 * 15.0  # 750.0

    # 1.0x -> days = 30
    row_10 = next(r for r in res.sensitivity_table if r.multiplier_label == "1.0x")
    assert row_10.days == 30.0
    assert row_10.aircraft_days_held == 4500.0
    assert row_10.model_a_net_handovers_lost == 45.0
    assert row_10.model_b_aircraft_days == 1500.0

    # 2.0x -> days = 60
    row_20 = next(r for r in res.sensitivity_table if r.multiplier_label == "2.0x")
    assert row_20.days == 60.0
    assert row_20.aircraft_days_held == 9000.0
    assert row_20.model_a_net_handovers_lost == 90.0
    assert row_20.model_b_aircraft_days == 3000.0


def test_blank_value_per_aircraft_produces_no_money_figure():
    """Phase 7 rule: If value_per_aircraft is blank, show no money figure."""
    inputs = CalculatorInputs(
        days_to_scope=29.0,
        aircraft_held_in_service=177.0,
        aircraft_held_undelivered=451.0,
        baseline_handover_rate_per_month=60.0,
        share_recovered_later=0.10,
        value_per_aircraft=None,  # BLANK
    )
    res = run_calculator(inputs)

    assert res.financial_impact_total is None
    assert res.one_day_cost_money is None
    for row in res.sensitivity_table:
        assert row.financial_impact is None


def test_entered_value_per_aircraft_computes_money_figure():
    """When value_per_aircraft is entered, computes financial impact."""
    val = 100_000_000.0  # $100M
    inputs = CalculatorInputs(
        days_to_scope=30.0,
        aircraft_held_in_service=0.0,
        aircraft_held_undelivered=10.0,
        baseline_handover_rate_per_month=30.0,
        share_recovered_later=0.0,
        value_per_aircraft=val,
    )
    res = run_calculator(inputs)

    # 30 days at 30/mo = 30 aircraft lost * $100M = $3,000,000,000
    assert res.model_a_net_handovers_lost == 30.0
    assert res.financial_impact_total == 3_000_000_000.0

    row_10 = next(r for r in res.sensitivity_table if r.multiplier_label == "1.0x")
    assert row_10.financial_impact == 3_000_000_000.0
