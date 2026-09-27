# Project Rules — Scientific Data Platform

These rules apply to **everyone working in this repository**: humans and AI agents.

## 1. Project identity

- This project **starts small** (USGS Earthquakes → Docker + Postgres → simple visualization) but is
  **the beginning of a larger platform**: more scientific data sources later, **culminating in an ML
  project**. Design decisions must not paint us into a single-source corner.
- Keep the README's **WORK IN PROGRESS** framing honest: never claim functionality that doesn't exist.

## 2. Code and structure

- **Python 3.11+** is the language end to end.
- Upcoming layout (follow it once Phase 1 starts):
  - `docker-compose.yml` at the repo root.
  - Application code under `app/`.
  - Raw/processed data references under `data/` (never commit large payloads).
- Keep code **simple and readable** — this is a learning project first, a platform second.
- Use `venv` + `requirements.txt` (or equivalent) for dependency pinning.

## 3. Don't break the learning path

- Favor the **least complex tool that fits** (Per README/TECHNOLOGIES.md plan). Don't introduce
  Airflow, dbt, or ML frameworks before the MVP exists — their time comes later.
- When a stage advances, **update `TECHNOLOGIES.md`** to reflect reality.

## 4. Data handling

- **Never commit secrets or API keys.** Use `.env` files (git-ignored) and `.env.example`.
- Only commit small sample datasets. Never commit bulk raw data.
- Prefer idempotent ingestion (re-running a load must not duplicate rows) from the very first script.

## 5. Version control

- Keep commits small, focused, and frequent.
- Commit message style: short imperative summary, e.g. `Add docker-compose for postgres`,
  `Fix retry logic in ingestion script`.
- Update the devlog entry on any non-trivial change (new milestone, tool change, blocked work).

## 6. Devlog discipline

- The `devlog/` folder documents the *why*. New milestone or decision → new dated entry
  (`YYYY-MM-DD-slug.md`) following `devlog/README.md`.
- Be honest, including about failures and blockers (🔴 entries are valuable, not shameful).

## 7. Agent-specific behavior

- **Never edit files without confirming the current state first** (read before write).
- Verify changes after making them (e.g., run the code, re-read the edited file).
- If a task is ambiguous, ask a clarifying question instead of guessing.
- Follow these rules across the whole session, not just the first response.

## 8. Definition of "done" for a task

1. Meets the requirement as stated (or clarified).
2. Follows the conventions above.
3. Verified to work (commands run / files re-read).
4. Documented: devlog updated when warranted, README/`TECHNOLOGIES.md` kept truthful.