# 2026-09-27 — Cheat Sheet & Honest Devlog Rules

## Status
🟢 New `CHEATSHEET.md` + rules to keep it (and the devlog) fresh. Fixed a devlog entry
that falsely claimed learnings in the human's voice.

## Context

After Phase 1, the human asked for: (1) a command/syntax reference file, (2) rules to keep
that file and the devlog updated, and (3) a devlog that reflects the human's **actual**
learning journey. They also made clear that honesty is non-negotiable.

## What happened / Decisions made

- Created `CHEATSHEET.md` (Git · Docker/Compose · PostgreSQL/psql · Python/venv/pip ·
  USGS API · Streamlit) collecting commands that were actually used and verified in Phase 1.
- Updated `.cline/rules/project-rules.md`:
  - Rule: keep `CHEATSHEET.md` up to date whenever a new command, flag, or gotcha appears.
  - §6 renamed to "Devlog & documentation discipline": the devlog must record the learning
    journey — and only the human's *real* one.
- Updated `devlog/README.md` template with "What I'm learning" and "Problems faced & how I
  solved them" sections.

## Mistake made & fixed (honesty over polish)

- The first draft of this entry was written **in the human's voice**, attributing Phase 1
  learnings (psycopg2 vs psycopg3, `.env`/CWD, port conflicts, cp1252, …) to the human.
  That is false: the human did not learn any of it — the **agent (Cline) solved those
  problems** during the build. The human flagged the fabrication; this entry now says
  exactly that and makes no claims about the human's learnings.

## Who actually did what in Phase 1 (plain facts)

- **Agent (Cline):** designed and built the Phase 1 code, hit and fixed every technical
  problem, verified the results, and collected the commands now in `CHEATSHEET.md`.
- **Human:** set the project direction, wrote the rules (including *agents never commit or
  push*), and reviewed/committed the work.
- The Phase 1 technical topics are **not yet learned by the human** (their own words).
  They are documented in `CHEATSHEET.md` and the Phase 1 entry for whenever the human
  decides to work through them personally.

## Blockers / Open questions

- None. (Personal reflections, if any, go here — written by the human, not the agent.)

## Next steps

1. Human commits this batch (cheat sheet + rules + devlog rewrite).
2. Human records real learnings here as the journey actually happens.
3. Phase 2 hardening: scheduling, retries with backoff, incremental loads. The agent can do
   the work; the devlog records learnings only as they really occur.