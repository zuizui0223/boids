# V8: time synchronization and relative-proximity admission before any Boids forecast

**Frozen prospectively 2026-10-26, before inspecting numeric GPS time or coordinate values.** This new assay is structurally separate from prior v7 ZIP and header-only admission, which confirmed 199 matched dual-tracker flight files, but did not determine timestamp synchrony or distances.

## Independent source and integrity

Pettit et al. pigeon GPS (two field sites), archived CC0 as Zenodo 5010830, DOI `10.5061/dryad.53f4b`. Exact `GPS_tracks.zip` length 35,052,731 bytes; MD5 `8c8e95641182363ea7ad6d0a9a50a3b1`. No source rows or coordinates are redistributed. Public source SHA-256 is re-checked at execution. The dataset is independent of bat v4/v6 and of the method-origin works in batter/ODSP/mina/louis.

## Question

Is there sufficient *actual* synchronized 3D track information to test whether other-pigeon kinematics predict future turning beyond self-history? A matched filename is **not** a synchronized episode.

## Fixed and fail-closed eligibility

1. Use only the two GPS files representing both directions of the *same site × sorted pigeon pair × paired-release index* from the v7 exact filename grammar. This is the flight unit; never double-count the two files.
2. Interpret `Date` and `Time` as absolute local recording clock times via the documented explicit formats in `pigeon_timing_gate.time_value`. Keep the same absolute clock for both birds; do not shift, warp or synchronize post hoc by matching the movement trajectories. Historical CR-only CSV is handled with universal newlines.
3. Each GPS observation needs finite `Latitude`, `Longitude`, and `Altitude`, with valid geographic coordinate ranges. Identical timestamps within a tracker are collapsed to a single record without interpolation. The field `Altitude` is GPS vertical position, **not** AGL or calibrated vertical distance. No model is fitted in this gate.
4. Greedily pair successive fixes without reuse or reversal at **at most 0.11 seconds time mismatch** (a half-sample allowance for published 5 Hz nominal sampling). A flight requires >=30 paired fixes spanning >=5 seconds. No overlap -> exclude with named structural reason.
5. Require >=8 eligible flights from >=3 distinct (site, dyad) groups. Otherwise stop; do not relax numerical cadence or minimum sample size after inspecting this outcome. Independently count the number of eligible flights having >=10 paired observations within 100m, 500m and 1,000m, purely as a social-detection opportunity and not as evidence of actual attraction/avoidance.
6. Outputs are only a structural receipt: aligned-fix counts, finite coordinate missingness, observed cadence, pair-distance quantiles, site/dyad structure. **Do not compute heading, relative velocity, steering coefficients, statistics of future turning, or prediction scores.** No GPS positions are committed.

## What is not identifiable yet

Neither 5 Hz label nor two filenames proves coordinate accuracy, centimeter-level altitude precision, biological perception distances, or enough neighbor-range variability to separately estimate attraction and repulsion. The next stage, if eligible, will predeclare a new pair-cluster holdout and own-versus-real-neighbor-versus-ghost forecasting contract, freezing temporal features and model complexity *before* opening steering outcomes. A positive forecast only identifies predictive information, not a causal Boids force.

The previous [Roy–Abaid bat 3D flight forecast](OBSERVED_BAT_PAIR_RESULT_V6.md) returned an inconclusive actual-versus-ghost gain and is scientifically frozen. It will not be refitted to rescue results.

## Format-only amendment after initial parser stop

The first GitHub numeric-eligibility run stopped at `STOP_REQUIRED_COLUMNS` before scoring any movement response. A separately pinned header-only pass then inspected all 398 matched CSV file headers and found **one identical column set after stripping header whitespace**, with no missing column fields. This is an input-header semantic inconsistency, not an ecological outcome. The numeric CSV reader was amended to trim only leading/trailing **column-label** whitespace (matching the already-used header audit); CSV values, timestamps, eligibility thresholds, and model quantities are untouched. The original stopped run remains in the history. An explicit whitespace-header regression fixture is added. If the unchanged numerical gate subsequently fails, it remains a stop and will not be rescued by retrospectively tuning its time/distance criteria.
