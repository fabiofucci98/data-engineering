# 2026-09-27 — TECHNOLOGIES.md Lists Only Current Tools

## Status
🟢 Rewrote `TECHNOLOGIES.md` from a per-stage roadmap into a "currently in use" document.

## Context

The human asked that the technologies document only specify current technologies.

## What happened / Decisions made

- Removed the Stage 0–6 plan tables (future schedulers, dbt, ML tooling, extra data sources).
- `TECHNOLOGIES.md` now lists only what the codebase actually runs — with versions and where
  each tool appears — plus a policy note: future tools are added only once adopted.
- Fixed `README.md` and `.cline/rules/project-rules.md` references that described it as a "plan".

## Who did what

- **Agent (Cline):** rewrote the document and the cross-references.
- **Human:** requested the change; will review and commit.

## Verification

- Repo search shows no remaining references that call `TECHNOLOGIES.md` a "plan" or "per stage".

## Next steps

- Human reviews and commits the change.