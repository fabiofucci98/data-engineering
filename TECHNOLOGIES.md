# Technologies by Stage

This is the **technology plan** for the Scientific Data Platform. It documents *what* we use,
*why* we use it, and *what the alternatives* are — for each stage of the project's evolution.

> **Guiding rules**
> - Start simple; make the least complex choice that meets current needs.
> - Prefer tools that scale gracefully into the later stages (multi-source, ML).
> - Everything listed here is the *plan* — revisit it in the devlog when reality differs.

## Current reality (as of Phase 1 — 2026-09-27)

The MVP is working locally with a subset of the plan:

| Item | Status |
|---|---|
| Postgres 16 + pgAdmin 4 in Docker Compose | ✅ in use |
| `requests` + `psycopg` v3 + SQLAlchemy (ingest/reads) | ✅ in use |
| Streamlit with native charts (`st.map`, `st.bar_chart`, `st.dataframe`) | ✅ in use |
| `pandas` for query results in the dashboard | ✅ in use |
| Scheduling (cron / Prefect / Airflow) | ⏳ still manual on-demand runs |
| dbt / Great Expectations | ⏳ not yet — Stage 3 |

The tables below remain the roadmap; anything marked ✅ is what the code uses today.

---

## Stage 0 — Foundations

| Tool | Why | Alternatives |
|---|---|---|
| **Git + GitHub** | Version control; collaborate; safe experimentation | GitLab, Gitea |
| **VS Code** | Lightweight editor with Python/Docker integration | PyCharm, Jupyter |
| **Docker + Docker Compose** | Zero-friction local Postgres; reproducible environment | Podman, bare-metal install |
| **Python 3.11+** | Best ecosystem for data + ML; readable for beginners | R (weaker ML/tooling path) |
| **Virtual environment (`venv`)** | Isolate Python deps per project | `uv`, Poetry, `conda` |

## Stage 1 — Ingestion (Earthquake MVP)

| Tool | Why | Alternatives |
|---|---|---|
| **USGS Earthquakes API** | Free, well-documented, no auth required — ideal first source | — |
| **Python `requests`** | Simple HTTP → GeoJSON | `httpx`, `urllib` |
| **`pandas`** | Normalize JSON into tabular form; easy data inspection | `polars` (faster, later) |
| **Plain scripts + cron** (or Windows Task Scheduler) | Simplest scheduling for the MVP | Prefect, Airflow (Stage 2) |

## Stage 2 — Storage & Scheduling

| Tool | Why | Alternatives |
|---|---|---|
| **PostgreSQL** (Docker container) | Robust, SQL standard, great for geospatial (PostGIS) later | MySQL, DuckDB (file-based, for local analysis) |
| **pgAdmin** | GUI to inspect tables/queries while learning | DBeaver, psql CLI |
| **Prefect / Airflow** | Production-grade scheduling, retries, observability | cron, Dagster (Stage 1 if needs grow early) |

## Stage 3 — Transformation & Data Quality

| Tool | Why | Alternatives |
|---|---|---|
| **SQL** | The language of Postgres; transformations close to data | — |
| **`pandas` / `polars`** | Clean/normalize before loading | — |
| **dbt (later)** | Versioned, testable SQL-based transformations | Plain SQL scripts (fine at MVP) |
| **Validation** (e.g., `great_expectations`) | Assert data quality as volume grows | Hand-rolled checks (fine at MVP) |

## Stage 4 — Visualization

| Tool | Why | Alternatives |
|---|---|---|
| **Streamlit** | Fast Python-native dashboards; maps/charts in minutes | Dash, Panel |
| **Matplotlib / Plotly** | Charting inside Streamlit or notebooks | Seaborn, Altair |
| **Grafana** (later) | Operational dashboards on live Postgres | Metabase, Superset |
| **Jupyter notebooks** | Exploratory analysis while learning | VS Code notebooks |

## Stage 5 — Expanding Beyond Earthquakes (Multi-Source)

| Source / Tool | Why |
|---|---|
| **NOAA climate data** | Complementary earth-science signal |
| **NASA open datasets** | Geospatial + remote-sensing data |
| **Other USGS feeds** (e.g., volcanoes, water) | Consistent API style with earthquakes |
| **Structured schema design** | One normalized model that fits *many* sources, not one bespoke table |
| **Object storage (S3 / MinIO)** (later) | Archive raw payloads cheaply before transformation |

## Stage 6 — Destination: Machine Learning

| Tool | Why | Alternatives |
|---|---|---|
| **pandas / polars** | Feature engineering on accumulated data | — |
| **scikit-learn** | Beginner-friendly classical ML (regression/classification) | XGBoost (later) |
| **Jupyter / VS Code notebooks** | Experimentation and documentation | — |
| **MLflow** (later) | Experiment tracking + model registry | Weights & Biases |
| **PostGIS** (if timeframe/geospatial features become features) | Nearest-neighbor, distance features in SQL | shapely / geopandas |

---

## Evolution summary

```
Foundations → USGS-only MVP → Hardened pipelines → Multi-source scientific data → ML project
     ↓              ↓                 ↓                      ↓                      ↓
  Git/Docker    requests/pandas    Prefect/dbt          NOAA/NASA/feeds        scikit-learn/MLflow
  /Python       /Postgres          /Postgres            + design pattern       + feature store
```

## Decision log

Major tech decisions and their rationale get recorded in the [devlog](devlog/README.md),
so the reasoning in this document stays traceable over time.