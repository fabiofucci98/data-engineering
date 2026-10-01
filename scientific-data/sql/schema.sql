-- Schema for the Scientific Data Platform — Phase 1 (Earthquakes).
-- Idempotent: safe to run repeatedly.
-- Keyed on the USGS event id so ingestion can upsert without duplicates.

CREATE TABLE IF NOT EXISTS earthquakes (
    event_id    TEXT PRIMARY KEY,          -- USGS event id
    mag         NUMERIC(6, 2),             -- magnitude
    place       TEXT,                      -- human-readable location
    time        TIMESTAMPTZ NOT NULL,      -- event time (UTC)
    updated     TIMESTAMPTZ,               -- last update time reported by USGS
    url         TEXT,                      -- USGS event page
    lat         NUMERIC(8, 5) NOT NULL,    -- latitude (deg)
    lon         NUMERIC(9, 5) NOT NULL,    -- longitude (deg)
    depth_km    NUMERIC(8, 2),             -- depth (km)
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_earthquakes_time ON earthquakes (time);
CREATE INDEX IF NOT EXISTS idx_earthquakes_mag  ON earthquakes (mag);