"""AeroTrust Storage & Ingestion Models (README Section 3 Schema).

Supports both PostgreSQL + PostGIS in containerized deployment and SQLite/In-Memory
for fast local test execution.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
import h3
import pandas as pd


class IngestionRepository:
    """In-memory and transactional repository for trajectory and cell data."""

    def __init__(self):
        self.aircraft: Dict[str, Dict[str, Any]] = {}
        self.track_points: List[Dict[str, Any]] = []
        self.interference_cells: Dict[str, Dict[str, Any]] = {}
        self.space_weather: List[Dict[str, Any]] = []

    def insert_aircraft_batch(self, aircraft_list: List[Dict[str, Any]]):
        for ac in aircraft_list:
            self.aircraft[ac["icao24"]] = ac

    def insert_track_points_batch(self, points: List[Dict[str, Any]], h3_res: int = 7):
        """Inserts track points, enriching each point with its H3 spatial index."""
        for pt in points:
            # Map lat/lon to H3 hexagon cell index (resolution 7: ~1.2 km edge length)
            cell = h3.latlng_to_cell(pt["lat"], pt["lon"], h3_res)
            enriched_pt = dict(pt)
            enriched_pt["h3_cell"] = cell
            self.track_points.append(enriched_pt)

    def insert_space_weather_batch(self, sw_list: List[Dict[str, Any]]):
        self.space_weather.extend(sw_list)

    def get_tracks_dataframe(self) -> pd.DataFrame:
        """Returns all ingested track points as a pandas DataFrame."""
        if not self.track_points:
            return pd.DataFrame()
        df = pd.DataFrame(self.track_points)
        return df

    def get_tracks_for_aircraft(self, icao24: str) -> pd.DataFrame:
        df = self.get_tracks_dataframe()
        if df.empty or "icao24" not in df.columns:
            return pd.DataFrame()
        return df[df["icao24"] == icao24].sort_values("ts")

    def get_tracks_in_window(self, start_ts: int, end_ts: int) -> pd.DataFrame:
        df = self.get_tracks_dataframe()
        if df.empty or "ts" not in df.columns:
            return pd.DataFrame()
        return df[(df["ts"] >= start_ts) & (df["ts"] <= end_ts)].sort_values("ts")

