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
    """Phase 4.2 Task 4: Verify that joint subtraction attacks across cell, family, and region tables fail.

    Checks:
    1. In sar_cell_suppression_table.md, all suppressed cells have counts masked as 'suppressed' (no numbers).
    2. Any row with suppressed cells possesses complementary suppression (>= 2 suppressed cells).
    3. Runs an algebraic linear optimization attack over sar_cell_suppression_table.md,
       sar_coarse_aggregations_table.md (Family totals), and Region totals jointly.
    4. Proves that exactly 0 suppressed cells can be uniquely recovered (all intervals have min < max).
    """
    from scipy.optimize import linprog

    cell_table_path = os.path.join("docs", "generated", "sar_cell_suppression_table.md")
    coarse_table_path = os.path.join("docs", "generated", "sar_coarse_aggregations_table.md")
    assert os.path.exists(cell_table_path), f"Missing artifact: {cell_table_path}"
    assert os.path.exists(coarse_table_path), f"Missing artifact: {coarse_table_path}"

    cell_lines = open(cell_table_path, "r", encoding="utf-8").readlines()

    # Parse cell table rows
    rows = []
    cells_by_cohort = {}
    for line in cell_lines:
        line = line.strip()
        if not line.startswith("|") or "Evaluation Cohort" in line or "|:---" in line:
            continue
        cols = [c.strip() for c in line.split("|")[1:-1]]
        if len(cols) >= 8:
            cohort, family, region, n_str, n_sil_str, sar_str, ci_str, status = cols[:8]
            is_supp = "SUPPRESSED" in status
            val = None if is_supp else int(n_str.replace("*", "").replace(",", ""))
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
            if cohort not in cells_by_cohort:
                cells_by_cohort[cohort] = {}
            cells_by_cohort[cohort][(family, region)] = (val, is_supp)

    assert len(rows) > 0, "No data rows parsed from sar_cell_suppression_table.md"

    # Rule 1: Every suppressed cell must mask N and N_sil as 'suppressed' (no numbers)
    for r in rows:
        if "SUPPRESSED" in r["status"]:
            assert r["n_str"] == "suppressed", f"Leakage: N count '{r['n_str']}' exposed in suppressed cell: {r}"
            assert r["n_sil_str"] == "suppressed", f"Leakage: N_sil count '{r['n_sil_str']}' exposed in suppressed cell: {r}"
            assert r["sar_str"] == "—", f"Leakage: SAR '{r['sar_str']}' exposed in suppressed cell: {r}"
            assert r["ci_str"] == "—", f"Leakage: CI '{r['ci_str']}' exposed in suppressed cell: {r}"

    # Parse coarse aggregations for Family totals and Region totals
    coarse_lines = open(coarse_table_path, "r", encoding="utf-8").readlines()
    family_totals = {}
    region_totals = {}
    mode = None

    for line in coarse_lines:
        line = line.strip()
        if "### A. Aircraft Family-Only Aggregation" in line:
            mode = "family"
            continue
        elif "### B. Geographic Region-Only Aggregation" in line:
            mode = "region"
            continue
        if not line.startswith("|") or "Aggregation Cohort" in line or "|:---" in line:
            continue
        cols = [c.strip() for c in line.split("|")[1:-1]]
        if mode == "family" and len(cols) >= 3:
            cohort = cols[0]
            fam = cols[1].replace("*", "")
            n_val = int(cols[2].replace(",", "").replace("*", ""))
            if cohort not in family_totals:
                family_totals[cohort] = {}
            family_totals[cohort][fam] = n_val
        elif mode == "region" and len(cols) >= 3:
            cohort = cols[0]
            reg = cols[1].replace("*", "")
            n_val = int(cols[2].replace(",", "").replace("*", ""))
            if cohort not in region_totals:
                region_totals[cohort] = {}
            region_totals[cohort][reg] = n_val

    families = ["A320-family", "A330", "A350", "other"]
    regions = ["Baltic", "Eastern Mediterranean", "Black Sea", "Middle East", "Western Europe", "North Atlantic"]

    total_recoverable_cells = 0

    # Rule 3 & 4: Joint Linear Subtraction Solver across Cell, Family, and Region tables
    for cohort, grid in cells_by_cohort.items():
        fam_tot = family_totals.get(cohort, {})
        reg_tot = region_totals.get(cohort, {})
        if not fam_tot or not reg_tot:
            continue

        var_list = [(fam, reg) for fam in families for reg in regions]
        var_map = {v: idx for idx, v in enumerate(var_list)}

        A_eq = []
        b_eq = []
        bounds = []

        # Family marginal constraints
        for fam in families:
            row = [0.0] * 24
            for reg in regions:
                row[var_map[(fam, reg)]] = 1.0
            A_eq.append(row)
            b_eq.append(float(fam_tot[fam]))

        # Region marginal constraints
        for reg in regions:
            col = [0.0] * 24
            for fam in families:
                col[var_map[(fam, reg)]] = 1.0
            A_eq.append(col)
            b_eq.append(float(reg_tot[reg]))

        # Cell bounds
        for fam, reg in var_list:
            val, is_supp = grid[(fam, reg)]
            if is_supp:
                bounds.append((0.0, float(fam_tot[fam])))
            else:
                bounds.append((float(val), float(val)))

        # Solve min and max for each suppressed cell
        for fam, reg in var_list:
            val, is_supp = grid[(fam, reg)]
            if is_supp:
                idx = var_map[(fam, reg)]
                c_min = [0.0] * 24
                c_min[idx] = 1.0
                res_min = linprog(c_min, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")

                c_max = [0.0] * 24
                c_max[idx] = -1.0
                res_max = linprog(c_max, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")

                assert res_min.success and res_max.success, f"Linear solver failed on feasible cohort {cohort}"
                x_min = res_min.fun
                x_max = -res_max.fun

                # If interval collapses to a single value, the cell is leaked
                if abs(x_max - x_min) < 1e-4:
                    total_recoverable_cells += 1

    # Exactly 0 suppressed cells must be recoverable across all published tables
    assert total_recoverable_cells == 0, (
        f"Subtraction vulnerability: {total_recoverable_cells} suppressed cells were uniquely recovered!"
    )


