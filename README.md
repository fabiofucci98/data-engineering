# Scientific Data Platform

> **🚧 WORK IN PROGRESS — NOT YET FUNCTIONAL**

This repository currently contains *project scaffolding only* (documentation, devlog, and agent rules).
No code, containers, or data pipelines exist yet — they are the very next steps on the roadmap below.

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

This diagram will be refined and turned into real `docker-compose.yml` + `app/` code in Phase 1.

## 🗺️ Roadmap

- [ ] **Phase 0 — Scaffolding** *(current)*
  - [x] README (this file)
  - [x] `TECHNOLOGIES.md` — technology plan by stage
  - [x] `devlog/` — development log with first entry
  - [x] `.cline/rules/` — agent / contributor working rules
  - [ ] Git repository initialization + first commit
- [ ] **Phase 1 — Earthquake MVP**
  - [ ] `docker-compose.yml` (Postgres + pgAdmin)
  - [ ] `app/` ingestion script hitting the USGS API
  - [ ] Schema + load into Postgres
  - [ ] Simple Streamlit dashboard with maps/charts
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
├── devlog/                 ← chronological project journal
├── .cline/rules/           ← rules loaded by Cline / agents working here
├── docker-compose.yml      ← [Phase 1]
├── app/                    ← [Phase 1] ingestion + visualization code
└── data/                   ← [Phase 1+] raw / processed data notes
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