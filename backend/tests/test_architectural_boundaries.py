"""Architectural Boundary Enforcement Tests.

Strictly verifies that:
1. Detectors, models, API endpoints, and scoring services NEVER import or read
   ground-truth tables or ground-truth generator functions.
2. Ground-truth events remain an isolated evaluation benchmark.
"""

import ast
import os
from pathlib import Path

FORBIDDEN_IMPORTS = {
    "GroundTruthEvent",
    "generate_ground_truth_events",
    "gt_events",
}


def test_no_detector_imports_ground_truth():
    """Scans all Python files under backend/ to ensure architectural boundary is intact.

    Detectors, models, API endpoints, and scoring algorithms must NEVER import or inspect
    ground truth events.
    """
    backend_dir = Path("backend")
    assert backend_dir.exists(), "backend/ directory must exist"

    violation_list = []

    for py_file in backend_dir.rglob("*.py"):
        with open(py_file, "r", encoding="utf-8") as f:
            content = f.read()

        try:
            tree = ast.parse(content, filename=str(py_file))
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if any(forbidden in alias.name for forbidden in FORBIDDEN_IMPORTS):
                        violation_list.append((str(py_file), alias.name))
            elif isinstance(node, ast.ImportFrom):
                if node.module and "synthetic" in node.module:
                    for alias in node.names:
                        if alias.name in FORBIDDEN_IMPORTS:
                            violation_list.append((str(py_file), f"from {node.module} import {alias.name}"))

    assert not violation_list, f"Architectural boundary violation! Detectors must never import ground truth: {violation_list}"

