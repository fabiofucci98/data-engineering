# Technologies — City simulation pipeline

Owns `city-simulation/docker-compose.yml` and its own Postgres (`city-db`).
Cross-stack/shared tooling is tracked in the root `TECHNOLOGIES.md`.

> Last reviewed: 2026-09-30 (stack moved into its own folder + compose during the repo restructure)

## Data source

| Technology | Where / Why |
|---|---|
| Simulated city (own generator — `citygen/generate.py`) | Deterministic fictional grid city: `--population` / `--buildings-per-block` in → districts, roads, buildings out; names from `pools/` word files (seeded, no AI) |

## Data storage

| Technology | Version | Where / Why |
|---|---|---|
| PostgreSQL | `postgres:16-alpine` | `city-db` service; `sql/city.sql` auto-applied at first boot; host port 5434, database `city` |

## Generator (`citygen/`)

| Technology | Version | Where / Why |
|---|---|---|
| Python | `python:3.13-slim` | `generate.py` — planning formulas, block placement, dictionary-driven naming, fill-to-target loop |
| `psycopg` (v3) | 3.2.3 | Postgres driver for the idempotent upserts into the `city` database |
| `python-dotenv` | 1.0.1 | repo-root `.env` on host runs |
| Name pools (data files) | — | `pools/*.txt` — one word per line per naming recipe; seeded draws, no AI at runtime |

## Version pinning

- `citygen/requirements.txt`; images pinned in this stack's compose file.
- The generator uses dedicated `CITY_POSTGRES_*` env so it can never hit the
  earthquakes database.

## Commands

All stack commands live in this folder's [`CHEATSHEET.md`](CHEATSHEET.md).