# Command & Syntax Cheat Sheet — City simulation

Stack commands only. Cross-stack/generic stuff (git, docker basics, python gotchas)
lives in the root [`CHEATSHEET.md`](../CHEATSHEET.md).

| Task | Command |
|---|---|
| Validate this stack | `docker compose -f city-simulation\docker-compose.yml config --quiet` |
| Start (db; the generator also runs once with defaults on `up`) | `docker compose -f city-simulation\docker-compose.yml up -d --wait` |
| Preview the city plan (writes nothing) | `docker compose -f city-simulation\docker-compose.yml run --rm citygen python generate.py --dry-run --seed 42` |
| Generate the city (idempotent; re-run = no-op) | `docker compose -f city-simulation\docker-compose.yml run --rm citygen python generate.py --population 1000 --buildings-per-block 8 --seed 42` |
| Build the generator image | `docker compose -f city-simulation\docker-compose.yml build citygen` |
| psql into the DB | `docker compose -f city-simulation\docker-compose.yml exec -T city-db psql -U postgres -d city -c "SELECT count(*) FROM buildings;"` |
| Wipe this stack's data | `docker compose -f city-simulation\docker-compose.yml down -v` *(destructive — `generate.py` re-fills it)* |

Networking: generator → DB as `city-db:5432` (container-internal); from the host the
DB is `localhost:5434`, database `city`.

## How the generator works

- Inputs: `--population`, `--buildings-per-block`, `--seed`. Everything else derives
  (planning formulas live in the `ASSUMPTIONS` block of `citygen/generate.py`).
- Same seed = same city, every time. Adding a word to a `pools/*.txt` file shifts which
  names a given seed produces — settle on a seed to keep a city stable.
- `--dry-run` previews the **exact** city a run will write (it mirrors the run's RNG
  draw order), so previews and results agree.

## Host runs (no Docker)

```powershell
$env:CITY_POSTGRES_HOST="localhost"; $env:CITY_POSTGRES_PORT="5434"; $env:CITY_POSTGRES_DB="city"
python city-simulation/citygen/generate.py --population 1000 --buildings-per-block 8 --seed 42
```
The generator reads `CITY_POSTGRES_*` first and `POSTGRES_*` as fallback — the two
stacks' connections can never be confused.

## Pools

- `pools/*.txt`, one word per line, one pool per file — recipe map in `pools/README.md`.
- Naming recipes per entity: roads `[first] [middle] [type]`, districts
  `[character] [place]`, schools `[name] [level]`, shops `[adjective] [noun]`, … — see
  the note `notes/city-geo-simulation.md`.
- Keep the product space ≥ 100× the largest city the pools will serve (grow the files,
  not the code).