"""Synthetic Data Adapter (FakeAdapter).

Supplies generated flight tracks, space weather observations, and aircraft registry.
Clearly flags `is_synthetic() == True`.
"""

from dataclasses import asdict
from typing import Any, Dict, List, Optional

from backend.app.adapters.base import BaseDataAdapter
from data.synthetic.generator import SyntheticWorldGenerator


class FakeAdapter(BaseDataAdapter):
    """Adapter serving deterministic synthetic simulation data."""

    def __init__(self, config_path: str = "config/synthetic.yaml", seed_mode: str = "dev"):
        self.generator = SyntheticWorldGenerator(config_path=config_path, seed_mode=seed_mode)
        self._cached_world: Optional[Dict[str, Any]] = None

    def _ensure_world(self):
        if self._cached_world is None:
            scale = self.generator.config.get("scale", {})
            n_aircraft = scale.get("n_aircraft", 40)
            n_flights = scale.get("n_flights", 100)
            n_days = scale.get("n_days", 7)
            sampling_sec = scale.get("sampling_interval_seconds", 30)

            start_ts = 1793491200  # Nov 2026 epoch reference
            end_ts = start_ts + (n_days * 86400)

            aircraft = self.generator.generate_aircraft_registry(n_aircraft)
            # Notice: generator creates ground truth events, but FakeAdapter ONLY retains tracks & space weather
            gt_events = self.generator.generate_ground_truth_events(start_ts, end_ts)
            tracks = self.generator.generate_flight_tracks(
                aircraft, gt_events, n_flights, start_ts, sampling_sec
            )
            space_weather = self.generator.generate_space_weather(start_ts, n_days)

            self._cached_world = {
                "aircraft": [asdict(a) for a in aircraft],
                "tracks": [asdict(t) for t in tracks],
                "space_weather": [asdict(sw) for sw in space_weather],
            }

    def fetch_flight_tracks(
        self,
        start_ts: int,
        end_ts: int,
        region: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        self._ensure_world()
        tracks = self._cached_world["tracks"]
        filtered = [
            pt for pt in tracks
            if start_ts <= pt["ts"] <= end_ts
        ]
        if limit:
            filtered = filtered[:limit]
        return filtered

    def fetch_aircraft_registry(self) -> List[Dict[str, Any]]:
        self._ensure_world()
        return list(self._cached_world["aircraft"])

    def fetch_space_weather(
        self, start_ts: int, end_ts: int
    ) -> List[Dict[str, Any]]:
        self._ensure_world()
        sw_records = self._cached_world["space_weather"]
        return [
            sw for sw in sw_records
            if start_ts <= sw["ts"] <= end_ts
        ]

    def is_synthetic(self) -> bool:
        return True

