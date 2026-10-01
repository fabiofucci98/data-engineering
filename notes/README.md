# Notes — Future & Thinking Space

This folder is for **ideas, plans, and visions that are not yet implemented**.
It exists so the root `README.md` can honestly describe only the current state.

## Rules

- Everything in this folder is **not implemented**. When a note becomes real, update the
  README (and `TECHNOLOGIES.md`), then mark the note done or archive it — see
  `.cline/rules/project-rules.md`.
- The devlog records what *actually happened*; these notes record what we *want to happen*.
- Notes may be scrappy, exploratory, or wrong — that is their purpose. No claims here
  count as "the project does X".

## Contents

| File | What it is |
|---|---|
| [`vision-and-roadmap.md`](vision-and-roadmap.md) | The bigger vision and the phases planned ahead |
| [`scientific-live-data-sources.md`](scientific-live-data-sources.md) | Candidate future data sources (NASA, NOAA, OpenAQ, …) — originally authored at repo root by the human, moved here |
| [`add-until-it-breaks.md`](add-until-it-breaks.md) | Performance-led learning plan: grow the workload on purpose until it visibly breaks, let the pain pick the next technique/tool |
| [`city-simulation.md`](city-simulation.md) | Simulated city as the data generator for the learning loop — roads → people → day-to-day data, split across sources so ingestion practices pulling from the right one |
| [`city-geo-simulation.md`](city-geo-simulation.md) | ✅ **Phase 0 implemented (2026-09-30)** — design reference for the working city generator (`city-simulation/` stack): fictional grid city into its own `city-db` Postgres; population + buildings-per-block in, formulas + no-AI name pools out |