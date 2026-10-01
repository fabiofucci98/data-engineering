"""End-to-end generator tests against a real Postgres (CI: city-integration job).

Marked `integration`; skipped unless RUN_INTEGRATION=1 is set (see conftest.py).
"""
import os
import subprocess
import sys
import time
from pathlib import Path

import psycopg
import pytest

pytestmark = pytest.mark.integration

CITYGEN_DIR = Path(__file__).resolve().parents[1]  # city-simulation/citygen
GENERATE = CITYGEN_DIR / "generate.py"
CITY_SQL = CITYGEN_DIR.parent / "sql" / "city.sql"  # city-simulation/sql/city.sql
REPO = CITYGEN_DIR.parent.parent  # repo root (subprocess cwd)


def _env(key: str, default: str) -> str:
    return os.getenv(key, default)


def db_url() -> str:
    return (
        f"postgresql://{_env('CITY_POSTGRES_USER', 'postgres')}:"
        f"{_env('CITY_POSTGRES_PASSWORD', 'postgres')}@"
        f"{_env('CITY_POSTGRES_HOST', 'localhost')}:{_env('CITY_POSTGRES_PORT', '5432')}/"
        f"{_env('CITY_POSTGRES_DB', 'city')}"
    )


def connect(retries: int = 30, delay: float = 1.0) -> psycopg.Connection:
    last: Exception | None = None
    for _ in range(retries):
        try:
            return psycopg.connect(db_url(), connect_timeout=2)
        except psycopg.OperationalError as exc:
            last = exc
            time.sleep(delay)
    raise RuntimeError(f"could not connect to Postgres: {last}")


def run_generate(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.setdefault("CITY_POSTGRES_HOST", "localhost")
    env.setdefault("CITY_POSTGRES_PORT", "5432")
    env.setdefault("CITY_POSTGRES_DB", "city")
    env.setdefault("CITY_POSTGRES_USER", "postgres")
    env.setdefault("CITY_POSTGRES_PASSWORD", "postgres")
    return subprocess.run(
        [sys.executable, str(GENERATE), *args],
        env=env,
        cwd=REPO,
        capture_output=True,
        text=True,
    )


def apply_schema(conn: psycopg.Connection) -> None:
    """Recreate the city schema from scratch so runs are isolated and repeatable."""
    with conn.cursor() as cur:
        cur.execute(
            "DROP TABLE IF EXISTS buildings, road_segments, intersections, "
            "districts, city_generation CASCADE"
        )
        for chunk in CITY_SQL.read_text(encoding="utf-8").split(";"):
            lines = [ln for ln in chunk.splitlines() if ln.strip()]
            if not lines or all(ln.lstrip().startswith("--") for ln in lines):
                continue
            cur.execute("\n".join(lines))
    conn.commit()


def table_count(conn: psycopg.Connection, table: str) -> int:
    with conn.cursor() as cur:
        cur.execute(f"SELECT count(*) FROM {table}")
        return cur.fetchone()[0]


@pytest.fixture(scope="module")
def fresh_city() -> dict[str, int]:
    """Reset the schema and generate the canonical 1000-person seed-42 city once."""
    conn = connect()
    apply_schema(conn)
    result = run_generate("--population", "1000", "--buildings-per-block", "8", "--seed", "42")
    assert result.returncode == 0, result.stdout + result.stderr
    counts = {
        "districts": table_count(conn, "districts"),
        "intersections": table_count(conn, "intersections"),
        "road_segments": table_count(conn, "road_segments"),
        "buildings": table_count(conn, "buildings"),
    }
    conn.close()
    return counts


def test_fresh_city_matches_plan(fresh_city: dict[str, int]) -> None:
    assert fresh_city == {
        "districts": 5,
        "intersections": 64,
        "road_segments": 112,
        "buildings": 353,
    }


def test_rerun_is_a_noop(fresh_city: dict[str, int]) -> None:
    conn = connect()
    result = run_generate("--population", "1000", "--buildings-per-block", "8", "--seed", "42")
    assert result.returncode == 0, result.stdout + result.stderr
    for table, expected in fresh_city.items():
        assert table_count(conn, table) == expected
    conn.close()


def test_different_seed_is_refused(fresh_city: dict[str, int]) -> None:
    result = run_generate("--population", "1000", "--buildings-per-block", "8", "--seed", "43")
    assert result.returncode != 0
    assert "canonical" in result.stdout + result.stderr


def test_different_population_is_refused(fresh_city: dict[str, int]) -> None:
    result = run_generate("--population", "2000", "--buildings-per-block", "8", "--seed", "42")
    assert result.returncode != 0
    assert "canonical" in result.stdout + result.stderr


def test_generation_metadata_is_recorded(fresh_city: dict[str, int]) -> None:
    conn = connect()
    with conn.cursor() as cur:
        cur.execute("SELECT population, buildings_per_block, seed FROM city_generation")
        row = cur.fetchone()
    conn.close()
    assert row == (1_000, 8, 42)