# v21-A Independent American redstart telemetry × observed NDVI source-admission contract

**Registered 2026-10-28 JST, before opening the new source's movement-response numeric values, forecasts, or environment-effect estimates.** This is independent of pigeon v15-v19 and guineafowl v20. The old results and their eligibility rules must stay frozen.

## Original source

Dossman, Rodewald & Marra (2024), *Hidden space use behaviors of a nonbreeding migratory bird: the role of environment and social context*, Movement Ecology 12:82, DOI [10.1186/s40462-024-00523-4](https://doi.org/10.1186/s40462-024-00523-4). Original publicly deposited data [Dryad DOI 10.5061/dryad.gb5mkkwx1](https://doi.org/10.5061/dryad.gb5mkkwx1), published file-version 2025-11-24.

**Source units as published, not yet independently verified by this workflow:** American redstarts (Setophaga ruticilla) nonbreeding in Jamaica, individually tagged birds, automated telemetry of transitions between receivers plus vegetation NDVI. The article tracked up to 141 tagged birds and modeled more restricted eligible cohorts (63 hand-tracked, 36 repeatedly detected foray-monitoring). **Do not treat published sample sizes as the source-file cohort or independent research sites.**

Public Dryad file inventory lists: `forays.rds` (971 bytes), `ndvi.rds` (2,240 bytes), `individual.rds` (5,890 bytes), `mcp.rds` (59,360 bytes), `change.rds` (2,430 bytes), `README.md` (8,190 bytes). The first three are the **minimal** candidate for a future ecological forecast. The published documentation describes `forays.rds` as motusID × year × week for median receiver transitions, habitat, sex, age and NDVI `pred`. A separate `ndvi.rds` has year × week raw `ndvi` and temporally GAM-smoothed `pred`; smoothed values might include **future weeks** and therefore **must not be accepted as a past-time predictor** without independent source timing proof.

## Outcome-blind Stage A: exact source bytes and eligibility only

1. Request public Dryad API `https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.gb5mkkwx1`. Require exact dataset DOI/version, original official file manifest, positive original byte length, official digest if present, license and file download URL. For every official file actually downloaded, validate exact provider byte length, digest when provided (MD5/SHA256), compute SHA256. Max 10 MB per file, 20 MB cumulative. No fabricated output or silent substitution of a different dataset if official GET returns 401 or 404.
2. Retrieve at least `forays.rds` and `ndvi.rds` only. Do NOT access `mcp.rds` tracking coordinates at source admission. If official file downloads require authentication, record **SOURCE_ACCESS_BLOCKED**, with each HTTP outcome and official metadata; no claim that source data are inspected.
3. Source-only parsing must emit **only** R object class, column schema/types, row counts, missing counts, unique year/week/motusID grain, duplicate individual-week-year keys, distinct individual IDs, number with ≥3 consecutive observed weeks, and overlap of source individual weeks with original NDVI weeks. **Never print source numerical NDVI, forays, physiological condition, raw receiver detections or animal coordinates.**
4. Before future weekly forecast eligibility: at least **8 distinct original motusIDs** with ≥3 chronologically separated eligible weeks (to supply past and future target), at least **30 measured future individual-week targets** with observed `median_transitions` or `total_transitions`, and source weekly NDVI measured from original imagery (not only temporal smoothing). At least 2 original years and 2 habitats if a broader across-environment claim is intended.
5. **No direct social network is recorded** in the described forays.rds; habitat, sex and age are proxies of context, NOT observed direct social contact. v21 may at most test **individual movement history and vegetation availability**, not flock network rewiring.
6. Original transmitter detections are ~10-second cadence but this deposited table is week aggregated; do NOT call `forays.rds` GPS, true Boids steering or direct fine-scale encounter data.

## Stage B (separate pre-outcome contract only if A passes)

Prospective question: *Does an individual's own previous foray rate improve prediction of the following week's observed receiver transitions beyond habitat, age/sex, year/week and the **previous week's raw measured NDVI**?* Predefine models and no-future leakage, target support, conditional time covariates, leave-year/individual holdouts, group/bootstrap inference and strict missingness **before opening any source foray counts or NDVI numerical values**.

- Environmental baseline must use **past available raw NDVI (t−1)**, not its smoothed `pred` that may contain future data.
- Individual-history predictor should use last observed weekly forays up to `t−1`; never use that individual at the future week.
- Compare identical future target rows; aggregate by actual independent bird IDs and shared study year separately to avoid pseudo-replication of NDVI, which is one series for all birds each year.
- No claim of real resource abundance (NDVI is a vegetation proxy), dominance causality (age/sex are proxies), animal cognition, or true interspecific niche without measured resource and individual encounter data.

**If source access fails, retain Stage A failure and seek a separate eligible open-source dataset rather than "rescuing" predictions by relying on the source paper's reported positive regression.**
