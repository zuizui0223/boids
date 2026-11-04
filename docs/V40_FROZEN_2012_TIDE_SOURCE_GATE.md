# v40 — 2012 UNOPENED TIDAL-OUTCOME HOLDOUT: SOURCE ADMISSION BEFORE ANY 2012 TIDE EFFECT

**Fixed 2026-11-03 JST.** v29–v39 results are already known. **No 2012 original GPS×RWS tide model score has been viewed under this research branch.** This first stage evaluates only source eligibility, no observed tidal hypothesis tests.

## Scientific question to evaluate only after source admission
Can an exploratory −120-minute measured-gauge phase shift that appeared predictive in Schiermonnikoog and Ameland's 2011 holdout (v36) transfer unchanged to **new calendar year 2012**, or was that apparent gain a year-specific feature-selection artifact? The choice of −120 minutes is explicitly post-v36, but 2012 tide-outcome data remain withheld at this freeze. Same-species, two-island temporal replication does not generalize across all shorebirds.

## Original prespecified 2012 source-only gate
- [Schiermonnikoog original Zenodo v5](https://zenodo.org/records/22296922), `O_SCHIERMONNIKOOG-gps-2012.csv.gz`, provider MD5 **`a2ccce5afe2a6cad09a27e2957beacaf`**.
- [Ameland original Zenodo v6](https://zenodo.org/records/10053853), `O_AMELAND-gps-2012.csv.gz`, provider MD5 **`12d5d3045578538f6a6ac9f8e78766df`**.
- Source Movebank `event-id, individual-local-identifier, timestamp, location-lat/long, visible` only. Within source site region (Schier lat [53.2,53.7] lon [5.7,6.6]; Ameland lat [53.2,53.6] lon [5.3,6.1]), original GPS timestamp interpreted *only as a native naive source timestamp* until its UTC/GPS ambiguity is adjudicated. This preflight uses relative timestamps and is unaffected by constant clock offsets. No tidal heights, phases or source RWS data are opened at this stage.
- Keep first original visible source fix in each native hour per animal, without interpolation. Adjacent chosen first-hour fixes must be 30 min to 2 hr apart, with great-circle speed ≤120 km/h. Count source-admitted 2012 fixes, birds with candidate original displacement steps, unique ISO weeks, and step counts only. No original bird IDs, raw source positions or exact timestamps output.
- **Pre-frozen test gate by site**: at least **3** birds with source steps, **4** distinct ISO weeks, and **1,000** possible 2012 movement steps; otherwise the new-year phase-prediction evaluation for that island is **NOT_ADMITTED**. A source gate failure is not an ecological non-replication.

## Frozen downstream field comparison, only for each admitted 2012 site
- 2010+2011 ORIGINAL GPS training cohorts, 2012 ORIGINAL GPS test year, independently per island and RWS station. No 2012 GPS outcome enters fitted model. Retrieve the original 2012 RWS `schiermonnikoog.waddenzee` or `ameland.nes` measured WATHTE (cm/NAP, fixed UTC+01) in the same quarter-batched source mode as v39, including strict 10-min gap and year-period checks.
- Hourly first-fix GPS for all source years, 0.5–2h displacement response `log1p(km/h)`. **M0** = true h(t), h(t)², source lat/lon, diel and season sin/cos. **Mphase0** = M0 + actual ebb/flood phase(t) + phase(t)×h(t). **Mphase−120** = M0 + RWS phase(t−120min) + that phase×true h(t), no future water level or extra rate terms. The **single primary** is Mphase0 MSE − Mphase−120 MSE, test year 2012; positive means the fixed past-2h phase model outperforms current phase. Secondary contrasts each against M0. Never pick a best lag from 2012.
- Same frozen ridge L2=10, training-only scaling, equal training total bird weight. Report **pooled equal-bird** MSE difference and matching whole-bird 95% bootstrap, and a **separate equal-week-then-bird** mean with its matching whole-week bootstrap; 4,000/10,000 fixed-seed replicates. Do not place a weekly CI next to an equal-bird point estimate as though they measure the same estimand.
- Original 2012 leap second means if tags used **GPS time** the GPS−UTC differential changes from 15 seconds to 16 seconds on 2012-07-01, whereas the original source says UTC OR GPS. Source status remains CLOCK_UNVERIFIED. Treat source native time provisionally UTC as primary; any -15/-16s historical sensitivity is separately labeled and must not be used to select a winning lag.
- 2014 AHN NAP DEM may permit future local exposure analysis, but its calendar year differs from 2009–2012 GPS and it does not by itself prove food exposure or a moving ecological front. No social Boids M3 estimand is admitted from the sparse pair-heading source.

## Source-only reproduction
```bash
PYTHONPATH=validation_v30:validation_v40 python -m unittest discover -s validation_v40 -p 'test_*.py' -v
PYTHONPATH=validation_v30:validation_v40 python validation_v40/source_gate_2012.py --output /tmp/boids_v40_2012_source_only.json
```
