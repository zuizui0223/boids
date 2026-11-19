# v39 frozen original Finnish bat diel-allocation transfer — time-limited generality

**2026-11-19 JST. Frozen pre-outcome model:** [v39 protocol](V39_FINLAND_THERMAL_NIGHT_ALLOCATION_TRANSFER_FREEZE.md).  
**Original execution:** [Actions 44463857136](https://github.com/zuizui0223/boids/actions/runs/44463857136), five synthetic tests PASS and publisher-MD5-verified original Zenodo \`18298435/Data.xlsx\` numeric group-heldout fit PASS. Original raw event/coordinates not re-published; machine-readable complete aggregate year/region scores retained in the named Actions artifact.

## Provenance boundaries

The original v38b **four-bin** source admission failed (actual \`quartiles\` categories were 1,2,3,4,BSS,ASR). Its failure remains immutable. After **source-only** observation (no numerical activity/weather opened), separately frozen v38c six-label source gate passed 4,536 distinct original active detector-nights with full six categories. Published manuscript confirms \`BSS\`=before sunset, \`ASR\`=after sunrise, while 1–4 are four equal-length nocturnal quartiles. The new v39 source-outcome protocol froze the night-only Q1–Q4 share and independent year/region holdouts **before numerical values were opened**. Do not retroactively call v38b PASS.

The original source comprises **one species, Eptesicus nilssonii**, in three Finnish regional labels, across seven years. All results condition on the original study's **active nights with at least 10 activity minutes across the full BSS–ASR window**; they are not detection/occupancy probabilities.

## Actual valid data and response

Source structural complete nights 4,536. Numeric source exclusions:
- 328 nights with missing/nonfinite weather or invalid night length;
- remaining **4,208** valid night Q1–Q4 compositions, entirely based on source \`n\` activity minutes, renormalized to exclude BSS/ASR.

M0 = train-year period-specific four-bin mean composition. M1 = period + mean temperature + night length + their centered standardized interaction with fixed ridge alpha 10; M2 adds wind and rain. No year or region target observations enter their fitted folds. Loss is night-level 4-bin cross entropy, averaged first within the withheld group, then equally across groups.

## Primary: whole-year heldout (7 years)

| Year | Source nights | M0−M1 cross-entropy gain (nats/night) |
|---|---:|---:|
| 2015 | 676 | +0.037381 |
| 2016 | 727 | **−0.003310** |
| 2017 | 404 | +0.035775 |
| 2018 | 496 | +0.026735 |
| 2019 | 597 | +0.002078 |
| 2020 | 653 | +0.016627 |
| 2021 | 655 | +0.010316 |

- Equal-year mean loss M0 **1.288640** vs M1 **1.270697** nats/night.
- Mean gain **+0.0179433** nats/night.
- Whole-year bootstrap 95% percentile interval **[+0.007166,+0.028800]**.
- **6/7** year-group improvements; one-sided exact sign p **0.062500**.
- **Predeclared primary positive gate: NOT SUPPORTED** because p > 0.05, despite positive mean/CI. Do not revise decision threshold after outcomes.

## Secondary: wholly new region (3 groups)

| Frozen anonymized group | Original detector nights | M0−M1 gain |
|---|---:|---:|
| region_group_1 | 1,556 | +0.032840 |
| region_group_2 | 334 | **−0.117115** |
| region_group_3 | 2,318 | **−0.032231** |

- Equal-region M0 loss **1.349097**, M1 **1.387932**, mean gain **−0.0388353**.
- Bootstrap region 95% **[−0.117115,+0.032840]**, only **1/3** regions positive, one-sided sign p **0.875**.
- This source does **not** show cross-region portability under frozen model, even though 6 of 7 years improved.
- With three regions, the smallest possible exact one-sided sign-test p for all concordant regions is 0.125, so region-universality cannot be confirmed at p<0.05 using that test.

## Fixed weather-increment secondary

Adding source wind and precipitation (M2 versus M1) slightly worsened held-out year loss (mean M1−M2 **−0.001471** nats/night) and held-out region loss (**−0.001426**). This is a secondary predictive contrast; not a demonstration that wind or rain have no biological influence.

## Mechanistic interpretation and limits

Original paper **already** identified night length×temperature associations. New evidence tests **retrospective contextual prediction on completely withheld detector-years/regions**, and indicates the important difference between year transfer and spatial transfer. The positive seven-year mean cannot be called a confirmed general rule under the registered exact-sign criterion; the spatial extension is weaker still.

The region failure might reflect limited climatic covariate support, unobserved local insect prey/landscape structure, recording conditions or real regional response differences. The present test **cannot identify which cause** and must not label the disparity as proof of an evolved regional flight policy.

Next permissible action is a **post-outcome, descriptive-only** environmental-support audit comparing withheld-region weather/night-length domains with each training region, no new movement predictions or hypothesis rescue. Definitive broader generality needs independent datasets with matched calibrated weather, observation effort and bat activity response; the other two 2026 sources (Italy and Belgium) do not yet meet those common-denominator requirements.
