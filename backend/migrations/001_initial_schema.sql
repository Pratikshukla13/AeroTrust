-- AeroTrust Database Migration 001: Initial Observatory Schema
-- Source of Truth: README.md Section 3 & Section 4
-- Target: PostgreSQL 16 + PostGIS extension

CREATE EXTENSION IF NOT EXISTS postgis;

-- 1. AIRCRAFT REGISTRY
CREATE TABLE IF NOT EXISTS aircraft (
    icao24 VARCHAR(10) PRIMARY KEY,
    registration VARCHAR(32) NOT NULL,
    type_code VARCHAR(8) NOT NULL,
    family VARCHAR(32) NOT NULL,
    operator VARCHAR(128) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_aircraft_family ON aircraft(family);

-- 2. FLIGHT TRACK POINTS (Trajectory points with PostGIS geometry & H3 cell)
CREATE TABLE IF NOT EXISTS flight_track_points (
    id BIGSERIAL PRIMARY KEY,
    icao24 VARCHAR(10) NOT NULL REFERENCES aircraft(icao24) ON DELETE CASCADE,
    ts BIGINT NOT NULL,
    lat DOUBLE PRECISION NOT NULL,
    lon DOUBLE PRECISION NOT NULL,
    baro_alt_m DOUBLE PRECISION NOT NULL,
    geo_alt_m DOUBLE PRECISION NOT NULL,
    gs_mps DOUBLE PRECISION NOT NULL,
    track_deg DOUBLE PRECISION NOT NULL,
    vrate_mps DOUBLE PRECISION NOT NULL,
    on_ground BOOLEAN NOT NULL DEFAULT FALSE,
    nic INTEGER NOT NULL,
    nacp INTEGER NOT NULL,
    sil INTEGER NOT NULL,
    source_note VARCHAR(128) DEFAULT 'SYNTHETIC_GENERATOR',
    h3_cell VARCHAR(24),
    geom GEOMETRY(Point, 4326)
);
CREATE INDEX IF NOT EXISTS idx_flight_track_points_icao_ts ON flight_track_points(icao24, ts);
CREATE INDEX IF NOT EXISTS idx_flight_track_points_ts ON flight_track_points(ts);
CREATE INDEX IF NOT EXISTS idx_flight_track_points_h3 ON flight_track_points(h3_cell);
CREATE INDEX IF NOT EXISTS idx_flight_track_points_geom ON flight_track_points USING GIST (geom);

-- 3. SPOOF CHECKS (Detector evaluation records)
CREATE TABLE IF NOT EXISTS spoof_checks (
    id BIGSERIAL PRIMARY KEY,
    icao24 VARCHAR(10) NOT NULL,
    ts_window_start BIGINT NOT NULL,
    ts_window_end BIGINT NOT NULL,
    check_name VARCHAR(64) NOT NULL,
    residual DOUBLE PRECISION NOT NULL,
    flag BOOLEAN NOT NULL,
    confidence DOUBLE PRECISION NOT NULL,
    n_points INTEGER NOT NULL,
    status VARCHAR(16) DEFAULT 'ok',
    reasons JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_spoof_checks_icao_window ON spoof_checks(icao24, ts_window_start, ts_window_end);
CREATE INDEX IF NOT EXISTS idx_spoof_checks_name ON spoof_checks(check_name);

-- 4. INTERFERENCE CELLS (Aggregated H3 spatial cells over time buckets)
CREATE TABLE IF NOT EXISTS interference_cells (
    id BIGSERIAL PRIMARY KEY,
    h3_cell VARCHAR(24) NOT NULL,
    time_bucket BIGINT NOT NULL,
    jam_score DOUBLE PRECISION,
    spoof_score DOUBLE PRECISION,
    n_aircraft INTEGER NOT NULL DEFAULT 0,
    n_checks INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(16) NOT NULL, -- 'ok', 'degraded', 'unknown'
    reasons JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_cell_bucket UNIQUE (h3_cell, time_bucket)
);
CREATE INDEX IF NOT EXISTS idx_interference_cells_h3_bucket ON interference_cells(h3_cell, time_bucket);
CREATE INDEX IF NOT EXISTS idx_interference_cells_status ON interference_cells(status);

-- 5. SPACE WEATHER (Solar proton flux and planetary Kp index)
CREATE TABLE IF NOT EXISTS space_weather (
    ts BIGINT PRIMARY KEY,
    kp DOUBLE PRECISION NOT NULL,
    proton_flux_10mev DOUBLE PRECISION NOT NULL,
    xray_flux DOUBLE PRECISION NOT NULL,
    raw_payload_ref VARCHAR(256) DEFAULT 'SYNTHETIC_SWPC_SERIES',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_space_weather_ts ON space_weather(ts);

-- 6. RADIATION INDEX (Calculated flight exposure index)
CREATE TABLE IF NOT EXISTS radiation_index (
    id BIGSERIAL PRIMARY KEY,
    icao24 VARCHAR(10) NOT NULL,
    ts BIGINT NOT NULL,
    alt_m DOUBLE PRECISION NOT NULL,
    geomag_lat DOUBLE PRECISION NOT NULL,
    relative_index DOUBLE PRECISION NOT NULL,
    components JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_radiation_index_icao_ts ON radiation_index(icao24, ts);

-- 7. TRUST SCORES (Flight-level integrated data integrity assessment)
CREATE TABLE IF NOT EXISTS trust_scores (
    id BIGSERIAL PRIMARY KEY,
    flight_id VARCHAR(64) NOT NULL,
    segment_start BIGINT NOT NULL,
    segment_end BIGINT NOT NULL,
    score DOUBLE PRECISION,
    uncertainty DOUBLE PRECISION,
    status VARCHAR(16) NOT NULL, -- 'ok', 'degraded', 'unknown'
    reasons JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_trust_scores_flight ON trust_scores(flight_id);
CREATE INDEX IF NOT EXISTS idx_trust_scores_status ON trust_scores(status);

-- 8. SAR AGGREGATE (Silent Acceptance Rate)
-- Privacy & Safety Rule 4: Aggregated strictly by family x region x month.
-- NEVER store icao24 or tail numbers in this table.
CREATE TABLE IF NOT EXISTS sar_aggregate (
    id BIGSERIAL PRIMARY KEY,
    family VARCHAR(32) NOT NULL,
    region VARCHAR(64) NOT NULL,
    month VARCHAR(7) NOT NULL, -- e.g. '2026-11'
    n_flights_flagged INTEGER NOT NULL,
    n_silent INTEGER NOT NULL,
    sar DOUBLE PRECISION,
    ci_low DOUBLE PRECISION,
    ci_high DOUBLE PRECISION,
    suppressed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_sar_aggregate UNIQUE (family, region, month)
);
CREATE INDEX IF NOT EXISTS idx_sar_aggregate_family_region ON sar_aggregate(family, region, month);

-- 9. INCIDENT CASES (Seeded Public Numbers from README Section 4.6)
CREATE TABLE IF NOT EXISTS incident_cases (
    case_id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(256) NOT NULL,
    trigger_date DATE NOT NULL,
    public_statement_date DATE NOT NULL,
    directive_date DATE NOT NULL,
    aircraft_held_in_service INTEGER NOT NULL,
    aircraft_held_undelivered INTEGER NOT NULL,
    days_to_scope INTEGER NOT NULL,
    source_urls TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 10. PRECURSOR CANDIDATES (Hypothesis generator only; private, never exported)
CREATE TABLE IF NOT EXISTS precursor_candidates (
    id BIGSERIAL PRIMARY KEY,
    icao24 VARCHAR(10) NOT NULL,
    ts BIGINT NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    vrate_dip DOUBLE PRECISION NOT NULL,
    altitude_loss DOUBLE PRECISION NOT NULL,
    radiation_index_at_time DOUBLE PRECISION,
    review_status VARCHAR(32) DEFAULT 'pending_review',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_precursor_candidates_ts ON precursor_candidates(ts);

