-- Schema for the simulated city — Phase 0 (geography only).
-- Idempotent: Postgres runs this once on a fresh city data volume
-- (docker-entrypoint-initdb.d pattern), and it is safe to run repeatedly.
-- Natural keys everywhere so the generator can upsert without duplicates.

CREATE TABLE IF NOT EXISTS city_generation (
    id                  INTEGER PRIMARY KEY DEFAULT 1 CHECK (id = 1),
    population          INTEGER NOT NULL,
    buildings_per_block INTEGER NOT NULL,
    seed                BIGINT  NOT NULL,
    total_buildings     INTEGER NOT NULL,
    grid_side           INTEGER NOT NULL,
    generated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS districts (
    district_id   SERIAL PRIMARY KEY,
    name          TEXT NOT NULL UNIQUE,
    district_type TEXT NOT NULL CHECK (district_type IN ('downtown', 'residential', 'industrial', 'park')),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS intersections (
    intersection_id SERIAL PRIMARY KEY,
    ix              INTEGER NOT NULL,
    iy              INTEGER NOT NULL,
    coord_x         INTEGER NOT NULL,  -- nominal meters on the fictional grid
    coord_y         INTEGER NOT NULL,
    UNIQUE (ix, iy)
);

CREATE TABLE IF NOT EXISTS road_segments (
    segment_id        SERIAL PRIMARY KEY,
    from_ix           INTEGER NOT NULL,
    from_iy           INTEGER NOT NULL,
    to_ix             INTEGER NOT NULL,
    to_iy             INTEGER NOT NULL,
    name              TEXT NOT NULL,
    road_class        TEXT NOT NULL CHECK (road_class IN ('avenue', 'residential')),
    speed_limit       INTEGER NOT NULL,
    lanes             INTEGER NOT NULL,
    capacity_per_hour INTEGER NOT NULL,
    length_m          INTEGER NOT NULL,
    UNIQUE (from_ix, from_iy, to_ix, to_iy),
    FOREIGN KEY (from_ix, from_iy) REFERENCES intersections (ix, iy),
    FOREIGN KEY (to_ix, to_iy)     REFERENCES intersections (ix, iy)
);

CREATE TABLE IF NOT EXISTS buildings (
    building_id   SERIAL PRIMARY KEY,
    building_type TEXT NOT NULL CHECK (building_type IN
        ('house', 'school', 'shop', 'workplace', 'hospital', 'park', 'restaurant', 'civic')),
    name         TEXT NOT NULL,
    capacity     INTEGER NOT NULL DEFAULT 0,
    block_ix     INTEGER NOT NULL,
    block_iy     INTEGER NOT NULL,
    slot         INTEGER NOT NULL,
    address      TEXT NOT NULL,
    district_id  INTEGER REFERENCES districts (district_id),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (block_ix, block_iy, slot)
);

CREATE INDEX IF NOT EXISTS idx_buildings_type     ON buildings (building_type);
CREATE INDEX IF NOT EXISTS idx_buildings_district ON buildings (district_id);