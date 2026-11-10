"""
backend/tests/test_claims_table_consistency.py

Verifies that every single number reported in the README claims table
and in the PDF summary table appears in at least one docs/generated/ table.
Fails otherwise (zero hand-typed or fabricated numbers permitted).
"""

import re
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS_GEN = REPO_ROOT / "docs" / "generated"
README_PATH = REPO_ROOT / "README.md"
PDF_HTML_PATH = DOCS_GEN / "claims_table.html"


def load_generated_corpus() -> str:
    """Concatenates all markdown files in docs/generated/ into a single corpus."""
    texts = []
    for md_file in sorted(DOCS_GEN.glob("*.md")):
        texts.append(md_file.read_text(encoding="utf-8"))
    return "\n".join(texts)


def extract_numbers_from_text(text: str) -> list[str]:
    """Extracts numeric values, percentages, and counts from table text.
    
    Ignores markdown footnote links, file extensions, and HTML tags.
    """
    # Remove file paths and URLs to avoid testing path numbers (like 3001 in paths)
    cleaned = re.sub(r"file:///[^\s\)]+", "", text)
    cleaned = re.sub(r"https?://[^\s\)]+", "", cleaned)
    cleaned = re.sub(r"<[^>]+>", "", cleaned)
    cleaned = re.sub(r"docs/generated/[a-zA-Z0-9_\.]+", "", cleaned)

    # Find numbers with optional decimals and %
    # Matches patterns like: 26.98%, 25.77%, 5,014, 18,000, 44, 0.01%, 83.0%, etc.
    raw_tokens = re.findall(r"\b\d+(?:,\d{3})*(?:\.\d+)?%?", cleaned)

    numbers = []
    for tok in raw_tokens:
        tok_clean = tok.strip()
        if not tok_clean:
            continue
        # Skip markdown table column indices or single-digit bullet points if any
        numbers.append(tok_clean)

    return numbers


def test_readme_claims_table_numbers_appear_in_docs_generated():
    """Every number in the README Claims and Evidence table must exist in docs/generated/."""
    corpus = load_generated_corpus()
    readme_text = README_PATH.read_text(encoding="utf-8")

    # Extract claims table section
    match = re.search(r"## Claims and Evidence\s*\n\n(.*?)(?=\n\n---)", readme_text, re.DOTALL)
    assert match is not None, "Claims and Evidence section not found in README.md"
    claims_table_text = match.group(1)

    numbers = extract_numbers_from_text(claims_table_text)
    assert len(numbers) > 10, f"Expected multiple numbers in claims table, found {len(numbers)}"

    missing = []
    for num in numbers:
        # Check both raw form (with comma/percent) and unformatted form
        clean_num = num.replace(",", "")
        if num in corpus or clean_num in corpus:
            continue
        missing.append(num)

    assert not missing, f"The following numbers in README claims table do not appear in docs/generated/: {missing}"


def test_pdf_table_numbers_appear_in_docs_generated():
    """Every number in the PDF HTML claims table must exist in docs/generated/."""
    corpus = load_generated_corpus()
    assert PDF_HTML_PATH.exists(), f"PDF HTML claims table missing at {PDF_HTML_PATH}"
    pdf_text = PDF_HTML_PATH.read_text(encoding="utf-8")

    numbers = extract_numbers_from_text(pdf_text)
    assert len(numbers) > 10, f"Expected multiple numbers in PDF table, found {len(numbers)}"

    missing = []
    for num in numbers:
        clean_num = num.replace(",", "")
        if num in corpus or clean_num in corpus:
            continue
        missing.append(num)

    assert not missing, f"The following numbers in PDF claims table do not appear in docs/generated/: {missing}"


def test_required_claims_rows_and_headers_present():
    """Verifies that all 6 required rows (a-f) and updated headers are present."""
    readme_text = README_PATH.read_text(encoding="utf-8")
    assert "Verified Metric" not in readme_text, "Old header 'Verified Metric' must be removed from README"
    assert "Reported value (synthetic data)" in readme_text, "Header 'Reported value (synthetic data)' required in README"
    assert "Unit and seeds" in readme_text, "Header 'Unit and seeds' required in README"
    assert "Source table" in readme_text, "Header 'Source table' required in README"

    # Row checks
    assert "Recall on all spoofed legs (pooled)" in readme_text, "Row (a) required"
    assert "Recall by attack type" in readme_text, "Row (b) required"
    assert "Observed leg-level precision per seed" in readme_text, "Row (c) required"
    assert "Expected precision at assumed threat prevalence (derived, assumed prevalence)" in readme_text, "Row (d) required"
    assert "Clean false positives per seed (v0.3.2 reproduced counts)" in readme_text, "Row (e) required"
    assert "Suppression and inactive/demo capabilities" in readme_text, "Row (f) required"

    # Check 42 to 52 removed
    assert "42 to 52 per seed" not in readme_text, "Superseded '42 to 52' range must be removed"

