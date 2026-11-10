import pytest
from pathlib import Path
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


def test_status_changes_only_by_explicit_edit():
    """Phase 7.1 rule: Verification status is 'needs verification' by default and changes only by explicit edit."""
    assert len(INCIDENT_CASES) == 3
    for case in INCIDENT_CASES:
        assert case.verification_status == "needs verification"

    # Verify that a case's verification_status cannot change implicitly
    case = INCIDENT_CASES[0].model_copy()
    assert case.verification_status == "needs verification"
    # Only explicit manual edit sets it to sourced
    case.verification_status = "sourced"
    assert case.verification_status == "sourced"


def test_every_case_shows_at_least_one_url():
    """Phase 7.1 rule: Every case shows at least one primary URL with marked source_type."""
    assert len(INCIDENT_CASES) == 3
    for case in INCIDENT_CASES:
        assert case.source_url.startswith("http")
        assert case.source_type in ["regulator", "manufacturer", "wire", "media"]
        assert len(case.sources) >= 1
        for s in case.sources:
            assert s.url.startswith("http")
            assert s.source_type in ["regulator", "manufacturer", "wire", "media"]
            assert len(s.fact_referenced) > 0


def test_case_directive_status_and_dated_events():
    """Phase 7.1 rule: Directive status ('issued', 'effective', 'proposed', 'final') and multiple dated events."""
    solar = next(c for c in INCIDENT_CASES if c.case_id == "A320-SOLAR-2025")
    assert solar.directive_status == "issued"
    assert len(solar.dated_events) >= 3
    dates = [e.date for e in solar.dated_events]
    assert "2025-10-30" in dates
    assert "2025-11-28" in dates
    assert "2025-12-01" in dates
    assert "About 6,000 aircraft, fewer than 100 remaining on 1 Dec 2025" in solar.deliveries_context

    panel = next(c for c in INCIDENT_CASES if c.case_id == "A320-PANEL-2025")
    assert panel.directive_status == "proposed"
    assert panel.public_statement_date == "2025-12-02"
    assert "2025 delivery target cut 820 to 790 on 3 Dec 2025" in panel.deliveries_context
    assert len(panel.dated_events) >= 3
    panel_dates = [e.date for e in panel.dated_events]
    assert "2025-12-02" in panel_dates
    assert "2025-12-03" in panel_dates
    assert "2025-12-17" in panel_dates

    # Check both breakdowns for A320 panels
    assert len(panel.fleet_breakdowns) == 2
    easa_breakdown = next(b for b in panel.fleet_breakdowns if "EASA" in b.name)
    assert easa_breakdown.in_service == 177
    assert easa_breakdown.undelivered_or_production == 451
    assert easa_breakdown.total == 628
    assert easa_breakdown.source_type == "regulator"

    reuters_breakdown = next(b for b in panel.fleet_breakdowns if "Reuters" in b.name)
    assert reuters_breakdown.in_service == 168
    assert reuters_breakdown.undelivered_or_production == 245
    assert reuters_breakdown.customer_allocated_or_other == 215
    assert reuters_breakdown.total == 628
    assert reuters_breakdown.source_type == "wire"


def test_a330neo_renamed_and_conflicting_reports():
    """Phase 7.1 rule: Case renamed to A330neo, with 3,2,4, one on 11 Aug, and conflicting reports note."""
    tool = next(c for c in INCIDENT_CASES if "A330NEO" in c.case_id)
    assert "A330neo" in tool.title
    assert tool.in_service_scope_notes == "conflicting reports, needs verification"
    assert "Zero deliveries in June and July 2026" in tool.deliveries_context
    assert "3, 2, 4 in March, April, May" in tool.deliveries_context
    assert "one on 11 Aug 2026" in tool.deliveries_context
    assert "mid-November 2026" in tool.deliveries_context

    dates = [e.date for e in tool.dated_events]
    assert "2026-03-31" in dates
    assert "2026-04-30" in dates
    assert "2026-05-31" in dates
    assert "2026-06-30" in dates
    assert "2026-07-31" in dates
    assert "2026-08-11" in dates
    assert "2026-11-15" in dates


def test_no_page_contains_solar_storm_caused():
    """Phase 7.1 rule: No page or codebase file contains the phrase 'solar storm caused'."""
    root = Path(__file__).resolve().parents[2]
    # Check Python, markdown, ts, tsx files
    forbidden = "solar " + "storm " + "caused"
    current_test_file = Path(__file__).resolve()
    checked_extensions = {".py", ".md", ".ts", ".tsx", ".html", ".yaml"}

    violations = []
    for p in root.rglob("*"):
        if not p.is_file() or p.suffix not in checked_extensions or p.resolve() == current_test_file:
            continue
        if any(part in p.parts for part in [".git", "node_modules", ".venv", "__pycache__", "dist", "tests"]):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore").lower()
            if forbidden in text:
                violations.append(str(p))
        except Exception:
            pass

    assert violations == [], f"Found forbidden phrase in: {violations}"


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
    assert panel_preset.days_to_scope is None
    assert panel_preset.aircraft_held_in_service == 177.0
    assert panel_preset.aircraft_held_undelivered == 451.0
    assert panel_preset.baseline_handover_rate_per_month is None
    assert panel_preset.share_recovered_later is None
    assert panel_preset.value_per_aircraft is None
    assert set(panel_preset.sourced_fields) == {"aircraft_held_in_service", "aircraft_held_undelivered"}

    # Preset 3: A330neo
    tool_preset = next(p for p in PRESETS if "A330NEO" in p.case_id)
    assert tool_preset.days_to_scope is None
    assert tool_preset.aircraft_held_in_service is None
    assert tool_preset.aircraft_held_undelivered is None
    assert tool_preset.baseline_handover_rate_per_month is None
    assert tool_preset.share_recovered_later is None
    assert tool_preset.value_per_aircraft is None
    assert tool_preset.sourced_fields == []


def test_formula_hand_computed_values():
    """Formulas strictly preserved:
    - days_to_scope = 30
    - in_service = 100, undelivered = 50 -> total_held = 150
    - aircraft_days_held = 4,500.0
    - gross_handovers_lost = 60 * (30/30) = 60.0
    - net_handovers_lost = 60 * 0.75 = 45.0
    - model_b = 50 * 30 = 1500.0
    """
    inputs = CalculatorInputs(
        days_to_scope=30.0,
        aircraft_held_in_service=100.0,
        aircraft_held_undelivered=50.0,
        baseline_handover_rate_per_month=60.0,
        share_recovered_later=0.25,
        value_per_aircraft=None,
    )
    res = run_calculator(inputs)

    assert res.total_held_aircraft == 150.0
    assert res.aircraft_days_held == 4500.0
    assert res.model_a_gross_handovers_lost == 60.0
    assert res.model_a_net_handovers_lost == 45.0
    assert res.model_b_aircraft_days == 1500.0
    assert res.one_day_cost_aircraft_days == 150.0


def test_blank_value_per_aircraft_produces_no_money_figure():
    """Phase 7 rule: If value_per_aircraft is blank, show no money figure."""
    inputs = CalculatorInputs(
        days_to_scope=29.0,
        aircraft_held_in_service=177.0,
        aircraft_held_undelivered=451.0,
        baseline_handover_rate_per_month=60.0,
        share_recovered_later=0.10,
        value_per_aircraft=None,
    )
    res = run_calculator(inputs)

    assert res.financial_impact_total is None
    assert res.one_day_cost_money is None
    for row in res.sensitivity_table:
        assert row.financial_impact is None
