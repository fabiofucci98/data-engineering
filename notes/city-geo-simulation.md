# City Geo Simulation — Phase 0 (the geography generator app)

> **Status: ✅ IMPLEMENTED (2026-09-30)** — the Phase 0 build described below exists and
> is verified working (`city-simulation/` stack: `city-db` + `citygen`, `pools/`,
> `sql/city.sql`). Kept as the design reference. Parent vision note:
> [`city-simulation.md`](city-simulation.md).

## What we are building (one paragraph)

**One containered Python application** (a new `citygen` Docker service) that generates a
**fictional grid city** — grid, road segments, intersections, districts, and buildings —
into a **new dedicated Postgres container (`citydb`)**, and **keeps filling the DB until
it reaches its target size**, then stops. Re-running **resumes and never duplicates**
(same fill-up-to-target + idempotent upsert discipline as `app/ingest.py`).
**The population (plus buildings-per-block) is the input**: the program is told how many
people the city will have, and derives everything else — grid size, road network, and
every building count — via city-planning formulas (see below). Entity names are
**deterministic and dictionary-driven — no AI at generation time** (see "Names"). People
themselves and day-to-day telemetry are later phases; this phase is geography only.

## Decisions locked for Phase 0 (human, 2026-09-30)

| # | Question (from `city-simulation.md`) | Decision |
|---|---|---|
| 1 | City shape | **Fictional stylized grid** — no real-world coordinates |
| 2 | Start size | **~1,000 residents** as the population reference for later phases (not generated in Phase 0) |
| 3 | First telemetry streams | **None for now** — Phase 0 is geography only |
| 4 | Time model | **Yes** — 24-h synthetic days, weekday/weekend variance, **seeded** (seed discipline starts now, even while geometry-only) |
| 5 | Source split | **One dedicated DB for Geography** for now (multi-source split is a later phase) |
| 6 | Buildings | **Yes — other building types too** (homes + offices + schools + shops + hospitals) |
| 7 | Target "size" | **Row counts per table** (confirmed) — derived from the population via formulas |
| 8 | Where the geo DB lives | **A new Postgres container** (`citydb`), separate from the platform `db` |
| 9 | App & DB naming | Services `citydb` + `citygen`, script `generate.py`, database `city` (chosen by agent) |
| 10 | Program inputs | **Population** + **buildings-per-block** (+ `--seed`); everything else derives |
| 11 | Grid size | Derives from population **and** buildings-per-block (both are inputs) |
| 12 | Naming | **No AI at runtime** — deterministic compound names from component dictionaries (e.g. 3-word road names) that can explode combinatorially |

## The fictional grid city (what we actually simulate)

- **Grid:** a simple N×M street grid whose **size is derived from the population and
  buildings-per-block** (see "City planning formulas" below); N and M are picked so it
  looks roughly square (`side = ceil(sqrt(blocks needed))`). Street names come from the
  **3-word name dictionaries** (see "Names" below). Intersection and road-segment counts
  follow from the grid side.
- **Districts:** downtown (core few blocks), residential rings around it, one industrial
  edge zone, 2–3 parks/squares. Type drives placement rules.
- **Road segments:** between consecutive intersections; road class (avenue / main /
  residential), speed limit, lanes, capacity/h. Child rows of intersections.
- **Buildings:** **counts come from city-planning formulas driven by the population**
  (see next section); placement per district rules — shops/food cluster downtown, homes
  fill residential rings, industrial on the edge, schools/hospitals distributed. Each
  has type, capacity, district, and a stable address-like id.
- **Seed:** one CLI `--seed` → the same city comes out every time (verifiable runs,
  repeatable experiments later).

## City planning formulas (the population is the core)

The **population is the single input**; every building type gets its count derived from
it through an explicit formula with named assumptions — same reasoning as the human's
draft: 1,000 people ÷ 3 per household → **333 houses**; 1 child per household → 333
children ÷ 150 per school → **3 schools**. First draft (ALL assumptions are guesses for
us to tune, not laws):

| Building type | Serves | Draft formula | Assumptions (draft) | @ 1,000 people |
|---|---|---|---|---|
| Houses (residential) | residents | `houses = floor(people / household_size)` | household_size = 3 | 333 |
| Schools (education) | children | `children = houses × kids_per_household`; `schools = ceil(children / school_capacity)` | kids_per_household = 1; school_capacity = 150 | 3 |
| Shops (retail) | residents | `shops = ceil(people / residents_per_shop)` | 1 shop serves 250 residents | 4 |
| Workplaces (offices, light industry) | workers | `workers = (people − children) × participation_rate`; `workplaces = ceil(workers / workplace_capacity)` | participation 80%; capacity 100 | 6 |
| Hospitals / clinics (healthcare) | residents | `hospitals = max(1, ceil(people / residents_per_hospital))` | 1 per 5,000 residents; min 1 | 1 |
| Parks (recreation) | residents | `parks = max(1, ceil(people / residents_per_park))` | 1 per 2,000 residents; min 1 | 1 |
| Restaurants (food) | residents + workers | `restaurants = ceil(people / residents_per_restaurant)` | 1 restaurant serves 250 people | 4 |
| Civic / culture (town hall, clock tower, guild hall, opera house) | residents | `civic = max(1, ceil(people / residents_per_civic))` | 1 per 2,000 residents; min 1 | 1 |

The grid itself is derived too — a city needs room for its buildings:

| Item | Draft formula | Assumptions (draft) | @ 1,000 people |
|---|---|---|---|
| Blocks | `blocks = ceil(total_buildings / buildings_per_block)`; grid side `side = max(3, ceil(sqrt(blocks)))` | **buildings-per-block is an input** (default 8); min side = 3 | ~353 buildings → side 7 (49 blocks) |
| Intersections | `(side + 1) × (side + 1)` | — | 64 |
| Road segments | `2 × side × (side + 1)` | — | 112 |

So `--population 1000 --buildings-per-block 8` yields the buildings *and* the grid,
streets, and intersections they live in. Placement (which block gets which
building/district) is a layout step inside the generator, not a count formula — counts
are what we formula-ize.

- Rounding: houses use `floor` (matches the human's 333); everything else uses `ceil` so
  supply covers demand.
- Draft total: **~353 buildings** for 1,000 people — small enough to verify by hand.
- These formulas become a single "planning assumptions" block inside the generator so
  they are readable and retunable; the **inputs are `--population`,
  `--buildings-per-block`, and `--seed`**, targets are *derived*, and per-table
  `--target-*` overrides remain as an escape hatch for pressure experiments later.

## Names — deterministic, no AI (dictionary-driven)

- **Rule:** names are generated *offline and deterministically* from **component
  dictionaries** — never by an AI/LLM at runtime. Same `--seed` → same city, identical
  names, every time.
- **Theme (chosen 2026-09-30): steam punk** — pools lean toward gears, brass, copper,
  steam, clockwork, airships, boilers, valves, foundries.
- **Pool files created 2026-09-30** under `city-simulation/pools/` — one file per pool
  (see `city-simulation/pools/README.md`); add words anytime, no code changes.
- **Road names = 3 words**, one drawn from each of three pools
  (`city-simulation/pools/road_first.txt`, `city-simulation/pools/road_middle.txt`,
  `city-simulation/pools/road_type.txt`), e.g.
  "Gilded Gear Avenue", "Copper Cog Way". Distinct names = |first| × |middle| × |type|
  — the seeded pools (34 × 40 × 25) yield **34,000 road names** vs ~112 roads needed at
  1,000 people.
- **Every entity type gets a naming recipe:**

| Entity | Recipe (one word drawn from each pool) | Example (steam punk) |
|---|---|---|
| Roads | `[first] [middle] [type]` | "Gilded Gear Avenue" |
| Districts | `[character] [place]` | "Ember Foundry" |
| Parks | `[name] Park` | "Steamgarden Park" |
| Schools | `[name] [level]` (Elementary / Middle / High) | "Brassworks Elementary" |
| Hospitals | `[name] Medical Center / General Hospital` | "Ironheart General Hospital" |
| Shops | `[adjective] [noun]` | "Gilded Gears", "Clockwork Fixers" |
| Workplaces | `[noun] Works / Industries` | "Ironbridge Works" |
| Restaurants | `[noun] & [noun]` | "Cog & Kettle", "Gear & Griddle" |
| Civic / culture | `[name] [civic_type]` (Town Hall / Clock Tower / Guild Hall / Opera House) | "Ironheart Clock Tower" |

- **Explosion rule:** each entity's pools must support ≥ **100×** the largest count that
  city can produce, so even a far-bigger city still samples a drop in the bucket. Pools
  are plain text files (`city-simulation/pools/*.txt`, one word per line) — adding a
  line grows the space with no code changes.
- **Pair-type capacity (fixed 2026-09-30):** restaurant names ("X & Y") are drawn
  without replacement from the *combination* space `n × (n-1)`; with 34 words that is
  1,122 names (~population 140k at 1 restaurant per 250). Other pool types are plain
  products (`school_name × school_level`, …). If a run ever fails with "Need N …
  from pool 'X'", the message states the capacity — **grow that pool file**, it is the
  designed lever.
- **Uniqueness & determinism:** names are drawn **without replacement** from the
  combination space using the seed's RNG; if a pool ever ran dry (shouldn't happen), the
  fallback is appending a number. Names become columns on the rows — readable, stable
  lookup keys.

## The app (one containered application)

### Where it lives
- The `citygen` service + its **own `city-db` Postgres service** live together in
  `city-simulation/docker-compose.yml` (`python:3.13-slim` + `postgres:16-alpine`).
  `citygen` bind-mounts its code and pools, and reads `CITY_POSTGRES_*` env, pointing
  at host `city-db`.
- Runs on demand: `docker compose -f city-simulation/docker-compose.yml run --rm citygen
  python generate.py --population 1000 --buildings-per-block 8 --seed 42` — no scheduler
  yet, least complex tool.

### Target-size fill loop (the core behavior)
- Targets are **row counts** (the "specific size" from the human), **all derived from the
  inputs**: `--population 1000 --buildings-per-block 8` → **~353 buildings** + a grid of
  49 blocks (side 7) with 64 intersections and 112 road segments (see formulas above).
  Per-table `--target-*` overrides stay available for experiments.
- Loop: connect → **count current rows** → generate **only the missing rows** (natural
  keys, upsert) in small batches (e.g. 5k rows/write) → repeat until every count ≥
  target → print a summary (rows generated, durations, per-table counts) → exit 0.
- Idempotent by construction: identical parameters → no-op (never duplicates).
- **One canonical city per database**: the DB is keyed by `(population,
  buildings-per-block, seed)`. Anything different (a new seed, a resize) would merge two
  seed-shaped cities via overlapping natural keys — so it is refused with clear
  instructions. To generate a different city, reset the volume first:
  `docker compose -f city-simulation/docker-compose.yml down -v`.
- Byte-size targets (`--target-mb`) can be layered on later if wanted.

### Key design / idempotency (same disciplines as the USGS pipeline)
- Natural keys everywhere: `district_id`, `intersection_id` (ix, iy),
  `road_segment_id` (from/to intersection ids), `building_id` (block, slot).
- `INSERT ... ON CONFLICT ... DO NOTHING` (or UPDATE) per batch.
- All randomness via `random.Random(seed)` (or `numpy.random.default_rng(seed)`).

## Database layout (its own Postgres container)

- **Service `city-db`** (`postgres:16-alpine`) lives in `city-simulation/docker-compose.yml`,
  created *for the city* — the earthquakes stack (`scientific-data/`) and its DB stay
  separate. Host port **5434** (5432 = machine, 5433 = earthquakes DB); internal 5432.
- Database name: **`city`** (the geo source). Tables (Phase 0): `districts`,
  `intersections`, `road_segments`, `buildings`.
- Schema bootstrap: **Postgres auto-runs the SQL at first boot** (chosen 2026-09-30) —
  `city-simulation/sql/city.sql` mounted into `city-db`'s `/docker-entrypoint-initdb.d/`;
  the generator never creates tables.

## What this phase teaches (why it is worth building)

- **Generating data on purpose at a target volume** — the "pressure supply" for the
  add-until-it-breaks loop, without waiting on real APIs.
- **Population-driven city planning** — building counts fall out of explicit assumptions
  + formulas instead of being eyeballed (the human's core idea here).
- **Fill-up-to-target, idempotent loading** — the exact behavior real backfills use
  (resume, never duplicate).
- A **second containered workload** (`citygen`) using the same proven patterns — no new
  tooling, no new stack.
- **Reproducible synthetic data** (seed) → every later phase (people, telemetry,
  analytics) can re-run against the same city and compare.
- **Deterministic synthetic identity** — entity names explode combinatorially from
  editable word pools (no runtime AI), which is how synthetic data stays cheap, fast,
  and reproducible at any scale.

## Guardrails

- **Generator, not a product** — good enough + on target, then stop; no over-engineering
  realism (no traffic simulation, no daytime, no visuals).
- Least complex tool that fits: plain Python + the already-used `psycopg`/SQLAlchemy.
- One dedicated Postgres container now (`city-db`); the Layer 3 multi-source split is
  already alive (a second source = a second stack) and lands fully later.
- README stays current-state-only until this actually runs; when it does,
  `TECHNOLOGIES.md` + `CHEATSHEET.md` update in the same change.

## Decisions & outcomes — this conversation

- **2026-09-30** — Human answered all six "what to simulate" open questions (see the
  decisions table above) and requested this Phase 0 spec: **one containered app filling
  the geo DB up to a target size**. This note created.
- **2026-09-30** — Human added the core design rule: **the population is the core** —
  building counts derive from city-planning formulas (333 houses, 3 schools, …), the
  geo store becomes a **new Postgres container** (`citydb`), and the size target is
  **row counts**. Draft formula set added above (all assumptions explicitly tunable).
- **2026-09-30** — Human clarified the program's contract: **population is the only
  input** — grid size derives from the population too (no independent grid flag). Grid
  formulas added above; placement (which block gets what) stays a generator-internal
  step.
- **2026-09-30** — Human extended the inputs and set the naming rule: **buildings-per-block
  is a first-class input** (grid size = f(population, buildings-per-block)), and the
  program must **never call an AI at runtime for names** — entity names are deterministic
  compounds from editable component dictionaries whose product space can "explode" far
  beyond any realistic city. (Supersedes the earlier "population only" phrasing.)
- **2026-09-30** — Human set the name theme: **steam punk** (gears, brass, copper, steam,
  clockwork, airships…) and **kept the formula assumptions as-is** for now. Building
  types still open — shortlist in the open questions.
- **2026-09-30** — Human closed the building-type question: **8 types** — the original 6
  plus **restaurants** and **civic/culture** (town halls, clock towers, guild halls,
  opera houses). Hotels/inns and factories stay parked for the people phase.
- **2026-09-30** — Human brought the naming pools forward: **`pools/` folder created**
  (one file per pool, steam-punk word lists, `pools/README.md`) and confirmed **rows
  only** as the size target (byte-size targets deferred to later).
- **2026-09-30** — Human resolved the last open question: **schema bootstrap = A**
  (Postgres auto-runs `sql/city.sql` at first boot; the generator never creates tables).
  All Phase 0 design questions are now closed — the build spec is complete.
- **2026-09-30** — **Phase 0 built and verified** (`citygen` + `citydb` in compose,
  `sql/city.sql`, `pools/`). Evidence: 5 districts / 64 intersections / 112 road
  segments / 353 buildings @ `--population 1000 --buildings-per-block 8 --seed 42`;
  re-run inserts 0; dry-run equals the written city; seed 42 twice identical. Two bugs
  found & fixed during the build (district-preference KeyError, district id/name dict
  swap) — devlog block 10. README documents the running state.
- **2026-09-30** — Human finding logged (**no code changed**): the generator "simulates
  all the data at once" — fine while the data is small or real-time isn't needed, but a
  poor fit for very large cities and the future time-ordered people/telemetry layers.
  Captured under "Known limitations" above; likely future shape: stream/tick mode with
  incremental fills.

## Phase 0 specifics — all resolved (2026-09-30)

- [x] Formula assumptions: the draft set (household_size = 3, 1 child/household, capacity
      150/school, 1 shop per 250 residents, 80% participation, 1 hospital per 5,000,
      1 park per 2,000) — **kept as-is (human, 2026-09-30)**.
- [x] Building types: **8 chosen (human, 2026-09-30)** — the original 6 plus restaurants
      and civic/culture. Hotels/inns and factories deferred to later phases (kept here
      as history, not lost).
- [x] Naming pools: **created under `pools/`** (2026-09-30) — one file per pool,
      steam-punk word lists; grow anytime by adding lines.
- [x] Schema bootstrap: **A — Postgres auto-runs the SQL on first boot** (chosen
      2026-09-30), the platform `db` pattern; new `sql/city.sql` mounted into
      `citydb`'s `/docker-entrypoint-initdb.d/`. `generate.py` never creates tables.
- [x] Byte-size targets — **deferred (human, 2026-09-30)**; rows only for now.

→ **Phase 0 is implemented (2026-09-30)** — verified in the running stack; the README
documents the current state and the devlog (block 10) records how it was built.

## Known limitations — human findings (no code changed)

- **2026-09-30 — "All the data is simulated at once."** The current generator is a
  one-shot bulk fill: one run computes the whole city and fills the DB to its targets.
  That only makes sense when the amount of data to generate is small (Phase 0: ~353
  buildings, sub-second) **or** when real-time behaviour simply isn't needed. It does
  NOT fit: (1) very large cities (a single bulk run becomes slow/heavy as rows scale),
  and (2) the future people/telemetry layers, which are time-ordered and continuous —
  data that appears *over time* rather than in one burst. Likely future direction: a
  "stream / tick mode" that generates a slice of time per run (incremental fills, on a
  schedule) instead of the whole world at once — cross-references the P2 pressure
  ingredient in [`add-until-it-breaks.md`](add-until-it-breaks.md). Logged as a finding;
  nothing changed yet.

## Related

- [`city-simulation.md`](city-simulation.md) — the parent "what to simulate" note (domain model + Layer 3 staged plan)
- [`add-until-it-breaks.md`](add-until-it-breaks.md) — the loop this simulator feeds