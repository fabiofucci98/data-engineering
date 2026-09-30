# Scientific Data Platform

> **🚧 WORK IN PROGRESS — EVOLVING PROJECT**
>
> **Phase 1 (earthquake MVP) and the simulated city generator are working locally, all
> in Docker:** two self-contained pipelines, each with **its own Postgres and its own
> compose file** — `scientific-data/` (USGS earthquakes app + dashboard) and
> `city-simulation/` (city generator). Shared dev tooling (pgAdmin) lives in the root
> compose. Future plans and ideas live in [`notes/`](notes/README.md).

---

## What is this?

A **beginner-level data engineering project** — co-existing pipelines, each with its own
Postgres database and Docker Compose file:

> **Pipeline 1 — Earthquakes:** Ingest **USGS Earthquake data** from a public API →
> store it in **PostgreSQL** (Docker) → present it with **simple visualizations**.
> **Pipeline 2 — Simulated city:** a generator creates a fictional steam-punk city
> (districts, roads, buildings) into its own Postgres.

The project is designed as the foundation for something bigger (more scientific data
sources later, an ML project further out); that future vision is kept in
[`notes/`](notes/README.md), separate from this README, which only describes what works today.

## 🧱 Architecture (current state)

Each pipeline owns **its own compose file and its own Postgres** — the databases stay
physically separate. The root `docker-compose.yml` runs only shared tooling (pgAdmin)
and creates the shared network `sdp-shared` that both stack databases join, so pgAdmin
can reach them by service name (`sci-db`, `city-db`).

```
┌─ scientific-data/ ───────────────┐   ┌─ city-simulation/ ────────────────┐
│ USGS API → ingest.py → Postgres  │   │ generate.py (formulas + pools)     │
│            → Streamlit dashboard │   │            → Postgres               │
│ compose: sci-db (:5433) + app    │   │ compose: city-db (:5434) + citygen  │
└──────────────────────────────────┘   └────────────────────────────────────┘
                 └────────────── root compose: pgAdmin + shared network ─────┘
```

## 🚀 Getting Started

### Prerequisites

- Docker Desktop (with Compose)

### 1. Start the shared tooling (pgAdmin + shared network)

```bash
docker compose up -d
```

### 2. Start the earthquakes stack (`scientific-data/`)

```bash
docker compose -f scientific-data/docker-compose.yml up -d --build --wait
```

- Postgres → `localhost:5433` (database `scientific_data`); inside the stack it is
  `sci-db:5432`
- Dashboard → http://localhost:8501

### 3. Load earthquake data

```bash
docker compose -f scientific-data/docker-compose.yml run --rm earthquakes-app python ingest.py
```

Re-running is safe: ingestion upserts keyed on the USGS event id, so rows are never
duplicated.

### 4. Start the simulated city stack (`city-simulation/`)

```bash
docker compose -f city-simulation/docker-compose.yml up -d --wait
docker compose -f city-simulation/docker-compose.yml run --rm citygen python generate.py --population 1000 --buildings-per-block 8 --seed 42
```

- City Postgres → `localhost:5434` (database `city`); inside the stack it is
  `city-db:5432`. Re-running the generator is a no-op.

### 5. pgAdmin

http://localhost:8080 (login `admin@example.com` / `admin`) — both databases are
**pre-registered automatically** from `pgadmin/servers.json` (the container loads it at
first init). Open the tree, pick a server and connect — password `postgres`.

### (Optional) Running the app directly on the host

For learning, you can also run the earthquakes scripts without Docker:

```bash
python -m venv .venv
pip install -r scientific-data/earthquakes/requirements.txt
python scientific-data/earthquakes/ingest.py
streamlit run scientific-data/earthquakes/dashboard.py
```

When run on the host, the scripts read the repo-root `.env` (`POSTGRES_HOST=localhost`,
`POSTGRES_PORT=5433`). The city generator uses `CITY_POSTGRES_HOST/PORT/DB` instead
(see `.env.example`).

## 🏭 Simulated city generator

The `city-simulation/` stack: the `citygen` service **generates a fictional steam-punk
grid city** (5 districts, 112 road segments, 64 intersections, ~353 buildings of 8
types) into its own Postgres container (`city-db`). Everything derives from two inputs
— `--population` and `--buildings-per-block` — via city-planning formulas (houses =
people ÷ 3, schools = children ÷ 150, grid side = f(total buildings), …). Names come
from editable word pools (`city-simulation/pools/`), drawn deterministically from a
seed — **no AI at generation time**.

```bash
docker compose -f city-simulation/docker-compose.yml run --rm citygen python generate.py --dry-run --seed 42   # preview
docker compose -f city-simulation/docker-compose.yml run --rm citygen python generate.py --seed 42             # generate
```

- Re-running is a **no-op** (idempotent fill-up-to-target) — same seed, same city, no
  duplicates, always.
- `city-db` listens on `localhost:5434` (database `city`); Postgres auto-creates the
  schema from `city-simulation/sql/city.sql` on first boot.
- The `--seed` is how you get the same city back, every time.

## 🧭 Current state vs. future

- **Implemented (this README):** Phase 0 (scaffolding), Phase 1 (earthquake MVP), and
  the simulated city generator — as two independent stacks, each with its own Postgres.
- **Not yet implemented:** future thoughts — hardening, more scientific sources, ML, and
  the city's people/telemetry layers — in [`notes/`](notes/README.md).

## 📚 Repository Layout

```
ScientificDataPlatform/
├── README.md               ← this file
├── TECHNOLOGIES.md         ← technologies currently in use
├── CHEATSHEET.md           ← command/syntax reference (keep fresh!)
├── WORKFLOW.md             ← portable template: recreate this workflow elsewhere
├── devlog/                 ← chronological project journal
├── notes/                  ← future plans & ideas (not yet implemented)
├── .cline/rules/           ← rules loaded by Cline / agents working here
├── docker-compose.yml      ← SHARED: pgAdmin + shared network (both stacks join it)
├── pgadmin/                ← shared pgAdmin seed: servers.json (auto-registers both DBs)
├── .env.example            ← env template; copy to .env (git-ignored)
├── scientific-data/        ← pipeline 1: USGS Earthquakes (own Postgres, own compose)
│   ├── docker-compose.yml  ← services: sci-db (Postgres 16, host :5433) + earthquakes-app
│   ├── CHEATSHEET.md       ← stack commands (USGS, ingest, psql, Streamlit)
│   ├── TECHNOLOGIES.md     ← stack technologies (scoped)
│   ├── sql/schema.sql      ← earthquakes schema (auto-applied on first sci-db boot)
│   └── earthquakes/
│       ├── Dockerfile      ← image for ingest + dashboard
│       ├── ingest.py       ← USGS API → Postgres (idempotent upsert)
│       ├── dashboard.py    ← Streamlit dashboard
│       └── requirements.txt← pinned Python dependencies
├── city-simulation/        ← pipeline 2: simulated city (own Postgres, own compose)
│   ├── docker-compose.yml  ← services: city-db (Postgres 16, host :5434) + citygen
│   ├── CHEATSHEET.md       ← stack commands (generate, dry-run, psql, pools)
│   ├── TECHNOLOGIES.md     ← stack technologies (scoped)
│   ├── sql/city.sql        ← city schema (auto-applied on first city-db boot)
│   ├── citygen/
│   │   ├── Dockerfile      ← image for the generator
│   │   ├── generate.py     ← deterministic generator (formulas + pools + fill loop)
│   │   └── requirements.txt← pinned Python dependencies
│   └── pools/              ← steam-punk name pools (one word per line; editable)
└── data/                   ← raw / processed data notes (never commit payloads)
```

## 🧰 Tech Stack — TL;DR

- **Language:** Python (end to end — ingestion → storage glue → visualization)
- **Storage:** PostgreSQL via Docker Compose — **one Postgres per pipeline** (sci + city), shared tooling separate
- **Visualization:** Streamlit (simple, beginner-friendly)
- **Simulation:** own deterministic generator (`city-simulation/citygen`) — planning formulas + word pools, no AI
- **AI assistance (dev workflow):** OpenRouter as the LLM provider
- **Current stack details:** see [`TECHNOLOGIES.md`](TECHNOLOGIES.md)

## 📓 Devlog

The project's evolution is journaled in [`devlog/`](devlog/README.md). Every meaningful milestone,
decision, blocker, and pivot gets a dated entry — this keeps the *why* behind the project alive.
