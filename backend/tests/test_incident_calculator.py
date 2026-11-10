import pytest
from pathlib import Path
from pydantic import ValidationError
from backend.app.schemas.incident import CalculatorInputs, IncidentCase
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


def test_status_changes_only_by_explicit_edit_and_requires_verified_url():
    """Phase 7.2 rule: A case can become 'sourced' only when it has a primary URL with status 'verified by user'."""
    assert len(INCIDENT_CASES) == 3
    for case in INCIDENT_CASES:
        assert case.verification_status == "needs verification"

    base_dict = INCIDENT_CASES[0].model_dump()

    # Attempting to set sourced when primary source_url is None must raise ValidationError / ValueError
    with pytest.raises((ValueError, ValidationError), match="primary URL"):
        IncidentCase(**{**base_dict, "source_url": None, "verification_status": "sourced"})

    # Setting primary URL but leaving status as 'unchecked' must also raise ValidationError
    with pytest.raises((ValueError, ValidationError), match="verified by user"):
        IncidentCase(
            **{
                **base_dict,
                "source_url": "https://example.com/verified-ad",
                "url_status": "unchecked",
                "verification_status": "sourced",
            }
        )

    # Only when primary URL is present AND status is 'verified by user' can it become sourced
    sourced_case = IncidentCase(
        **{
            **base_dict,
            "source_url": "https://example.com/verified-ad",
            "url_status": "verified by user",
            "verification_status": "sourced",
        }
    )
    assert sourced_case.verification_status == "sourced"
    assert sourced_case.source_url == "https://example.com/verified-ad"
    assert sourced_case.url_status == "verified by user"


def test_no_invented_urls_and_all_url_status_unchecked():
    """Phase 7.2 rule: Every URL must be either a real user-provided URL or null.
    Invented/placeholder URLs (including ad.easa.europa.eu patterns) are deleted.
    Every URL shows status 'unchecked'.
    """
    assert len(INCIDENT_CASES) == 3
    for case in INCIDENT_CASES:
        # All placeholder URLs deleted; currently None awaiting user-provided URLs
        assert case.source_url is None
        assert case.url_status == "unchecked"

        for s in case.sources:
            assert s.url is None
            assert s.url_status == "unchecked"

        for evt in case.dated_events:
            assert evt.source_url is None
            assert evt.url_status == "unchecked"

        for fb in case.fleet_breakdowns:
            assert fb.source_url is None
            assert fb.url_status == "unchecked"


def test_case_directive_status_and_dated_events():
    """Phase 7.1/7.2 rule: Directive status and dated events."""
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

    # Phase 7.2 rule: Reuters breakdown labels
    reuters_breakdown = next(b for b in panel.fleet_breakdowns if "Reuters" in b.name)
    assert reuters_breakdown.in_service == 168
    assert reuters_breakdown.undelivered_or_production == 245
    assert reuters_breakdown.customer_allocated_or_other == 215
    assert reuters_breakdown.total == 628
    assert reuters_breakdown.source_type == "wire"
    assert "168 in service" in reuters_breakdown.notes
    assert "245 on assembly lines (about 100 due for delivery in 2025)" in reuters_breakdown.notes
    assert "215 in earlier production" in reuters_breakdown.notes
    assert "parts supplier" not in reuters_breakdown.notes.lower()
    assert "airline fleet" not in reuters_breakdown.notes.lower()


def test_a330neo_directive_status_and_scope_note():
    """Phase 7.2 rule: directive_status is 'none_published_or_unknown', scope note updated, no '24 vs 4'."""
    tool = next(c for c in INCIDENT_CASES if "A330NEO" in c.case_id)
    assert "A330neo" in tool.title
    assert tool.directive_status == "none_published_or_unknown"
    assert tool.directive_status != "proposed"

    expected_scope = (
        "Reports conflict: one says no retroactive fix is required for in-service "
        "aircraft, another says inspections are recommended for aircraft delivered from early 2021 to "
        "end of May 2026, with final requirements under discussion with the regulator. Needs verification."
    )
    assert tool.in_service_scope_notes == expected_scope
    assert "24 vs 4" not in tool.in_service_scope_notes
    assert "24 vs 4" not in tool.deliveries_context

    assert "Zero deliveries in June and July 2026" in tool.deliveries_context
    assert "3, 2, 4 in March, April, May" in tool.deliveries_context
    assert "one on 11 Aug 2026" in tool.deliveries_context
    assert "mid-November 2026" in tool.deliveries_context


def test_no_page_contains_solar_storm_caused():
    """Phase 7.1/7.2 rule: No page or codebase file contains the phrase 'solar storm caused'."""
    root = Path(__file__).resolve().parents[2]
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


def test_a320_solar_preset_days_to_scope_empty():
    """Phase 7.2 rule: Remove days_to_scope = 29 from the A320 radiation preset.
    Store as separate display-only field 'days_event_to_public_statement' (29) with helper text.
    The preset leaves days_to_scope empty.
    """
    assert len(PRESETS) == 3

    # Preset 1: Solar
    solar_preset = next(p for p in PRESETS if p.case_id == "A320-SOLAR-2025")
    assert solar_preset.days_to_scope is None  # Strictly empty!
    assert solar_preset.days_event_to_public_statement == 29.0
    expected_helper = (
        "This is the public gap between the incident and Airbus's statement. "
        "It is not a hold period and not a scoping time."
    )
    assert solar_preset.days_event_to_public_statement_helper == expected_helper
    assert solar_preset.aircraft_held_in_service is None
    assert solar_preset.aircraft_held_undelivered is None
    assert solar_preset.baseline_handover_rate_per_month is None
    assert solar_preset.share_recovered_later is None
    assert solar_preset.value_per_aircraft is None
    assert solar_preset.sourced_fields == []  # Cannot feed calculator!

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
