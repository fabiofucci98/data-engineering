# Simulated City — What to Simulate (and how it feeds the platform)

> **Status: DRAFT — living planning note.** Started 2026-09-30, updated as the planning
> conversation evolves. Nothing here is implemented — this is `notes/` thinking space.
> When any piece becomes real, it moves to the README / `TECHNOLOGIES.md` and this note
> records that it did.

## The idea (one paragraph)

Build a **simulated city** that generates believable, on-demand data about roads, people,
and their day-to-day activity — used as the *pressure supplier* for the
[`add-until-it-breaks.md`](add-until-it-breaks.md) loop: arbitrary volume, velocity, and
controlled chaos, without waiting on real-world API rate limits or on nature to produce
events. Build it **gradually**: first the **roads** (geography), then the **people**
(population), then the **data about their day** (telemetry/events). A key design
requirement from the human: the simulated data will live in **different databases /
services**, so the platform must learn to pull from the *correct* source — or consume
each service's API — exactly like the real multi-source world this platform is heading
toward. This note currently focuses on **what to simulate**; the how (pipeline, infra)
comes after the domain is decided.

## Why this note exists

The add-until-it-breaks strategy needs *data on demand*. Real scientific APIs (USGS,
NASA, NOAA…) are rate-limited and, more importantly, **slow by nature** — you can't
schedule a million earthquakes. A simulator can: 1M rows in seconds, repeatable
(seeded), and it can inject the failures (duplicates, gaps, spikes) that real APIs won't
hand you on schedule. Real scientific data stays the **endgame** (analytics + ML on real
sources); the simulator is the training ground that makes the platform volume-proof first.

## Guiding requirement (from the human, 2026-09-30)

> The data will stay in different databases, so the platform has to pull from the correct
> one — or an API is created for that service and the data is pulled from there.

Consequences we design *for* from day one (even if the first build is simpler):

- Every entity has a clear **owning source** (`geo` / `people` / `events`) — like a
  service boundary.
- Natural keys are **stable and global** (e.g. `person_id`, `road_segment_id`) so the
  platform can join across sources even when they are separate.
- Ingestion becomes **source-aware**: a *source registry* (which endpoint/DB holds what)
  decides where each pull goes — the "pull from the correct one" skill.
- Cross-source analytics (people × telemetry × geography) is a first-class exercise, not
  an afterthought.

## What to simulate — the domain model (built gradually)

### Layer 0 — Geography: roads & places *(static reference data, the base)*

| Entity | Attributes that matter | Notes |
|---|---|---|
| `districts` | id, name, type (downtown / residential / industrial / park), polygon/bbox | coarse spatial grouping |
| `road_segments` | id, endpoints, length_m, road class, speed limit, lanes, capacity/h | the traffic backbone |
| `intersections` | id, coords, control (light / stop / roundabout) | connects segments |
| `buildings` | id, type (home / office / school / shop / hospital), capacity, coords, district | home + workplace are the minimum |

*Emits:* mostly **static reference** tables; later, slow changes (road closures, new builds).

### Layer 1 — People & devices *(the population, dimension data)*

| Entity | Attributes that matter | Notes |
|---|---|---|
| `residents` | id, home building, workplace building, commute mode (car / bike / transit / walk), work hours, car ownership | the "agents" of the sim |
| `vehicles` | id, owner, fuel type (ICE / EV) | traffic + later CO₂ angle |
| `devices` | id, owner, type (phone / car tracker / smart meter), polling cadence | what "emits" telemetry |
| `meters` | id, building, type (energy / water) | building-level time series |

*Emits:* **dimension** rows; slow-changing facts (someone moves, buys an EV) come later.

### Layer 2 — Day-to-day activity *(the actual data stream — the "big data")*

Each resident follows a daily **schedule template** (home → commute → work → errands →
home) with variance. The simulation steps time and emits **events** with natural keys
(e.g. `(<device_id>, <timestamp>)`) so the existing **idempotent upsert** pattern applies
as-is:

| Stream | What it emits | Killer feature |
|---|---|---|
| Traffic | GPS pings per vehicle; per-road occupancy per 5 min | highest volume; map-friendly |
| Air quality | neighborhood sensor reads per 5 min, **correlated with traffic load** | gives data a "science" story: traffic → emissions → AQ |
| Energy | smart-meter reads per building per 15 min | morning/evening spikes; easy to scale later |
| Transit | tap-in / tap-out events at stations | event-shaped, less map-heavy |
| Water | household reads per hour | simple, steady |

*Start small:* **traffic + air quality** are the recommended first pair (correlated, feed
both maps and time series, and they make cross-source ML interesting later).

### Layer 3 — Distributed sources *(the "pull from the correct one" skill — staged)*

| Stage | What it is | What you practice |
|---|---|---|
| A | One Postgres, three **schemas** (`geo`, `people`, `events`) | learn the entity model before paying infra cost |
| B | Three **separate databases** (one `db` service each, or one instance with three DBs) | source registry: config-driven "which source do I pull" |
| C | Each source behind its **own API** (FastAPI) | ingestion talks HTTP exactly as it does to USGS today — local and breakable on purpose; retries, schema drift, wrong-source bugs |

Cross-source analytics (e.g. "is this downtown AQ spike explained by traffic?") is the
recurring exercise at every stage.

## Dials (later, at build time)

Resident count · tick rate · time horizon · noise / missing % / duplicate % · spike
probability · **seed** (reproducible experiments). These feed the pressure menu P1–P5 in
[`add-until-it-breaks.md`](add-until-it-breaks.md) unchanged — the simulator is the
**pressure supply**, that note stays the **how-to-pressure** playbook.

## Guardrails

- The simulator is a **data generator, not a product** — done when it emits believable
  data at the volume/velocity we dial. No over-engineering realism.
- Least complex tool that fits: no Kafka/streaming framework until the simple Postgres
  pipeline visibly groans (same ladder as add-until-it-breaks).
- Multi-source is a *guiding requirement*, but the **first build may be Stage A** to
  learn the domain first — splitting comes when it teaches something.
- README stays current-state-only; this whole note is `notes/` until pieces are real.

## Decisions & outcomes — this conversation

- **2026-09-30** — Decision: **build the simulated city** as the platform's pressure
  supplier, built **gradually** (roads → people → day-to-day data). Current focus =
  deciding **what to simulate** (this note). The multi-database / per-service-API design
  ("pull from the correct source") is adopted as a **guiding requirement** for the later
  layers.
- **2026-09-30** — Human answered all six "what to simulate" questions (decisions below)
  and asked for a concrete Phase 0 build spec: **one containered app filling a dedicated
  Geography DB up to a target size** — see
  [`city-geo-simulation.md`](city-geo-simulation.md).

## Decisions — what to simulate (all resolved 2026-09-30)

- City shape → **fictional stylized grid**.
- Start size → **~1,000 residents** (a reference for later phases, not generated in Phase 0).
- First telemetry streams → **none for now**; Phase 0 is geography only.
- Time model → **yes**: 24-h synthetic days, weekday/weekend variance, **seeded** for reproducibility.
- Source split → **one dedicated DB for Geography** for now (multi-source split is a later phase).
- Buildings → **8 types**: houses, schools, shops, workplaces, hospitals, parks,
  restaurants, and civic/culture — formulas in
  [`city-geo-simulation.md`](city-geo-simulation.md).
- Phase 0 status → **Layer 0 (geography) implemented 2026-09-30**; layers 1–3 (people,
  telemetry, multi-source split) remain future.
- City planning → **inputs are population + buildings-per-block**, from which grid size,
  road network, and building counts all derive via formulas (houses = people /
  household size, schools = children / capacity, grid side = f(total buildings), …) —
  first draft in [`city-geo-simulation.md`](city-geo-simulation.md).
- Naming → **no AI at runtime, steam-punk themed**: entity names are deterministic
  compounds from editable word dictionaries (e.g. 3-word road names) whose product space
  can explode far beyond any realistic city size.
- Geo storage → **a dedicated new Postgres container** (`city-db`, host port 5434),
  separate from the existing platform `db`; schema auto-applied by Postgres at first
  boot (`city-simulation/sql/city.sql` → `/docker-entrypoint-initdb.d/`), platform pattern.

## Related

- [`add-until-it-breaks.md`](add-until-it-breaks.md) — the pressure-based learning loop the simulator feeds
- [`city-geo-simulation.md`](city-geo-simulation.md) — Phase 0 build spec for the geography generator app
- [`vision-and-roadmap.md`](vision-and-roadmap.md) — Phase 3 "multi-source federation": the simulator trains exactly this muscle, locally
- [`scientific-live-data-sources.md`](scientific-live-data-sources.md) — the real sources that return once the platform is volume-proof