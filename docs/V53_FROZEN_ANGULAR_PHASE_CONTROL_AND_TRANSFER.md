# v53 — Frozen before new outcomes: actual versus 365-day-old tide phase for bearing prediction, plus 2012 transfer

Date: 2026-11-06 JST. Base: `459a40eefca981ba92551997fdfe074b6bee3775` (v52, PR #65).

## Question and evidence status
Does the angular accuracy benefit seen in v52 depend on the contemporaneous measured tidal phase rather than the same station's phase 365 days earlier? Does that bearing benefit recur in 2012 when fitted using 2010+2011?

This is **post-v52 exploratory analysis on the same historically inspected birds**. Earlier speed, vector-error and 2012 outcomes are known. Neither re-scoring 2011 nor computing a newly unscored angular endpoint for 2012 constitutes a new independent population or an untouched raw-data study. No favorable site/year is selected after inspecting outcomes.

## Alternatives and chosen design
A more elaborate spatial/environment model would alter the meaning of the existing positive result. Another AHN2 mask analysis would revisit an already attenuated contrast. Instead, keep the original movement model/source cohort and add one previously specified kind of temporal negative control; assess a fixed subsequent-year split. This choice is an analysis decision under the user's continuation request, not an asserted independent protocol approval.

## Immutable source and model
- Original Zenodo O_SCHIERMONNIKOOG and O_AMELAND annual GPS gzip, 2010–2012. Published MD5 and previously recorded SHA256 must match. Import original v41 hourly first-fix, region/visibility, three-fix eligibility and 0.4–120 km/h and 30–120 minute gates unchanged. Primary native source clock is provisionally UTC (0 seconds), as v52. UTC/GPS standard remains unresolved, particularly the 2012 leap-second change; no clock search.
- Actual measured RWS WATHTE meting, cm NAP converted to metres, source fixed UTC+01 at the original two stations. Use v39 historical source helper for 2009–2011 and v40 original-2012 helper. Expect 52,561 unique observations per nonleap year and 52,705 for 2012. Any source failure is a STOP, not an ecological null.
- Keep true tide h(t), phase p(t) and source rows exactly as v41. Current slack phase is excluded by that existing parser. The placebo is **p(t−365 days)** from genuine measured water at the same station, not a synthetic sine wave. Merge the original 2009–2012 gauge objects with strict duplicate consistency for placebo lookup, since in leap-year 2012 a fixed 365-day shift is not the same calendar date of the prior year and late December 2012 can map to January 2012. Never silently substitute calendar-year replacement.
- Retain only the common rows with actual and 365-day-old phase available, before fitting ALL compared models. Placebo phase zero is retained. Report all removed counts. Predictor replacement changes only `phase`, not actual h(t), position, private movement history, clocks or target. All outputs remain source aggregates; no original tracks, tag IDs, exact observation times or source gauge values committed.

M0 = original v41 baseline: actual height and square, current B position, diel/year clocks, own previous A→B unit heading and log1p speed.
Mactual = M0 + actual p(t) and p(t)×actual h(t).
M365 = M0 + measured p(t−365d) and p(t−365d)×actual h(t).

Import the original v41 `forecast` unchanged: training-only feature scaling, equal total training weight per bird, ridge 10, no test-derived tuning. M365 is obtained by replacing the phase field in both train and test copies, then invoking the same level-1 model. C position, C heading, future speed and tide-derived outcomes never enter features.

## Splits, replay and admission
Primary: train 2010, test 2011, separately at BOTH sites. Before placebo/common-support scoring, replay the exact v52/v43 whole-source counts and M0/Mactual vector losses using v52 `check_replay`. New common-support model outcomes are not conflated with the old full-source forecast.

Secondary temporal transfer: train 2010+2011, test 2012. Retain the existing directional minimum: >=1,000 train and test episodes, >=3 test birds, >=4 ISO weeks. Schier 2012 previously had 869 original heading episodes and remains NOT_ADMITTED if unchanged; do not lower the gate. Ameland 2012 previously had 1,186 episodes from 3 birds. Check original 2012 source counts and, for the admitted unfiltered Ameland cohort, reproduce previous vector MSEs (M0 0.4389851852; Mactual 0.4101246782, tolerance 1e-9) before new angular claims. A failure of source admission produces counts only, not a fitted test result.

## Endpoints and uncertainty
For every admitted test cohort, normalize each model's nonzero predicted vector. No norm clipping, direction fitting or target-dependent row filtering. A norm <=1e-12 in any compared model triggers angular NOT_ADMITTED for that cohort; do not assign arbitrary bearings.

Primary endpoint: equal-bird cosine loss `1 − dot(observed_unit_heading, predicted_unit_heading)`. **Primary contrast: M365 loss − Mactual loss** on identical rows. Positive means contemporaneous phase beats the specified historical control. Also report M0−Mactual and M0−M365 regardless of sign. Secondary: absolute angular error in degrees and original vector half-MSE.

Compute per-bird averages first and resample paired whole birds 10,000 times (seed 20261106), keeping all models together. Separately average equal present-bird means within ISO weeks then equal weeks, with paired whole-week 4,000 draws and seed+1. Each point must be paired with its own matching interval; weeks are serially dependent and these intervals do not represent independent populations. Report positive bird/week counts and each model's mean loss. For 2012, compute the same three contrasts as explicitly secondary temporal evidence; 3 birds yield fragile population inference.

## Interpretation limits
A real-over-M365 angular benefit supports time-specific predictive information beyond this one historical temporal control; it does not exclude all periodic, spatial, behavioral or sampling alternatives. A M365 benefit can arise from retained tidal/seasonal structure; never describe prior-year water as physically causing the bird's current action. A 2012 improvement extends a temporal forecast within source cohorts, not species/site universality.

No tide-front pursuit, food availability, calibrated acceleration, Reynolds social force, or species niche separation identified. Preserve existing v52 positives and v51 matched-mask results even when a new contrast is uncertain or negative. Do not add new lags, favorable subsets or alternative losses after seeing these outcomes.

## Implementation plan and checks
1. Add pure tests before implementation for fixed-duration placebo dates (including 2012-12-31), actual-height immutability, common row support, placebo zero, chronological gates, undefined bearings, paired bird/week estimands and cross-model loss consistency.
2. Implement a small pure comparison module plus a lazy-import source runner. Reuse v52 decomposition and original v41 forecasts instead of recreating estimators. Test source SHA/MD5 and original replay gates.
3. Run local pure v53 and v52 tests plus an independent numerical aggregation check. Publish only additive files on this isolated research branch; main/prior files unchanged.
4. One serialized two-site GitHub Actions run with original field sources and inherited regression tests. Save aggregate JSONs only. Do not repeatedly dispatch while waiting.
5. Inspect both observed outcomes, compute user-facing degrees/uncertainty from saved evidence, archive result notes and open a Draft stacked PR. Report any unfinished source evaluation honestly rather than promise later delivery.
