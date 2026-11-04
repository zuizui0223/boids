# v41 OBSERVED: tide phase changes out-of-year *heading prediction* after own prior motion, but site-level admission differs

**Date: 2026-11-05 JST.** Original source-backed research result, fixed source/model contract at [V41_FROZEN_2012_TIDAL_DIRECTION_FORECAST.md](V41_FROZEN_2012_TIDAL_DIRECTION_FORECAST.md) before opening v41 next-heading scores. Original 2012 GPS birds were previously used for the *speed* outcome in v40; this is a new conditional **directional** endpoint, not an independent animal population or a new controlled experiment.

## Original GPS + measured water level sources

Two original Zenodo oystercatcher tracking data sources were re-downloaded; original gzip provider MD5 checks **passed** in both study islands for 2010, 2011, 2012. RWS measured 10-minute WATHTE stations `schiermonnikoog.waddenzee` and `ameland.nes` use physical cm **NAP** water heights with historic fixed `+01:00` timestamps. Three-genuine-fix sequences within individual, using first source fix each hour and BOTH prior and following 0.5–2h displacements with horizontal speed 0.4–120km/h, define (at middle point B) a real previous heading and real next heading as target. A great-circle horizontal displacement is **not** confirmed feeding, flight speed, prey access or physical Boids steering.

The fixed M0 predicts next east+north horizontal unit heading using location B, measured water height h(B), h(B)^2, diel/year cyclic clock, own immediately preceding unit displacement direction and log1p(previous km/h). M1 adds observed rising/falling phase(B) and phase×h(B) using trailing 20-minute gauge slope. Both fit equal-source-bird weighted ridge λ10 on all admitted 2010+2011 original episodes, then evaluate all admitted 2012 episodes without test outcomes informing parameters. Retrospective measured gauge is not an operational, future available water prediction.

## Frozen 2012 source gate results, by original island

| Study island | Original GPS 2012 raw fixes | 2010+2011 admitted train triple-fix heading episodes | Real 2012 qualifying three-fix test episodes | 2012 test birds | 2012 test ISO weeks | Prior source gate (>=1000/3 birds/4 weeks) |
|---|---:|---:|---:|---:|---:|---|
| **Ameland** | 12,080 | **8,431** | **1,186** | **3** | **50** | **ADMITTED** |
| **Schiermonnikoog** | 27,873 | **12,859** | **869** | **5** | **35** | **NOT_ADMITTED** |

Schier 2012 869/1000 fails the **precommitted** outcome eligibility threshold, because stationary or noisy-heading displacements were excluded by the source-independent 0.4km/h minimum. It is **not** a biological non-replication of tide-conditioned turning, not a negative effect and not an invitation to relax the source threshold after seeing the counts. Schier directional model scores are not computed or reported for 2012.

## Ameland: ORIGINAL OUT-OF-YEAR 2D next-heading field forecast

Primary original clock interpreted as UTC (native UTC vs GPS time distinction remains unresolved):

| Endpoint: half squared 2D unit-heading-vector error | Ameland 2012, original 3 birds, 1,186 episodes, 50 source weeks |
|---|---:|
| **M0** prior bird heading and previous speed, local location/clock/height | **0.4389851852** |
| **M1** M0 plus current true ebb/flood gauge phase | **0.4101246782** |
| **Pooled equal-bird** M0−M1 signed improvement | **+0.0288605070 (6.574% of M0)** |
| Positive original test birds | **2/3** |
| **Whole-bird 95% bootstrap for pooled equal-bird gain** | **[−0.0227871981,+0.0610097003]** |
| **Separate equal-week-then-bird** gain | **+0.0459055481** |
| Positive original source test weeks | **38/50** |
| **Whole-week 95% bootstrap for that separate equal-week estimand** | **[+0.0246917751,+0.0659576819]** |

The source clock provisional −15-second sensitivity has the same direction: M0 half-MSE 0.438732 vs M1 0.409573, relative reduction 6.646%, 2/3 birds positive, 38/50 weeks positive, pooled-bird bootstrap [−0.021765,+0.061299] and separate week bootstrap [+0.025174,+0.066252].

**The two uncertainty summaries measure different estimands.** Whole-week resampling is favorable within this original source cohort, but **3** tracked birds and a whole-bird interval spanning zero prevent any claim of a robust population-wide tidal steering effect. No identified cause of the additional directional information follows from a positive predictive difference.

## Reconcile with earlier v39–v40 SPEED endpoints, do not compare MSE scales

- At Ameland, original 2012 SOURCE SPEED test (2010+2011 fit, earlier v40) found only +0.0357% pooled equal-bird speed MSE reduction for phase, 2/3 birds positive and bird bootstrap interval spanning zero (10,527 source speed steps). That is a different **scalar speed endpoint and eligibility sample** from v41's faster-than-0.4km/h **1,186 three-fix turning episodes**, so the two MSE percentages are NOT directly comparable quantitative effect sizes.
- v41 suggests **tide-state information might enter movement *direction* even when a broader all-movement speed endpoint lacks a robust across-bird gain**. It does NOT establish that tide controls turning more than speed in the same original GPS opportunities. Such a joint matched-episode speed-vs-direction test is a distinct post-v41 exploratory hypothesis that must be defined before looking at its joint outcomes.
- At Schier, prior v39 and v40 positive true-phase source-speed predictive results remain exactly as established. v41's directional source STOP does not contradict them.

## Biological interpretation and next decisive mechanism test

The original conditional directional phase response is **compatible with tide-dependent reorganization of movement pathways or spatial niche use**. Distinguishing a shifting wet–dry resource boundary from routine commutes, spatially correlated habitat preferences or GPS sampling requires independent local elevation/shoreline exposure or confirmed behavioral state. There is no actual-neighbor/ghost social effect or Boids force identified; the v35–v38 original field social-source gates stay NOT_ADMITTED.

An external original GPS time/gauge synchronization check (GPS native time might be UTC or GPS time, with 2012 GPS−UTC leap offset changing from 15 to 16 seconds after 2012-07-01) and additional independent bird identities/sites are required before species-general claims.

## Reproduce

- [Original observed 2-island CI 41922892457](https://github.com/zuizui0223/boids/actions/runs/41922892457): both source jobs success and all pure known-truth regression tests pass. Aggregate artifact receipts contain source MD5/SHA256, admission, and exact 2D MSE scores; **no original individual ID or GPS coordinate** committed.
- `validation_v41/original_heading_tide.py` and `test_original_heading_tide.py`.
- [Frozen before v41 directional field outcome](V41_FROZEN_2012_TIDAL_DIRECTION_FORECAST.md). This is a prospective endpoint within a prior-inspected bird cohort, not fully new independent field data.
