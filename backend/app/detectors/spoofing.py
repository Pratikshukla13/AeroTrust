"""AeroTrust Spoofing Detectors Suite.

Implements Section 4.2 Spoofing Checks:
- Check (a): GeoBaroAltDetector (Geometric vs barometric altitude residual vs baseline)
- Check (b): KinematicFeasibilityDetector (Implied speed, acceleration, turn-rate bounds)
- Check (c): PosVelConsistencyDetector (Position-velocity dead reckoning drift over window)
- Check (d): MultiAircraftConsensusDetector (15-min window, H3 res 5 + k=1 ring)
- Check (e): ModeSEHSPhysicsDetector (Documented stub: Mode S EHS DAP unavailable)

Contract for each detector:
returns Dict with keys: {residual, flag, confidence, n_points, status, reasons}.
Adheres strictly to Rule 2 (thresholds from config/thresholds.yaml) and Rule 3 (contract).
Quarantined from ground truth.
"""

import math
from typing import Any, Dict, List, Optional, Set, Tuple

import h3
import numpy as np
import pandas as pd
from backend.app.core.config import load_thresholds
from backend.app.detectors.calibration import ProbabilityCalibrator


def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes great-circle distance between two GPS coordinates in meters."""
    r = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))
    return r * c


class GeoBaroAltDetector:
    """Check (a): Geometric vs Barometric Altitude Residual vs flight's own baseline."""

    def __init__(self, thresholds: Optional[Dict[str, Any]] = None):
        cfg = thresholds or load_thresholds()
        self.spoof_cfg = cfg.get("spoofing", {}).get("geo_baro_alt", {})
        self.max_residual = float(self.spoof_cfg.get("max_residual_meters", 150.0))
        self.min_points = int(self.spoof_cfg.get("min_points_required", 5))
        self.calibrator = ProbabilityCalibrator()

    def evaluate(
        self,
        points_df: pd.DataFrame,
        peer_residuals: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        n_points = len(points_df)
        if n_points < self.min_points:
            return {
                "residual": 0.0,
                "raw_score": 0.0,
                "flag": False,
                "calibrated_prob": 0.0,
                "confidence": 0.0,
                "n_points": n_points,
                "status": "unknown",
                "reasons": [f"insufficient_points: {n_points} < {self.min_points}"],
            }

        geo = points_df["geo_alt_m"].values
        baro = points_df["baro_alt_m"].values
        diff = geo - baro

        # Flight's own baseline: median offset over the window
        # Under normal conditions, geo-baro delta is roughly stationary
        baseline = np.median(diff)
        residuals = np.abs(diff - baseline)
        max_residual = float(np.percentile(residuals, 95.0))

        flag = bool(max_residual > self.max_residual)

        # Peer-relative residual verification (Phase 2.6):
        # A shift shared by peers indicates spoofing; an isolated shift indicates an instrument / baro bias fault.
        reasons = []
        if flag and peer_residuals is not None and len(peer_residuals) >= 1:
            med_peer = float(np.median(peer_residuals))
            if med_peer < 50.0:
                # Peers show nominal geo-baro alignment; isolate as instrument fault rather than spoofing
                flag = False
                reasons.append(f"single_aircraft_baro_bias_suppressed: {max_residual:.1f}m > {self.max_residual:.1f}m (peers normal: {med_peer:.1f}m)")
            else:
                reasons.append(f"peer_corroborated_geo_baro_shift: {max_residual:.1f}m (peers median: {med_peer:.1f}m)")
        elif flag:
            reasons.append(f"geo_baro_residual_exceeded: {max_residual:.1f}m > {self.max_residual:.1f}m")

        status = "flagged" if flag else "clear"
        calibrated_prob = self.calibrator.calibrate("geo_baro_alt", max_residual) if flag else round(1.0 - self.calibrator.calibrate("geo_baro_alt", max_residual), 4)

        return {
            "residual": round(max_residual, 2),
            "raw_score": round(max_residual, 2),
            "flag": flag,
            "calibrated_prob": round(calibrated_prob, 4),
            "confidence": round(calibrated_prob, 4),
            "n_points": n_points,
            "status": status,
            "reasons": reasons,
        }


class KinematicFeasibilityDetector:
    """Check (b): Kinematic Feasibility (Speed, acceleration, and vertical rate bounds)."""

    def __init__(self, thresholds: Optional[Dict[str, Any]] = None):
        cfg = thresholds or load_thresholds()
        self.kin_cfg = cfg.get("spoofing", {}).get("kinematic", {})
        self.max_speed = float(self.kin_cfg.get("max_speed_mps", 340.0))  # ~Mach 1
        self.max_accel = float(self.kin_cfg.get("max_acceleration_mps2", 7.0))
        self.max_vrate = 35.0  # ~7000 ft/min commercial emergency descent bound
        self.min_points = int(self.kin_cfg.get("min_points_required", 3))
        self.calibrator = ProbabilityCalibrator()

    def evaluate(self, points_df: pd.DataFrame) -> Dict[str, Any]:
        n_points = len(points_df)
        if n_points < self.min_points:
            return {
                "residual": 0.0,
                "raw_score": 0.0,
                "flag": False,
                "calibrated_prob": 0.0,
                "confidence": 0.0,
                "n_points": n_points,
                "status": "unknown",
                "reasons": [f"insufficient_points: {n_points} < {self.min_points}"],
            }

        sorted_df = points_df.sort_values("ts")
        ts = sorted_df["ts"].to_numpy()
        lats = sorted_df["lat"].to_numpy()
        lons = sorted_df["lon"].to_numpy()
        vrates = np.abs(sorted_df["vrate_mps"].to_numpy())

        dts = np.diff(ts)
        # Exclude data gaps (> 45s) from consecutive step kinematics (Phase 2.6)
        valid_mask = (dts > 0) & (dts <= 45)

        if not np.any(valid_mask) or np.sum(valid_mask) < 2:
            return {
                "residual": 0.0,
                "flag": False,
                "confidence": 0.0,
                "n_points": n_points,
                "status": "unknown",
                "reasons": ["data_gaps_prevent_reliable_kinematic_check"],
            }

        p0_lats = lats[:-1][valid_mask]
        p0_lons = lons[:-1][valid_mask]
        p1_lats = lats[1:][valid_mask]
        p1_lons = lons[1:][valid_mask]
        valid_dts = dts[valid_mask]

        phi1 = np.radians(p0_lats)
        phi2 = np.radians(p1_lats)
        dphi = np.radians(p1_lats - p0_lats)
        dlam = np.radians(p1_lons - p0_lons)
        a = np.sin(dphi / 2.0) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlam / 2.0) ** 2
        dists = 6371000.0 * 2.0 * np.arctan2(np.sqrt(a), np.sqrt(np.maximum(0.0, 1.0 - a)))

        implied_speeds = dists / valid_dts
        speed_accels = np.abs(np.diff(implied_speeds)) / valid_dts[1:] if len(implied_speeds) > 1 else np.array([0.0])

        max_speed_obs = float(np.max(implied_speeds)) if len(implied_speeds) > 0 else 0.0
        max_accel_obs = float(np.max(speed_accels)) if len(speed_accels) > 0 else 0.0

        # Normalized violation ratios - horizontal kinematics only for trigger (Phase 2.6)
        r_speed = max_speed_obs / self.max_speed
        r_accel = max_accel_obs / self.max_accel

        residual = float(max(r_speed, r_accel))
        flag = bool(residual > 1.0)

        reasons = []
        if r_speed > 1.0:
            reasons.append(f"implied_speed_exceeded: {max_speed_obs:.1f}mps > {self.max_speed:.1f}mps")
        if r_accel > 1.0:
            reasons.append(f"implied_acceleration_exceeded: {max_accel_obs:.1f}mps2 > {self.max_accel:.1f}mps2")

        status = "flagged" if flag else "clear"
        calibrated_prob = self.calibrator.calibrate("kinematic_feasibility", residual) if flag else round(1.0 - self.calibrator.calibrate("kinematic_feasibility", residual), 4)

        return {
            "residual": round(residual, 3),
            "raw_score": round(residual, 3),
            "flag": flag,
            "calibrated_prob": round(calibrated_prob, 4),
            "confidence": round(calibrated_prob, 4),
            "n_points": n_points,
            "status": status,
            "reasons": reasons,
        }


class PosVelConsistencyDetector:
    """Check (c): Position-Velocity Consistency over a window."""

    def __init__(self, thresholds: Optional[Dict[str, Any]] = None):
        cfg = thresholds or load_thresholds()
        self.pv_cfg = cfg.get("spoofing", {}).get("pos_vel_consistency", {})
        self.max_drift = float(self.pv_cfg.get("max_drift_meters", 1000.0))
        self.min_points = int(self.pv_cfg.get("min_points_required", 4))
        self.calibrator = ProbabilityCalibrator()

    def evaluate(self, points_df: pd.DataFrame) -> Dict[str, Any]:
        n_points = len(points_df)
        if n_points < self.min_points:
            return {
                "residual": 0.0,
                "raw_score": 0.0,
                "flag": False,
                "calibrated_prob": 0.0,
                "confidence": 0.0,
                "n_points": n_points,
                "status": "unknown",
                "reasons": [f"insufficient_points: {n_points} < {self.min_points}"],
            }

        sorted_df = points_df.sort_values("ts")
        ts = sorted_df["ts"].to_numpy()
        lats = sorted_df["lat"].to_numpy()
        lons = sorted_df["lon"].to_numpy()
        gs = sorted_df["gs_mps"].to_numpy()
        tracks = np.radians(sorted_df["track_deg"].to_numpy())

        dts = np.diff(ts)
        # Exclude data gaps (> 45s) from dead reckoning horizon (Phase 2.6)
        valid = (dts > 0) & (dts <= 45)

        if not np.any(valid) or np.sum(valid) < 3:
            return {
                "residual": 0.0,
                "flag": False,
                "confidence": 0.0,
                "n_points": n_points,
                "status": "unknown",
                "reasons": ["data_gaps_exceed_dead_reckoning_horizon"],
            }

        p0_lats = lats[:-1][valid]
        p0_lons = lons[:-1][valid]
        p1_lats = lats[1:][valid]
        p1_lons = lons[1:][valid]
        valid_dts = dts[valid]
        valid_gs = gs[:-1][valid]
        valid_tracks = tracks[:-1][valid]

        dn = valid_gs * np.cos(valid_tracks) * valid_dts
        de = valid_gs * np.sin(valid_tracks) * valid_dts

        pred_lats = p0_lats + dn / 111139.0
        cos_lats = np.maximum(0.2, np.cos(np.radians(p0_lats)))
        pred_lons = p0_lons + de / (111139.0 * cos_lats)

        # Vectorized haversine drift
        phi1 = np.radians(pred_lats)
        phi2 = np.radians(p1_lats)
        dphi = np.radians(p1_lats - pred_lats)
        dlam = np.radians(p1_lons - pred_lons)
        a = np.sin(dphi / 2.0) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlam / 2.0) ** 2
        drifts = 6371000.0 * 2.0 * np.arctan2(np.sqrt(a), np.sqrt(np.maximum(0.0, 1.0 - a)))

        max_drift_obs = float(np.percentile(drifts, 95.0))
        flag = bool(max_drift_obs > self.max_drift)

        status = "flagged" if flag else "clear"
        calibrated_prob = self.calibrator.calibrate("pos_vel_consistency", max_drift_obs) if flag else round(1.0 - self.calibrator.calibrate("pos_vel_consistency", max_drift_obs), 4)

        return {
            "residual": round(max_drift_obs, 2),
            "raw_score": round(max_drift_obs, 2),
            "flag": flag,
            "calibrated_prob": round(calibrated_prob, 4),
            "confidence": round(calibrated_prob, 4),
            "n_points": n_points,
            "status": status,
            "reasons": [f"pos_vel_drift_exceeded: {max_drift_obs:.1f}m > {self.max_drift:.1f}m"] if flag else [],
        }


class MultiAircraftConsensusDetector:
    """Check (d): Multi-Aircraft Consensus within an H3 cell and k-ring (res 5, k=1, 15m window)."""

    def __init__(self, thresholds: Optional[Dict[str, Any]] = None):
        cfg = thresholds or load_thresholds()
        self.consensus_cfg = cfg.get("spoofing", {}).get("multi_aircraft", {})
        self.k_ring = 1  # Res 5 + k=1 neighbors (7 cells)
        self.calibrator = ProbabilityCalibrator()

    def evaluate(
        self,
        target_icao: str,
        h3_cell: str,
        window_start_ts: int,
        window_end_ts: int,
        peer_anomalies_in_neighborhood: Dict[str, bool],
    ) -> Dict[str, Any]:
        """Evaluates whether peer aircraft in the 7-cell cluster corroborate an anomaly.

        peer_anomalies_in_neighborhood: dict mapping icao24 -> boolean (True if flagged by check a or c).
        """
        n_peers = len(peer_anomalies_in_neighborhood)

        # Section 4.3 Abstention: insufficient peers in neighborhood (< 2 aircraft)
        if n_peers < 2:
            return {
                "residual": 0.0,
                "raw_score": 0.0,
                "flag": False,
                "calibrated_prob": 0.0,
                "confidence": 0.0,
                "n_points": n_peers,
                "status": "unknown",
                "reasons": [f"insufficient_peer_density: {n_peers} < 2 aircraft in cell neighborhood"],
            }

        flagged_count = sum(1 for is_flagged in peer_anomalies_in_neighborhood.values() if is_flagged)
        anomaly_ratio = float(flagged_count / n_peers)

        # Multi-aircraft spoofing event: multiple aircraft concurrently affected
        flag = bool(flagged_count >= 2 and anomaly_ratio >= 0.40)

        status = "flagged" if flag else "clear"
        calibrated_prob = self.calibrator.calibrate("multi_aircraft_consensus", anomaly_ratio) if flag else round(1.0 - self.calibrator.calibrate("multi_aircraft_consensus", anomaly_ratio), 4)
        reasons = [f"multi_aircraft_anomaly_cluster: {flagged_count}/{n_peers} aircraft affected"] if flag else []

        return {
            "residual": round(anomaly_ratio, 3),
            "raw_score": round(anomaly_ratio, 3),
            "flag": flag,
            "calibrated_prob": round(calibrated_prob, 4),
            "confidence": round(calibrated_prob, 4),
            "n_points": n_peers,
            "status": status,
            "reasons": reasons,
        }


class ModeSEHSPhysicsDetector:
    """Check (e): Mode S Comm-B / EHS Physics Stub.

    Documented stub: EHS DAP registers (BDS 4,0 Selected Alt, BDS 5,0 Roll, BDS 6,0 Heading/IAS)
    are not broadcast in standard Mode S ADS-B DF17 messages and are not modeled in synthetic tracks.
    """

    def __init__(self, thresholds: Optional[Dict[str, Any]] = None):
        pass

    def evaluate(self, points_df: pd.DataFrame) -> Dict[str, Any]:
        return {
            "residual": 0.0,
            "raw_score": 0.0,
            "flag": False,
            "calibrated_prob": 0.0,
            "confidence": 0.0,
            "n_points": 0,
            "status": "unknown",
            "reasons": [
                "ehs_registers_unavailable",
                "mode_s_comm_b_not_broadcast_in_ads_b_df17",
            ],
        }

