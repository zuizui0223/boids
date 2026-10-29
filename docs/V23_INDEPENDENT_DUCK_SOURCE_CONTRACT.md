# v23-A – Original independent wild dabbling-duck GPS source gate

Registered 2026-10-29 JST **before reading movement outcomes or environmental response values**.

## Independent source

Van Toor & Waldenström (2025), Zenodo original record [16940654](https://zenodo.org/records/16940654), DOI 10.5281/zenodo.16940654. Original file `250823_LNU_dabbling_ducks_hourly.csv`; published MD5 `1972d0ef08b83c2b88a169ba07bb48b3`, published 46.3 MB approximate display, but accept **only exact provider API byte count**; record original independently computed SHA256. Author metadata describes seven species of GPS-tagged dabbling ducks captured across Sweden, Netherlands, Lithuania, Bangladesh, Mongolia, Portugal, etc. Original GPS timestamps are UTC, WGS84 coordinates, hourly/2-hour sensor duty, and original `individual.id`, `study.name`, `individual.taxon.canonical.name`, `gps.hdop`, `ground.speed` columns. All these are **publication metadata**, to be verified against original bytes. Source license and source DOI must be read from exact provider API, not assumed.

### Stage A source-only admissions (no GPS movement target values)

1. Obtain `https://zenodo.org/api/records/16940654`. Verify exact record ID, original filename, provider MD5, actual positive file byte count <=120,000,000, exact provider URL with `zenodo.org` domain, original license and parent DOI. Download into ephemeral CI, check exact size, published MD5, and compute SHA256. A 403/404 or missing checksum yields a source STOP.
2. Read **header, IDs, timestamps, species and named study ONLY** from original CSV. Never open latitude, longitude, ground.speed, GPS heading or HDOP numerical values in this phase. Count total physical data rows, nonempty individual ID×UTC day units, unique individuals, UTC duplicate individual timestamps, original species/study group sizes, true repeated days (>7, >14, >30), distinct months for each individual, observation year range and records with bad/missing timestamps. Keep only aggregate counts, no original animal ID or exact GPS coordinates/time.
3. Check whether source is actually GPS receiver telemetry rather than interpolated track fixes, whether source membership in 7 species is borne out, and whether source provides a **measured environmental covariate**. The metadata does not name a rainfall, temperature or NDVI field, so **do not assert a climate/resource gain from this file alone**.
4. Minimum novel individual-history source gate: >=20 independent original individual IDs with >=14 GPS-observed distinct UTC dates and valid season/year progression; no group-level social network can be inferred from co-occurring GPS records without original group-assignment labels.
5. Before any ecological forecast, freeze **separate** v23-B target, time horizon, habitat availability or independent weather join protocol: e.g. external daily weather from verifiable temporal/geographic source, with no response-driven station selection, and baseline environment/calendar versus previous individual movement. Source ID-only passage alone does not authorize fitting later GPS movement responses.
6. Source studies share research and many species, so individual IDs are **not** independent regions or species. Whole individual and study/year blocking required. A new species is not established merely by listing seven source taxa. Avoid eBird entirely.
7. Treat GPS-only future spatial predictions without independent used/available resource patches as **movement forecasts**, not true resource competition, social memory, or ecological niches.

## Alternative original measured habitat/weather source

Osborne et al. (2024), [Dryad DOI 10.5061/dryad.1ns1rn93p](https://doi.org/10.5061/dryad.1ns1rn93p) has a 498-KB **daily movement summary already linked to measured station temperature, wind, pressure and precipitation**, plus an original ~35-MB hourly GPS file from ducks. The official webpage confirms variables `band,date_cst,mean_dist,sum_dist,avetemp,mean_wind,total_precip`, but the Dryad original is **not independently downloaded here**. Follow official provider version+SHA links and preserve blocked access separately. Do not substitute paper-reported effects for new original-data forecasts.

No v13-v22 old endpoint will be rewritten or used to retune this source. Stage A output is a source-quality receipt, not an observed ecological effect.
