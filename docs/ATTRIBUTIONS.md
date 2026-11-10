# AeroTrust Attributions & Third-Party Assets

This document catalogues all third-party datasets, textures, public sources, and open-source libraries used within the AeroTrust repository, along with their respective licenses and upstream source URLs.

---

## 1. Cartographic & Earth Visualization Assets

### 1.1 Earth Surface Texture (`frontend/public/textures/earth_atmos_2048.jpg`)
* **File Name**: `frontend/public/textures/earth_atmos_2048.jpg`
* **Status**: **provenance not yet verified**
* **Attributed Upstream**: NASA Visible Earth / Blue Marble: Land Surface, Shallow Water, and Shaded Topography.
* **URL**: https://visibleearth.nasa.gov/images/57752/blue-marble-land-surface-shallow-water-and-shaded-topography
* **TODO**: Replace `frontend/public/textures/earth_atmos_2048.jpg` with a direct NASA Visible Earth download from an authenticated public-domain archive to establish full cryptographic provenance.

### 1.2 Natural Earth Vector GeoJSON Data
* **Files**:
  - `frontend/public/data/ne_110m_admin_0_countries.geojson`
  - `frontend/public/data/ne_110m_land.geojson`
* **Source**: Natural Earth (Free vector and raster map data at naturalearthdata.com).
* **URL**: https://www.naturalearthdata.com/about/terms-of-use/
* **License**: **Public Domain** (All versions of Natural Earth raster and vector map data entered the public domain 2009-present. No license fee or attribution required; provided as free public domain cartography).

---

## 2. Public Data Sources & Incident Documentation

### 2.1 NOAA Space Weather Prediction Center (SWPC)
* **Usage**: Solar flux and geomagnetic storm data structures for space-weather risk assessment (`backend/app/ingestion/space_weather.py`).
* **Source**: NOAA SWPC Services.
* **URL**: https://services.swpc.noaa.gov
* **License**: **Public Domain** (U.S. Federal Government open scientific data).

### 2.2 Aviation Safety Bulletins & Regulatory Incident Notices
* **Usage**: Historical incident benchmarks in `data/incident_cases.json` and Incident Clock (`/incidents`).
* **Sources**:
  - European Union Aviation Safety Agency (EASA): Emergency Airworthiness Directives (EAD) & Proposed Directives. URL: https://ad.easa.europa.eu/
  - Direction Générale de l'Aviation Civile (DGAC / BEA France): Technical safety communications.
  - Airbus Commercial Aircraft: Customer Service Information Letters (OIT/AOT) and press statements.
* **License / Terms**: Official public safety notices and regulatory government documents cited for historical/academic benchmark purposes.

---

## 3. Core Open-Source Libraries

### 3.1 Frontend Libraries
| Library | License | Source / Upstream URL |
| :--- | :--- | :--- |
| **React & React DOM** | MIT | https://github.com/facebook/react |
| **Vite** | MIT | https://github.com/vitejs/vite |
| **TypeScript** | Apache-2.0 | https://github.com/microsoft/TypeScript |
| **Tailwind CSS** | MIT | https://github.com/tailwindlabs/tailwindcss |
| **Three.js** | MIT | https://github.com/mrdoob/three.js |
| **Leaflet** | BSD-2-Clause | https://github.com/Leaflet/Leaflet |
| **React-Leaflet** | MIT | https://github.com/PaulLeCam/react-leaflet |
| **Lucide React** | ISC | https://github.com/lucide-icons/lucide |
| **d3-geo / topojson-client** | ISC / BSD-3-Clause | https://github.com/d3/d3-geo |
| **Axe-Core / @axe-core/playwright**| MPL-2.0 | https://github.com/dequelabs/axe-core |
| **Vitest** | MIT | https://github.com/vitest-dev/vitest |

### 3.2 Backend & Data Science Libraries
| Library | License | Source / Upstream URL |
| :--- | :--- | :--- |
| **FastAPI** | MIT | https://github.com/fastapi/fastapi |
| **Pydantic** | MIT | https://github.com/pydantic/pydantic |
| **Uvicorn** | BSD-3-Clause | https://github.com/encode/uvicorn |
| **PostGIS / PostgreSQL** | GPL-2.0+ / PostgreSQL License | https://postgis.net / https://www.postgresql.org |
| **Psycopg2** | LGPL-3.0 with OpenSSL exception | https://github.com/psycopg/psycopg2 |
| **H3 / h3-py** | Apache-2.0 | https://github.com/uber/h3-py |
| **PyYAML** | MIT | https://github.com/yaml/pyyaml |
| **Requests / httpx** | Apache-2.0 / BSD-3-Clause | https://github.com/psf/requests |
| **Pytest** | MIT | https://github.com/pytest-dev/pytest |
