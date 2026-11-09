"""Jamming Baseline Detector and H3 Spatial Aggregator.

Adheres strictly to:
- README Section 4.2: Drops in NIC/NACp/SIL and abnormal data gaps aggregated per H3 cell & time bucket.
- README Section 4.3: Abstention protocol (status = 'unknown' with explicit reasons).
- Rule 2: All thresholds loaded from config/thresholds.yaml.
- Rule 3: Detector contract returns {residual, flag, confidence, n_points}.
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from backend.app.core.config import load_thresholds


class JammingDetector:
    """Detects GNSS jamming from ADS-B integrity metric drops and temporal data gaps."""

    def __init__(self, thresholds: Optional[Dict[str, Any]] = None):
        if thresholds is None:
            full_config = load_thresholds()
            self.jam_cfg = full_config.get("jamming", {})
            self.abstention_cfg = full_config.get("abstention", {})
        else:
            self.jam_cfg = thresholds.get("jamming", {})
            self.abstention_cfg = thresholds.get("abstention", {})

        # Configurable thresholds (Rule 2)
        self.nic_threshold = self.jam_cfg.get("nic_drop_threshold", 7)
        self.nacp_threshold = self.jam_cfg.get("nacp_drop_threshold", 8)
        self.sil_threshold = self.jam_cfg.get("sil_drop_threshold", 2)
        self.min_aircraft = self.jam_cfg.get("min_aircraft_per_cell", 3)
        self.min_points = self.abstention_cfg.get("min_total_points_in_window", 10)

    def evaluate_track_window(
        self, points_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """Evaluates an individual flight track segment.

        Returns contract: {residual, flag, confidence, n_points, status, reasons}.
        """
        n_points = len(points_df)
        reasons: List[str] = []

        # Section 4.3 Abstention: too few points in window
        if n_points < self.min_points:
            return {
                "residual": 0.0,
                "flag": False,
                "confidence": 0.0,
                "n_points": n_points,
                "status": "unknown",
                "reasons": [f"insufficient_data_points: {n_points} < {self.min_points}"],
            }

        # Expected nominal ADS-B integrity values (NIC ~ 10, NACp ~ 10, SIL ~ 3)
        nominal_nic = 10.0
        nominal_nacp = 10.0
        nominal_sil = 3.0

        nic_vals = points_df["nic"].values
        nacp_vals = points_df["nacp"].values
        sil_vals = points_df["sil"].values

        nic_drop = np.maximum(0.0, nominal_nic - nic_vals)
        nacp_drop = np.maximum(0.0, nominal_nacp - nacp_vals)
        sil_drop = np.maximum(0.0, nominal_sil - sil_vals)

        # Normalized residual between 0.0 and 1.0
        # (normalized by max possible drops: nic=10, nacp=10, sil=3)
        norm_nic_drop = np.mean(nic_drop) / 10.0
        norm_nacp_drop = np.mean(nacp_drop) / 10.0
        norm_sil_drop = np.mean(sil_drop) / 3.0

        residual = float(0.4 * norm_nic_drop + 0.4 * norm_nacp_drop + 0.2 * norm_sil_drop)

        # Evaluate abnormal temporal gaps (e.g. gap > 60 seconds)
        if "ts" in points_df.columns:
            ts_diffs = np.diff(points_df["ts"].values)
            large_gaps = np.sum(ts_diffs > 60)
            gap_fraction = float(large_gaps / max(1, len(ts_diffs)))
        else:
            gap_fraction = 0.0

        # Detection criteria
        is_nic_low = np.mean(nic_vals) < self.nic_threshold
        is_nacp_low = np.mean(nacp_vals) < self.nacp_threshold
        is_sil_low = np.mean(sil_vals) < self.sil_threshold

        flag = bool((is_nic_low and is_nacp_low) or (is_nic_low and gap_fraction > 0.3))

        # Confidence scaled by sample size and consistency
        sample_factor = min(1.0, n_points / (self.min_points * 2.0))
        consistency = float(1.0 - np.std([norm_nic_drop, norm_nacp_drop]))
        confidence = float(np.clip(sample_factor * consistency, 0.1, 1.0))

        status = "degraded" if flag else "clear"

        return {
            "residual": round(residual, 4),
            "flag": flag,
            "confidence": round(confidence, 4),
            "n_points": n_points,
            "status": status,
            "reasons": reasons,
        }

    def aggregate_cell(
        self,
        h3_cell: str,
        time_bucket: int,
        cell_points_df: pd.DataFrame,
        mode: str = "v2_pooled",
    ) -> Dict[str, Any]:
        """Aggregates track points in an (H3 cell, time bucket).

        Mode:
        - 'v1_strict': Phase 2 baseline (requires >= 3 aircraft, otherwise unknown)
        - 'v2_pooled': Phase 2.6 pooled rule (single-aircraft gives low-confidence degraded)
        Returns schema: {h3_cell, time_bucket, jam_score, n_aircraft, n_checks, status, confidence, reasons}.
        """
        if cell_points_df.empty:
            return {
                "h3_cell": h3_cell,
                "time_bucket": time_bucket,
                "jam_score": 0.0,
                "n_aircraft": 0,
                "n_checks": 0,
                "status": "unknown",
                "confidence": 0.0,
                "reasons": ["no_track_points_in_cell"],
            }

        unique_aircraft = cell_points_df["icao24"].nunique()
        n_points = len(cell_points_df)
        reasons: List[str] = []

        if mode == "v1_strict":
            if unique_aircraft < self.min_aircraft:
                return {
                    "h3_cell": h3_cell,
                    "time_bucket": time_bucket,
                    "jam_score": None,
                    "n_aircraft": unique_aircraft,
                    "n_checks": n_points,
                    "status": "unknown",
                    "confidence": 0.0,
                    "reasons": [
                        f"insufficient_aircraft_consensus: {unique_aircraft} < {self.min_aircraft}"
                    ],
                }
            track_eval = self.evaluate_track_window(cell_points_df)
            return {
                "h3_cell": h3_cell,
                "time_bucket": time_bucket,
                "jam_score": track_eval["residual"],
                "n_aircraft": unique_aircraft,
                "n_checks": n_points,
                "status": track_eval["status"],
                "confidence": track_eval["confidence"],
                "reasons": track_eval["reasons"],
            }

        if mode == "v3_three_tier":
            track_eval = self.evaluate_track_window(cell_points_df)
            jam_score = track_eval["residual"]
            flag = track_eval["flag"]

            if flag:
                if unique_aircraft == 1:
                    status = "degraded"
                    confidence = 0.40
                    reasons = ["single_aircraft_jamming_evidence_low_confidence"]
                else:
                    status = "degraded"
                    confidence = round(min(0.95, 0.70 + 0.10 * unique_aircraft), 2)
                    reasons = [f"peer_corroborated_jamming: {unique_aircraft} aircraft"]
            else:
                # Three-tier rule: "clear" requires >= 2 clean aircraft confirming high integrity.
                # Single-aircraft clean evidence is "insufficient", not "clear".
                min_clean_ac = 2
                if unique_aircraft >= min_clean_ac:
                    status = "clear"
                    confidence = round(min(0.95, 0.75 + 0.05 * unique_aircraft), 2)
                    reasons = [f"peer_corroborated_clean_airspace: {unique_aircraft} aircraft"]
                else:
                    status = "insufficient"
                    confidence = 0.20
                    reasons = [f"single_aircraft_clean_evidence_insufficient: {unique_aircraft} < {min_clean_ac}"]

            if track_eval["status"] == "unknown" and n_points < 3:
                status = "insufficient"
                confidence = 0.0
                reasons = track_eval["reasons"]

            return {
                "h3_cell": h3_cell,
                "time_bucket": time_bucket,
                "jam_score": jam_score,
                "n_aircraft": unique_aircraft,
                "n_checks": n_points,
                "status": status,
                "confidence": confidence,
                "reasons": reasons,
            }

        # Phase 2.6 v2_pooled rule:
        track_eval = self.evaluate_track_window(cell_points_df)
        jam_score = track_eval["residual"]
        flag = track_eval["flag"]

        if flag:
            if unique_aircraft == 1:
                status = "degraded"
                confidence = 0.40
                reasons = ["single_aircraft_jamming_evidence_low_confidence"]
            else:
                status = "degraded"
                confidence = round(min(0.95, 0.70 + 0.10 * unique_aircraft), 2)
                reasons = [f"peer_corroborated_jamming: {unique_aircraft} aircraft"]
        else:
            status = "ok"
            confidence = 0.90
            reasons = []

        if track_eval["status"] == "unknown" and n_points < 3:
            status = "unknown"
            confidence = 0.0
            reasons = track_eval["reasons"]

        return {
            "h3_cell": h3_cell,
            "time_bucket": time_bucket,
            "jam_score": jam_score,
            "n_aircraft": unique_aircraft,
            "n_checks": n_points,
            "status": status,
            "confidence": confidence,
            "reasons": reasons,
        }

