# Devlog

A **chronological journal** of this project's evolution — and of **your learning journey**.
It records the *why*: the reasoning behind choices, what you learned, what you struggled
with, and how you solved it.

## Conventions

- **One file per day** — every calendar day gets exactly one file: `YYYY-MM-DD.md`
  (e.g., `2026-09-27.md`). Never create multiple files per day.
- **Every chat with an agent is logged in the day's file** — each request gets a short
  block recording its **core idea**, whatever the kind is:
  - 🔧 **change request** — implement / refactor / restructure something
  - ❓ **info gathering** — a question (including ones answered without changing files)
  - ⚖️ **decision** — a rule, direction, or constraint set by the human
  - 🎓 **learning** — something the human actually learned or discovered
  - 🔴 **blocked / failed attempt** — recorded honestly
- Blocks are added chronologically; each starts with a number and a title.
- The day's file is a **running log**: append the next block whenever a chat happens.
  Files are consolidated only when the human asks.

### Block template (short blocks are fine — 3–6 lines each)

```markdown
## N. short-title `kind`

**Core idea:** one or two lines on what was asked.

**Done:** what actually happened (who did what).
**Who:** ...
**Status:** 🟢 / 🟡 / 🔴
```

### When a day deserves more detail

- A bigger change can have a few more bullets in its block.
- The day file is the history; `notes/`, `README.md`, and `CHEATSHEET.md` carry the detail.

## Tips

- Write short, honest entries — a block can be 3–6 lines.
- **Honesty over polish, always.** If an agent did the work, say so. Never claim you
  learned something you didn't. The devlog is *your* account; agents must not write in
  your voice or attribute anything to you that you didn't express.
- It is a **learning journal first**: write down what you actually learn and struggle
  with — 🔴 "I tried X, it failed because Y" entries are gold.
- Agents working here must add a block to that day's file for the chat they are handling
  (that's the rule), stating plainly who did what.

## Days

- [2026-09-27.md](2026-09-27.md) — project kickoff, Phase 1 build, rule changes,
  containerization, docs restructure (11 chat entries).
- [2026-09-29.md](2026-09-29.md) — "add until it breaks" strategy + first milestone
  decisions (2 chat entries).
- [2026-09-30.md](2026-09-30.md) — simulated city direction — what to simulate
  (1 chat entry so far, WIP).