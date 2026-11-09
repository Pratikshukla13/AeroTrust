"""AeroTrust Core Configuration Loader."""

import os
from pathlib import Path
from typing import Any, Dict

import yaml
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    DATA_MODE: str = "SYNTHETIC"  # SYNTHETIC or REAL
    CONFIG_PATH: str = "config/thresholds.yaml"
    SYNTHETIC_CONFIG_PATH: str = "config/synthetic.yaml"

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }


settings = Settings()


def load_thresholds(path: str = settings.CONFIG_PATH) -> Dict[str, Any]:
    """Loads centrally parameterized thresholds per Rule 2."""
    resolved_path = Path(path)
    if not resolved_path.exists():
        # Fallback relative to project root
        resolved_path = Path(__file__).resolve().parents[3] / path
    with open(resolved_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_synthetic_config(path: str = settings.SYNTHETIC_CONFIG_PATH) -> Dict[str, Any]:
    """Loads synthetic world configuration."""
    resolved_path = Path(path)
    if not resolved_path.exists():
        resolved_path = Path(__file__).resolve().parents[3] / path
    with open(resolved_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
