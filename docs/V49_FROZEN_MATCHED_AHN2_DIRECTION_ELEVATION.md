# v49 FROZEN POST-v48 matched AHN2-valid original GPS direction versus destination height phase test

**2026-11-05 JST; fixed before ANY v49 matched direction-versus-elevation numerical score.** Existing v43/v44 original direction field positives and v48 AHN2 destination height negative/inconclusive results are already known. This is strictly **post-result exploratory**, not independent confirmatory replication or a new bird cohort.

## Biological and statistical question

On the **EXACT SAME** original three-fix GPS sequences A→B→C for which the historical AHN2 source provides a valid **next destination terrain elevation** `z(C)`, is measured real tide ebb/flood phase at B more predictive of (1) the next original horizontal **direction** B→C, than of (2) the next independently measured **terrain elevation** z(C)?

Earlier comparisons v43/v44 heading used Schier 4,948 and Ameland 4,678 original 2011 triples while v48 z(C) used Schier **1,009** and Ameland **1,238**. v49 fixes that original denominator mismatch. DO NOT claim directional effect persists on height-labeled subset before running and inspecting v49 original results.

## Source, same triple and physical limits

- Reuse v48 code `source_hourly`, `freeze_training_cells`, `source_tile`, `admission_rows` UNCHANGED. Published original Zenodo GPS gzip and source MD5, 2010/2011 original hourly visible A→B→C with both 30–120min and both 0.4–120 km/h, same 2010 selected K=8 2km RD source cells, historical AHN2 2007–2012 official WCS DTM EPSG:28992 NAP metre **candidate** first band with second normalized 0–1 auxiliary ≥0.999. No water/no-data fill. Original 2011 C-only source height available Schier 1,018, Ameland 1,243 before tide/slack joins.
- Independently reread original 2010/2011 three-fix A,B,C from the source *in memory* and derive the observed **next B→C east/north unit vector**, keyed by exact `(source_bird, original B timestamp)`. Cross-check with each v48 row after provisional UTC shift; require every v48 admission row to match **exactly once**, and no future C direction or z(C) may enter features. Source matching errors are hard SOURCE_STOP; do not select a favorable subset by observed effects.
- Three RWS source WATHTE `meting` years 2009,2010,2011 at exactly `schiermonnikoog.waddenzee` / `ameland.nes`, fixed original UTC+01 and NAP cm converted to metres. Original current tide h(B), prior-20min ebb/flood phase p(B) ±.012 m/h; source previous-year p(B−365 days) negative control from the same original station. All three models share exact source rows and true current h(B), excluding true slack source only, retaining ghost slack.
- GPS native UTC vs GPS time is unresolved. Primary = original source naive time interpreted UTC; sensitivity −15s, **no model or date selection**.

## Fixed 2010-to-2011 external-year paired forecast

All 2010 source C-valid A→B→C rows fit each island's separately trained model; all 2011 source C-valid A→B→C rows are held out with no outcome-derived selection. Same exactly imported v41 12-feature M0 design and 14-feature Mreal/Mghost design, same train-only standardization, equal source-bird total training weights, ridge λ=10, unpenalized intercept.

Two independent target columns on **identical rows**:
1. Next horizontal direction B→C: original east/north unit-vector target. Loss `0.5×[(e−pred_e)^2+(n−pred_n)^2]` (dimensionless).
2. Historical AHN2 original destination first-band height z(C) NAP m, **independent of tidal water source**. Loss `[z_C−pred_z]^2` (m²), same as v48.

**Frozen models:** M0=absolute contemporaneous height h(B), h², current source B lat/lon, diel+year cyclical time, previous own east/north direction and log1p prior speed; Mreal=M0+source p(B)+p(B)×h(B); Mghost=M0+same station observed p(B−365d)+pghost×actual h(B). Independent ridge response-head fits with EXACT same features, training row weights and test source rows. **Mandatory replay gate:** matching direction predictions on exact v48 C-height-valid original rows must agree with imported v41 `forecast(train,test,0/1)` to absolute tolerance 1e−9; matching z(C) predictions with v48 `predict_z` for M0/Mreal/Mghost must agree 1e−9. No adjustment if replay fails.

**Predeclared source gates** retained from v48: >=400 training rows, >=500 2011 heldout test rows, >=3 heldout birds, >=4 ISO weeks, >=2 original selected terrain cells. If any fail, both targets marked **NOT_ADMITTED** and NO predictive ecological effects computed.

For each endpoint: M0 and Mreal loss, signed relative error reduction `R=1−MSE(Mreal)/MSE(M0)`. Primary cross-axis comparison `R_heading−R_zC` (ratio-of-own-baseline, percentage points), resampling **all 4 aligned test loss columns** together at source bird level for 10k whole-bird paired bootstrap and independently at week level 4k, both fixed seed 20261105. Each CI must match its corresponding pooled equal-bird or equal-week-then-bird point. Report 0/positive birds & weeks for each endpoint and gap; no comparison of raw MSE units. The negative-control paired comparison **Mghost−Mreal** for direction and altitude is secondary; report signed MSE gain and bird-level boot CI for both without selecting a favorable outcome.

## Explicit limits

A **positive heading vs altitude relative skill gap** in C-source-valid common GPS source would support a *predictive* distinction between directional re-routing information and simply arriving at a different historical ground elevation. It does not show the bird followed a newly exposed front or that source C height is a synchronous, wet/dry physical condition. A negative or uncertain result would show that earlier full-cohort heading benefit may not transfer to the AHN2-observable subset, not falsify existing v43/v44 all-moving GPS results. The selected C-habitat domain differs from all GPS, and the source terrains omit water with uncertain source auxiliary-band semantics and changing intertidal bed surveys. No verified feeding, prey, local tide phase propagation, 3D flight forces, species-level niche divergence or actual social Boids Reynolds coefficients follow from these endpoints.

Treat all population-wide claims as tentative: Schier and Ameland are same species and geographically close; original data and sites already inspected repeatedly. This is post-result exploratory and requires separate independent coastal tracking populations for confirmation.
