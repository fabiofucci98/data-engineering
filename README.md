# Scientific Data Platform

> **🚧 WORK IN PROGRESS — EVOLVING PROJECT**
>
> **Phase 1 (earthquake MVP) is working locally:** Postgres + pgAdmin run in Docker,
> `app/ingest.py` loads USGS Earthquake data into Postgres, and `app/dashboard.py`
> visualizes it with Streamlit. Later phases expand to other scientific data sources
> and culminate in an ML project (see the roadmap below).

---

## What is this?

A **beginner-level data engineering project** that starts with a single goal:

> Ingest **USGS Earthquake data** from a public API → store it in **PostgreSQL** running in **Docker** → present it with **simple visualizations**.

But that is only the *starting point*.

## 🎯 The Vision

This project is explicitly designed to grow **far beyond** a simple one-source demo:

| Phase | What happens | When |
|---|---|---|
| **0 — Scaffolding** | Repo foundation: README, tech plan, devlog, agent rules | Now |
| **1 — Earthquake MVP** | Docker + Postgres + USGS API ingestion + a simple dashboard | Next |
| **2 — Hardening** | Scheduled runs, error handling/retries, incremental loads, SQL transformations | Later |
| **3 — Multi-source data** | Expand **beyond earthquakes** to other scientific/open data: NOAA, NASA, climate feeds, etc. | Future |
| **4 — Machine Learning** | The project **culminates in an ML project** built on the accumulated scientific data | Destination |

Every decision made today — tech choices, schema design, folder layout — keeps this evolution in mind, so the pipeline generalizes beyond a single dataset and beyond a single visualization.

## 🧱 Architecture (current vision)

```
┌────────────┐    ┌─────────────────┐    ┌──────────────┐    ┌──────────────┐
│  Public    │──▶│  Ingestion       │──▶│  PostgreSQL  │──▶│  Simple      │
│  Data APIs │    │  (Python,       │    │  (Docker)    │    │  Visualization│
│  (USGS...) │    │  scheduled)     │    │              │    │  (Streamlit) │
└────────────┘    └─────────────────┘    └──────────────┘    └──────────────┘
```

This is now real: see `docker-compose.yml` and the `app/` folder. The diagram will be
refined as later phases (multi-source, ML) land.

## 🚀 Getting Started (Phase 1)

### Prerequisites
- Docker Desktop (with Compose)
- Python 3.11+ (tested on 3.13)

### 1. Start the database stack

```bash
docker compose up -d
```

- Postgres → `localhost:5433` (a machine-local Postgres already owns 5432)
- pgAdmin → http://localhost:8080 (login `admin@example.com` / `admin`)
- In pgAdmin, register a server with host `db` and port `5432` (inside the Docker network, user `postgres`).

### 2. Install Python dependencies

```bash
python -m venv .venv
.venv\Scripts\activate           # Windows
source .venv/bin/activate        # macOS / Linux
pip install -r app/requirements.txt
```

### 3. Load earthquake data

```bash
python app/ingest.py                                     # last 30 days, min magnitude 2.5
python app/ingest.py --starttime 2026-01-01 --endtime 2026-03-01 --min-magnitude 4.0
```

Re-running is safe: ingestion upserts keyed on the USGS event id, so rows are never duplicated.

### 4. View the dashboard

```bash
streamlit run app/dashboard.py
```

Open http://localhost:8501 — filter by magnitude and date in the sidebar.

## 🗺️ Roadmap

- [x] **Phase 0 — Scaffolding** *(current)*
  - [x] README (this file)
  - [x] `TECHNOLOGIES.md` — technology plan by stage
  - [x] `devlog/` — development log with first entry
  - [x] `.cline/rules/` — agent / contributor working rules
  - [x] Git repository initialization + first commit
- [x] **Phase 1 — Earthquake MVP** *(working locally)*
  - [x] `docker-compose.yml` (Postgres + pgAdmin)
  - [x] `app/` ingestion script hitting the USGS API
  - [x] Schema + load into Postgres
  - [x] Simple Streamlit dashboard with maps/charts
- [ ] **Phase 2 — Hardening**
  - [ ] Scheduling (cron / Prefect / Airflow)
  - [ ] Retries, backoff, idempotent loads
  - [ ] SQL transformations / analytics-ready tables
- [ ] **Phase 3 — More scientific data sources**
  - [ ] NOAA / NASA / climate datasets
  - [ ] Multi-source schema federation
- [ ] **Phase 4 — Machine Learning**
  - [ ] Feature store on accumulated data
  - [ ] First ML experiments (e.g., classification/regression on events)

## 📚 Repository Layout

```
ScientificDataPlatform/
├── README.md               ← this file
├── TECHNOLOGIES.md         ← tech stack per stage (the "plan")
├── CHEATSHEET.md           ← command/syntax reference (keep fresh!)
├── devlog/                 ← chronological project journal
├── .cline/rules/           ← rules loaded by Cline / agents working here
├── docker-compose.yml      ← Postgres 16 + pgAdmin 4 (Phase 1)
├── .env.example            ← env template; copy to .env (git-ignored)
├── sql/
│   └── schema.sql          ← auto-applied on the first `docker compose up`
├── app/
│   ├── ingest.py           ← USGS API → Postgres (idempotent upsert)
│   ├── dashboard.py        ← Streamlit dashboard
│   └── requirements.txt    ← pinned Python dependencies
└── data/                   ← raw / processed data notes (never commit payloads)
```

## 🧰 Tech Stack — TL;DR

- **Language:** Python (end to end — ingestion → storage glue → visualization → future ML)
- **Storage:** PostgreSQL via Docker Compose
- **Visualization:** Streamlit (simple, beginner-friendly; alternatives listed in the tech plan)
- **Full breakdown by stage:** see [`TECHNOLOGIES.md`](TECHNOLOGIES.md)

## 📓 Devlog

The project's evolution is journaled in [`devlog/`](devlog/README.md). Every meaningful milestone,
decision, blocker, and pivot gets a dated entry — this keeps the *why* behind the project alive.

## 🤝 Contributing / Working Here

Anyone (human or AI agent) working in this repo must follow the conventions in
[`.cline/rules/project-rules.md`](.cline/rules/project-rules.md).