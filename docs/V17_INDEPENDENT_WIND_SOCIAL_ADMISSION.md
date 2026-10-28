# v17-A — Independent wind × social-information source admission (frozen before turning outcomes)

**Registered: 2026-10-28 JST. STATUS: source/provenance admission only, NO v17 movement outcomes.**

## Objective and evidence boundaries

Test whether environmental information (especially **observed wind speed and direction relative to movement**) changes the *out-of-sample additional predictive value* of actual social partners for short-horizon flight turns. This is NOT a regression of published weather effects, NOT proven causal force estimation, NOT an animal feeding-niche result and NOT a reanalysis/tuning of the already opened v15/v16 source records.

**Primary independent candidate:** Taylor, Taylor, Lambert, Walker, Biro & Portugal (2019), *Birds invest wingbeats to keep a steady head and reap the ultimate benefits of flying together*, PLOS Biology DOI [10.1371/journal.pbio.3000299](https://doi.org/10.1371/journal.pbio.3000299). Raw source [Zenodo record 5026107](https://zenodo.org/records/5026107) (dataset DOI `10.5061/dryad.m7253n8`).

The publication describes **20 pigeons**, experiment 1 with six releases in each of four fixed phases (solo / matched-size pair / different-size pair / solo), raw 5-Hz GPS and 200-Hz accelerometers, and a weather station near the loft recording mean wind speed/minute and rolling wind bearing/10min, air temperature, humidity and barometric pressure. **Sunny days and wind <7m/s were required**, so the study cannot identify effects of *sun visibility* or all-weather generality. The paper reports GPS positional accuracy of approximately 3m for 50% of fixes; this is not a comprehensive error covariance estimate. The published pair/solo comparison is background, not the outcome of our new independent forecast.

Potential companion independent *sun-specific* study: 2013 PLOS ONE [10.1371/journal.pone.0063130](https://doi.org/10.1371/journal.pone.0063130), raw data [10.5061/dryad.pc7pg](https://doi.org/10.5061/dryad.pc7pg), clock-shifted pigeon solo GPS (no independent social-partner test). Keep separate. It cannot by itself establish a sun × social interaction. Do not pool its individual flight fixes with independent partner studies as if sharing a homogeneous observation process.

## Exactly pinned provider expectations (source provenance, not raw-content effects)

- Zenodo record ID **5026107**, direct metadata `https://zenodo.org/api/records/5026107`; only accept exact returned record ID.
- Source files must include exactly one each:
  - `Experiment 1 - GPS data.zip`, provider MD5 **`499943131e1f6596187cf2a756e3c8dd`**;
  - `Experiment 1 - Weather Data.csv`, provider MD5 **`1a8c56601ed982a7f2968f1348831317`**.
- Verify API-reported positive byte sizes, file URLs, provider license and version. No guessed byte lengths; cap GPS download at **400,000,000 bytes** and weather CSV at **30,000,000 bytes**. Compute actual SHA256 plus MD5 and **require exact provider byte and MD5 match**. If blocked, return UNKNOWN/STOP; never claim acquisition succeeded. The Zip and weather original remain temporary on CI only; no animal GPS rows or weather event records redistributed.
- Within GPS ZIP reject unsafe paths/duplicate names, encrypted members, archive totals exceeding 8GB, individual entries >1GB, nested opaque containers (report them rather than assuming usable), or undocumented source-only signatures.
- List entry extension counts, only **first ≤40 distinct natural file-name examples**, and first header/schema line from at most **32 preselected by alphabetical name** candidate CSV/log files. Do not read positions, headings, wingbeat signals, forecast effects, or target outcomes during Stage A.
- Weather: inspect exact CSV header, physical row count and time/wind *column presence*, but no wind-time/heading correlation and no source GPS overlap joins yet.
- Potentially groupable bird/phase/flight ID references in source filenames are **structural suggestions only**. Co-measured partners, stable IDs and social vs solo treatment identity must be verified against a **separate published release/pair ledger** (S3 Table or original source manifest), not guessed from file names or movement similarity.

## Pre-registered eligibility thresholds for later analysis (NOT automatically claimed as results)

- At least **8 independent biological clusters** of track-level heldout prediction (bird-connected components or intact pair-network clusters); 8 releases/individuals are not 8 independent clusters when overlapping partner identities. Each valid cluster must have ≥2 genuinely separated recorded flight sessions; the entire connected component must be in a single train or test fold.
- Independently recorded raw UTC and GPS time precision ≤1s (5Hz nominal alone is not proof of 0.2s synchrony); count *raw*, not interpolated, cross-individual co-fixes with contemporaneous tolerance ≤0.2s, stable bird IDs, measured distance ≤50m. If no raw cross-bird synchronicity, **do not admit short-step social model**.
- Weather station date/time must be in a verified timezone, matched to flight UTC with explicit clock offset/range; **do not match minute wind by nearest date string** without proving timezone and recording alignment. No weather record to support a specific test flight => no valid wind-gated test for that flight. Preserve all missingness and differential availability.
- Wind speed and bearing must have unambiguous units and wind-from/wind-to convention from source metadata; do not infer weather-derived condition by flight outcome.
- Solar azimuth can be computed astronomically using original UTC/location (if sufficient), **but solar visibility/light context cannot be inferred from solar elevation alone**. No solar *uncertainty* effect is admissible without cloud/light/compass perturbation annotations.
- For any paired vs solo comparison, require original phase/release assignment and a no-partner comparator, with device/protocol and cohort effects separated. Do not infer a partner's presence simply because two GPS tracks overlap on an extrapolated interpolation grid.
- If <8 independent biological pair-network groups, do not claim a confirmatory mechanism/general species-level conclusion, but allow a predeclared labeled *exploratory* demonstration with valid source structure and entire connected-component holdouts; do not relax thresholds after opening model outcomes.

## Before ANY numerical movement prediction, freeze a separate v17-B contract

The contract must fix short-step prediction target, own/environment/wind-only baseline, present-neighbor addition, same-partner-stale/partner-swap controls, visibility/availability conditioning, training/test connected-component split, exact repeated-session validation horizon, smoothing/regularization and whole-cluster uncertainty. Decide whether observed wind overlap supports **wind-gated** social prediction BEFORE viewing any per-flight turning outcomes. A context-gated hypothesis requires a *difference in predictive information between independent wind conditions*, not simply an average partner gain. In the absence of adequate source support, halt and report a source-admission boundary.

**Do not update** frozen v6, v8, v15, v16 empirical endpoints or v13 toy-simulation receipts. A v17 source-gate pass alone does not establish an ecological insight.
