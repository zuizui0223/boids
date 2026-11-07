# v62 frozen: unseen-identity 2010 training and actual matched 2011 tidal headings

**Frozen 2026-11-07 after viewing both positive v60/v61 historical 2011 matched outcomes, and BEFORE any new v62 identity-disjoint model score.** Consequently this is explicitly **post-result exploratory robustness** on the same birds and not an independent confirmatory replication. Main/companion v60/v61 metrics and observational claims must remain unchanged.

## What v62 asks

In Schiermonnikoog v61, 2010-to-2011 prediction was time-heldout but training could include 2011 test bird identities. Is the previously reported positive matched rising/falling movement concordance still present when the 2010 fitted model sees **zero identities that occur in 2011**?

This is a stronger test of *transfer to unseen fitted individuals*, not a tide manipulation or a test of social Boids force.

## Immutable source and source-only gates

1. Same original Zenodo source, unchanged publisher MD5 + exact prior SHA256, original Schier `schiermonnikoog.waddenzee` RWS NAP 2009–2011 with 52,561 genuine values each gauge year. Reuse prior `load_site('schiermonnikoog')` and original v43 full heldout replay.
2. Exact unchanged original three-fix GPS: 2010 source 7,911 / 21 original birds, 2011 evaluation 4,948 / 13 original birds. No new original GPS rows from other datasets or new temporal eligibility rule.
3. Before any new model score, rebuild v59's source-only fixed **211 disjoint opposite-phase observed B-start pairs**, 10 birds with at least one pair, **7 birds with >=10 pairs**, 45 source weeks, 12 months, and all original seven sequential candidate counts: **[1784,1294,1276,969,572,277,248]**. Same 1km native grid, measured h≤15cm, different observations ≥24h, season≤30 days, provisional UTC time≤3h, preceding heading≤45°, preceding log-speed≤0.40. Use private pair-index reproducibility check from the unchanged v60 implementation, not observed B→C heading.
4. Remove **all** 2010 GPS records whose literal original bird ID occurs anywhere in 2011 before the model fit. Require 2010 remaining **1,508 original three-fix episodes from 8 original birds**, train/test literal ID overlap zero, and all 2011 GPS retained. These support counts follow previously published v55 source receipt; do not reduce >=1000 source gate or fallback to leave-one-out. The source identity strings have not been biologically independently adjudicated.
5. Re-run original full-2010-train v61 source model at the exact unchanged 2011 matched pairs and require equality of its already-observed equal-bird T **0.22867885497020074** to within 1e-9 before fitting the unseen-identity model. The known value is a source/model replay check, **not** a new result.

## Frozen v62 outcomes, labels, and uncertainty

For both the original 211 matched opposite-phase observed pairs and the **source-only** predeclared >=10-pairs-per-bird subset (7 qualified birds, number of paired rows to report only from source counts), fit **exactly the unchanged v41 lambda=10 ridge with original bird-equal weights** on the 1,508 remaining 2010 training episodes. All 2011 evaluation B states, true tide height/phase, old previous heading and clock variables are unchanged. No training on 2011, no training on original excluded 2010 identities, no new feature/lag/tuning.

Apply literally the v60 primary observed directional concordance, `T=dot(y_real_rising - y_real_falling,g_fixed_model_phase_switch)/4`, and same T zero-gradient policy, trained source model predictions under both phase signs at both real B states. Score the 2011 next direction **only after all source gates**. The primary is **all 211 v59 pairs**, same source-bird-equal mean, 10k whole-bird bootstrap 95%, positive bird count, one-sided exhaustive sign-flip sensitivity. **Never replace the primary with the >=10-pairs sensitivity if the primary is uncertain.** Report all original/qualified bird/episode denominators, separate week then bird estimate and 4k whole-week bootstrap, actual-vs-flip cosine gain, observed paired absolute angle and orthogonal projection as v60. No model refit to improve outcome; if qualified sensitivity separately invokes deterministic `forecast`, it is identical original training/scaling/λ and must reproduce full-sample phase predictions.

Decision: positive exploratory unseen-bird concordance only if original **all-pair equal-bird mean T > 0 AND its bird-bootstrap 95% lower > 0**. If CI spans zero or source changes, report null/NOT_ADMITTED without changing past v61 positive result. Train-fitted coefficient uncertainty is still not covered by the test bird bootstrap; 8 training birds may limit transfer precision.

## Limits and publishable materials

- Schier original source is a historical single-species Wadden Sea cohort and may have repeated behavioral and ecological states; the 2011 test individuals are unseen by the *2010 fit*, but not unseen to the researcher after v55/v61.
- The paired observations are real opposed tide phases, not randomized intervention. No unique tide-caused turning mechanism, current velocity field, prey-front tracking or social Reynolds force is estimated. No species-general niche outcome follows.
- Publish only aggregate original cohort counts, source checksum, group-size summaries, exact primary/qualified T and uncertainty, source-control and original code/run receipts. Never publish original raw bird identifiers, individual spatial coordinates/times, per-pair indices, model prediction vectors, per-bird outcomes or raw RWS measurements.

All new code in `validation_v62/`, a new dedicated GitHub Actions workflow and results document, stacked on PR #74 without changing any old v59–v61 code or results.
