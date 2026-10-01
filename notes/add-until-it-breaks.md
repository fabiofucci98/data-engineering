# Add Until It Breaks — Performance-Led Learning Plan

> **Status: DRAFT — living planning note.** Started 2026-09-29, updated as the planning
> conversation evolves. Name confirmed: `add-until-it-breaks.md` (2026-09-29).
> Nothing in this file is implemented — this is `notes/` thinking space (see
> `notes/README.md`). When a technique from here becomes real, it moves to the README /
> `TECHNOLOGIES.md` and this note records that it did.

## The strategy (one paragraph)

Stop choosing the next stack component on paper. **Grow the workload on purpose** — more
data, more sources, heavier analytics, even a small ML experiment — until the current
simple stack (single Postgres + one Streamlit process + a manual ingest script) becomes
*visibly* slow. Each slowdown is a signal that names the next data-engineering
technique/tool to learn. The symptom picks the tool; the roadmap
(`notes/vision-and-roadmap.md`) stays the place where adopted techniques land.

### The loop

1. **Add** a workload ingredient (history backfill / new source / analytics / ML / dashboard weight).
2. **Measure** the pain so it is visible (query time, dashboard load, ingest duration, row counts).
3. **Diagnose** the bottleneck (`EXPLAIN ANALYZE`, `pg_stat_statements`, timings).
4. **Fix** with the *least complex* technique that removes it (see ladder below).
5. **Lock in** the learning: update `TECHNOLOGIES.md` + `CHEATSHEET.md` when the technique
   is actually adopted.

## Current baseline (2026-09-29 — read from the code)

| Layer | Today | Known weak spot |
|---|---|---|
| Data | ~2k rows in one `earthquakes` table (USGS, last ~30 days, mag ≥ 2.5) | Tiny — nothing can be slow yet |
| Ingest | Manual `docker compose -f scientific-data/docker-compose.yml run --rm earthquakes-app python ingest.py`; idempotent upsert on `event_id` | No scheduler; nobody notices staleness |
| Storage | Postgres 16 (Docker); indexes on `(time)` and `(mag)` only | Filter/join-heavy queries will seq-scan |
| Dashboard | Streamlit; 1 parameterized query per run + `st.cache_data(ttl=60)`; pandas does `resample`/`value_counts` in app memory | Whole-result pull; `st.map` will choke on big point sets |
| Observability | None | Can't tell "it got slow" from "it broke" |

## Pressure menu (ingredients we add on purpose)

| # | Ingredient | How to add it | Expected pain | Technique the pain unlocks |
|---|---|---|---|---|
| P1 | History backfill | USGS full catalog (e.g. 2000→now, lower min mag) → 10⁵–10⁶ rows | slow scans, slow `st.map`/charts, big memory | covering indexes → materialized views / precomputed aggregations → partitioning |
| P2 | High-frequency source | NOAA space weather (Kp index ~3h, solar wind ~1 min) or OpenAQ | stale data, many small writes, wider/normalized schema | scheduling → incremental loading → orchestration (retries/backoff/alerting) |
| P3 | Heavy analytics | cross-source time-series (e.g. quake rate vs Kp-index spikes), rolling windows | repeated heavy recompute in the dashboard | transformation layer / analytics-ready tables (plain SQL first, dbt only when demanded) |
| P4 | Small ML experiment | e.g. forecast next-day quake rate; cluster aftershocks | feature engineering over full history is slow | feature/analytics tables, maybe an analytics engine for reads |
| P5 | Dashboard + users | more charts (scatter maps, drill-downs), several open sessions | query storm, pool exhaustion | caching, indexes, query budgets, monitoring |

*(First round decided 2026-09-29: M1 = P3 + P4 analytics & tiny ML — see "Milestones".
P1/P2/P5 stay in the menu for later rounds.)*

## Ladder — symptom → next component (least complex first)

| Symptom | Next step |
|---|---|
| Dashboard/queries get sluggish on big filters | Explain plans → add indexes; then precompute the hot aggregations (SQL `VIEW` / materialized view) |
| Hot aggregations still recomputed every run | Refine to an **analytics-ready table** (a mart) refreshed incrementally; dashboard queries marts, not raw rows |
| Data goes stale / loads forgotten | Timer-based scheduling in the container (cron) → custom runner with retries/backoff → **Prefect** when real DAGs + alerting appear (Airflow only if that's outgrown) |
| One Postgres groans under analytics + OLTP | Keep Postgres as system of record; point heavy analytics at **DuckDB** over an exported Parquet/index dump (cheap, local, columnar) |
| ML training queries too slow | Build feature tables **once** (materialized), not per run; consider DuckDB as the feature/analytics engine |
| "Slow" vs "broken" indistinguishable | Start an observability log: `EXPLAIN ANALYZE`, `pg_stat_statements`, an `ingest_runs` timing table, dashboard-side timings |

## Milestones (concrete plan)

### M1 — Analytics layer + tiny ML, data enabler included (P3 + P4) — chosen 2026-09-29

*Goal:* real analytics on real history, with query timings visible on screen — so the first
real numbers show what "it's getting slow" looks like.

1. **Enabler — give analytics something to chew on.** ~2k rows can't hurt anything. Backfill
   USGS history with the existing idempotent ingest (same table, same upsert; just a wider
   date range, e.g. 2000→now @ mag ≥ 2.5 → 10⁵–10⁶ rows).
2. **Analytics queries — plain SQL first (least complex).** New `app/analytics.py` (CLI +
   importable) exposing:
   - rolling quake rate: daily counts + 7-day rolling mean,
   - depth-vs-magnitude profile,
   - swarm detector: per 5° grid cell, daily-count z-score; flag cells/weeks that spike,
   - big-quake context: for every event ≥ M5, small-quake activity within ±2° / ±30 days before.
   Each query prints its plan + duration (`EXPLAIN (ANALYZE, BUFFERS)` + wall time).
3. **Tiny ML (P4) — one experiment.** Binary classifier: "within 24 h will this grid cell see
   a quake ≥ M?" — features built in SQL (recent rate, max recent mag, mean depth, hour of
   day), logistic regression (scikit-learn) as the least-complex entry. Training loop stays a
   plain script; no framework.
4. **Dashboard:** new "Analytics lab" section rendering the heavy outputs, each with a small
   "⏱ <duration>" caption so slowness is visible on screen.
5. **Thresholds:** the human declares "broken enough" per symptom; until then we only record
   timings (a `query_timing` table or log lines), never guess.

*After M1:* whatever hurts first picks the ladder step — likely precomputed aggregations
(views/marts) with incremental refresh, or scheduling once refresh gets forgotten.

**When implemented:** new deps (e.g. `scikit-learn`) enter `requirements.txt` +
`TECHNOLOGIES.md` in the same change, and M1 is "done" only when verified (definition of
done rule).

## Guardrails (project rules we keep)

- Least complex tool that fits; **no Airflow/dbt/ML before the MVP** — and when anything
  above is adopted, `TECHNOLOGIES.md` + `CHEATSHEET.md` are updated in the same change.
- README stays current-state-only; this note lives in `notes/` until pieces are real.
- The devlog records what *actually happened*; this note records what we *plan*.
- Big changes: plan → human approves → implement (agents never commit/push).

## Decisions & outcomes — this conversation

- **2026-09-29** — Strategy adopted: **"add until it breaks"** — grow workloads on purpose
  so visible slowdowns dictate the next technique/tool. Note created (working name
  `add-until-it-breaks.md`, name TBD), `notes/README.md` index updated.
- **2026-09-29** — Decision: first pressure ingredient = **P3 + P4, analytics + tiny ML**
  (M1 above), with a modest USGS history backfill as its enabler (2k rows can't hurt).
  P1/P2/P5 stay in the menu for later rounds.
- **2026-09-29** — Decision: **"broken enough" thresholds are the human's to declare** —
  this note only records timings; no numbers are invented here.
- **2026-09-29** — Decision: note name stays **`add-until-it-breaks.md`**.

## Open questions

- [x] Which pressure ingredient first → **P3+P4 analytics + tiny ML** (M1), with a modest USGS backfill as enabler. *(decided 2026-09-29)*
- [ ] "Broken enough" thresholds — **the human declares these** when they hurt; only timings are recorded until then.
- [x] Note name → `add-until-it-breaks.md`. *(decided 2026-09-29)*