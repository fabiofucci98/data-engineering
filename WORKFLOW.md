# Workflow Template — Agent-Assisted Development

A self-contained recipe for setting up agent-assisted development in **any new project**:
how the human works with AI agents, what rules everyone runs under, and how the
documentation stays honest (README = current, notes = future, technologies = what's
actually used).

> Replace every `[PLACEHOLDER]` with your project's real names, tools, and paths.

## How to use this template

1. Create the folder/file structure below.
2. Copy each **`PASTE →`** block into the matching file.
3. Replace every `[PLACEHOLDER]` with your real names/tools.
4. Initialize git and make the first commit — **the human does this** (agents never commit/push).
5. From day one: create `devlog/YYYY-MM-DD.md` and log every chat with the agent.
6. Keep the whole thing honest: docs reflect reality, the devlog is a learning journal.

## Target structure

```
my-project/
├── README.md               ← current state ONLY (what works today)
├── TECHNOLOGIES.md         ← technologies in use ONLY (no roadmap)
├── CHEATSHEET.md           ← commands/syntax that proved useful (keep fresh!)
├── WORKFLOW.md             ← this template (keep in sync with reality)
├── devlog/
│   ├── README.md           ← conventions (one file per day, block per chat)
│   └── YYYY-MM-DD.md       ← the day's log (append a block per chat)
├── notes/                  ← future plans & ideas (NOT implemented)
│   └── README.md
├── .cline/
│   └── rules/
│       ├── README.md       ← how Cline loads rules
│       └── project-rules.md ← the actual working rules
├── .gitignore              ← always ignore .env, venv/, __pycache__/, data/
└── .env.example            ← env template; real .env stays git-ignored
```

---

## How the human works with agents (the habits)

1. **The human owns git.** Agents **never** run `git commit`/`git push`. Agents prepare and
   verify; the human stages, commits, and pushes.
2. **Every chat is logged.** Each message to an agent becomes one block in that day's devlog
   (core idea + kind — see the devlog conventions).
3. **Honesty is non-negotiable.** The devlog is the human's own account. Agents never write
   in the human's voice or claim the human learned/solved something they didn't; they state
   plainly who did what.
4. **Plan first, then act.** Big or ambiguous changes: the agent proposes a plan, the human
   approves, then it gets implemented. Questions can be answered without changing files.
5. **Docs reflect reality.** README = current state only · `notes/` = not-yet-implemented ·
   `TECHNOLOGIES.md` = in use only · `CHEATSHEET.md` = commands that actually worked.
6. **Simplicity first.** Least complex tool that fits; it's a learning project first, a
   platform second. No Airflow/dbt/ML until the MVP exists.
7. **Verify before done.** The agent runs the code / re-reads files and reports evidence.
8. **Ask when ambiguous.** Never guess.

### First-week bootstrap checklist

- [ ] Create the folder structure above and paste the blocks below (replace `[PLACEHOLDERS]`).
- [ ] `git init` + first commit by the human.
- [ ] Create `devlog/YYYY-MM-DD.md` and log the very first chat with the agent.
- [ ] Explicitly agree with the agent on: never commit/push, honest devlog, log every chat.
- [ ] Open a `CHEATSHEET.md` on day one — write down the first command you look up twice.

---

## 1. `.cline/rules/README.md` — `PASTE →`

This file tells the agent what the rules folder is:

````markdown
# `.cline/rules/`

Rule files in this folder are **automatically loaded by Cline (and other rules-aware agents)**
whenever they work inside this repository. They define how work is done here.

## How it works

- Every `*.md` file in this directory (recursively) is treated as an instruction set.
- Rules are loaded automatically per project — no manual include step needed for Cline.
- They apply to the whole repository.

## Files

| File | Purpose |
|---|---|
| `README.md` | This overview |
| `project-rules.md` | The actual working rules: conventions, guardrails, process |

## Advice for writing rules

- Prefer clear, actionable statements over vague intent ("Never do X…", "Always do Y…").
- Keep rules short; update a rule when reality changes (note it in the devlog).
````

> Note: this block is wrapped in *quadruple* backticks only so you can copy it raw —
> the pasted file itself uses regular triple backticks.

---

## 2. `.cline/rules/project-rules.md` — `PASTE →`

This is the core rules file. Customize the `[PLACEHOLDERS]`:

````markdown
# Project Rules — [PROJECT NAME]

These rules apply to **everyone working in this repository**: humans and AI agents.

## 1. Project identity
- This project **starts small** ([first source / MVP]) but is **the beginning of a larger
  [platform / data project]**: more [data sources] later, possibly culminating in
  [destination, e.g. an ML project]. Design decisions must not paint us into a single-source corner.
- Keep the README's **WORK IN PROGRESS** framing honest: never claim functionality that doesn't exist.

## 2. Code and structure
- **[Language, e.g. Python 3.11+]** is the language end to end.
- Layout:
  - [Orchestration, e.g. `docker-compose.yml`] at the repo root.
  - Application code under `app/` (or `src/`).
  - Raw/processed data references under `data/` (never commit large payloads).
  - Future plans and ideas live under `notes/` — never in the README.
- Keep code **simple and readable** — a learning project first, a platform second.
- Use `venv` + `requirements.txt` (or equivalent) for dependency pinning.

## 3. Don't break the learning path
- Favor the **least complex tool that fits**. Don't introduce [heavy tools: Airflow, dbt, ML
  frameworks] before the MVP exists — their time comes later.
- When a stage advances, **update `TECHNOLOGIES.md`** to reflect reality.

## 4. Data handling
- **Never commit secrets or API keys.** Use `.env` files (git-ignored) and `.env.example`.
- Only commit small sample datasets. Never commit bulk raw data.
- Prefer idempotent ingestion (re-running a load must not duplicate rows).

## 5. Version control
- **Agents must NEVER run `git commit` or `git push`.** Version control belongs to the human:
  agents prepare and verify changes, then hand them over for the human to stage, review, commit, and push.
- Keep commits small, focused, and frequent (short imperative messages).
- Log every request in the day's devlog file (core idea + kind — see §6).

## 6. Devlog & documentation discipline
- The `devlog/` folder documents the **why** and is the human's **learning journal**.
  **One file per day** (`YYYY-MM-DD.md`): every chat with an agent is appended to that day's
  file as a block with the request's **core idea** and its kind — change request, info
  gathering, decision, learning, or blocker. See `devlog/README.md`.
- Be honest, including about failures and blockers (🔴 entries are valuable, not shameful).
- **Never fabricate the human's learning journey.** Agents never claim the human learned,
  discovered, or struggled with something they didn't express. State plainly who did what.
- **Keep `CHEATSHEET.md` up to date**: any command, flag, or syntax that proves useful — or a
  gotcha that cost time — belongs there so it is never relearned.
- The **README describes the current state only**; anything not implemented belongs in `notes/`.
- **Keep `WORKFLOW.md` in sync**: when a convention changes, update the template too.

## 7. Agent-specific behavior
- **Never run `git commit` or `git push`** — version control is the human's job, always.
- **Never write devlog content in the human's voice** or attribute learnings to the human
  they didn't express. Keep "who did what" strictly factual.
- **Log every request you handle** in that day's devlog file (core idea + kind) as part of
  finishing the task.
- **Never edit files without confirming the current state first** (read before write).
- Verify changes after making them (run the code / re-read the edited file).
- If a task is ambiguous, ask a clarifying question instead of guessing.

## 8. Definition of "done" for a task
1. Meets the requirement as stated (or clarified).
2. Follows the conventions above.
3. Verified to work (commands run / files re-read).
4. Documented: devlog updated when warranted; README / `TECHNOLOGIES.md` kept truthful.
````

---

## 3. `devlog/README.md` — `PASTE →`

````markdown
# Devlog

A **chronological journal** of this project's evolution — and of **your learning journey**.
It records the *why*: the reasoning behind choices, what you learned, what you struggled
with, and how you solved it.

## Conventions

- **One file per day** — every calendar day gets exactly one file: `YYYY-MM-DD.md`
  (e.g., `2026-09-27.md`). Never create multiple files per day.
- **Every chat with an agent is logged** in the day's file — each request gets a short block
  recording its **core idea**, whatever the kind is:
  - 🔧 **change request** — implement / refactor / restructure something
  - ❓ **info gathering** — a question (including ones answered without changing files)
  - ⚖️ **decision** — a rule, direction, or constraint set by the human
  - 🎓 **learning** — something the human actually learned or discovered
  - 🔴 **blocked / failed attempt** — recorded honestly
- Blocks are added chronologically; each starts with a number and a title.
- The day's file is a **running log**: append the next block whenever a chat happens.

### Block template (short blocks are fine — 3–6 lines each)

```markdown
## N. short-title `kind`

**Core idea:** one or two lines on what was asked.

**Done:** what actually happened (who did what).
**Who:** ...
**Status:** 🟢 / 🟡 / 🔴
```

## Tips

- Write short, honest entries — a block can be 3–6 lines.
- **Honesty over polish, always.** If an agent did the work, say so. Never claim you learned
  something you didn't. The devlog is *your* account; agents must not write in your voice.
- It is a **learning journal first**: write down what you actually learn and struggle with —
  🔴 "I tried X, it failed because Y" entries are gold.
- Agents working here must add a block to that day's file for the chat they are handling,
  stating plainly who did what.

## Days

- [YYYY-MM-DD.md](YYYY-MM-DD.md) — first entry.
````

---

## 4. `CHEATSHEET.md` — `PASTE →` (starter skeleton)

Fill in each section with commands as you actually use them:

````markdown
# Command & Syntax Cheat Sheet

> **Living document** — update me whenever a command, flag, or syntax snippet proves useful
> (or a gotcha costs time). Nothing here is relearned twice.

## [Git]
| Task | Command |
|---|---|
| Status | `git status --short` |
| Stage | `git add -A` |
| Commit | `git commit -m "Short imperative summary"` |
| History | `git log --oneline --graph --decorate -5` |
| Ignore check | `git check-ignore .env` |

⚠️ Agents never run `git commit`/`git push`; run git commands **sequentially**
(parallel git → `index.lock` conflicts).

## [Docker / Docker Compose]
| Task | Command |
|---|---|
| Validate | `docker compose config --quiet` |
| Start (wait healthy) | `docker compose up -d --wait` |
| Status | `docker compose ps` |
| Run one-off | `docker compose run --rm <svc> <cmd>` |
| Logs | `docker compose logs -f <svc>` |

Key syntax: port mapping `"host:container"`, named volumes, healthchecks,
auto-init scripts `./sql:/docker-entrypoint-initdb.d:ro` (run once, empty volume only),
**service-to-service networking** (inside compose, reach a service by its name + internal port).

## [Database / SQL]
| Task | Command |
|---|---|
| List tables | `psql ... -c "\dt"` |
| Count | `SELECT count(*) FROM ...;` |

Idempotent upsert (re-runs never duplicate):
```sql
INSERT INTO t (id, col) VALUES (%s, %s)
ON CONFLICT (id) DO UPDATE SET col = EXCLUDED.col;
```

## [Language & package management]
| Task | Command |
|---|---|
| venv | `python -m venv .venv` / activate |
| Install | `pip install -r requirements.txt` |
| Syntax check | `python -m py_compile app/main.py` |

Gotchas that cost real time: driver/dialect naming (e.g. `psycopg2` vs `psycopg` v3 →
`postgresql+psycopg://`), `.env` loading depends on the working directory, Windows console
`cp1252` crashes on unicode `print("→")`.

## [Data source API]
- Base URL / endpoint:
- Key params:
- Response shape (remember field order, e.g. GeoJSON `coordinates = [lon, lat, depth]`):
- Auth: key needed? rate limits?

## [Visualization / dashboard]
| Task | Command |
|---|---|
| Run | `[runtime] run [path/to/dashboard.py]` |
| Headless test | e.g. `streamlit.testing.v1.AppTest` |

Headless test pattern (adapt the import path to your project):
```python
from streamlit.testing.v1 import AppTest

at = AppTest.from_file("path/to/dashboard.py", default_timeout=90)
at.run()
print(len(at.exception), [e.value for e in at.exception])
```
````

---

## 5. `TECHNOLOGIES.md` — `PASTE →` (current-only policy)

````markdown
# Technologies in Use

This document lists the technologies **currently in use** in this repository.
It is not a roadmap: future tools are added here only when they are actually adopted.

## Data source

| Technology | Where / Why |
|---|---|
| [API / source] | ... |

## Infrastructure & storage

| Technology | Version | Where / Why |
|---|---|---|
| Docker + Docker Compose | ... | orchestrates the services |
| Git + GitHub | — | version control — humans commit/push; agents never |
| [editor, e.g. VS Code] | — | editor used for this repo |
| [LLM provider, e.g. OpenRouter] | — | LLM provider for AI-assisted development |
| [database] | image/version | storage service |

> Note: dev-tooling rows (editor, LLM provider) describe how this repo is built and edited,
> not the running pipeline.

## Application code

| Technology | Version | Where / Why |
|---|---|---|
| [language] | ... | language end to end |
| [HTTP client] | ... | API calls |
| [DB driver] | ... | database access |
| [query/ORM lib] | ... | reading data |
| [dataframe lib] | ... | query results → charts |
| [dashboard lib] | ... | visualization |
| [config loader] | ... | `.env` loading |

## How the pieces connect
- Inside Docker: `app` → `db` via service name, internal port.
- From the host: published ports / URLs.

## Version pinning
- Dependencies pinned in `requirements.txt`; images pinned in compose/Dockerfile.

## Policy
- Future tools (schedulers, dbt, ML frameworks, extra data sources) do **not** belong in this
  document until they are part of the codebase.
````

---

## 6. `notes/README.md` — `PASTE →`

```markdown
# Notes — Future & Thinking Space

Everything in this folder is **not implemented**. It exists so the root `README.md` can
honestly describe only the current state.

## Rules
- When a note becomes real: update the README (and `TECHNOLOGIES.md`), then mark the note
  done or archive it.
- The devlog records what *actually happened*; these notes record what we *want to happen*.
- Notes may be scrappy, exploratory, or wrong — that is their purpose.
- No claims here count as "the project does X".

## Contents
| File | What it is |
|---|---|
| (add files as you create them) | |
```

---

## 7. `README.md` — guidance (not a paste block)

The readme describes **only the current state**. Adopt this shape:

```markdown
# [Project Name]

> **🚧 WORK IN PROGRESS — EVOLVING PROJECT**
> Current phase + what actually works. Future plans live in [`notes/`](notes/README.md).

## What is this?
A [learner-level] project with a single current pipeline:
[source API] → [storage] → [simple visualization].

## Getting started / run it
Working commands only (with `docker compose ...`, etc.).

## Repository layout
... include `devlog/`, `notes/`, `CHEATSHEET.md`, `TECHNOLOGIES.md`, `.cline/rules/`.

## Docs in this repo
- `TECHNOLOGIES.md` — technologies in use
- `CHEATSHEET.md` — commands/syntax that worked
- `devlog/` — the journal (one file per day)
- `notes/` — future plans (not implemented)
- `WORKFLOW.md` — this template
```

---

*End of template. Keep every section in sync with how you actually work — the template is
only useful if it stays true.*