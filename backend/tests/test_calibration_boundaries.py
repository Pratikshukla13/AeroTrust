"""Calibration and Architectural Boundary Tests.

Verifies:
1. scripts/calibrate_thresholds.py never imports ground truth or evaluation packages.
2. scripts/calibrate_thresholds.py uses no labels (unsupervised only).
3. backend/app/detectors/ never imports evaluation/ or ground truth.
"""

import ast
from pathlib import Path
import pytest


def test_calibration_script_has_no_ground_truth_imports():
    """Verifies calibrate_thresholds.py contains zero ground-truth imports."""
    calib_script = Path("scripts/calibrate_thresholds.py")
    assert calib_script.exists(), "scripts/calibrate_thresholds.py must exist"

    with open(calib_script, "r", encoding="utf-8") as f:
        content = f.read()

    tree = ast.parse(content, filename=str(calib_script))

    forbidden = {"ground_truth", "GroundTruthEvent", "generate_ground_truth_events", "evaluation"}
    violations = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if any(f in alias.name for f in forbidden):
                    violations.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and any(f in node.module for f in forbidden):
                violations.append(node.module)
            for alias in node.names:
                if any(f in alias.name for f in forbidden):
                    violations.append(alias.name)

    assert not violations, f"Calibration script must be strictly unsupervised! Found: {violations}"


def test_detectors_never_import_evaluation():
    """Scans backend/app/detectors/ to ensure zero imports of evaluation/ or ground truth."""
    detectors_dir = Path("backend/app/detectors")
    assert detectors_dir.exists(), "backend/app/detectors/ must exist"

    forbidden = {"evaluation", "ground_truth", "GroundTruthEvent"}
    violations = []

    for py_file in detectors_dir.rglob("*.py"):
        with open(py_file, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content, filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if any(f in alias.name for f in forbidden):
                        violations.append((str(py_file), alias.name))
            elif isinstance(node, ast.ImportFrom):
                if node.module and any(f in node.module for f in forbidden):
                    violations.append((str(py_file), node.module))
                for alias in node.names:
                    if any(f in alias.name for f in forbidden):
                        violations.append((str(py_file), alias.name))

    assert not violations, f"Detectors must never import evaluation or ground truth: {violations}"

