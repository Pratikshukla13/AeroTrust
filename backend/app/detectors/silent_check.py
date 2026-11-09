"""AeroTrust Centralized Silent Acceptance Definition (Phase 3.3).

Adheres to Phase 3.3 Requirement 2:
Single canonical definition of silent spoofing:
- silent = True if and only if NO integrity indicator (NIC, NACp, SIL) crosses
  the naive baseline thresholds and there is no telemetry gap during the spoofing window.
- The generator manifest, the naive baseline, and the evaluation framework all call this function.
- By definition, the naive baseline's recall on silent flights is exactly 0.0%.

Also defines `nic_high`:
- nic_high = True if average NIC >= 7 during the flight window (legacy metric).
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd


# Canonical naive baseline thresholds from config/thresholds.yaml
NAIVE_NIC_THRESHOLD = 8   # Flags if NIC < 8
NAIVE_NACP_THRESHOLD = 8  # Flags if NACp < 8
NAIVE_SIL_THRESHOLD = 2   # Flags if SIL < 2
NAIVE_MAX_GAP_SEC = 60.0  # Flags if telemetry gap > 60 seconds


def evaluate_naive_baseline(
    points_df: pd.DataFrame,
    start_ts: Optional[int] = None,
    end_ts: Optional[int] = None,
) -> Dict[str, Any]:
    """Evaluates the flags-only naive baseline on ADS-B integrity indicators and gaps.
    
    Flags True if ANY integrity indicator drops below threshold or if a gap occurs.
    """
    if points_df.empty:
        return {"flag": False, "reasons": ["empty_trajectory"]}

    df = points_df
    if start_ts is not None and end_ts is not None:
        df = df[(df["ts"] >= start_ts) & (df["ts"] <= end_ts)]
        if df.empty:
            return {"flag": False, "reasons": ["no_points_in_window"]}

    min_nic = int(df["nic"].min()) if "nic" in df.columns else 11
    min_nacp = int(df["nacp"].min()) if "nacp" in df.columns else 11
    min_sil = int(df["sil"].min()) if "sil" in df.columns else 3

    ts_arr = df["ts"].values
    max_gap = float(np.max(np.diff(ts_arr))) if len(ts_arr) > 1 else 0.0

    flagged_reasons = []
    if min_nic < NAIVE_NIC_THRESHOLD:
        flagged_reasons.append(f"nic_drop: {min_nic} < {NAIVE_NIC_THRESHOLD}")
    if min_nacp < NAIVE_NACP_THRESHOLD:
        flagged_reasons.append(f"nacp_drop: {min_nacp} < {NAIVE_NACP_THRESHOLD}")
    if min_sil < NAIVE_SIL_THRESHOLD:
        flagged_reasons.append(f"sil_drop: {min_sil} < {NAIVE_SIL_THRESHOLD}")
    if max_gap > NAIVE_MAX_GAP_SEC:
        flagged_reasons.append(f"telemetry_gap: {max_gap:.1f}s > {NAIVE_MAX_GAP_SEC}s")

    is_flagged = len(flagged_reasons) > 0
    return {
        "flag": is_flagged,
        "min_nic": min_nic,
        "min_nacp": min_nacp,
        "min_sil": min_sil,
        "max_gap_sec": max_gap,
        "reasons": flagged_reasons,
    }


def is_silent_flight(
    points_df: pd.DataFrame,
    inj_start_ts: Optional[int] = None,
    inj_end_ts: Optional[int] = None,
) -> bool:
    """Canonical Single Definition of Silent Acceptance.
    
    silent = True if and only if NO integrity indicator (NIC, NACp, SIL) crosses
    the naive baseline thresholds and there is no gap during the spoofing window.
    
    By construction, evaluate_naive_baseline(df)["flag"] == False <=> is_silent_flight(df) == True.
    """
    res = evaluate_naive_baseline(points_df, start_ts=inj_start_ts, end_ts=inj_end_ts)
    return not res["flag"]


def is_nic_high(
    points_df: pd.DataFrame,
    start_ts: Optional[int] = None,
    end_ts: Optional[int] = None,
    threshold: float = 7.0,
) -> bool:
    """Legacy secondary metric: tracks maintain high average navigational integrity."""
    df = points_df
    if start_ts is not None and end_ts is not None:
        df = df[(df["ts"] >= start_ts) & (df["ts"] <= end_ts)]
    if df.empty or "nic" not in df.columns:
        return False
    return bool(np.mean(df["nic"].values >= threshold) > 0.5)

