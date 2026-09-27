# Vision & Roadmap — Future

> **Nothing in this file is implemented yet.** What works today is described in the
> README; this file only plans what comes next. (Roadmap content moved here from the
> README on 2026-09-27.)

## The bigger vision

The project starts with USGS Earthquakes but is designed to grow far beyond a single,
single-source demo: more scientific data sources later, culminating in an ML project.
Design decisions (schema, layout, containerization) are made to keep that path open.

## Roadmap

- [ ] **Phase 2 — Hardening**
  - [ ] Scheduling (cron / Prefect / Airflow)
  - [ ] Retries, backoff, idempotent loads
  - [ ] SQL transformations / analytics-ready tables
- [ ] **Phase 3 — More scientific data sources**
  - [ ] NOAA / NASA / climate datasets
  - [ ] Multi-source schema federation
- [ ] **Phase 4 — Machine Learning**
  - [ ] Feature store on accumulated data
  - [ ] First ML experiments (e.g., classification/regression on events)

## Related thinking

- [`scientific-live-data-sources.md`](scientific-live-data-sources.md) — candidate
  future data sources and a normalized multi-source schema idea.