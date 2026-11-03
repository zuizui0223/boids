# v39 — PRE-OUTCOME OF v39: historical tidal-phase identity versus previous-year temporal placebo

**2026-11-02 JST. Fixed before seeing ANY v39 original placebo outcomes.** Prior v32, v33, v34 and v36 observational results were already known. This is **POST-RESULT DIAGNOSTIC**, not a new untouched confirmation of v32.

## Ecological and measurement question
Can the original observed phase at the bird's time contribute to out-of-year movement prediction beyond measured water height, geography, annual/diel rhythms, **and the same station's different tidal phase exactly one calendar year earlier**? The previous-year phase retains a real station's amplitude, nonstationary meteorological variation, seasonal/daytime sampling and other cyclical structure but has no reason to mark the precise original bird's contemporaneous exposure. It is a *specific source-grounded negative control*, not the sole possible null.

## Frozen cohort and identical predictions
Original, provider MD5 verified 2010 and 2011 GPS annual files from two studies: Schiermonnikoog Zenodo 22296922 and Ameland Zenodo 10053853. Historical measured WATHTE NAP (cm) from RWS original station `schiermonnikoog.waddenzee` and `ameland.nes`, calendar years **2009, 2010, 2011**. Fixed monthly or year-aggregated original RWS historical source API, strict source metre/datum/time acceptance, including original fixed UTC+01 in all seasons.

For each island **fit solely 2010 GPS and predict every eligible 2011 GPS bird**; original first visible GPS fix per UTC hour, next source fix 0.5–2h later, great-circle displacement `log1p(km/h)`, exactly same source spatial bounds, both sites and all years. Treat original native GPS timestamp as provisional UTC (primary) and -15s (sensitivity). No prior source GPS joined to different-year bird outcomes.

For each 2010/2011 source GPS step at t, receive original contemporaneous water level h(t) and source observed phase at t using trailing 20-min gauge slope with ±0.012m/h threshold (phase -1/0/+1). Placebo is **the same station at t−365 days**, trailing 20-min phase, from genuine verified 2009 and 2010 observations. Sample is restricted to rows for which both contemporaneous and year-ago phase are available with no >30min RWS sampling gap. No phase-specific filtering AFTER original true-phase slack exclusion; importantly the placebo phase **can equal zero** without dropping a row. Exact same train and test rows for ALL compared models.

Three fixed models with exact v33 design:
- `M0`: intercept, true original h(t), h², source lat/lon and diel/year sin/cos.
- `Mactual`: M0 + true tide phase(t) and phase(t)×h(t).
- `Myear_ago`: M0 + previous-year tide phase(t−365d) and phase(t−365d)×original h(t).
- Fixed train-only standardization, ridge penalty λ=10, equal bird training weights. No learned model tuning or alternate lag selection.

Pre-frozen primary signed predictor contrasts for each site: `M0−Mactual` (actual phase additional info), `M0−Myear_ago` (temporal placebo), `Myear_ago−Mactual` (incremental true over placebo). Report all including negatives.

## Honest confidence intervals for actual estimands
For each contrast, compute:
1. **Equal-bird pooled MSE contrast** = mean over test birds of source test-row MSE differences; 10,000 whole-bird bootstrap draws, 95% percentile CI for precisely this equal-bird estimand.
2. **Equal-week-then-bird MSE contrast** = mean across test ISO weeks of that week's equal-bird-per-present-week MSE difference; 4,000 whole-week resamples, 95% percentile CI for precisely this distinct equal-week estimand.

Do not position the equal-week bootstrap CI as a confidence interval for the pooled equal-bird headline statistic; v36 had precisely this mismatch. Also report number of shared source-bird and source-weeks, test steps, positive birds, positive weeks, original checksums and exact source-unit receipts. A few test birds or serial week dependence limit frequentist interpretation; this audit does not identify a causal tidal response.

## Interpretation
- Actual beats year-ago placebo in an independent 2011 test: compatible with biologically relevant exact-phase timing beyond broad calendar and station annual structure. Does NOT identify actual prey-exposure front, social force or animal sensory cue. Native source clocks UTC vs GPS time unresolved, gauge local lag and animal activity mix remain.
- Placebo also predictive: phase may be proxying seasonal/diel sampling or other patterns, interpret with appropriate caveat rather than selecting model to rescue the original thesis.
- Actual does not outperform placebo: the historical association lacks phase-specific evidence under this control, not necessarily a real zero tide effect.
- Same species in two neighboring Wadden islands: still no multi-species generality, no original local intertidal DEM, no causal moving wet/dry boundary or social Boids inference.

No raw animal fixes, individual identifiers or raw water observations committed. All results from checked original bytes stored as aggregate JSON only. Execute identical inputs, UTC and -15s scenarios, neither result allowed to determine a post hoc lag choice.
