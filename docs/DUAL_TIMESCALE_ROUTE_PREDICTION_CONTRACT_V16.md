# v16-B outcome-blind dual-timescale prediction protocol — conditional on verified GPS schema

**Registered 2026-10-28 before any v16 fast/slow target or held-out prediction outcome was computed.** This is separate from the [v16-A source gate](EIGHT_FLOCK_INDEPENDENT_SOURCE_CONTRACT_V16.md). Its numerical endpoints are NOT run until timestamps, coordinate encoding, fix status and source eligibility have been confirmed by the source-only schema scan.

## Scientific question

Does repeated personal/flock route history carry predictive information across releases when extra **instantaneous neighbor motion** may carry little transferable information in rapid course adjustment?

This is a test of **navigation-route predictability across timescales**, not food-resource/feeding niche partition, true animal memory, innate strategy, experimentally rewired network edges or biological Reynolds coefficients. The paper's clock-shift manipulation supplies independent variation in *navigational information quality*, but categorical treatment labels must be verified from a pre-outcome schedule before any condition-wise causal interpretation.

## Shared source

- 8 experimental pigeon flocks in Watts et al. (2016), Zenodo [4943714](https://zenodo.org/records/4943714), dataset DOI `10.5061/dryad.508j2`, CC0.
- Pinned downloaded source `Data.zip`, 272,270,105 bytes, published MD5 `ab0950ffebd924950632f727cd487c27`, independently computed SHA256 `7380feccd8c2e4e1675679411d1ee8075cd29ccbd2dada98e317ca88053ffbfa`.
- Source contains **559 recognized true GPS CSVs**, **178 AppleDouble `._` sidecar files discarded** (not biological samples). Original CSV header has `VALID`, `UTC DATE`, `UTC TIME`, `MS`, `LATITUDE`, `N/S`, `LONGITUDE`, `E/W`, `ALTITUDE`, `SPEED`, `HEADING`, etc. Pure header/filename gate already found 8 flocks with 13–15 release IDs and at least 4 recurrent bird IDs per flock. No outcome has been analyzed.
- All data processing is ephemeral; only aggregate per-flock and per-release validation/performance is saved. No source tracks are redistributed.

## Shared observation and independence constraints

- Parse **actual recorded UTC date/time+milliseconds**; do not equalize rows by ordinal index or synthesize missing clock records. If time parsing/clock-resolution checks fail, report `NOT_ADMITTED` for the fast layer without rescuing by interpolating timestamps.
- Geographic origin is the published release site at Bladon (51°49'23.48"N, 1°21'26.29"W). Convert original GPS coordinates to metric east/north axes using a single fixed small-area equirectangular projection (reference latitude from site, Earth radius 6,371,008.8 m). This is adequate for the ~5.3-km short routes and may be sensitivity-checked with a metric UTM CRS only if declared separately.
- Define an *in-flight spatial window* using **first outbound radial progress from 500m through 4500m** from the published release site. Only recorded fixes with finite valid coordinates, UTC, and non-duplicated GPS times are eligible. Do not interpret pre-launch stationary fixes or home-rest time as flight. Fix gaps >1.0s split segments; any speed/position plausibility guard must be set from independent device metadata and sensor-quality checks, not fitted target outcomes.
- Group is the published *flock identifier*, not an inferred post-outcome cluster; identity is the original *flock + bird code*, not the bird code alone. Treat complete flock as the independent inferential unit (N at most 8); repeated birds and releases are not independent clusters.
- Define *flock-level cross-validation* with exactly 8 leave-one-flock-out folds. Training for generic parameters can only use the other seven flocks. Within the held-out flock, **past releases may be used only to construct an explicitly permitted historic template** used for forecasting strictly later releases. No future-release data are used for predictor engineering, normalization, social network definition or tuning.

## Slow route-state target (registered primary, pending source-time admission)

- Reference each bird's release route by the first **observed outward crossing** of nine preselected radial shells: `r=500,1000,...,4500m`. A crossing is admitted only if the first recorded point at/above the radius is within **50m** of the target shell and belongs to an unbroken valid track. Do not linearly interpolate a fictional GPS observation.
- Response: circular **geographic bearing** from published release site to the observed crossing. This is a predictable route-state marker, *not a measured feeding niche or interspecific competition*.
- **Historic** training: releases `5–8` only for bird/flock template (the last four published training releases). Test: releases `9–15` as available; never mix a future release into historical references. If sources show different actual treatment/stage mapping, retain numeric release split and do not relabel it after opening outcomes.
- Slow models, all scored on the same held-out bird×release×shell records:
  - `S0` other-flock **source-population** baseline: circular-mean historical bearing at each radial shell, using releases 5–8 of *seven other flocks*, each flock total contribution equal;
  - `S1` *same flock's historic* bearing at each radial shell, mean across its repeated birds/releases, with equal bird weighting;
  - `S2` *same individual's historic* bearing at each radial shell, with group backoff **only** when the individual has no source-fixed historic support; such unsupported records must be scored by all three models or omitted from all three **based solely on historical support**, never outcome value.
- Main slow predictive endpoint: `Δ_slow = MSE(S0) - MSE(S1)` in wrapped bearing radians². Secondary individual addition `MSE(S1) - MSE(S2)`. Report every flock, positive count, full number of releases/shell observations, and equal-flock mean. No per-fix or per-shell iid p-value.

## Fast turn target (registered secondary; require actual synchronous clocks)

- Response `wrap(course_heading(t+1s) - course_heading(t))`, with original non-interpolated measured GPS heading; nominal candidate anchor every **5 seconds UTC**, requiring measured heading at t−10, t−1, t and t+1 within **≤0.2 seconds** each from that requested time and from the same valid ongoing segment.
- Nearest *recorded at/before t* neighbor within **100m**, and the **same neighbor** tracked t−10 with their observation at/before focal's t−10 position, no later than 0.2 s. Do not select neighbor based on response or future releases. Fixed feature sets:
  - `F0`: intercept, sin/cos own t heading, own course-turn over t−1→t, own speed/scale if units established, path progress fraction and cross-track position to the release–home orientation (all at/before t);
  - `F1`: F0 + relative present-neighbor along/lateral displacement and relative heading at t;
  - `F2`: F0 + **same** relative features using both focal and partner states at t−10. Do not compare stale neighbor to present focal position.
- Fixed ridge penalty `alpha=30`, training-fold mean/scale only, training trials balanced by independent flock, 8 source-flock holdouts. Primary fast contrast `Δ_fast = MSE(F2) - MSE(F1)`; also show own versus current. If one flock has <60 common eligible target anchors or <3 focal birds, report **fast-layer NOT_ADMITTED** rather than changing the threshold. With 8 flocks a one-sided unanimous sign-test could be as small as 1/256=0.00390625, but this does *not* establish universality.
- Clock-shift conditions are NOT a fast model feature until independently verified for all releases. Since small timestamp errors can affect turn targets, no positive force coefficients are inferred from any F model.

## Cross-timescale synthesis and falsification

- Report signed `Δ_fast`, `Δ_slow` **separately** in rad² on different outcomes and their 8-flock paired sign table. These numeric magnitudes are **not comparable as a single pooled effect size**; do not simply subtract radians² for two distinct targets and call it a universal hierarchy index.
- Do not call fast absence merely because p>0.05; an *equivalence* claim would require an independently justified effect margin and enough clusters. Association between fast and slow gains across flocks is exploratory, not causal proof of social learning.
- If S1 fails to beat S0 on held-out future releases, the proposed transferable flock-history effect is **not supported**. If S2 beats S1, it suggests additional *predictive individual-history structure* but does not identify memory versus persistent route/environment effects. If F1 beats F2, it suggests contemporaneous information in this predictor; it does not recover attractive/repulsive Reynolds forces.
- In any event leave v6/v8/v15 observed endpoints frozen and v13 synthetic mechanism strictly separated.
