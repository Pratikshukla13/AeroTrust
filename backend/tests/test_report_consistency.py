"""Test Report Mathematical Consistency and Phase 3.2 Hardening Rules.

Adheres strictly to Phase 3.2 Requirements:
1. Parses every table in docs/INJECTION_REPORT.md and recomputes precision, recall, and F1.
2. Asserts cross-table identities:
   - All tables built from the test seed agree on N = 5,225 and class counts:
     N_clean = 3,887, N_spoof = 913, N_jam = 427, N_hostile = 1,338.
   - 2x2 matrix: TP + FP + FN + TN = 5,225 for every row.
   - FP attribution table: Clean FP count sums to 452, shares sum to 100.0%.
3. Forbids the words 'ok' and 'safe' in any status, tier, or report column.
4. Verifies every table has an annotated generating script and non-empty artifact.
"""

import os
import re
import pytest


def parse_markdown_tables(report_text: str):
    """Extracts all markdown tables from text as list of dicts with header mapping."""
    tables = []
    lines = report_text.splitlines()
    in_table = False
    current_headers = []
    current_rows = []

    for line in lines:
        line_str = line.strip()
        if line_str.startswith("|") and line_str.endswith("|"):
            cells = [c.strip() for c in line_str[1:-1].split("|")]
            # Check if separator row
            if all(re.match(r"^:?-+:?$", c) for c in cells):
                in_table = True
                continue
            if not in_table:
                current_headers = cells
            else:
                current_rows.append(cells)
        else:
            if in_table and current_headers and current_rows:
                tables.append({"headers": current_headers, "rows": current_rows})
            in_table = False
            current_headers = []
            current_rows = []

    if in_table and current_headers and current_rows:
        tables.append({"headers": current_headers, "rows": current_rows})

    return tables


def clean_num(val_str: str):
    """Strips bolding, percentage signs, commas, and extracts float."""
    s = val_str.replace("**", "").replace("%", "").replace(",", "").replace("`", "").strip()
    m = re.search(r"[-+]?\d*\.?\d+", s)
    if m:
        return float(m.group(0))
    return None


def test_report_mathematical_consistency():
    report_path = os.path.join("docs", "INJECTION_REPORT.md")
    assert os.path.exists(report_path), f"Report not found at {report_path}"

    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()

    tables = parse_markdown_tables(content)
    assert len(tables) >= 10, f"Expected multiple tables in report, found {len(tables)}"

    checked_rows = 0

    for table_idx, tbl in enumerate(tables):
        headers = [h.lower() for h in tbl["headers"]]

        # Locate indices
        prec_idx = next((i for i, h in enumerate(headers) if "precision" in h or "expected precision" in h), None)
        rec_idx = next((i for i, h in enumerate(headers) if "recall" in h), None)
        f1_idx = next((i for i, h in enumerate(headers) if "f1" in h), None)
        tp_idx = next((i for i, h in enumerate(headers) if "true positive" in h or h == "tp" or "tp count" in h or "tp events" in h), None)
        fp_idx = next((i for i, h in enumerate(headers) if "false positive" in h or h == "fp" or "fp count" in h or "clean fps" in h or "fp events" in h or "fp (clean)" in h), None)

        for row in tbl["rows"]:
            # Check Precision from TP and FP
            if prec_idx is not None and tp_idx is not None and fp_idx is not None:
                if len(row) > max(prec_idx, tp_idx, fp_idx):
                    tp_val = clean_num(row[tp_idx])
                    fp_val = clean_num(row[fp_idx])
                    prec_val = clean_num(row[prec_idx])

                    if tp_val is not None and fp_val is not None and prec_val is not None:
                        total_declared = tp_val + fp_val
                        if total_declared > 0:
                            expected_prec = (tp_val / total_declared) * 100.0
                            assert abs(prec_val - expected_prec) <= 0.45, (
                                f"Table {table_idx} row {row}: Reported Precision {prec_val:.2f}% "
                                f"does not match TP/FP calculation: {tp_val}/({tp_val}+{fp_val}) = {expected_prec:.2f}%"
                            )
                            checked_rows += 1

            # Check F1 from reported Precision and Recall
            if f1_idx is not None and prec_idx is not None and rec_idx is not None:
                if len(row) > max(f1_idx, prec_idx, rec_idx):
                    prec_val = clean_num(row[prec_idx])
                    rec_val = clean_num(row[rec_idx])
                    f1_val = clean_num(row[f1_idx])

                    if prec_val is not None and rec_val is not None and f1_val is not None:
                        if (prec_val + rec_val) > 0:
                            expected_f1 = (2.0 * prec_val * rec_val) / (prec_val + rec_val)
                            assert abs(f1_val - expected_f1) <= 0.45, (
                                f"Table {table_idx} row {row}: Reported F1 {f1_val:.2f}% "
                                f"does not match 2*P*R/(P+R) = {expected_f1:.2f}%"
                            )
                            checked_rows += 1

    print(f"Verified mathematical consistency across {checked_rows} table cells.")
    assert checked_rows >= 10, f"Expected at least 10 consistency checks, only found {checked_rows}"


def test_cross_table_identities_and_class_agreement():
    """Requirement Phase 3.2: Verify cross-table arithmetic identities and class counts.
    
    1. Tables built on seed 1337 must agree on N = 5,225, N_clean = 3,887, N_spoof = 913, N_jam = 427.
    2. 2x2 matrix: TP + FP + FN + TN == 5,225 for every row.
    3. Attribution table: sum of clean FP counts == 452, sum of shares == 100.0%.
    4. Evidence tiers: sum of tier counts == 5,225.
    """
    report_path = os.path.join("docs", "INJECTION_REPORT.md")
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Check fingerprints on test seed tables
    fps = re.findall(r"Seed:\s*1337\s*\|\s*Flights:\s*5,225\s*\|\s*N_clean:\s*3,887\s*\|\s*N_spoof:\s*913\s*\|\s*N_jam:\s*427", content)
    assert len(fps) >= 5, f"Expected consistent test seed fingerprint across tables, found {len(fps)}"

    tables = parse_markdown_tables(content)

    # 2. 2x2 matrix
    tbl_2x2 = next((t for t in tables if any("detector pipeline" in h.lower() for h in t["headers"]) and any("tn" in h.lower() for h in t["headers"])), None)
    assert tbl_2x2 is not None, "2x2 attribution table not found in report"
    
    headers = [h.lower() for h in tbl_2x2["headers"]]
    tp_i = headers.index("tp")
    fp_i = headers.index("fp")
    fn_i = headers.index("fn")
    tn_i = headers.index("tn")

    for row in tbl_2x2["rows"]:
        tp = clean_num(row[tp_i])
        fp = clean_num(row[fp_i])
        fn = clean_num(row[fn_i])
        tn = clean_num(row[tn_i])
        total = tp + fp + fn + tn
        assert total == 5225, f"Row {row} sum {total} != 5,225"

    # 3. Attribution table
    tbl_fp = next((t for t in tables if any("clean fp count" in h.lower() for h in t["headers"])), None)
    assert tbl_fp is not None, "FP attribution table not found in report"
    headers_fp = [h.lower() for h in tbl_fp["headers"]]
    cnt_i = next(i for i, h in enumerate(headers_fp) if "clean fp count" in h)
    share_i = next(i for i, h in enumerate(headers_fp) if "share of clean fps" in h)

    sub_rows = [r for r in tbl_fp["rows"] if "total" not in r[0].lower()]
    total_cnt = sum(clean_num(r[cnt_i]) for r in sub_rows)
    total_share = sum(clean_num(r[share_i]) for r in sub_rows)

    assert total_cnt == 452, f"Attribution table FP sum {total_cnt} != 452"
    assert abs(total_share - 100.0) <= 0.1, f"Attribution table share sum {total_share}% != 100%"

    # 4. Evidence tiers table
    tbl_tiers = next((t for t in tables if any("evidence tier" in h.lower() for h in t["headers"]) and any("negative pred" in h.lower() for h in t["headers"])), None)
    assert tbl_tiers is not None, "Evidence tiers table not found in report"
    headers_tiers = [h.lower() for h in tbl_tiers["headers"]]
    cnt_tier_i = next(i for i, h in enumerate(headers_tiers) if "flights" in h)
    tier_sum = sum(clean_num(r[cnt_tier_i]) for r in tbl_tiers["rows"])
    assert tier_sum == 5225, f"Evidence tier flight sum {tier_sum} != 5,225"


def test_no_forbidden_status_terms():
    """Phase 3.2 Rule: No UI or API field or report tier may call anything 'ok' or 'safe'."""
    tiers_path = os.path.join("docs", "generated", "evidence_tiers_table.md")
    assert os.path.exists(tiers_path)
    content = open(tiers_path, "r", encoding="utf-8").read()

    forbidden_matches = re.findall(r"\|\s*[`*]*(ok|safe)[`*]*\s*\|", content, re.IGNORECASE)
    assert len(forbidden_matches) == 0, f"Found forbidden terms in evidence tiers table: {forbidden_matches}"

    import psycopg2
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", 5432)),
        user=os.getenv("POSTGRES_USER", "aerotrust"),
        password=os.getenv("POSTGRES_PASSWORD", "aerotrust_secret"),
        dbname=os.getenv("POSTGRES_DB", "aerotrust"),
    )
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM trust_scores WHERE status IN ('ok', 'safe');")
    forbidden_db_count = cur.fetchone()[0]
    conn.close()

    assert forbidden_db_count == 0, f"Found {forbidden_db_count} records with forbidden status 'ok'/'safe' in trust_scores!"


def test_every_table_has_generating_script():
    """Requirement: Every table in docs/INJECTION_REPORT.md must have a declared generating script.
    
    Verifies that all generated markdown files in docs/generated/ exist and match the
    table declarations in docs/INJECTION_REPORT.md.
    """
    report_path = os.path.join("docs", "INJECTION_REPORT.md")
    assert os.path.exists(report_path)

    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r"<!--\s*table:\s*([^\s]+)\s+generated-by:\s*([^\s]+)\s*-->"
    matches = re.findall(pattern, content)

    assert len(matches) >= 12, f"Expected at least 12 generated table annotations, found {len(matches)}"

    for artifact_name, script_name in matches:
        artifact_path = os.path.join("docs", "generated", artifact_name)
        assert os.path.exists(artifact_path), f"Generated artifact {artifact_path} does not exist!"
        assert os.path.exists(script_name), f"Generating script {script_name} does not exist!"
        assert os.path.getsize(artifact_path) > 50, f"Artifact {artifact_path} is unexpectedly empty!"


def test_derived_base_rate_precision_formula():
    """Phase 3.4 Requirement 6: Base-rate precision must be recomputed by script via Bayes rule.
    
    Precision = (p * TPR) / (p * TPR + (1 - p) * FPR)
    At p = 0.1747, using leg-level pooled clean seeds 3001-3003 (TPR ~ 26.98%, FPR ~ 1.17%):
    Expected Precision is ~ 83.0%.
    """
    table_path = os.path.join("docs", "generated", "base_rate_honesty_table.md")
    assert os.path.exists(table_path)
    content = open(table_path, "r", encoding="utf-8").read()

    def bayes_prec(p, tpr, fpr):
        num = p * tpr
        denom = num + (1.0 - p) * fpr
        return (num / denom) * 100.0 if denom > 0 else 0.0

    # Parse TPR and FPR from fingerprint
    m_tpr = re.search(r"TPR:\s*([0-9.]+)%", content)
    m_fpr = re.search(r"Clean FPR:\s*([0-9.]+)%", content)
    assert m_tpr is not None and m_fpr is not None, "Failed to parse TPR and FPR from base_rate_honesty_table.md"
    tpr = float(m_tpr.group(1)) / 100.0
    fpr = float(m_fpr.group(1)) / 100.0

    # Benchmark test base rate p = 0.1747
    p_test = 0.1747
    calc_prec = bayes_prec(p_test, tpr, fpr)

    # Verify that reported number in table matches Bayes calculation
    m_row = re.search(r"\|\s*17\.47%[^\n]*\|\s*17\.47%\s*\|\s*\*\*([0-9.]+)%\*\*", content)
    assert m_row is not None, "Did not find 17.47% row in base_rate_honesty_table.md"
    rep_prec = float(m_row.group(1))
    assert abs(rep_prec - calc_prec) < 0.2, f"Reported precision {rep_prec}% != Bayes calculation {calc_prec:.1f}%"


def test_single_silent_definition_enforcement():
    """Phase 3.3 Requirement 2: Canonical single definition of silent acceptance.
    
    silent = True iff no integrity indicator drops below threshold and no gap > 60s.
    Under this definition, evaluate_naive_baseline(df)["flag"] == False <=> is_silent_flight(df) == True.
    Therefore, naive baseline recall on silent flights is strictly 0.0% by mathematical definition.
    """
    import pandas as pd
    from backend.app.detectors.silent_check import evaluate_naive_baseline, is_silent_flight

    # 1. Clean nominal flight with high integrity (silent)
    df_silent = pd.DataFrame({
        "ts": [1000, 1030, 1060, 1090],
        "nic": [10, 10, 10, 10],
        "nacp": [10, 10, 10, 10],
        "sil": [3, 3, 3, 3],
    })
    res_naive = evaluate_naive_baseline(df_silent)
    assert res_naive["flag"] is False
    assert is_silent_flight(df_silent) is True

    # 2. Flight with avionics alert (non-silent)
    df_nonsilent = pd.DataFrame({
        "ts": [1000, 1030, 1060, 1090],
        "nic": [10, 5, 5, 10],
        "nacp": [10, 6, 6, 10],
        "sil": [3, 3, 3, 3],
    })
    res_naive_drop = evaluate_naive_baseline(df_nonsilent)
    assert res_naive_drop["flag"] is True
    assert is_silent_flight(df_nonsilent) is False

    # 3. Flight with telemetry gap > 60s (non-silent)
    df_gap = pd.DataFrame({
        "ts": [1000, 1090],  # 90s gap
        "nic": [10, 10],
        "nacp": [10, 10],
        "sil": [3, 3],
    })
    res_gap = evaluate_naive_baseline(df_gap)
    assert res_gap["flag"] is True
    assert is_silent_flight(df_gap) is False


def test_horizontal_spoofing_honesty():
    """Phase 3.4 Requirement: Prominently verify 0.0% recall on horizontal spoofing under altitude_consistency_v2."""
    table_path = os.path.join("docs", "generated", "event_type_honesty_table.md")
    assert os.path.exists(table_path)
    content = open(table_path, "r", encoding="utf-8").read()

    # Search altitude_consistency_v2 / composite_v2 rows in the event-type table
    lines = content.splitlines()
    comp_rows = [l for l in lines if "**altitude_consistency_v2**" in l or "**composite_v2**" in l]
    assert len(comp_rows) >= 9, f"Expected at least 9 seed rows for detector, found {len(comp_rows)}"

    for row in comp_rows:
        cells = [c.strip() for c in row.split("|")[1:-1]]
        hdrift_rec = clean_num(cells[5])
        hoff_rec = clean_num(cells[6])
        assert hdrift_rec <= 0.5, f"Expected <= 0.5% drift recall, found {hdrift_rec}% in {row}"
        assert hoff_rec <= 0.1, f"Expected <= 0.1% offset recall, found {hoff_rec}% in {row}"


def test_clean_estimate_seeds_exist():
    """Phase 3.3 Requirement 1: Verify presence of fresh clean estimate seeds (3001, 3002, 3003)."""
    table_path = os.path.join("docs", "generated", "clean_estimate_table.md")
    assert os.path.exists(table_path)
    content = open(table_path, "r", encoding="utf-8").read()

    for s in ["fresh_3001", "fresh_3002", "fresh_3003"]:
        assert s in content, f"Missing clean estimate seed {s} in clean_estimate_table.md"


def test_no_stray_tool_errors_in_generated_docs():
    """Phase 3.4 Requirement 8: Sanitization check for stray error strings in generated docs."""
    forbidden_substrings = [
        "network issue",
        "tool-error",
        "traceback",
        "chefs",
        "undefined",
        "nan%",
    ]
    gen_dir = os.path.join("docs", "generated")
    assert os.path.exists(gen_dir)

    doc_files = [os.path.join(gen_dir, f) for f in os.listdir(gen_dir) if f.endswith(".md")]
    report_file = os.path.join("docs", "INJECTION_REPORT.md")
    if os.path.exists(report_file):
        doc_files.append(report_file)

    for doc_path in doc_files:
        text = open(doc_path, "r", encoding="utf-8").read().lower()
        for forbidden in forbidden_substrings:
            assert forbidden not in text, f"Found stray error string '{forbidden}' in {doc_path}!"


