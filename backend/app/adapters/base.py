"""Abstract Base Data Adapter Interface for AeroTrust."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseDataAdapter(ABC):
    """Abstract interface for all trajectory and space weather data providers."""

    @abstractmethod
    def fetch_flight_tracks(
        self,
        start_ts: int,
        end_ts: int,
        region: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Fetches normalized track points adhering to Section 3 schema:

        (icao24, ts, lat, lon, baro_alt_m, geo_alt_m, gs_mps, track_deg, vrate_mps,
         on_ground, nic, nacp, sil, source_note).
        """
        pass

    @abstractmethod
    def fetch_aircraft_registry(self) -> List[Dict[str, Any]]:
        """Fetches aircraft registry adhering to Section 3 schema:

        (icao24, registration, type_code, family, operator).
        """
        pass

    @abstractmethod
    def fetch_space_weather(
        self, start_ts: int, end_ts: int
    ) -> List[Dict[str, Any]]:
        """Fetches space weather observations:

        (ts, kp, proton_flux_10mev, xray_flux, raw_payload_ref).
        """
        pass

    @abstractmethod
    def is_synthetic(self) -> bool:
        """Returns True if the underlying data source is synthetic simulation data."""
        pass

