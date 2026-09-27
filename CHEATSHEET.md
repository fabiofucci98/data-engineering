# Command & Syntax Cheat Sheet

> **Living document** — update me whenever you use a new command, flag, or syntax snippet
> (that's a project rule — see `.cline/rules/project-rules.md`). Everything below was
> **used and verified** in this repo (Phase 1, 2026-09-27).

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

## Docker & Docker Compose

| Task | Command |
|---|---|
| Validate config | `docker compose config --quiet` |
| Start (wait for healthy) | `docker compose up -d --wait` |
| Status | `docker compose ps` |
| Logs | `docker compose logs -f db` |
| Stop (keep data) | `docker compose down` |
| Stop + destroy volumes | `docker compose down -v` |
| Exec in db container | `docker compose exec -T db psql -U postgres -d scientific_data -c "SELECT 1"` |

Key `docker-compose.yml` syntax (verified):
- Port mapping `"${POSTGRES_PORT:-5433}:5432"` → `host:container`
- Named volume: `db_data:/var/lib/postgresql/data`
- **Auto-init on first boot**: mount `./sql:/docker-entrypoint-initdb.d:ro` — runs `*.sql`
  alphabetically, but ONLY when the data volume is empty
- Healthcheck + `--wait`:
  ```yaml
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres} -d ${POSTGRES_DB:-scientific_data}"]
  ```
- Compose auto-reads `.env` from the same folder

## PostgreSQL / psql

| Task | Command |
|---|---|
| List tables | `psql -U postgres -d scientific_data -c "\dt"` |
| Describe a table | `psql -U postgres -d scientific_data -c "\d earthquakes"` |
| Count | `SELECT count(*) FROM earthquakes;` |
| Exit | `\q` |

Verified patterns that matter here:
- **Idempotent upsert** (re-runs never duplicate rows):
  ```sql
  INSERT INTO earthquakes (event_id, mag, ...) VALUES (%s, %s, ...)
  ON CONFLICT (event_id) DO UPDATE SET mag = EXCLUDED.mag, ...;
  ```
- Timestamps: `TIMESTAMPTZ NOT NULL DEFAULT now()` (UTC-aware)
- `CREATE TABLE IF NOT EXISTS ...` / `CREATE INDEX IF NOT EXISTS ...` → re-runnable schema
- pgAdmin server: host = `db` (container name), port = `5432` (**container-internal**), user = `postgres`

## Python / venv / pip

| Task | Command |
|---|---|
| Create venv | `python -m venv .venv` |
| Activate (Windows) | `.venv\Scripts\activate` |
| Activate (macOS/Linux) | `source .venv/bin/activate` |
| Install | `pip install -r app/requirements.txt` |
| Syntax check | `python -m py_compile app/ingest.py app/dashboard.py` |

Dependency gotchas (each cost me time once — see devlog):
- **SQLAlchemy defaults to `psycopg2`**, but we use psycopg v3 → connection URL must be
  `postgresql+psycopg://user:pass@host:port/db`
- **`load_dotenv()` uses CWD** — Streamlit runs scripts from another directory. Use:
  `load_dotenv(Path(__file__).resolve().parent.parent / ".env")`
- **Windows console is `cp1252`**: `print("→")` crashes → keep console output ASCII-safe

## USGS Earthquake API

Base: `https://earthquake.usgs.gov/fdsnws/event/1/query`

| Use case | Query |
|---|---|
| Last 30 days, min mag 2.5 | `?format=geojson&starttime=2026-08-28&minmagnitude=2.5&eventtype=earthquake&orderby=time` |
| Count only | `https://earthquake.usgs.gov/fdsnws/event/1/count?starttime=2026-01-01&endtime=2026-01-02` |

GeoJSON shape (memorize!):
- `features[].properties.{mag, place, time, updated, url, ...}`
- `features[].geometry.coordinates = [longitude, latitude, depth_km]` — **longitude FIRST**
- Paging: `limit` + `offset`; total comes back in `metadata.count`
- Public API — no key needed

## Streamlit

| Task | Command |
|---|---|
| Run | `streamlit run app/dashboard.py` |
| Test headlessly | `streamlit.testing.v1.AppTest` (below) |

Widgets verified in this repo:
- `st.map(df[["lat","lon"]])` — points on a map (needs lowercase `lat`, `lon` columns)
- `st.bar_chart(series)` — quick bar chart from a pandas Series
- `st.metric("Label", value)` — KPI numbers
- `st.dataframe(df, column_config={...})` — filterable table with typed/link columns
- `st.cache_data(ttl=60)` — cache a function's result (e.g., DB queries)
- Sidebar: `with st.sidebar:` + `st.slider`, `st.date_input`

Headless test that caught real bugs:
```python
from streamlit.testing.v1 import AppTest

at = AppTest.from_file("app/dashboard.py", default_timeout=90)
at.run()
print(len(at.exception), [e.value for e in at.exception])
```