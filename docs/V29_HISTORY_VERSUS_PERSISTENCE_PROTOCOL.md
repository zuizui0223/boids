# v29: Does multi-day duck history beat yesterday's observed movement?

**Same-source exploratory extension, specified 2026-10-30 JST before computing the new persistence comparison.** The positive v23 results are already known. This is neither an independent replication nor a preregistration made before access to this dataset.

## Question and reason

v23 found that the same bird's recent history improves next-day horizontal GPS spread prediction over other birds' weather-stratified history. It did not compare that history with simply carrying forward yesterday's measured spread. That missing comparator matters: useful personal history need not imply stable individuality, learned memory, or a multi-day mechanism.

We add exactly one predictor to the unchanged v23 task. The alternatives considered were a new source search, a fitted state/history regression, and this direct persistence comparator. The direct comparator addresses the missing baseline without new fit parameters, cohort selection, weather bins or smoothing weights. This is an implementation choice for the authorized research continuation.

## Unchanged original task

- Base repository: `47cf12b51553c865027961ae5c162f1b479f5c8c`.
- Import the existing `validation_v23/duck_daily_era5_forecast.py`, source and weather gates. Do not edit them.
- Download the same original GPS CSV, verify its published MD5 and SHA256 `001ec8ffe1e9be5258129dfb931b0abd6551785080e2c755cbd4c72cd79ec52e`, and reverify both original canonical ERA5 digests through v23.
- Apply exactly the v23 raw duplicate, HDOP, coverage, prior-location, weather, history and chronological eligibility rules.
- Recreate `prequential_predictions` on the original candidate days. Retain exactly its target records and original four model squared errors. The expected frozen receipt has 49 birds and 2,664 future bird-days.
- Before reporting a new comparison, check the original cohort counts, each anonymized bird's count and all four per-bird mean errors against the saved v23 receipt, absolute tolerance `1e-12`. A mismatch stops the new result rather than authorizing a replacement cohort.

## Five predictors and fixed comparisons

The target remains `y(i,t)=log(1+R(i,t))`, where R is the within-day horizontal GPS radius of gyration in km.

| Predictor | Exact definition |
|---|---|
| M0 | Original v23 other-bird, same-wetland historical mean |
| ME | Original v23 other-bird historical mean conditional on the fixed prior-day weather class, with its original fallback |
| MI | Original v23 mean of the last 3–14 eligible same-bird, same-site event days |
| MEI | Original v23 fixed combination of ME and MI, `w=n/(n+2)` |
| MP | The same bird's actual complete UTC day t−1 GPS target `y(i,t−1)` |

MP uses `parse_original_gps` daily values for the **exact preceding calendar date**. It must not substitute the latest eligible historical event: an eligible target guarantees a complete raw t−1 day, but that day need not itself have been eligible as an event at the same site. No same-day or future outcome enters MP.

Primary: `MSE(MP) − MSE(MEI)`, positive when the existing combined history predictor beats simple persistence. Secondary: `MSE(MP) − MSE(MI)`. Descriptive comparators `MP−ME` and `MP−M0` are also reported, together with the five absolute errors. There is no threshold, fitted parameter, model selection or subsequent alternative after opening these results.

Average daily errors within each original bird first, then give every bird equal weight. Use paired whole-bird bootstrap with 10,000 draws and RNG seed `20261030`. Report exact one-sided sign probability for positive/nonzero bird gains as a complementary summary. Confidence intervals are conditional on this shared study; they do not represent independent wetland, weather, taxon or year replication.

## History chronology audit

Export aggregate counts/quantiles only for:

- number of eligible prior observations in MI;
- calendar age of the oldest and newest of those observations;
- number of targets where exact day t−1 is included in MI;
- whether a previous-day eligible event exists at a different site, or whether no previous-day event exists.

The audit must use the same date-batched ordering as v23 and keep current-day outcomes out of history. It changes no model or target. No individual GPS coordinates, timestamps, daily target values or real animal IDs are exported. Anonymous bird-level mean errors and source taxa remain permissible as in v23.

## Interpretation fixed before new scores

- Positive primary: a specific multi-day history predictor improves on a last-day persistence rule on this source. Averaging, noisy measurements, slowly varying environment and persistent behavior are still alternative explanations.
- Primary near zero or negative: the original improvement over the external-bird comparator remains true, but does not establish an advantage over yesterday's state.
- MP winning does not prove absent cognition; MEI winning does not identify learning, a stable behavioral trait, resource partition or a causal social force.
- This is a forecast of later days for already-observed birds. It is not unseen-animal, future-climate or 3D niche prediction.

## Deliverables and verification

Add a standalone `validation_v29/persistence_benchmark.py`, focused tests, source replay workflow, an aggregate-only JSON result, and a result note. Test exact-date lag selection, missing-prior failure, current/future-date exclusion, unchanged source-record errors, equal-bird weighting, and receipt-mismatch failure on known-truth fixtures before opening new real-data scores. Reproduce all original v23 per-bird results during the real-source run, and preserve earlier files unchanged.
