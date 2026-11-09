"""AeroTrust Two-Axis Trust Score Engine (Phase 3.3 & 3.4).

Computes integrated flight data integrity along two orthogonal axes:
- Axis A: Hostile RF Interference (Calibrated probability from composite_v2 = a OR d,
          with b and c as supporting reasons, plus 3-tier jamming status).
- Axis B: Natural Radiation Exposure (Relative radiation exposure in discrete bins:
          low, moderate, elevated, reported separately).

Rule-based overall status: {ok, degraded, unknown} with explicit human-readable reasons.
Never mixes radiation index into a fake probability.
Strict abstention arbitration when peer density or sensor data is insufficient.
"""

import json
import math
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import yaml


class TrustScoreEngine:
    """Evaluates multi-axis flight trust and generates deterministic integrity assessments."""

    def __init__(
        self,
        config_path: str = "config/thresholds.yaml",
        calibration_path: str = "config/calibration_models.json",
    ):
        # Load thresholds
        cfg_file = Path(config_path)
        if not cfg_file.is_absolute():
            root = Path(__file__).resolve().parents[3]
            cfg_file = root / config_path
            if not cfg_file.exists():
                cfg_file = Path(config_path)
        with open(cfg_file, "r", encoding="utf-8") as f:
            self.thresholds = yaml.safe_load(f)

        # Load calibration parameters (fitted on dev seed 42)
        cal_file = Path(calibration_path)
        if not cal_file.is_absolute():
            root = Path(__file__).resolve().parents[3]
            cal_file = root / calibration_path
            if not cal_file.exists():
                cal_file = Path(calibration_path)
        with open(cal_file, "r", encoding="utf-8") as f:
            self.calibration = json.load(f)

        self.w_comp = float(self.calibration.get("composite", {}).get("w", 3.20))
        self.b_comp = float(self.calibration.get("composite", {}).get("b", -1.50))

    def evaluate_axis_a(
        self,
        checks: Dict[str, Dict[str, Any]],
        jamming_status: str = "clear",
        jamming_confidence: float = 0.80,
    ) -> Dict[str, Any]:
        """Evaluates Axis A: Hostile RF Interference.

        Primary triggers: Check a (Geo-Baro Alt) OR Check d (Multi-Aircraft Consensus).
        Supporting checks: Check b (Kinematics) & Check c (Pos-Vel Consistency).
        """
        chk_a = checks.get("geo_baro_alt", {})
        chk_b = checks.get("kinematic_feasibility", {})
        chk_c = checks.get("pos_vel_consistency", {})
        chk_d = checks.get("multi_aircraft_consensus", {})

        flag_a = bool(chk_a.get("flag", False))
        flag_d = bool(chk_d.get("flag", False))
        conf_a = float(chk_a.get("confidence", 0.0))
        conf_d = float(chk_d.get("confidence", 0.0))

        flag_b = bool(chk_b.get("flag", False))
        flag_c = bool(chk_c.get("flag", False))

        # Composite v2 Primary Trigger: (a OR d)
        primary_triggered = flag_a or flag_d
        primary_triggers = []
        if flag_a:
            primary_triggers.append("geo_baro_alt_anomaly")
        if flag_d:
            primary_triggers.append("multi_aircraft_consensus_anomaly")

        # Supporting reasons from checks b and c
        supporting_reasons = []
        if flag_b:
            supporting_reasons.append("kinematic_feasibility_supporting_deviation")
        if flag_c:
            supporting_reasons.append("pos_vel_consistency_supporting_drift")

        # Isotonic piecewise calibration for Composite v2 (fitted on dev seed 42)
        raw_evidence = max(conf_a if flag_a else 0.0, conf_d if flag_d else 0.0)
        iso_data = self.calibration.get("composite_v2_isotonic")
        if iso_data and "x_thresholds" in iso_data and "y_calibrated" in iso_data:
            calibrated_prob = float(
                np.interp(raw_evidence, iso_data["x_thresholds"], iso_data["y_calibrated"])
            )
        else:
            calibrated_prob = float(1.0 / (1.0 + np.exp(-(self.w_comp * raw_evidence + self.b_comp))))

        # Adjust for jamming tier
        is_jam_degraded = (jamming_status == "degraded")
        if is_jam_degraded:
            primary_triggers.append("corroborated_jamming_environment")
            calibrated_prob = max(calibrated_prob, 0.75)

        axis_a_status = "degraded" if (primary_triggered or is_jam_degraded) else "clear"

        return {
            "status": axis_a_status,
            "calibrated_prob": round(calibrated_prob, 4),
            "confidence": round(1.0 - calibrated_prob if axis_a_status == "clear" else calibrated_prob, 4),
            "primary_triggered": primary_triggered,
            "primary_triggers": primary_triggers,
            "supporting_reasons": supporting_reasons,
            "jamming_status": jamming_status,
            "jamming_confidence": round(jamming_confidence, 2),
        }

    def evaluate_axis_b(
        self,
        radiation_summary: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Evaluates Axis B: Natural Space Radiation Exposure.

        Reported strictly in discrete operational tiers: {low, moderate, elevated}.
        Never expressed as a probability.
        """
        if not radiation_summary:
            return {
                "level": "low",
                "relative_index": 1.0,
                "notes": "nominal_standard_atmosphere",
            }

        level = radiation_summary.get("level", "low")
        rel_index = float(radiation_summary.get("relative_index", 1.0))
        return {
            "level": level,
            "relative_index": round(rel_index, 3),
            "components": radiation_summary.get("components", {}),
        }

    def evaluate_overall_flight(
        self,
        flight_id: str,
        segment_start: int,
        segment_end: int,
        checks: Dict[str, Dict[str, Any]],
        total_points: int,
        jamming_status: str = "clear",
        jamming_confidence: float = 0.80,
        radiation_summary: Optional[Dict[str, Any]] = None,
        peer_support_ratio: float = 1.0,
    ) -> Dict[str, Any]:
        """Synthesizes Two-Axis assessment into evidence tiers:
        - assured_clear: >= 2 independent usable checks and peer support (>= 50% windows), none fired
        - no_alert: no check fired but evidence is partial (single aircraft / sparse airspace, or single check)
        - degraded: hostile interference detected (primary check a/d or degraded jamming)
        - insufficient: points < 5 or insufficient telemetry
        - unknown: conflicting sensor evidence or unresolvable ambiguity
        """
        reasons: List[str] = []

        # 1. Telemetry sufficiency check
        if total_points < 5:
            return {
                "flight_id": flight_id,
                "segment_start": segment_start,
                "segment_end": segment_end,
                "score": None,
                "uncertainty": 1.0,
                "status": "insufficient",
                "reasons": ["insufficient_telemetry_points"],
                "axis_a": {"status": "insufficient", "calibrated_prob": None},
                "axis_b": self.evaluate_axis_b(radiation_summary),
            }

        # 2. Evaluate Axis A
        axis_a = self.evaluate_axis_a(checks, jamming_status, jamming_confidence)

        # 3. Evaluate Axis B
        axis_b = self.evaluate_axis_b(radiation_summary)

        # 4. Check for abstention / unknown triggers
        chk_d = checks.get("multi_aircraft_consensus", {})
        chk_a = checks.get("geo_baro_alt", {})
        chk_b = checks.get("kinematic_feasibility", {})
        chk_c = checks.get("pos_vel_consistency", {})
        is_consensus_unknown = (chk_d.get("status") == "unknown")
        is_jam_insufficient = (jamming_status == "insufficient")

        # Conflict check: Check a flags with high confidence, but consensus confirms nominal peers with high confidence
        if chk_a.get("flag") and chk_d.get("flag") is False and chk_d.get("confidence", 0.0) >= 0.80:
            reasons.append("conflicting_sensor_evidence: barometric deviation uncorroborated by peers")
            return {
                "flight_id": flight_id,
                "segment_start": segment_start,
                "segment_end": segment_end,
                "score": None,
                "uncertainty": 0.85,
                "status": "unknown",
                "reasons": reasons,
                "axis_a": axis_a,
                "axis_b": axis_b,
            }

        # Sparse traffic abstention: low density in off-corridor airspace when checks are uncertain
        if is_jam_insufficient and is_consensus_unknown and not axis_a["primary_triggered"]:
            # Single aircraft in sparse airspace with partial evidence
            reasons.append("insufficient_peer_density: single aircraft in sparse airspace")
            return {
                "flight_id": flight_id,
                "segment_start": segment_start,
                "segment_end": segment_end,
                "score": round(1.0 - axis_a["calibrated_prob"], 4),
                "uncertainty": 0.70,
                "status": "no_alert",
                "reasons": reasons,
                "axis_a": axis_a,
                "axis_b": axis_b,
            }

        # 5. Determine Overall Status {degraded, assured_clear, no_alert}
        if axis_a["status"] == "degraded":
            final_status = "degraded"
            reasons.extend(axis_a["primary_triggers"])
            reasons.extend(axis_a["supporting_reasons"])
            if axis_b["level"] == "elevated":
                reasons.append("elevated_space_radiation_exposure")
            score = round(1.0 - axis_a["calibrated_prob"], 4)
            uncertainty = round(axis_a["calibrated_prob"], 4)
        else:
            # Check evidence completeness
            usable_checks = [
                c for c in [chk_a, chk_b, chk_c, chk_d]
                if c.get("status") not in ["unknown", "insufficient", None]
            ]
            has_peer_support = (peer_support_ratio >= 0.50) and not is_consensus_unknown

            if len(usable_checks) >= 2 and has_peer_support:
                final_status = "assured_clear"
                reasons.append("corroborated_nominal_integrity_multi_check")
            else:
                final_status = "no_alert"
                if not has_peer_support:
                    reasons.append("no_alert: partial_evidence_lacking_peer_support")
                else:
                    reasons.append("no_alert: partial_evidence_single_usable_check")

            if axis_b["level"] == "elevated":
                reasons.append("notice: elevated_space_radiation_exposure_nominal_rf")
            score = round(1.0 - axis_a["calibrated_prob"], 4)
            uncertainty = round(axis_a["calibrated_prob"], 4)

        return {
            "flight_id": flight_id,
            "segment_start": segment_start,
            "segment_end": segment_end,
            "score": score,
            "uncertainty": uncertainty,
            "status": final_status,
            "reasons": reasons,
            "axis_a": axis_a,
            "axis_b": axis_b,
        }

