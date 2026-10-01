# Command & Syntax Cheat Sheet — shared / cross-stack

Per-stack commands live next to each pipeline:
- [`scientific-data/CHEATSHEET.md`](scientific-data/CHEATSHEET.md) — USGS earthquakes stack
- [`city-simulation/CHEATSHEET.md`](city-simulation/CHEATSHEET.md) — simulated city stack

> **Living document** — update me whenever a command, flag, or syntax snippet proves useful
> (that's a project rule — `.cline/rules/project-rules.md`). Everything below was
> **used and verified** in this repo (through 2026-09-30, repo restructure day).

## Git

| Task | Command |
|---|---|
| Status | `git status --short` |
| Stage | `git add -A` (or by file: `git add README.md app`) |
| Commit | `git commit -m "Short imperative summary"` |
| Push | `git push origin main` |
| History | `git log --oneline --graph --decorate -5` |
| Diff (uncommitted) | `git diff` / `git diff HEAD --stat` |
| Ignore check | `git check-ignore .env` |
| Tracked files | `git ls-files` |
| Remotes | `git remote -v` |

> ⚠️ **Agents never run `git commit` / `git push`** — the human always does.
> ⚠️ Run git commands **sequentially** — parallel git in the same repo causes
> `index.lock` conflicts and garbled commits.

## Docker & Docker Compose (shared)

Three compose files: root = shared tooling (pgAdmin + the shared network); each pipeline
folder owns its stack **and its own Postgres** in its compose file.

| Task | Command |
|---|---|
| Validate root config | `docker compose config --quiet` |
| Start shared tooling (pgAdmin + shared network) | `docker compose up -d` *(first — the stacks join its network)* |
| Inspect the shared network | `docker network inspect sdp-shared` |
| Stop the shared tooling | `docker compose down` |
| Wipe shared data | `docker compose down -v` *(destructive)* |

pgAdmin notes (verified):
- Servers are **auto-registered** from `pgadmin/servers.json` — the image's entrypoint
  runs `setup.py load-servers <file> --user <email>` on first init (env
  `PGADMIN_SERVER_JSON_FILE`, default `/pgadmin4/servers.json`).
- If DB hosts ever change: refresh on a fresh init (wipe the pgAdmin volume once) or set
  `PGADMIN_REPLACE_SERVERS_ON_STARTUP=True` so every restart re-syncs the file.

Key compose syntax (verified):
- **One compose per pipeline**: each stack owns its DB, its network, its volumes — the
  databases are physically separate. Shared components live only in the root file.
- Stacks attach their DBs to the shared network with:
  ```yaml
  networks:
    shared:
      external: true
      name: sdp-shared
  ```
- Port mapping `"${PORT:-5433}:5432"` → `host:container`
- Named volumes per stack (`sci_db_data`, `city_db_data`); `pgadmin_data` at root
- **Auto-init on first boot**: mount `./sql:/docker-entrypoint-initdb.d:ro` (whole
  folder) or a single file — runs ONLY when the volume is empty
- Healthcheck + `--wait`:
  ```yaml
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres} -d scientific_data"]
  ```
- `.env` lives at the repo root; run compose from the root so `${VAR}` interpolates it
- Gotcha: a string that *looks* like `\"SELECT 1\"` on screen is usually a plain `"` in
  the file (PowerShell merely displays the escape). When an exact-match edit refuses to
  find text, hex-dump the line — `((Get-Content file)[N]) | Format-Hex` — to see the
  real bytes.

## PostgreSQL / psql (generic patterns)

- **Idempotent upsert** (re-runs never duplicate rows):
  ```sql
  INSERT INTO earthquakes (event_id, mag, ...) VALUES (%s, %s, ...)
  ON CONFLICT (event_id) DO UPDATE SET mag = EXCLUDED.mag, ...;
  ```
  Or `ON CONFLICT (...) DO NOTHING` when a fill loop owns regeneration (the city
  generator's pattern).
- Timestamps: `TIMESTAMPTZ NOT NULL DEFAULT now()` (UTC-aware)
- `CREATE TABLE IF NOT EXISTS ...` / `CREATE INDEX IF NOT EXISTS ...` → re-runnable schema
- psql for a specific database runs via its stack — see the per-stack cheat sheets.

## Python / venv / pip

| Task | Command |
|---|---|
| Create venv | `python -m venv .venv` |
| Activate (Windows) | `.venv\Scripts\activate` |
| Activate (macOS/Linux) | `source .venv/bin/activate` |
| Install | `pip install -r <stack>/requirements.txt` |
| Syntax check | `python -m py_compile <script.py>` |
| Unit tests | `pytest -m "not integration"` (needs `pip install -r requirements-dev.txt`; no Docker/network) |
| Integration tests (needs a Postgres) | `$env:RUN_INTEGRATION="1"; $env:CITY_POSTGRES_HOST="localhost"; $env:CITY_POSTGRES_PORT="5434"; $env:CITY_POSTGRES_DB="city"; pytest -m integration` |

Dependency gotchas (each cost time once — see devlog):
- **SQLAlchemy defaults to `psycopg2`**, but we use psycopg v3 → connection URL must be
  `postgresql+psycopg://user:pass@host:port/db`
- **`load_dotenv()` uses CWD** — always load by absolute path
  (`Path(__file__).resolve().parent.parent.parent / ".env"` with per-pipeline folders;
  harmless no-op inside containers where compose sets the env)
- **Windows console is `cp1252`**: `print("→")` crashes → keep console output ASCII-safe