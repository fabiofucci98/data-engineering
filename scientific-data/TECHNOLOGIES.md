# Technologies — Scientific Data pipeline (USGS earthquakes)

Owns `scientific-data/docker-compose.yml` and its own Postgres (`sci-db`).
Cross-stack/shared tooling is tracked in the root `TECHNOLOGIES.md`.

> Last reviewed: 2026-09-30 (stack moved into its own folder + compose during the repo restructure)

## Data source

| Technology | Where / Why |
|---|---|
| USGS Earthquakes API (FDSN Event Service) | `earthquakes/ingest.py` fetches `format=geojson` events; no API key required |

## Data storage

| Technology | Version | Where / Why |
|---|---|---|
| PostgreSQL | `postgres:16-alpine` | `sci-db` service; `sql/schema.sql` auto-applied at first boot; host port 5433, database `scientific_data` |

## App (`earthquakes/`)

| Technology | Version | Where / Why |
|---|---|---|
| Python | `python:3.13-slim` | ingest + dashboard |
| `requests` | 2.32.3 | USGS API calls |
| `psycopg` (v3) | 3.2.3 | Postgres driver in `ingest.py`; SQLAlchemy dials it via `postgresql+psycopg://` |
| `SQLAlchemy` | 2.0.36 | the dashboard's engine |
| `pandas` | 2.2.3 | query results → DataFrames |
| `Streamlit` | 1.40.0 | dashboard (`st.map`, `st.bar_chart`, `st.dataframe`, `st.metric`) |
| `python-dotenv` | 1.0.1 | repo-root `.env` on host runs |

## Version pinning

- `earthquakes/requirements.txt`; images pinned in this stack's compose file.
- Host runs read the repo-root `.env` (`POSTGRES_HOST=localhost`, `POSTGRES_PORT=5433`).

## Commands

All stack commands (and the USGS/Streamlit reference notes) live in this folder's
[`CHEATSHEET.md`](CHEATSHEET.md).