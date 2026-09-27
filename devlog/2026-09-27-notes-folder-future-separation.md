# 2026-09-27 — notes/ Folder: README = Current, notes = Future

## Status
🟢 Created `notes/`; moved future plans out of the README; rules updated.

## Context

The human asked to add a `notes/` folder, move everything not yet implemented there
(e.g., README's future content), make the README reflect only the current state, and
update the rules.

## What happened / Decisions made

- Created `notes/` with a `README.md` (purpose + rules) and `vision-and-roadmap.md`
  (the multi-phase vision + roadmap, moved out of the README).
- Moved `scientific-live-data-sources.md` (the human's candidate future data sources)
  from the repo root into `notes/`, unmodified.
- Rewrote the README: removed the "Vision" table and "Roadmap" section; the banner and
  architecture caption now describe only the current state; the layout lists `notes/`.
- Updated `.cline/rules/project-rules.md`:
  - Layout bullet: future plans live under `notes/`, never in the README.
  - New documentation rule: README describes the current state only; when an idea becomes
    real, move it from `notes/` into the README.

## Who did what

- **Agent (Cline):** created the notes folder and files, moved the data-sources doc,
  rewrote the README, updated the rules.
- **Human:** requested the restructure; will review and commit.

## Verification

- Repo search: the README no longer contains the roadmap/vision sections; future content
  now lives in `notes/` only.

## Next steps

- Human reviews and commits.
- Future phase work (Phase 2+) is tracked in `notes/vision-and-roadmap.md`.