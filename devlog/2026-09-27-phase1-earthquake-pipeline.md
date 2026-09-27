# 2026-09-27 — Phase 1: Earthquake Pipeline MVP

## Status
🟢 Working locally end to end: Docker Postgres → USGS ingest → Streamlit dashboard.

## Context

After scaffolding (project init), we executed Phase 1 of the roadmap: Postgres in Docker,
an ingestion script for the USGS Earthquakes API, and a simple visualization.

## What happened / Decisions made

- **`docker-compose.yml`**: Postgres 16 (alpine) + pgAdmin 4, named volumes, healthcheck,
  and `sql/schema.sql` auto-applied on first boot via `/docker-entrypoint-initdb.d`.
- **Host port 5433**: this machine already runs a native Postgres on 5432 — Docker Postgres
  publishes to 5433 so nothing conflicts.
- **Schema**: `earthquakes` table keyed on USGS `event_id` (PK); ingestion uses
  `INSERT … ON CONFLICT DO UPDATE`, so it is **idempotent by design**.
- **`app/ingest.py`**: USGS FDSN `query` API (`format=geojson`, `eventtype=earthquake`),
  paged requests, CLI args (`--starttime`, `--endtime`, `--min-magnitude`), config from `.env`.
- **`app/dashboard.py`**: Streamlit native charts only (`st.map`, `st.bar_chart`,
  `st.dataframe`, sidebar filters, metrics). Verified with streamlit **AppTest**
  (0 exceptions) and a live `streamlit run` server (HTTP 200).
- **Windows gotchas fixed (worth remembering):**
  1. Console `print()` with `→` crashes under the default `cp1252` codepage → ASCII-safe output.
  2. SQLAlchemy defaults to `psycopg2`; we use psycopg v3 → URL must say `postgresql+psycopg://`.
  3. `load_dotenv()` looks in CWD, which differs under Streamlit → load `.env` by absolute path
     (`Path(__file__).resolve().parent.parent / ".env"`).
- Environment: Python **3.13.3**; pins in `app/requirements.txt` verified on it.

## Verification

- `docker compose ps` → `sdp-db` and `sdp-pgadmin` both healthy.
- Ingest run twice → **1956 rows, 1956 distinct ids** (no duplicates, max mag 6.6).
- AppTest run → 0 exceptions; metrics rendered (1,956 / 6.6 / 52.1).

## Next steps (Phase 2 — hardening)

1. Scheduling (cron / Prefect), retries with backoff, incremental loads.
2. SQL transformations / analytics-ready views.
3. README "Run book" polish; consider a `Makefile`-style convenience script list.