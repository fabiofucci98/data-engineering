# Technologies in Use

This document lists the technologies **currently in use** in this repository.
It is not a roadmap: future tools are added here only when they are actually adopted.

> Last reviewed: 2026-09-27 (end of Phase 1, Python app containerized)

## Data source

| Technology | Where / Why |
|---|---|
| USGS Earthquakes API (FDSN Event Service) | `app/ingest.py` fetches `format=geojson` events; no API key required |

## Infrastructure

| Technology | Version | Where / Why |
|---|---|---|
| Docker + Docker Compose | Docker Engine 29.x, Compose v5 | Runs the whole platform — `db`, `pgadmin`, `app` services (`docker compose up -d`) |
| Git + GitHub | — | Version control — humans commit/push; agents never |
| VS Code | — | Editor used for this repo |

## Data storage

| Technology | Version | Where / Why |
|---|---|---|
| PostgreSQL | `postgres:16-alpine` | `db` service; `sql/schema.sql` auto-applied on first boot; published on host port 5433 |
| pgAdmin 4 | `dpage/pgadmin4:latest` | `pgadmin` service; web UI at http://localhost:8080 |

## Python application (`app` service)

| Technology | Version | Where / Why |
|---|---|---|
| Python | `python:3.13-slim` | Language end to end (ingest + dashboard) |
| `requests` | 2.32.3 | USGS API calls |
| `psycopg` (v3) | 3.2.3 | Postgres driver in `ingest.py`; SQLAlchemy dials it via `postgresql+psycopg://` |
| `SQLAlchemy` | 2.0.36 | Engine used by the dashboard to query Postgres |
| `pandas` | 2.2.3 | Query results → DataFrames for charting |
| `Streamlit` | 1.40.0 | Dashboard (`st.map`, `st.bar_chart`, `st.dataframe`, `st.metric`) |
| `python-dotenv` | 1.0.1 | Loads `.env` configuration |

## How the services connect

- Inside Docker: `app` → `db` via hostname `db`, port `5432` (container-internal).
- From the host: Postgres at `localhost:5433`, dashboard at `localhost:8501`, pgAdmin at `localhost:8080`.

## Version pinning

- Python dependencies: pinned in `app/requirements.txt`.
- Images: pinned in `docker-compose.yml` (`postgres:16-alpine`) and `app/Dockerfile`
  (`python:3.13-slim`); pgAdmin tracks `latest`.

## Policy

- Future tools (schedulers such as cron / Prefect / Airflow, dbt, ML frameworks, additional
  data sources) do **not** belong in this document until they are part of the codebase.