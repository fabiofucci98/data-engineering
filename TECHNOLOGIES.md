# Technologies in Use — shared / cross-stack

This document covers the **repo-wide and shared** technologies only. Each pipeline
folder keeps its own focused `TECHNOLOGIES.md`:
- [`scientific-data/TECHNOLOGIES.md`](scientific-data/TECHNOLOGIES.md) — USGS earthquakes stack
- [`city-simulation/TECHNOLOGIES.md`](city-simulation/TECHNOLOGIES.md) — simulated city stack

> Last reviewed: 2026-09-30 (per-pipeline TECHNOLOGY docs introduced during the restructure)

## Infrastructure (shared)

| Technology | Version | Where / Why |
|---|---|---|
| Docker + Docker Compose | Docker Engine 29.x, Compose v5 | Three compose files — root = shared tooling (pgAdmin, shared network); each pipeline owns its stack + Postgres in its own compose |
| pgAdmin 4 | `dpage/pgadmin4:latest` | Root compose only (shared dev tool); web UI at http://localhost:8080; databases auto-registered from `pgadmin/servers.json` at first init |
| Git + GitHub | — | Version control — humans commit/push; agents never |
| VS Code | — | Editor used for this repo |
| OpenRouter | — | LLM provider for AI-assisted development (e.g., Cline) in this environment |

> Dev-tooling rows (VS Code, OpenRouter) describe how this repo is built and edited —
> they are not part of the running pipelines.

## Shared network

- `sdp-shared` (created by the root compose): `scientific-data`'s `sci-db` and
  `city-simulation`'s `city-db` join it, so pgAdmin reaches both by service name
  (`sci-db:5432`, `city-db:5432`).

## Policy

- Per-stack technologies (Postgres per database, Python app versions, the generator,
  word pools) belong in the pipeline's own `TECHNOLOGIES.md`, not here.
- Future tools (schedulers such as cron / Prefect / Airflow, dbt, ML frameworks,
  additional data sources) do **not** belong in any tech doc until they are part of
  the codebase.