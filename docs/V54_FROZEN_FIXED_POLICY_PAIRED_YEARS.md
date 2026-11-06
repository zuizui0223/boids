# v54 — Fixed 2010 directional policy, shared individuals and 2011–2012 transfer

**Frozen 2026-11-06 before new v54 scores. Base commit `1e256592fb7b20d3fa9184aef0a1436684a9d8b5`.** v52–v53 angular outcomes are already known. This is post-result exploratory diagnosis of previously inspected historical Ameland GPS, not an untouched population/year confirmation.

## Question and design choice

The v53 2011 and 2012 comparison changed both the training sample (2010 versus 2010+2011) and test individuals/observations. We will distinguish (a) the consequence of updating the fitted model on the SAME 2012 test observations and (b) year-associated performance on the SAME original tracked identities with a FIXED 2010-trained policy. Independent new field data would be stronger confirmation but are outside this diagnostic. No new lag, environmental term, estimator or source selection is tuned.

**Only Ameland** is analyzed: its original 2012 cohort passes the unchanged 1,000-episode/3-individual/4-week gate. Schiermonnikoog's original 869 episodes remain NOT_ADMITTED; no lowering of that threshold and no new Schier 2012 score. This choice is fixed from v53 source support, not from new v54 outcomes.

## Immutable original sources and predictors

Reuse v53 original annual GPS downloads, publisher MD5 and pinned SHA256, original RWS `ameland.nes` WATHTE meting cm/NAP fixed UTC+01, years 2009–2012, counts 52,561/52,561/52,561/52,705. Reuse the v41 original three-fix parser and weighted ridge: earliest genuine visible GPS fix per source UTC-assumed hour; both A–B and B–C 30–120 minutes and 0.4–120 km/h; current source tide phase from trailing 20-minute slope; no new interpolated animal fixes. Actual source clock remains UTC/GPS unresolved.

M0: actual height and square, B latitude/longitude, diel/annual cycles, previous own unit heading and log1p speed. Mactual adds actual phase and phase×height; M365 replaces only phase with the same gauge's original phase exactly 365 days earlier, current h unchanged. Merge original gauge years consistently as v53; previous-year slack retained. All three models must share original rows. Require zero removals from the historical-phase join to preserve the exact known cohorts.

Original Ameland counts: 2010 training 3,753, 2011 test 4,678 (5 individuals, 53 weeks), 2012 test 1,186 (3 individuals, 50 weeks). Recheck source SHA/MD5 and full v52 2011 vector replay, v41 2012 vector replay, plus v53 scalar angular baselines before any new interpretation. No raw animal identifiers, tracks, observation timestamps or raw water records persisted.

## Fitted policies and estimands

1. **Fixed policy F10**: fit M0/Mactual/M365 only on 2010. Use those unchanged parameters/scaling to predict BOTH 2011 and 2012 (one concatenated test prediction per model). 2011 is the already established v53 result; 2012 under F10 is new.
2. **Updated policy F1011**: fit only on 2010+2011 and predict 2012. This must exactly replay v53 2012; do not evaluate it on its own 2011 training outcomes.
3. Normalize bearings exactly as v52, with hard stop on undefined near-zero predicted vector; never drop unfavorable undefined rows or invent a bearing. Primary metric is cosine loss. Mean absolute angular error (degrees) and original vector half-MSE are secondary.

Let G = loss(M365) − loss(Mactual), positive favors actual over historical phase. Also retain H = loss(M0) − loss(Mactual). Report all model loss means, G and H, including negatives.

**Primary diagnostic:** for repeated original identifiers meeting both-year support, D_year = G(F10, 2012) − G(F10, 2011). The SAME bird's paired annual mean is the resampling unit. D_year < 0 means the fixed policy's actual-versus-historical benefit is smaller on these 2012 observations. This is a prediction-performance change, not a causal change of biological tidal sensitivity.

**Training-update diagnostic:** on exactly the same 1,186 test rows/three birds in 2012, D_update = G(F1011, 2012) − G(F10, 2012). Pair all model errors within individual. Also report old-minus-updated losses for each of M0/Mactual/M365, so differential changes in the comparator cannot be mislabeled as improvement in actual heading accuracy.

## Repeated-identity and calendar matching

Use exact `individual-local-identifier` strings within the original study as recurrent tracked identities; no biological re-identification beyond provider metadata. Do not assume every 2012 individual occurs in 2011. Publish overlap COUNTS only.

Repeated-identity primary support: at least 3 shared source identifiers; each has at least 50 admitted original episodes and 4 ISO weeks in EACH test year. If fewer than 3, return NOT_ADMITTED for paired inference and retain full-cohort forecasts/source counts without an invented paired CI. The original full-year source gate remains mandatory; the paired analysis is a nested descriptive diagnostic, not a relaxed new source holdout.

Prespecified secondary: within each eligible shared identity, retain calendar months with at least 10 episodes in EACH year. Require at least 2 common months per identity, at least 3 identities, and at least 100 total retained observations in EACH year. Average each month equally within identity, then average identities equally; use the SAME retained month set and weights for both years. Resample whole identities in paired form. This controls month participation, not route, clock-hour, tidal stage, activity, local habitat or detection differences. A failed calendar gate is NOT_ADMITTED, not a zero effect. Do not introduce different time bins after looking at scores.

## Uncertainty and replay

10,000 paired whole-identity bootstrap draws, fixed seed 20261106; all relevant model loss columns resampled together. Report point differences and percentile intervals for their actual paired equal-identity estimand. Each year’s full-cohort v53 summaries also include distinct equal-week-then-present-identity estimates/4,000-week draws; these are not intervals for the bird-equal estimates. No claim that weeks are independent ecosystems. With only three 2012 identities, all population-level intervals remain conditional and fragile.

## Implementation plan

- [ ] Pure module `validation_v54/paired_year_diagnostics.py`: assemble aligned v52 angular losses; paired year and paired training-update summaries; strict input years/unique keys and original identity matching; matching source gates.
- [ ] Tests first, observe missing-feature failure, then implement. Test positive/negative paired signs, unequal monthly opportunity, ID turnover, missing/duplicate source rows, undefined bearings, leakage/phase replacement, and invariance to prediction length.
- [ ] Runner `validation_v54/run_fixed_policy_years.py`: lazy inherited source imports, exact original-source replay, F10 fixed prediction and F1011 replay, aggregate-only outputs. One serialized original-source CI job, no duplicate pull-request-triggered remote downloads.
- [ ] Independent synthetic calculation by a separate aggregation implementation; inherited v52/v53/v41/v43 tests; fresh verification before reporting.
- [ ] Record all results and limitations in a Japanese research note and aggregate numerical receipt, create Draft stacked PR only. Do not merge main.

## Interpretation boundary

No new species, independent field population, prey-front tracking, true social force or physical angular acceleration is measured. Training-update and cohort/calendar diagnostics are distinct conditional comparisons, not an additive causal decomposition of the old 2011-versus-2012 difference. Preserve original v52/v53 positives while distinguishing fixed-policy transfer from parameter updating and source identity/calendar composition.