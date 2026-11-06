# v55 — identity-disjoint and year-held-out angular tidal prediction

Frozen 2026-11-06 before v55 source support or predictive outcomes. Base: `09e6e28ef9c6c0b3e59cb1490cacfc22c6f58a7c` (v54). Earlier source outcomes are known: explicitly post-result exploratory, not an independent new field collection.

## Question and approach
Does the original 2010 tide-conditioned next-bearing model transfer to future-year birds whose source identities were completely absent from its fitting data? A year split alone can retain the same birds in both years. We choose one pooled identity-disjoint training set rather than per-bird refitting: it gives one shared fitted rule and removes ALL evaluation birds simultaneously. A source failure will not be rescued by switching to leave-one-bird-out or lowering thresholds.

Primary: Ameland 2011 actual-phase versus authentic 365-day historical-phase angular cosine loss. Report identical Schiermonnikoog 2011 comparison as a same-design companion. Secondary: Ameland 2012 with exactly the same identity-disjoint 2010 training. Existing Schier 2012 source gate (869 < 1000 episodes) remains untouched and is not newly evaluated.

## Original-source controls
Original annual Zenodo O_AMELAND and O_SCHIERMONNIKOOG GPS gzip provider MD5 and pinned SHA256, unchanged v41 first-visible-fix/hour source triples, both intervals 30–120 min and speeds 0.4–120 km/h, original study bounds, native GPS provisionally UTC. No new GPS filters, resampling or AHN2 mask restriction.

Authentic local RWS WATHTE meting cm/NAP, fixed UTC+01, original 2009–2011 gauges for both islands and 2012 for Ameland. Counts 52,561 per 2009/2010/2011 station-year and 52,705 for 2012. Original gauge-year union and exact 365-day history lookup from v53, no calendar-year replacement across leap dates. Historical slack retained, actual slack exclusion unchanged. Stop if history join changes original full source cohorts.

## Strict split, chosen before counts
For Ameland, collect the UNION of original source `individual-local-identifier` strings in admitted 2011 and 2012 test episodes. For Schier, use all 2011 test identities. REMOVE every 2010 training row with ANY of those source identities. No test outcomes or coordinates influence selection, only membership in the predefined identity holdout. Keep every future test row unchanged. Assert empty intersection between training identities and all evaluation identities, and training year exactly 2010.

This verifies provider identity separation, not independent adjudication of tagging identity/re-tagging. All evaluation identities have already been inspected in prior research; unseen means unseen to this fitted model, not a previously unopened dataset. Neighboring sites, same species and correlated environments remain.

Training admission: >=1000 rows and >=3 source identities AFTER exclusion. Per test year: >=1000 original rows, >=3 birds, >=4 ISO weeks. Failure => NOT_ADMITTED, source counts only, no new fitted effect for that site/year. Never drop unfavorable birds to pass.

## Immutable models and metrics
Import v41 `forecast` unmodified: training-only feature scaling, equal total training weight per bird, ridge 10, unpenalized intercept. M0: h, h squared, current position, diel/year clocks, own past heading and speed. Mactual adds measured current phase and phase-by-height. M365 substitutes same-station observed phase exactly 365 days earlier, leaving true current height and all other inputs unchanged. Neither target next position nor target heading is a fitting input.

Fit all 3 models on the SAME eligible 2010 identity-disjoint cohort, then predict concatenated future years in one call per model before splitting outputs. No 2011 retraining for the 2012 secondary test.

Use existing v53 `summarize_models`: primary normalized cosine loss, secondary mean absolute angular error in degrees and vector half-MSE. Primary signed contrast M365 minus Mactual; report M0 minus Mactual and M0 minus M365 too. Paired whole-bird 10,000-draw intervals, seed 20261106; separate equal-week-then-bird 4,000-draw intervals, seed+1. Each interval accompanies its own point estimand. No zero prediction vector may invent a bearing or silently remove a row.

Before new results, replay all-train 2010 -> 2011 original v52 vector means/counts for both sites, plus all-train Ameland 2010 -> 2012 v54 angular model means (M0 69.62997611500825, Mactual 59.66726851878847, M365 67.34326266351121) to 1e-9. Preserve these old results, do not relabel them identity-disjoint. Report removed training rows/identities and remaining training support; no raw IDs, positions, exact times or water series persisted.

## Interpretation
Positive actual-versus-baseline alone does not establish actual-versus-historical phase specificity. A positive strict holdout result supports within-region transfer across fitted-source identities AND year, not a new population, species generality, social force or physical prey-front response. A weak result can reflect less training information or covariate shift after withholding identities, not proof that earlier results were invalid or that tide response is purely individual-specific. Bootstrap conditions on the fitted training data and few evaluated birds; does not include training-fit uncertainty.

Method context: Roberts et al., Ecography 2017, DOI 10.1111/ecog.02881 (structured temporal/hierarchical validation and extrapolation caveats).

## Implementation plan
New files: `validation_v55/unseen_identity_transfer.py` (pure split/fit/score), `validation_v55/run_unseen_identity_transfer.py` (original-source runner), corresponding tests, one source workflow, aggregate receipts/result document. No older file edited.
1. Tests first: union identity exclusion, no test target influence on split, chronologically wrong rows/duplicates/missing IDs rejected, gate before fitting, single concatenated test forecasting, unchanged ghost inputs, exact bird/row scoring, undefined bearing hard stop.
2. Run failing tests, implement pure functions, pass them with synthetic inputs. Independently verify angular arithmetic with atan2 and grouped means.
3. Runner imports unchanged original source helpers, authenticates hashes/gauge counts, replays old metrics, applies frozen identity split and scores only admitted support.
4. Run source jobs once per island, scoped inherited tests, inspect exact logs. Keep source STOP distinct from a biological null. Publish all contrasts, including uncertain/negative results, as Draft only.
