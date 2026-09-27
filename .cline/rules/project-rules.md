# Project Rules — Scientific Data Platform

These rules apply to **everyone working in this repository**: humans and AI agents.

## 1. Project identity

- This project **starts small** (USGS Earthquakes → Docker + Postgres → simple visualization) but is
  **the beginning of a larger platform**: more scientific data sources later, **culminating in an ML
  project**. Design decisions must not paint us into a single-source corner.
- Keep the README's **WORK IN PROGRESS** framing honest: never claim functionality that doesn't exist.

## 2. Code and structure

- **Python 3.11+** is the language end to end.
- Layout (in use since Phase 1):
  - `docker-compose.yml` at the repo root.
  - Application code under `app/`.
  - Raw/processed data references under `data/` (never commit large payloads).
  - Future plans and ideas live under `notes/` — never in the README.
- Keep code **simple and readable** — this is a learning project first, a platform second.
- Use `venv` + `requirements.txt` (or equivalent) for dependency pinning.

## 3. Don't break the learning path

- Favor the **least complex tool that fits**. Don't introduce
  Airflow, dbt, or ML frameworks before the MVP exists — their time comes later.
- When a stage advances, **update `TECHNOLOGIES.md`** to reflect reality.

## 4. Data handling

- **Never commit secrets or API keys.** Use `.env` files (git-ignored) and `.env.example`.
- Only commit small sample datasets. Never commit bulk raw data.
- Prefer idempotent ingestion (re-running a load must not duplicate rows) from the very first script.

## 5. Version control

- **Agents must NEVER run `git commit` or `git push`.** Version control belongs to the human:
  agents prepare and verify changes, then hand them over for the human to stage, review,
  commit, and push.
- Keep commits small, focused, and frequent.
- Commit message style: short imperative summary, e.g. `Add docker-compose for postgres`,
  `Fix retry logic in ingestion script`.
- Update the devlog entry on any non-trivial change (new milestone, tool change, blocked work).

## 6. Devlog & documentation discipline

- The `devlog/` folder documents the **why** — decisions, milestones, blockers — and is also a
  **learning journal**: what the human is learning, discovering, and struggling with, as they go.
  New milestone, decision, or notable learning → new dated entry (`YYYY-MM-DD-slug.md`)
  following `devlog/README.md`.
- Be honest, including about failures and blockers (🔴 entries are valuable, not shameful).
- **Never fabricate the human's learning journey.** The devlog is the human's own account:
  agents never claim that the human learned, discovered, or struggled with something they
  didn't express. When an agent writes an entry, it must state plainly who did what.
- **Keep `CHEATSHEET.md` (repo root) up to date**: any command, flag, or syntax snippet that
  proves useful — or a gotcha that cost time — belongs there so it is never relearned.
  A stage that introduces new tooling should update it in the same change.
- The **README describes the current state only**: anything not yet implemented belongs in
  `notes/` (the thinking space for the future). When an idea becomes real, move it from
  `notes/` into the README and mark the note accordingly.

## 7. Agent-specific behavior

- **Never run `git commit` or `git push`** — version control is the human's job, always.
- **Never write devlog content in the human's voice** or attribute learnings/experiences to
  the human that they did not express. Keep "who did what" strictly factual.
- Keep `CHEATSHEET.md` and the devlog current while working; surface learning moments
  (new discoveries, solved problems) for the human to capture.
- **Never edit files without confirming the current state first** (read before write).
- Verify changes after making them (e.g., run the code, re-read the edited file).
- If a task is ambiguous, ask a clarifying question instead of guessing.
- Follow these rules across the whole session, not just the first response.

## 8. Definition of "done" for a task

1. Meets the requirement as stated (or clarified).
2. Follows the conventions above.
3. Verified to work (commands run / files re-read).
4. Documented: devlog updated when warranted, README/`TECHNOLOGIES.md` kept truthful.