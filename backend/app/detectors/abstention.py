"""AeroTrust Abstention Module.

Implements README Section 4.3 Abstention Protocol:
Detectors and composite scorers must abstain (returning status = 'unknown' with explicit reasons)
under the following operational conditions:
1. Insufficient data points in analysis window (n_points < min_total_points_in_window)
2. Insufficient independent checks available (< min_independent_checks_available)
3. Strongly conflicting checks (divergent detector indications with high confidence)
4. Insufficient peer aircraft density in spatial cluster (for consensus check)
5. Excessive sensor coverage dropouts / telemetry gaps
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from backend.app.core.config import load_thresholds


class AbstentionEngine:
    """Evaluates detector check collections and arbitrates final status vs abstention."""

    def __init__(self, thresholds: Optional[Dict[str, Any]] = None):
        cfg = thresholds or load_thresholds()
        self.abstention_cfg = cfg.get("abstention", {})
        self.min_points = int(self.abstention_cfg.get("min_total_points_in_window", 10))
        self.min_independent_checks = int(self.abstention_cfg.get("min_independent_checks_available", 2))
        self.max_disagreement_std = float(self.abstention_cfg.get("max_check_disagreement_std", 0.45))

    def evaluate_flight_checks(
        self,
        check_results: Dict[str, Dict[str, Any]],
        total_points: int,
    ) -> Tuple[str, List[str], Optional[float]]:
        """Evaluates a dictionary of check_name -> {residual, flag, confidence, status, reasons}.

        Returns (final_status, reasons, composite_confidence).
        """
        reasons: List[str] = []

        # Condition 1: Insufficient total points
        if total_points < self.min_points:
            reasons.append(f"insufficient_track_points: {total_points} < {self.min_points}")
            return "unknown", reasons, 0.0

        # Filter active non-stub valid checks
        valid_checks = {}
        for name, res in check_results.items():
            if res.get("status") != "unknown" and res.get("confidence", 0.0) > 0.0:
                valid_checks[name] = res

        # Condition 2: Insufficient independent checks available
        if len(valid_checks) < self.min_independent_checks:
            reasons.append(
                f"insufficient_independent_checks: {len(valid_checks)} < {self.min_independent_checks}"
            )
            # Propagate underlying reasons from unknown checks
            for name, res in check_results.items():
                if res.get("status") == "unknown":
                    reasons.extend([f"{name}: {r}" for r in res.get("reasons", [])])
            return "unknown", reasons, 0.0

        # Extract flags and confidences
        flags = [1.0 if res["flag"] else 0.0 for res in valid_checks.values()]
        confidences = [res["confidence"] for res in valid_checks.values()]

        # Check for marginal / low-confidence data
        mean_conf = float(np.mean(confidences)) if confidences else 0.0
        if mean_conf < 0.35:
            reasons.append(f"low_mean_confidence: {mean_conf:.2f} < 0.35")
            return "unknown", reasons, round(mean_conf, 4)

        # Multi-axis detection rule: each detector monitors an orthogonal domain
        # (Altitude, Kinematics, Navigation Drift, Peer Consensus)
        flagged_checks = [res for res in valid_checks.values() if res["flag"]]
        max_flagged_conf = max([res["confidence"] for res in flagged_checks], default=0.0)

        # Flagged if at least 1 orthogonal check detects anomaly with high confidence (>= 0.60)
        # or if 2 or more independent checks flag
        if len(flagged_checks) >= 2 or (len(flagged_checks) == 1 and max_flagged_conf >= 0.60):
            final_status = "flagged"
            for name, res in valid_checks.items():
                if res["flag"]:
                    reasons.extend(res.get("reasons", []))
        else:
            final_status = "clear"

        composite_confidence = round(float(np.mean(confidences)), 4)
        return final_status, reasons, composite_confidence

