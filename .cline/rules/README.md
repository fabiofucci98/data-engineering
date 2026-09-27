# `.cline/rules/`

Rule files in this folder are **automatically loaded by Cline (and other Cline/rules-aware agents)**
whenever they work inside this repository. They define how work should be done here so every
contributor — human or AI — stays consistent.

## How it works

- Every `*.md` file in this directory (recursively) is treated as an instruction set.
- Rules are loaded automatically per project — no manual include step needed for Cline.
- They apply to the whole repository, regardless of which folder a task touches.

## Files

| File | Purpose |
|---|---|
| `README.md` | This overview |
| `project-rules.md` | Actual working rules: conventions, guardrails, process |

## General advice when writing rules

- Prefer **clear, actionable statements** over vague intent ("Never do X…", "Always do Y…").
- Keep rules short so they stay effective — nobody (or no agent) reads walls of text.
- Update a rule when the project's reality changes, and note the change in the devlog.