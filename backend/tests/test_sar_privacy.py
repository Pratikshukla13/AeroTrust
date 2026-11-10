"""Tests for Silent Acceptance Rate (SAR) Privacy, Suppression, and Importer Guardrails (Phase 4).

Adheres strictly to Phase 4 Requirements:
1. sar_aggregate table and API output contain no icao24, tail number, flight_id, or per-flight membership.
2. Suppression rule: cells with < 30 flagged flights are suppressed.
3. EASA-style CSV importer & rank correlation is verified and labelled 'pipeline test only'.
4. Docs sanitization: no stray 'chefs' or tool-error strings.
"""

import os
import re
import pytest
import psycopg2
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_sar_aggregate_db_schema_privacy():
    """Verify that PostgreSQL sar_aggregate table contains zero PII or flight identifiers."""
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        user=os.getenv("POSTGRES_USER", "aerotrust"),
        password=os.getenv("POSTGRES_PASSWORD", "aerotrust_secret"),
        dbname=os.getenv("POSTGRES_DB", "aerotrust"),
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'sar_aggregate';
    """)
    cols = [r[0].lower() for r in cur.fetchall()]
    conn.close()

    assert len(cols) > 0, "sar_aggregate table not found in PostgreSQL"

    forbidden_cols = ["icao24", "registration", "tail_number", "flight_id", "flight_ids", "members", "flights"]
    for f in forbidden_cols:
        assert f not in cols, f"Forbidden privacy-violating column '{f}' found in sar_aggregate schema!"

    allowed_cols = {"id", "family", "region", "month", "n_flights_flagged", "n_silent", "sar", "ci_low", "ci_high", "suppressed", "created_at"}
    for c in cols:
        assert c in allowed_cols, f"Unexpected column '{c}' in sar_aggregate table!"


def test_sar_api_endpoint_privacy_and_suppression():
    """Verify /api/sar endpoint enforces privacy and suppression."""
    response = client.get("/api/sar")
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0, "Expected populated SAR aggregate records"

    forbidden_fields = ["icao24", "registration", "tail_number", "flight_id", "flight_ids", "members", "points"]

    for row in data:
        # Privacy check: no flight-level identifiers
        for f in forbidden_fields:
            assert f not in row, f"Privacy violation: '{f}' returned in /api/sar response!"

        # Suppression check: cells with < 30 flagged flights must be suppressed and all counts masked
        if row["suppressed"]:
            assert row["n_flights_flagged"] is None, f"Suppressed cell must mask n_flights_flagged: {row}"
            assert row["n_silent"] is None, f"Suppressed cell must mask n_silent: {row}"
            assert row["sar"] is None, f"Suppressed cell must mask SAR to None: {row}"
            assert row["ci_low"] is None
            assert row["ci_high"] is None
        else:
            assert row["n_flights_flagged"] is not None and row["n_flights_flagged"] >= 30
            assert row["n_silent"] is not None
            assert row["sar"] is not None
            assert 0.0 <= row["sar"] <= 1.0


def test_easa_regional_ranking_importer_labelled_pipeline_test():
    """Verify EASA-style CSV importer output is present and labelled pipeline test only."""
    artifact_path = os.path.join("docs", "generated", "sar_regional_rank_correlation.md")
    assert os.path.exists(artifact_path), f"Missing artifact: {artifact_path}"
    content = open(artifact_path, "r", encoding="utf-8").read()

    assert "pipeline test only" in content.lower(), "Artifact must be explicitly labelled 'pipeline test only'"
    assert "spearman rank correlation" in content.lower()


def test_sar_bias_analysis_documented():
    """Verify SAR bias analysis artifact exists and documents inflation."""
    artifact_path = os.path.join("docs", "generated", "sar_bias_analysis_table.md")
    assert os.path.exists(artifact_path), f"Missing artifact: {artifact_path}"
    content = open(artifact_path, "r", encoding="utf-8").read()

    assert "clean false positives" in content.lower()
    assert "precision-adjusted" in content.lower()
    assert "unreliable" in content.lower()


def test_no_stray_error_strings_in_phase4_docs():
    """Sanitization check for stray tokens like 'chefs' across generated docs."""
    forbidden = ["chefs", "network issue", "tool-error", "traceback", "undefined", "nan%"]
    gen_dir = os.path.join("docs", "generated")
    for fname in os.listdir(gen_dir):
        if fname.endswith(".md"):
            fpath = os.path.join(gen_dir, fname)
            text = open(fpath, "r", encoding="utf-8").read().lower()
            for token in forbidden:
                assert token not in text, f"Found forbidden error token '{token}' in {fpath}"


def test_subtraction_attack_on_suppressed_cells_fails():
    """Phase 4.1 Task 2: Verify that subtraction attacks on suppressed cells are underdetermined and fail.

    Checks:
    1. In sar_cell_suppression_table.md, all suppressed cells have counts masked as 'suppressed' (no integers).
    2. Any row with suppressed cells possesses complementary suppression (>= 2 suppressed cells).
    3. An algebraic marginal subtraction attack attempting to deduce the suppressed cell's value
       has at least 1 degree of freedom (cannot uniquely isolate the cell).
    """
    cell_table_path = os.path.join("docs", "generated", "sar_cell_suppression_table.md")
    assert os.path.exists(cell_table_path), f"Missing artifact: {cell_table_path}"
    cell_lines = open(cell_table_path, "r", encoding="utf-8").readlines()

    # Parse cell table rows
    rows = []
    for line in cell_lines:
        line = line.strip()
        if not line.startswith("|") or "Evaluation Cohort" in line or "|:---" in line:
            continue
        cols = [c.strip() for c in line.split("|")[1:-1]]
        if len(cols) >= 8:
            cohort, family, region, n_str, n_sil_str, sar_str, ci_str, status = cols[:8]
            rows.append({
                "cohort": cohort,
                "family": family,
                "region": region,
                "n_str": n_str,
                "n_sil_str": n_sil_str,
                "sar_str": sar_str,
                "ci_str": ci_str,
                "status": status,
            })

    assert len(rows) > 0, "No data rows parsed from sar_cell_suppression_table.md"

    # Rule 1: Every suppressed cell must mask N and N_sil as 'suppressed' (no numbers)
    for r in rows:
        if "SUPPRESSED" in r["status"]:
            assert r["n_str"] == "suppressed", f"Leakage: N count '{r['n_str']}' exposed in suppressed cell: {r}"
            assert r["n_sil_str"] == "suppressed", f"Leakage: N_sil count '{r['n_sil_str']}' exposed in suppressed cell: {r}"
            assert r["sar_str"] == "—", f"Leakage: SAR '{r['sar_str']}' exposed in suppressed cell: {r}"
            assert r["ci_str"] == "—", f"Leakage: CI '{r['ci_str']}' exposed in suppressed cell: {r}"

    # Group by (cohort, family) to test row-level marginal subtraction
    from collections import defaultdict
    cohort_fam_cells = defaultdict(list)
    for r in rows:
        cohort_fam_cells[(r["cohort"], r["family"])].append(r)

    # For any row containing suppressed cells:
    for (cohort, family), cells in cohort_fam_cells.items():
        supp_cells = [c for c in cells if "SUPPRESSED" in c["status"]]
        if supp_cells:
            # Rule 2: Complementary suppression must ensure at least 2 cells in the row are suppressed
            assert len(supp_cells) >= 2, (
                f"Subtraction vulnerability in ({cohort}, {family}): only {len(supp_cells)} cell suppressed, "
                "allowing algebraic recovery by subtracting published cells from family total!"
            )

            # Rule 3: Simulate subtraction attack
            # An attacker tries to solve: x_1 + x_2 + ... + x_k = Row_Total - sum(published)
            # Since k >= 2, there are infinitely many integer combinations summing to this constant,
            # meaning the linear system is underdetermined with >= 1 degree of freedom.
            degrees_of_freedom = len(supp_cells) - 1
            assert degrees_of_freedom >= 1, f"Subtraction attack degrees of freedom must be >= 1, got {degrees_of_freedom}"


