"""USGS Earthquake ingestion into PostgreSQL.

Fetches earthquake events from the USGS FDSN Event API as GeoJSON and
upserts them into the `earthquakes` table.

Idempotent: rows are keyed on the USGS event id, so re-running the script
updates existing rows instead of creating duplicates.

Examples:
    python app/ingest.py
    python app/ingest.py --starttime 2026-01-01 --endtime 2026-03-01 --min-magnitude 4.0
"""
from __future__ import annotations

import argparse
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import psycopg
import requests
from dotenv import load_dotenv

USGS_QUERY_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
PAGE_SIZE = 2000  # events per API call (well under the 20000 cap)
DEFAULT_MIN_MAGNITUDE = 2.5
DEFAULT_LOOKBACK_DAYS = 30

UPSERT_SQL = """
    INSERT INTO earthquakes (event_id, mag, place, time, updated, url, lat, lon, depth_km)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (event_id) DO UPDATE SET
        mag        = EXCLUDED.mag,
        place      = EXCLUDED.place,
        time       = EXCLUDED.time,
        updated    = EXCLUDED.updated,
        url        = EXCLUDED.url,
        lat        = EXCLUDED.lat,
        lon        = EXCLUDED.lon,
        depth_km   = EXCLUDED.depth_km,
        ingested_at = now()
"""


def parse_iso(value: str) -> datetime:
    """Parse an ISO 8601 string; missing timezone is assumed to be UTC."""
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load USGS earthquake events into Postgres.")
    now = datetime.now(timezone.utc)
    parser.add_argument(
        "--starttime",
        type=parse_iso,
        default=now - timedelta(days=DEFAULT_LOOKBACK_DAYS),
        help=f"Earliest event time, ISO 8601 (default: {DEFAULT_LOOKBACK_DAYS} days ago).",
    )
    parser.add_argument(
        "--endtime",
        type=parse_iso,
        default=now,
        help="Latest event time, ISO 8601 (default: now).",
    )
    parser.add_argument(
        "--min-magnitude",
        type=float,
        default=DEFAULT_MIN_MAGNITUDE,
        help=f"Minimum magnitude (default: {DEFAULT_MIN_MAGNITUDE}).",
    )
    return parser.parse_args()


def database_url() -> str:
    """Build the Postgres connection string from environment variables."""
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    dbname = os.getenv("POSTGRES_DB", "scientific_data")
    return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"


def fetch_events(payload: dict) -> list[dict]:
    """Fetch all GeoJSON features matching the query payload, handling paging."""
    features: list[dict] = []
    offset = 1
    while True:
        response = requests.get(
            USGS_QUERY_URL,
            params={**payload, "limit": PAGE_SIZE, "offset": offset},
            timeout=60,
        )
        response.raise_for_status()
        body = response.json()
        page = body.get("features") or []
        features.extend(page)

        total = (body.get("metadata") or {}).get("count", 0)
        if not page or offset + PAGE_SIZE > total:
            break
        offset += PAGE_SIZE
    return features


def _to_datetime(epoch_ms: int | None) -> datetime | None:
    if epoch_ms is None:
        return None
    return datetime.fromtimestamp(epoch_ms / 1000.0, tz=timezone.utc)


def normalize(features: list[dict]) -> list[tuple]:
    """Convert GeoJSON features into rows for the earthquakes table.

    GeoJSON coordinates are [longitude, latitude, depth(km)].
    """
    rows: list[tuple] = []
    for feature in features:
        event_id = feature.get("id")
        props = feature.get("properties") or {}
        coords = (feature.get("geometry") or {}).get("coordinates") or []
        if not event_id or not coords:
            continue
        rows.append((
            event_id,
            props.get("mag"),
            props.get("place"),
            _to_datetime(props.get("time")),
            _to_datetime(props.get("updated")),
            props.get("url"),
            coords[1],  # latitude
            coords[0],  # longitude
            coords[2] if len(coords) > 2 else None,  # depth (km)
        ))
    return rows


def upsert_events(conn: psycopg.Connection, rows: list[tuple]) -> None:
    """Upsert event rows — idempotent, keyed on the USGS event id."""
    with conn.cursor() as cur:
        cur.executemany(UPSERT_SQL, rows)
    conn.commit()


def main() -> None:
    # Load .env by absolute path so CWD never matters.
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    args = parse_args()

    payload = {
        "format": "geojson",
        "starttime": args.starttime.isoformat(),
        "endtime": args.endtime.isoformat(),
        "minmagnitude": args.min_magnitude,
        "eventtype": "earthquake",
        "orderby": "time",
    }
    print(
        f"Querying USGS for earthquakes {args.starttime.isoformat()} to "
        f"{args.endtime.isoformat()} (min magnitude {args.min_magnitude}) ..."
    )

    features = fetch_events(payload)
    rows = normalize(features)
    print(f"Found {len(features)} events; {len(rows)} with usable coordinates.")

    with psycopg.connect(database_url()) as conn:
        upsert_events(conn, rows)
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM earthquakes")
            print(f"Upserted {len(rows)} rows. Total rows in table: {cur.fetchone()[0]}")


if __name__ == "__main__":
    main()