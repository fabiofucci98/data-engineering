# Live Scientific Data Sources
### Space & Astronomy · Earth & Geoscience · NOAA Space Weather

A reference guide to free, live-updating scientific APIs, organized for a phased data project that starts narrow and expands outward.

---

## 1. Space & Astronomy

### NASA Open APIs
**Base:** `https://api.nasa.gov` · **Auth:** Free API key (instant signup, generous rate limits, or use `DEMO_KEY` for light testing)

One key unlocks several independent live datasets — ideal as a project hub:

| Endpoint | What it gives you | Update frequency |
|---|---|---|
| **APOD** (Astronomy Picture of the Day) | Daily curated image/video + scientific explanation | Daily |
| **NeoWs** (Near Earth Object Web Service) | Live-tracked asteroids/comets passing near Earth, with size, velocity, miss-distance | Continuous |
| **Mars Rover Photos** | Raw images from Curiosity, Perseverance, Opportunity, Spirit, by sol/camera | Per rover transmission |
| **EPIC** (Earth Polychromatic Imaging Camera) | Real, full-disk images of Earth from the DSCOVR satellite at L1 | Every ~1–2 hours |
| **Exoplanet Archive** | Confirmed exoplanet parameters (mass, orbit, host star) | Updated as discoveries are confirmed |
| **DONKI** (Space Weather Database) | Solar flares, CMEs, geomagnetic storms — NASA's own feed (complements NOAA below) | Near real-time |

### ISS Live Position
**Base:** `http://api.open-notify.org/iss-now.json` · **Auth:** None

Returns current latitude/longitude of the International Space Station, updated every few seconds. Also offers ISS pass-over predictions for a given location.

### N2YO / Space-Track
Satellite tracking (TLE orbital data) for thousands of objects, including the ISS and Starlink constellations. Requires free registration; useful once you want to expand beyond the ISS to general satellite tracking.

---

## 2. Earth & Geoscience

### USGS Earthquake Feed
**Base:** `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/` · **Auth:** None

- GeoJSON feeds updated **every minute**, filterable by magnitude (`significant`, `4.5`, `2.5`, `1.0`, `all`) and time window (hour/day/week/month).
- Fields include magnitude, depth, coordinates, location name, and time — no signup required, making it the simplest possible starting point for a live pipeline.

### NOAA Climate & Weather APIs
**Base:** `https://www.ncei.noaa.gov` (Climate Data Online) and `https://api.weather.gov` (live forecasts/alerts) · **Auth:** Token required for CDO; none for weather.gov

- Live weather forecasts, active alerts, and observational station data (`api.weather.gov`).
- Historical and near-real-time climate records: temperature, precipitation, storm events (NCEI/CDO).
- Ocean buoy data (wave height, sea temperature) via NOAA's National Data Buoy Center.

### OpenAQ
**Base:** `https://api.openaq.org` · **Auth:** Free API key

Live global air quality sensor network — PM2.5, PM10, ozone, NO₂, and more, aggregated from government monitoring stations worldwide. Good complement to weather data for an "environmental health" angle.

### GBIF (Global Biodiversity Information Facility)
**Base:** `https://api.gbif.org` · **Auth:** None for read access

Real-time species occurrence records — if the project later grows into ecology/biodiversity tracking, this bridges geoscience and life sciences.

---

## 3. NOAA Space Weather

**Base:** `https://services.swpc.noaa.gov` · **Auth:** None

NOAA's Space Weather Prediction Center publishes continuously updated JSON feeds — this is where "earth science" and "astronomy" intersect, since space weather (solar activity) directly affects Earth systems (power grids, GPS, aurorae).

| Feed | What it gives you |
|---|---|
| **Solar flares** | Real-time X-ray flux from GOES satellites, flare classification (A/B/C/M/X) |
| **Geomagnetic storms (Kp-index)** | 3-hour planetary geomagnetic activity index, live-updated |
| **Aurora forecast** | Predicted visibility bands for the northern/southern lights |
| **Solar wind** | Real-time speed, density, and magnetic field data from the DSCOVR satellite |
| **CME (Coronal Mass Ejection) tracking** | Alerts and modeled arrival times at Earth |

This pairs naturally with NASA's DONKI feed above — NOAA gives you the raw, live measurements; DONKI gives curated event summaries.

---

## Suggested Project Architecture

**Phase 1 — one source, one pipeline**
Start with the **USGS Earthquake feed** (zero setup, updates every minute) or **NASA NeoWs** (one key, immediately interesting). Store into a simple table: `event_id, type, magnitude/size, location, timestamp, source`.

**Phase 2 — expand within a domain**
Add sibling NASA endpoints (APOD, Mars photos, EPIC) using the same key — each is a new ingestion function, same storage pattern.

**Phase 3 — cross domain**
Bring in NOAA Space Weather feeds and correlate with NASA DONKI events (e.g., does a CME alert precede a Kp-index spike?). This is where "Space" and "Earth" data start talking to each other.

**Phase 4 — environmental layer**
Add OpenAQ air quality and NOAA climate data to build an "Earth systems" dashboard alongside the "Space systems" one — same architecture, new tables, shared dashboard.

**Common schema idea across all sources:**
```
source, category, event_type, value, unit, latitude, longitude, timestamp_utc, raw_payload (JSON)
```
Keeping every source flowing into one normalized table from day one makes every later expansion additive rather than a rebuild.

---

## Quick Reference: Auth Requirements

| Source | Key needed? | Rate limit (free tier) |
|---|---|---|
| USGS Earthquakes | No | None published, very high volume OK |
| ISS Position | No | Light polling recommended |
| NASA APIs | Yes (instant, free) | 1,000 requests/hour |
| NOAA Space Weather | No | None published |
| NOAA Weather.gov | No | Reasonable use policy |
| NOAA CDO (climate) | Yes (free token) | 5 req/sec, 10,000/day |
| OpenAQ | Yes (free) | Generous free tier |
| GBIF | No | None published |
