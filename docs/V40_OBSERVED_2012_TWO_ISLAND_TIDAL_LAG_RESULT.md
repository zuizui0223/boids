# v40: Original 2012 untouched calendar-year tidal-phase test — current phase transfers at Schiermonnikoog, selected -120-minute lag does not establish stable increment

**Original real-field test completed 2026-11-03 JST.** This is a genuinely previously **tide-outcome-unopened 2012 heldout calendar year**, NOT an independently chosen lag hypothesis: the `−120-minute` phase representation was selected from earlier v36 2011 lag-grid results. The original 2012 GPS source-only gate [CI 41564939899](https://github.com/zuizui0223/boids/actions/runs/41564939899) passed before the new outcome was computed, and both real tide evaluations passed [Actions 41565468337](https://github.com/zuizui0223/boids/actions/runs/41565468337).

## Verified original field data and frozen cohort

| Original source | Train years | Training source steps on equal lag support | Unseen 2012 test steps | 2012 birds | 2012 ISO weeks | Original RWS 2012 NAP values |
|---|---|---:|---:|---:|---:|---:|
| **Schiermonnikoog** | 2010+2011 | **117,197** | **9,052** | **5** | **36** | **52,705** |
| **Ameland** | 2010+2011 | **62,072** | **10,527** | **3** | **50** | **52,705** |

- Both original 2012 Zenodo GPS provider MD5 and independent SHA256 verified; Schier `f9935a50a9b557795ecf38ebd77890f52566b8e9d6c5a6650b46b18b6cb6d3d0`, Ameland `0b4d53cbe12437150425e7a36461485fe9d9e61b50486cf162aba3fbdb874c7a`.
- Original RWS `schiermonnikoog.waddenzee` and `ameland.nes` WATHTE **measured** cm/NAP, fixed UTC+01 timestamp; 2012 leap year original 52,705 ten-minute NAP source values in each station, no >30-minute gauge gaps, original 2010 and 2011 each 52,561 values. No raw GPS or gauge values are committed.
- Native original GPS clock is documented as UTC **or GPS time**, still not adjudicated; primary assumes UTC. Fixed -15sec sensitivity does not fully model the 2012-07-01 GPS−UTC leap-second change (15s→16s); do not report a fully calibrated telemetry clock.
- M0: measured h(t)+h², source GPS location, diel/year cycles. Mphase0: M0 plus source ebb/flood phase(t) and interaction with h(t). Mphase−120: M0 plus observed source station phase(t−120min) and interaction with **unchanged contemporaneous** h(t). Exact frozen ridge λ10 and equal train-source bird weights, fixed 2010+2011 fit and all-2012 test. Source rows common across three models, without tuning the lag after seeing 2012.

## Core 2012 MSE results (primary source clock treated UTC)

| Island | M0 equal-bird test MSE | Mphase0 MSE | Mphase−120 MSE | Test birds / weeks |
|---|---:|---:|---:|---|
| **Schiermonnikoog** | 0.240599058 | 0.237272655 | 0.236980130 | 5 birds, 36 weeks |
| **Ameland** | 0.184337617 | 0.184271729 | 0.183571046 | 3 birds, 50 weeks |

**Pre-frozen single primary comparison (Mphase0−Mphase−120, positive favors selected −120-minute gauge phase):**

| Island | Mean pooled equal-bird signed MSE improvement | Whole-bird 95% bootstrap of that estimand | Positive test birds | Separate equal-week-bird signed gain | Whole-week 95% bootstrap of that estimand | Positive weeks |
|---|---:|---|---:|---:|---|---:|
| Schiermonnikoog | **+0.000292525** | **[−0.00919914, +0.00886716]** | 3/5 | +0.001520485 | **[−0.00132045,+0.00411663]** | 21/36 |
| Ameland | **+0.000700683** | **[−0.00328327,+0.00406289]** | 2/3 | +0.000509321 | **[−0.00161209,+0.00230447]** | 33/50 |

**Interpretation: the selected -120-minute lag does NOT robustly beat the unshifted current tide phase in the previously unopened 2012 year at either study island.** Both signed point estimates were positive, but both target-estimand confidence intervals span zero; few test individuals make bird intervals wide. The 2011 exploratory lag-grid positive at −120 is retained in v36 without claiming its special advantage replicates.

## Important positive secondary result: genuine current-phase value at Schiermonnikoog

The explicitly prespecified secondary `M0−Mphase0` result in the **untouched 2012** year was:

- **Schiermonnikoog:** pooled equal-bird improvement **+0.003326403** MSE = **+1.3825% of M0**; **5/5** test birds improve; **31/36** test weeks improve. Whole-bird 95% **[+0.001258338,+0.005119814]**. Separate equal-week-bird mean +0.002591587, matching whole-week 95% **[+0.001341109,+0.003821819]**. Both independently defined source-resampled estimands are positive.
- **Ameland:** pooled equal-bird improvement +0.000065888 MSE = **+0.0357% of M0**; **2/3** birds, **31/50** weeks positive. Whole-bird 95% [−0.000457144,+0.000634191] includes zero. Separate equal-week-bird mean +0.000198024, whole-week 95% [+0.000017873,+0.000392042]. **The bird-pooled main point and bird CI are inconclusive despite a small positive week-weighted effect**; do not declare robust site-wide predictive gain.

- Phase−120 versus M0 in 2012: Schier pooled +0.003618928, **4/5** birds but bird CI [−0.007854411,+0.013556551] spans zero; Ameland pooled +0.000766571, **2/3** birds with bird CI [−0.003740419,+0.004697083]. Neither is uniformly convincing across test birds.
- Pre-fixed −15-second native GPS time shift preserved the 2012 Schier M0−Mphase0 positive sign (+0.003368645, 5/5 birds, and bird/week confidence intervals both positive), while chosen lag incremental is again inconclusive for both sites.

## Ecological interpretation (conservative)

1. **Supported within-source temporally transferable observation:** Schiermonnikoog original GPS displacement is better predicted with the true observed tide-phase direction in heldout **2011** (v32/v33 and v39 authentic previous-year phase placebo), and the same source-defined phase model improves an additional **previously unopened 2012** year after fitting 2010+2011. This strengthens evidence that tide timing matters beyond contemporaneous height at this original bird study site.
2. **Not supported as a universal 2-hour delay:** the post-v36 selected -120-minute station phase does not reliably improve 2012 predictions over current station phase on either island. A station-tide time shift is not a uniquely measured resource-front or animal response delay.
3. **Heterogeneity remains:** Ameland's 2011 unshifted true phase was near zero and did not beat a previous-year phase placebo (v34/v39), and 2012 unshifted phase is tiny at pooled bird scale. One site, year, cohort, behavioral mixture and different local exposure environments could all matter. No cause identified.
4. **No social Boids force, exposure-front or prey mechanism identified.** No local measured intertidal elevation at each bird GPS fix, patch exposure duration, local tide propagation time, prey abundance or actual-neighbor ghost forecasts. v35–v38 social-source gates remained NOT_ADMITTED. The 2014 Dryad AHN LiDAR site maps require calendar/extent checks before being joined to 2009–2012 GPS.

## Reproducible source receipts and constraints

- [Frozen v40 2012 pre-outcome/source-only protocol](V40_FROZEN_2012_TIDE_SOURCE_GATE.md) and [source-only pass 41564939899](https://github.com/zuizui0223/boids/actions/runs/41564939899).
- [Original real 2012 independent-year both-island workflow 41565468337](https://github.com/zuizui0223/boids/actions/runs/41565468337), two original GPS/RWS jobs success, full aggregate JSON artifacts retained, no raw animal coordinates/IDs.
- Code `validation_v40/heldout_2012_tidal_lag.py` reuses frozen v33 predictors, v39 quarterly source and matching bird/week bootstrap estimands.
- This branch is a **stacked follow-up to PR #52** and should remain Draft pending independent scientific review, local environmental exposure data and proper GPS clock uncertainty accounting.
