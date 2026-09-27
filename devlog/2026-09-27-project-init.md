# 2026-09-27 — Project Init & Scaffolding

## Status
🟢 Scaffolding created: README, tech plan, devlog conventions, agent rules.

## Context

Goal: a **beginner data engineering project** — ingest **USGS Earthquakes API** data, store it in
**PostgreSQL (Docker)**, and visualize it simply. The project is explicitly meant to **evolve**:
beyond a beginner project, beyond earthquakes, into other scientific data sources, and finally into
a **machine learning project**.

At kickoff the repo was an **empty directory** (not yet a git repo) on the local machine.

## What happened / Decisions made

- Created `README.md` framing the multi-phase vision (scaffolding → earthquake MVP → hardening →
  multi-source → ML). It is flagged prominently as **WORK IN PROGRESS** — nothing is functional yet.
- Created `TECHNOLOGIES.md`, the per-stage tech plan:
  - **Foundations:** Git/GitHub, VS Code, Docker Compose, Python 3.11+
  - **Ingestion (MVP):** Python `requests` + `pandas`, plain scripts/cron
  - **Storage:** PostgreSQL in Docker, pgAdmin
  - **Transformation:** SQL first, `pandas`/`polars`, `dbt` later
  - **Visualization:** **Streamlit** (simple, beginner-friendly) + Matplotlib/Plotly; Grafana later
  - **Multi-source future:** NOAA / NASA / other USGS feeds, object storage later
  - **ML destination:** scikit-learn, Jupyter, MLflow later
- Created `devlog/` with a convention doc and this first entry.
- Created `.cline/rules/` with project rules for Cline/agents working here.

## Blockers / Open questions

- None yet. Repo not yet initialized with git — that's an immediate next step.
- Visualization stack (Streamlit) is the default pick; revisit when the dashboard milestone arrives.

## Next steps

1. `git init` + initial commit.
2. Write `docker-compose.yml` (Postgres + pgAdmin) and verify locally.
3. Create `app/` with the USGS Earthquake ingestion script (Phase 1 of the roadmap).