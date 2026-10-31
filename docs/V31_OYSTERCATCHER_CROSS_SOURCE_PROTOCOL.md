# Boids v31: independent species and source validation of yesterday + multi-day movement history

**Frozen design (2026-10-31 JST), prior to opening any GPS coordinates or daily movement target values from the two selected sources.** Prior v23/v29/v30 dabbling-duck outcomes, including the v30 four-site positive exploratory hybrid comparison, are already known. This is therefore an independent-original-source, *prospective-outcome-validation* test of a previously selected specific model contrast, not a blind discovery study or global animal movement law.

## Why this test

The v30 four held-out duck study cohorts (112 birds, 8,369 future days, all from ONE Zenodo 16940654 archive) gave a positive fixed secondary comparison between exact previous-day persistence MP and a 50:50 mix MH of MP and the last 3–14 earlier eligible movement days. Four study-level point estimates favored MH, but exact one-sided study sign p=0.0625; an independent species and original publisher source are needed. This experiment freezes the **same 50:50 comparison as its primary** before any new animal movement outcomes.

## Original external sources, frozen before source ID/date audit

1. **O_SCHIERMONNIKOOG**: published Zenodo [10053970](https://zenodo.org/records/10053970), 2023 version v4 (43 tagged Eurasian oystercatchers reported by source authors), GPS years 2008–2014. Exact match only `O_SCHIERMONNIKOOG-gps-YYYY.csv.gz` where YYYY is one of 2008..2014, all seven years, and `datapackage.json` for schema. Do **not** use current successor record 22296922.
2. **O_WESTERSCHELDE**: published Zenodo [10053702](https://zenodo.org/records/10053702), version v6 (13 tagged Eurasian oystercatchers reported), all three GPS years 2018–2020, `O_WESTERSCHELDE-gps-YYYY.csv.gz`, plus `datapackage.json`.

No acceleration data, author results, experiment effects or opportunistic region/years. This is a different bird species and raw telemetry from v23–v30. The two sites are not two globally representative ecosystems; both are NW European coastal birds tracked by related UvA-BiTS technologies, with potential shared device/cycle bias.

### Admission of original sources

First run a **source-only** original Zenodo API manifest + published MD5 byte check, compute SHA256 for every original GPS-year gzip, and read only CSV headers, original individual IDs, and UTC datetimes (no GPS locations, altitude, movement speed, distance, habitat, prey or responses). Retain only anonymized counts. All data must have identifiable bird and date columns, stable site and original taxon. If any of the 10 original gzip files is missing, corrupt, too large, or checksum-inconsistent, declare STOP: no alternative version/year/taxonomic subset selected.

Keep each original gzip ≤80MB, cumulative GPS compressed bytes ≤100MB, ≤2 million decompressed CSV records per gzip, and ≤3 million original GPS records total. If data exceed caps, declare STOP rather than silently subselect. Record source metadata, exact original provider file count and derived SHA. Source identity/temporal audit must finish **before** reading any location data.

## Prediction outcome and fixed eligibility (stage B)

Use only original, actually recorded GPS fixes from the selected ten source files, including year boundary continuity. Coordinates WGS84 finite; if an original `gps:hdop` field is available, require finite [0,15] as in v23–v30, but the absence of that field in a different source is not itself evidence of high quality—report availability and use source quality flags. If an original `visible` field exists, accept only provider-verified visible TRUE records (1/true/t, case-insensitive); if source meaning is ambiguous, STOP before modeling. Remove **all** duplicates for each exact study×bird×UTC timestamp (never arbitrarily keep the first observation). Do not interpolate or invent altitudes. A complete day has at least 6 distinct valid fixes covering ≥8 hours of that UTC calendar date.

Follow v30 exact target: daily horizontal radius of gyration `R=sqrt(mean(((lat-mean(lat))*111.2)^2+((lon-mean(lon))*111.2*cos(mean(lat)))^2))` km, `y=log(1+R)`. This is within-day GPS spread, not actual food-use niche or movement distance.

One next-day target (bird,t) is eligible only if both day t and **exact calendar t−1** have complete GPS days, and there are ≥3 earlier eligible event days for this bird (last 14 eligible dates, allowed calendar gaps). Population source prior must have at least 5 **other** original bird IDs and 20 prior eligible bird-day events *within the same site*, strictly before t. Score all birds on date t before adding any of those day-t outcomes to history. No target-date information enters any predictor.

### Four fixed models on the SAME target days

- **M0** historical other-bird state within the site, first mean by external bird and then mean across external birds.
- **MP** exact previous calendar day's observed y for this same bird.
- **MI** fixed mean of the last 3–14 prior eligible event-day y values for this bird (not a fixed number of calendar days).
- **MH** `0.5*MP+0.5*MI`, without fitted smoothing weight or tuned fallback. No weather or externally generated resource proxies in this test.

**Primary** signed MSE gain `MSE(MP)-MSE(MH)`; positive means a fixed hybrid beats one-day state, as in v30. **Secondary** `MSE(M0)-MSE(MP)` and `MSE(MP)-MSE(MI)`, all in these directions regardless of outcome.

### Fixed STOP, uncertainty and audit

Each original study must supply ≥8 eligible distinct bird IDs and ≥80 common future bird-day targets, and both together ≥20 birds and ≥300 common target days. Otherwise **no pooled model scores exported**, only all source/quality/admission counts. No lowering thresholds or changing data years in response. Site is inference unit; within study first mean errors by bird then equal weight bird, then equal weight two studies. 10,000 paired site-level resamples, RNG seed 20261031, plus exact one-sided signs across TWO sites (minimum all-positive sign p=0.25), and descriptive whole-bird bootstrap **within** each study. Never use bird-day fixes as independent ecosystems. Preserve all three comparisons and each study's absolute errors; do not report only a positive subgroup.

Source-only stages can discover column-name mismatches; fix **header/UTC grammar only** prior to stage B, documenting repair before GPS outcomes open. Failing the stated study/bird/date support gate cannot be "rescued" post-outcome. Any observed positive result does NOT identify cognition, Boids alignment/cohesion, competition, tidal behavior, food acquisition, 3D niches, or heritable individual specialization. These are day-ahead GPS spread forecasts for *previously tracked* animals; not movement trajectories of untracked animals.

No eBird, no TinyFish, and no raw individual bird IDs, timestamps, GPS/altitude coordinates, or per-date responses redistributed. Preserve earlier v29/v30 PRs and main unchanged. Create separate draft PR and exact machine-readable aggregate result.
