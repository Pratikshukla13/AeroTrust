"""Pytest Configuration and Path Setup."""

import sys
from pathlib import Path

# Add project root to sys.path
root_path = Path(__file__).resolve().parents[2]
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

