# 2026-09-27 — Python App Containerized

## Status
🟢 The Python code (ingest + dashboard) now runs in Docker as the `app` Compose service;
verified end to end.

## Context

The human asked to containerize the Python code. Until now only Postgres + pgAdmin ran in
Docker; ingest and dashboard ran on the host via a venv.

## What happened / Decisions made

- Added `app/Dockerfile` (`python:3.13-slim`, pinned requirements, default CMD = Streamlit
  dashboard on `0.0.0.0:8501`) and `app/.dockerignore`.
- Added an `app` service to `docker-compose.yml`: builds from `./app`, bind-mounts
  `./app:/app` (live code — no rebuild needed while developing), waits for `db` healthy,
  publishes host `${STREAMLIT_PORT:-8501}` → container `8501`.
- **Container-to-container networking:** inside the compose network the app reaches Postgres
  via hostname `db` on the internal port `5432`, so the `app` service overrides
  `POSTGRES_HOST=db` / `POSTGRES_PORT=5432`. The `.env` values (`localhost` / `5433`) remain
  for host-side runs of the same scripts.
- Run patterns: dashboard → `docker compose up -d app`; ingest → `docker compose run --rm
  app python ingest.py` (overrides the default CMD).
- Updated `README.md` (Getting Started + layout), `CHEATSHEET.md` (docker commands +
  service-networking note), `TECHNOLOGIES.md` (reality table).

## Who did what

- **Agent (Cline):** created the Dockerfile, compose service, and docs; ran all verification.
- **Human:** requested the container; will review and commit.

## Verification

- `docker compose build app` → image `scientific-data-platform-app` built.
- `docker compose run --rm app python ingest.py` → connected to `db`, fetched 1955 events;
  table total went 1956 → 1960 (5 genuinely new events). `distinct_ids = total` → no duplicates.
- `docker compose up -d app` → dashboard up, **HTTP 200** at http://localhost:8501.
- AppTest run **inside the container** → 0 exceptions; metrics 1,960 / 6.6 / 52.0.

## Blockers / Open questions

- None. Phase 2 question remains: cron/Prefect for scheduling the containerized ingest.

## Next steps

1. Human reviews / commits / pushes.
2. Phase 2: schedule `docker compose run --rm app python ingest.py`, add retries, incremental
   loads. Any human learnings get recorded here truthfully as they happen.