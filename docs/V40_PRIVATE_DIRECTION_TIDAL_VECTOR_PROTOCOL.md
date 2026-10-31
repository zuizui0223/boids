# v40 — Does previous movement DIRECTION forecast future GPS vector beyond tide, location and previous speed?

**Frozen 2026-10-31 JST before opening the NEW next-step vector/direction contrast.** All v33–v39 original GPS velocity/tidal effects were already known; this is an explicitly *exploratory*, same-source, time-forward question, NOT independent animal/population replication, not prospective in advance of observing original data, not confirmation of an identified cognitive mechanism.

## Motivation & fixed scope

The exact original v39 source experiment, at Schiermonnikoog Waddenzee, finds held-out speed MSE 0.2522385→0.2464089 when adding the SAME bird's prior disjoint speed after flexible current tide H,dH, their interaction, time/season, location, tag regime and bird effects (21 birds/305257 future step episodes; 2010–12). But scalar speed may predict without predicting direction, spacing or Boids social steering.

Our present question: **Does the prior moving direction within the SAME bird add out-of-time predictive information about the NEXT observed horizontal movement vector, after conditioning on the prior SPEED and contemporaneous tidal state?**

Exactly one source:
- Zenodo **10053970 v4** original `O_SCHIERMONNIKOOG` Eurasian oystercatcher GPS, all seven 2008–2014 original gzip files, original published MD5 and previously pinned SHA256. Reuse original `validation_v32/forecast.py` source admission and `validation_v33/phase_response.py` original flags and de-duplicated fixes.
- Rijkswaterstaat official `schiermonnikoog.waddenzee` **ASTRONOMICAL** WATHTE, 10min, cm/NAP, original 2008–2014, source timestamp +01:00 offset converted to UTC; no future actual measured storm tide.
- Do not fetch alternative data or optimize bird/year based on observed directions.

## Original exact cohort + leakage gate

Reuse the **v39** original candidate episode definition IDENTICALLY, from four distinct GPS points `i-2,i-1,i,i+1` per bird: prior disjoint original step i-2→i-1 in [5,30]min, gap from old step END to upcoming step START [5,360]min, future original observed step i→i+1 in [5,30]min, all four points within 25km of the RWS gauge. Original source outlier/visible filters; no interpolation; no original pair shares a GPS fix. Use the *same* current/tide/clock/location/bird/cadence E1 baseline X matrix from v39 and its exact source task. The unknown next-fix INTERVAL is used to determine the evaluation cohort and response but NEVER provided as a forecast feature. This is a *conditional next-observed-GPS-pair forecast*, not operational prediction of arbitrary future position.

**Before any directional score is released**:
1. Recalculate frozen v33-D original high-low tide source + 36-bird/5422 matched-strata full anonymous numerical/source receipt to abs 1e-12.
2. Recalculate ALL v39 frozen 21-bird / 305257 held-out speed predictive model, baseline/four-model MSE and signed results + per-bird numbers to abs 1e-12 against GitHub-committed `validation_v39/results/conditional_private_history_over_tide_v39.json`. Exact equality tolerance 1e-12 for all floats and no missing keys.
3. New *directional* eligible episodes must match original v39's exact original 328323 candidate rows, original `start`, `end`, `bird`, prior log-speed and original future log-speed for every row. STOP before new scores if anything drifts.

## Fixed new directional response

At target original GPS start (known)→future next original GPS coordinate (observed only as ground truth), compute true great-circle displacement D km and spherical initial bearing θ (east = D×sin θ, north=D×cos θ); divide each component by the original future GPS pair's actual duration in h **only for computing the target label**. Inverse of source asinh target transform is exact velocity km/h, with **no future duration used in predictors**.

The two response coordinates are `Y_e = asinh(v_e / 1km/h)`, `Y_n = asinh(v_n / 1km/h)`. This bounds tail influence but does not censor fast flights; every original v39 episode is retained, including zero-displacement points (Y=0). **PRIMARY SCORE:** per episode squared 2D transformed movement vector error `(Y_e-pred_e)^2+(Y_n-pred_n)^2`. MSE by whole original bird then equal bird, on exactly the v39 original common 305257 eligible future episodes; no favorable direction or distance subset.

**SECONDARY directional-only score**: for an *actually observed* future target displacement >= **0.05 km** (to avoid interpreting stationary GPS jitter as a reliable direction), calculate `1−cos(θ_true−θ_pred)`. Convert predicted asinh two-axis output back to km/h with sinh, use normalized 2D predicted bearing; if predicted speed norm <0.05 km/h, give a neutral loss **1.0**, rather than drop difficult predictions. This outcome-specific observation threshold is an explicit **evaluation-only** subset and cannot become a target-feature. Score only if at least 20 birds each with ≥20 future directional episodes and ≥10000 full angular future episodes, otherwise no angle result. Match EXACTLY the same directional subset for all four models.

## Frozen four vector models

All four fit the identical previous v39 ridge features with frozen `alpha=25` and time-blocked 7d-embargo protocol. Model coefficients are fitted separately for two response axes by two-output ridge with a common X, not post-result joint tuning. No data-driven standardization fitted on test or future telemetry.

- **V0**, environment-and-private-speed baseline: original v39 **E1** features: current astronomical H,dH, H²/dH², H×dH, |dH|, analytic non-georeferenced v38 tide-height×direction term, UTC hours (12h & 24h), annual season/year, bird fixed intercept, current public-gauge-relative latitude/longitude and fixed quadratic/cross spatial terms, **past observed GPS pair duration and gap**, and previous disjoint same-bird scalar log1p SPEED. Thus previous amplitude of motion is already controlled.
- **V1**, V0 + previous **disjoint** same-bird step heading unit vector `(sin θ_prev, cos θ_prev)` (if original prior displacement is exactly zero set both to zero and retain the point); this is the ONLY prespecified primary added predictor.
- **V2**, V0 + previous astronomical H,dH from exactly **t−3 hours**, already found weak in scalar v39.
- **V3**, V0 + previous heading unit vector + previous astronomical H,dH.

**PRIMARY signed difference `MSE(V0)−MSE(V1)`**, positive if the same bird's *previous direction* adds held-out future vector prediction beyond private scalar speed. Preset secondary `V0−V2`, `V2−V3`, `V1−V3`. Report all four absolute errors, all contrast signs/95% whole-bird bootstrap/individual signs, both vector and angular secondary, and original-year/year-month heterogeneity even if null, negative or source stop.

## Chronological scoring and support fixed from v39

Test original UTC months 2010-01 through 2014-12. Each test month M is trained only on original future-step outcomes with **end UTC < first day of M minus 7 calendar days**. Minimum **5000** eligible training steps from **10** distinct original birds before scoring each month; same four-model target days, no current/future outcome fitted to ridge. Held-out final whole-bird gate: ≥20 original bird IDs with ≥30 future step episodes, ≥10000 future episodes, spanning ≥3 original GPS calendar years and ≥12 original UTC months; else `NOT_ADMITTED` and NO direction MSE/angle effect. 10k paired whole-bird bootstrap, RNG 20261031, exact one-sided positive sign tail; additional naïve equal-month bootstrap descriptive only, not independent ecosystems.

Annual source coverage is expected to be 2010–12 and dominated by 2010, as v39; report source effect differences without asserting 2013/14 future support. Any positive predictive information may reflect **inertial heading**, same site/corridor, unmeasured flow/wind, food and roost location, GPS duty or correlated errors. It does not identify internal navigational memory, social alignment/separation/cohesion, causal wetland accessibility, 3D vertical niche or between-species community mechanisms. Conversely a null does not prove individual heading has no role in other source cohorts.

## Reproducibility & privacy

- Commit this protocol separately before final implementation and new directional score; unit tests must check nonoverlapping four original fixes, true spherical E/N vector, zero-displacement bearing, exact v39 feature and episode identity, fixed tide lag, identical model cohort, embargo, source effect sign, high-dist angular mask and low predicted direction neutral penalty. Source CI replays all previous receipts in read-only runner.
- No new raw animal GPS files, bird IDs/coordinates/timestamps, raw tide curves or per-fix directions in repository; save anonymized per-bird and annual/month aggregate only. Preserve prior PR #42 and #40 and all v29–v39 source outcomes without merge. Separate draft PR stacked on v39.
