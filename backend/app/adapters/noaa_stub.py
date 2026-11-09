"""NOAA Space Weather Prediction Center (SWPC) Real Data Adapter (STUB).

Documented stub ready for real-world integration with NOAA SWPC JSON services.
Per Rule 7: Do not guess NOAA field names; exact field mapping left as verified TODOs.
"""

from typing import Any, Dict, List, Optional

from backend.app.adapters.base import BaseDataAdapter


class NOAAAdapterStub(BaseDataAdapter):
    """Stub adapter for NOAA SWPC JSON endpoints."""

    def __init__(self, base_url: str = "https://services.swpc.noaa.gov"):
        self.base_url = base_url
        # TODO-NOAA-S1: Verify exact endpoints for:
        # 1. Proton flux (>10 MeV): e.g. /json/goes/primary/integral-protons-1-day.json
        # 2. Planetary Kp index: e.g. /json/planetary_k_index_1m.json
        # 3. Solar X-ray flux: e.g. /json/goes/primary/xrays-1-day.json

    def fetch_flight_tracks(
        self,
        start_ts: int,
        end_ts: int,
        region: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """NOAA does not provide flight tracks."""
        return []

    def fetch_aircraft_registry(self) -> List[Dict[str, Any]]:
        """NOAA does not provide aircraft registry."""
        return []

    def fetch_space_weather(
        self, start_ts: int, end_ts: int
    ) -> List[Dict[str, Any]]:
        """TODO: Ingest and parse real NOAA SWPC JSON payloads.

        - Map timestamp to unix epoch.
        - Map proton flux >10 MeV field name.
        - Map Kp index and X-ray flux fields.
        - Store raw payload reference for data provenance.
        """
        raise NotImplementedError(
            "NOAAAdapterStub is a documented stub. Real NOAA API endpoints require live network auditing. "
            "Use FakeAdapter for synthetic simulation."
        )

    def is_synthetic(self) -> bool:
        return False

