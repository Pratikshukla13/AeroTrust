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

        # Suppression check: cells with < 30 flagged flights must be suppressed and sar masked
        if row["n_flights_flagged"] < 30:
            assert row["suppressed"] is True, f"Cell with {row['n_flights_flagged']} flagged flights not suppressed: {row}"
            assert row["sar"] is None, f"Suppressed cell must mask SAR to None: {row}"
            assert row["ci_low"] is None
            assert row["ci_high"] is None
        else:
            assert row["suppressed"] is False
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
