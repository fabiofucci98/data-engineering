"""Unit tests for the USGS ingest helpers (offline — no network)."""
from datetime import timezone

import pytest

# ingest.py imports `requests` at module level; skip this module (not fail
# collection) when a job didn't install the earthquakes requirements.
pytest.importorskip("requests")

from ingest import normalize, parse_iso


def sample_feature(event_id="us1000abc", mag=4.2, place="Somewhere", ms=1_700_000_000_000,
                   coords=(12.5, 41.9, 10.0)):
    return {
        "id": event_id,
        "properties": {"mag": mag, "place": place, "time": ms, "updated": ms, "url": "x"},
        "geometry": {"coordinates": coords},
    }


def test_normalize_geojson_shape() -> None:
    rows = normalize([sample_feature()])
    assert len(rows) == 1
    event_id, mag, place, time, updated, url, lat, lon, depth = rows[0]
    assert event_id == "us1000abc"
    assert mag == 4.2
    assert lat == 41.9    # longitude first in GeoJSON, latitude second
    assert lon == 12.5
    assert depth == 10.0
    assert time.tzinfo is not None


def test_normalize_skips_bad_rows() -> None:
    good = sample_feature()
    missing_id = sample_feature(event_id=None)
    missing_coords = sample_feature()
    missing_coords["geometry"]["coordinates"] = []
    rows = normalize([good, missing_id, missing_coords])
    assert len(rows) == 1


def test_normalize_empty() -> None:
    assert normalize([]) == []


def test_parse_iso_z_becomes_utc() -> None:
    dt = parse_iso("2026-01-01T12:00:00Z")
    assert dt.tzinfo == timezone.utc


def test_parse_iso_naive_becomes_utc() -> None:
    dt = parse_iso("2026-01-01T12:00:00")
    assert dt.tzinfo == timezone.utc