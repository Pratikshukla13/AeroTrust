"""OpenSky Network Real Data Adapter (STUB).

Documented stub ready for real-world integration when live credentials become available.
Per Rule 7: Do not guess OpenSky field names; exact field mapping left as verified TODOs.
Per Rule 8: Secrets must only be loaded from .env.
"""

from typing import Any, Dict, List, Optional

from backend.app.adapters.base import BaseDataAdapter


class OpenSkyAdapterStub(BaseDataAdapter):
    """Stub adapter for real OpenSky Network (REST/Trino) queries."""

    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        self.username = username
        self.password = password
        # TODO-OPENSKY-AUTH: Load and validate credentials strictly from environment (.env)
        # TODO-OPENSKY-AUDIT: Confirm historical Trino partition schema:
        # e.g., default.state_vectors_data4 vs raw flight_track tables

    def fetch_flight_tracks(
        self,
        start_ts: int,
        end_ts: int,
        region: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """TODO: Implement real OpenSky Trino/REST query once credentials/fields are verified.

        Field Audit Checklist:
        - F1: Verify field names for barometric altitude and geometric altitude.
          TODO: Verify exact column names (e.g. 'baroaltitude', 'geoaltitude').
        - F2: Verify field names for ADS-B integrity/accuracy.
          TODO: Verify availability of 'nic', 'nac_p', 'sil'.
        - F3: Mode S Comm-B / EHS registers (e.g. true airspeed, wind).
          TODO: Verify if available in target dataset.
        """
        raise NotImplementedError(
            "OpenSkyAdapterStub is a documented stub. Real data credentials are not configured. "
            "Use FakeAdapter for synthetic simulation."
        )

    def fetch_aircraft_registry(self) -> List[Dict[str, Any]]:
        """TODO: Implement OpenSky aircraft metadata database lookup.

        TODO: Map icao24 to aircraft family (A320-family, A330, A350, other).
        """
        raise NotImplementedError("OpenSky aircraft registry lookup stub.")

    def fetch_space_weather(
        self, start_ts: int, end_ts: int
    ) -> List[Dict[str, Any]]:
        """Space weather is not provided by OpenSky (handled by NOAA)."""
        return []

    def is_synthetic(self) -> bool:
        return False

