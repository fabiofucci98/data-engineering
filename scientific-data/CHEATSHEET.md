# Command & Syntax Cheat Sheet — Scientific Data (USGS earthquakes)

Stack commands only. Cross-stack/generic stuff (git, docker basics, python gotchas)
lives in the root [`CHEATSHEET.md`](../CHEATSHEET.md).

| Task | Command |
|---|---|
| Validate this stack | `docker compose -f scientific-data\docker-compose.yml config --quiet` |
| Start (db + dashboard; waits healthy) | `docker compose -f scientific-data\docker-compose.yml up -d --build --wait` |
| Logs (dashboard) | `docker compose -f scientific-data\docker-compose.yml logs -f earthquakes-app` |
| Run ingest (idempotent) | `docker compose -f scientific-data\docker-compose.yml run --rm earthquakes-app python ingest.py` |
| Ingest a custom window | `docker compose -f scientific-data\docker-compose.yml run --rm earthquakes-app python ingest.py --starttime 2026-01-01 --endtime 2026-03-01 --min-magnitude 4.0` |
| Build the image | `docker compose -f scientific-data\docker-compose.yml build earthquakes-app` |
| psql into the DB | `docker compose -f scientific-data\docker-compose.yml exec -T sci-db psql -U postgres -d scientific_data -c "SELECT count(*) FROM earthquakes;"` |
| Dashboard | http://localhost:8501 |

Networking: app → DB as `sci-db:5432` (container-internal); from the host the DB is
`localhost:5433`, database `scientific_data`.

## Host runs (no Docker)

```bash
python -m venv .venv && pip install -r scientific-data/earthquakes/requirements.txt
python scientific-data/earthquakes/ingest.py
streamlit run scientific-data/earthquakes/dashboard.py
```
`.env` at the repo root supplies `POSTGRES_HOST=localhost` / `POSTGRES_PORT=5433`.

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
| Run | `streamlit run scientific-data/earthquakes/dashboard.py` |
| Test headlessly | `streamlit.testing.v1.AppTest` (snippet in the root CHEATSHEET) |

Widgets verified in this repo:
- `st.map(df[["lat","lon"]])` — points on a map (needs lowercase `lat`, `lon` columns)
- `st.bar_chart(series)`, `st.metric("Label", value)`, `st.dataframe(column_config=...)`
- `st.cache_data(ttl=60)` — cache query results; sidebar: `st.slider`, `st.date_input`