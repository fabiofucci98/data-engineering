# Scientific Data Platform

> **🚧 WORK IN PROGRESS — EVOLVING PROJECT**
>
> **Phase 1 (earthquake MVP) is working locally, all in Docker:** Postgres + pgAdmin +
> the Python app (`app/ingest.py` loads USGS Earthquake data, `app/dashboard.py`
> visualizes it with Streamlit). Future plans and ideas live in [`notes/`](notes/README.md).

---

## What is this?

A **beginner-level data engineering project** — currently a single pipeline:

> Ingest **USGS Earthquake data** from a public API → store it in **PostgreSQL** running in **Docker** → present it with **simple visualizations**.

The project is designed as the foundation for something bigger (more scientific data
sources later, an ML project further out); that future vision is kept in
[`notes/`](notes/README.md), separate from this README, which only describes what works today.

## 🧱 Architecture (current state)

```
┌────────────┐   ┌─────────────────┐   ┌──────────────┐    ┌────────────────┐
│  Public     ──▶ Ingestion        ──▶ PostgreSQL     ──▶  Simple          
│  Data APIs │   │  (Python,       │   │  (Docker)    │    │  Visualization │
│  (USGS...) │   │  manual)       │   │              │    │  (Streamlit)   │
└────────────┘   └─────────────────┘   └──────────────┘    └────────────────┘
```

All three boxes run under Docker Compose (`db`, `pgadmin`, `app`). Ingestion is run
manually today (`docker compose run --rm app python ingest.py`).

## 🚀 Getting Started (Phase 1)

### Prerequisites

- Docker Desktop (with Compose)

### 1. Start the whole stack (db + pgAdmin + app)

```bash
docker compose up -d --build
```

- Postgres → `localhost:5433` (a machine-local Postgres already owns 5432)
- pgAdmin → http://localhost:8080 (login `admin@example.com` / `admin`)
- Dashboard → http://localhost:8501
- In pgAdmin, register a server with host `db` and port `5432` (inside the Docker
  network, user `postgres`).

The `app` service waits for Postgres to be healthy, and `--build` rebuilds the image
when the Python code changes.

### 2. Load earthquake data (inside the app container)

```bash
docker compose run --rm app python ingest.py                                     # last 30 days, min magnitude 2.5
docker compose run --rm app python ingest.py --starttime 2026-01-01 --endtime 2026-03-01 --min-magnitude 4.0
```

Re-running is safe: ingestion upserts keyed on the USGS event id, so rows are never duplicated.

### 3. Restart / inspect the dashboard container

```bash
docker compose up -d app        # start just the dashboard container
docker compose logs -f app      # follow its logs
```

Open http://localhost:8501 — filter by magnitude and date in the sidebar.

### (Optional) Running the app directly on the host

For learning, you can also run it without Docker:

```bash
python -m venv .venv
pip install -r app/requirements.txt        # after activating the venv (see CHEATSHEET.md)
python app/ingest.py
streamlit run app/dashboard.py
```

When run on the host, the app reads `.env` (`POSTGRES_HOST=localhost`, `POSTGRES_PORT=5433`)
to reach the same Docker Postgres.

## 🧭 Current state vs. future

- **Implemented (this README):** Phase 0 (scaffolding) and Phase 1 (earthquake MVP).
- **Not yet implemented:** future thoughts — upcoming phases (hardening, multi-source
  data, ML) are planned in [`notes/vision-and-roadmap.md`](notes/vision-and-roadmap.md).

## 📚 Repository Layout

```
ScientificDataPlatform/
├── README.md               ← this file
├── TECHNOLOGIES.md         ← technologies currently in use
├── CHEATSHEET.md           ← command/syntax reference (keep fresh!)
├── devlog/                 ← chronological project journal
├── notes/                  ← future plans & ideas (not yet implemented)
├── .cline/rules/           ← rules loaded by Cline / agents working here
├── docker-compose.yml      ← Postgres 16 + pgAdmin 4 + app (Docker)
├── .env.example            ← env template; copy to .env (git-ignored)
├── sql/
│   └── schema.sql          ← auto-applied on the first `docker compose up`
├── app/
│   ├── Dockerfile          ← container image for ingest + dashboard
│   ├── .dockerignore
│   ├── ingest.py           ← USGS API → Postgres (idempotent upsert)
│   ├── dashboard.py        ← Streamlit dashboard
│   └── requirements.txt    ← pinned Python dependencies
└── data/                   ← raw / processed data notes (never commit payloads)
```

## 🧰 Tech Stack — TL;DR

- **Language:** Python (end to end — ingestion → storage glue → visualization)
- **Storage:** PostgreSQL via Docker Compose
- **Visualization:** Streamlit (simple, beginner-friendly)
- **AI assistance (dev workflow):** OpenRouter as the LLM provider
- **Current stack details:** see [`TECHNOLOGIES.md`](TECHNOLOGIES.md)

## 📓 Devlog

The project's evolution is journaled in [`devlog/`](devlog/README.md). Every meaningful milestone,
decision, blocker, and pivot gets a dated entry — this keeps the *why* behind the project alive.

## 🤝 Contributing / Working Here

Anyone (human or AI agent) working in this repo must follow the conventions in
[`.cline/rules/project-rules.md`](.cline/rules/project-rules.md).