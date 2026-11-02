# v32: Original GPS × measured tide cross-year speed prediction — observed result

**Date:** 2026-11-02 JST  
**Source and independent execution:** [GitHub Actions 41409138767](https://github.com/zuizui0223/boids/actions/runs/41409138767) — successful pure tests, original-source byte pins and observed M0/M1 evaluations. Source-specific protocol was frozen separately in [V32_PREOUTCOME_THREE_YEAR_TIDE_TRANSFER.md](V32_PREOUTCOME_THREE_YEAR_TIDE_TRANSFER.md) before the outcome was opened.

## Scientific question
Can tidal phase (flood vs ebb plus local change rate and phase×height) improve prediction of a shorebird's horizontal speed beyond **absolute water height, location, time of day and season** in a calendar year excluded from training? This is a predictive ecological association, not a demonstration of a physical moving resource front or inter-bird steering.

Original [Zenodo O_SCHIERMONNIKOOG GPS v5](https://zenodo.org/records/22296922): real 2009, 2010, 2011 annual sources independently fetched and published provider MD5-pinned in run. RWS original [DDAPI2](https://github.com/Rijkswaterstaat/wm-ws-dl): station `schiermonnikoog.waddenzee`, genuine 10-min WATHTE `meting`, datum NAP, cm, fixed UTC+01 in all months. 52,561 unique gauge samples per year (including endpoint conventions). Original GPS source native timestamps described as UTC **or GPS time**; primary scenario uses minus 15 seconds as GPS-to-UTC, with unshifted UTC sensitivity.

Same-site GPS step definitions inherited from v31: first GPS fix per individual per hour (not interpolated), 0.5–2h horizontal movement and log1p(km/hour). Each model is trained with equal bird total weights, train-only standardization and fixed ridge regularization. Independent calendar-year test averaged **equally per heldout bird**; uncertainty assessed via separate bird cluster and test-week bootstrap, 4,000 replicates each.

## Real cross-year observed result (GPS clock -15 seconds)
| Frozen training/test split | Train steps | Test steps | Test individuals | M0 equal-bird test MSE | M1 equal-bird test MSE | M0−M1 gain | % MSE reduction | Birds gain | Weeks gain | 95% bird bootstrap on gain | 95% week bootstrap on gain |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| **2010 → 2011 (primary)** | 70,575 | 46,654 | 13 | 0.163153 | 0.158676 | **+0.004477** | **+2.744%** | 12/13 | 47/53 | [0.002569, 0.006713] | [0.001221, 0.003484] |
| 2009 → 2010 | 13,555 | 70,575 | 21 | 0.172244 | 0.169774 | **+0.002470** | **+1.434%** | 19/21 | 45/53 | [0.001917, 0.002980] | [0.001492, 0.002599] |
| 2009+2010 → 2011 | 84,130 | 46,654 | 13 | 0.164640 | 0.160350 | **+0.004290** | **+2.606%** | 12/13 | 48/53 | [0.002503, 0.006385] | [0.001172, 0.003378] |

All 3 comparisons improve under the **unchanged and uncorrected UTC** original timestamp interpretation as well: primary 2010→2011 +2.728%; 2009→2010 +1.408%; pooled 2009+2010→2011 +2.591%. Both bird-level and week-level bootstrapped 95% intervals for gains are above zero for the two tested clock assumptions. The calendar years differ but the ecosystem/population does not constitute an independent geographical or species replication.

## Observed matched-water-level hysteresis (descriptive only)
Same individual × month × 0.15m water-height band × 6h clock bin, ≥3 ebb and ≥3 flood observations per matched stratum; capped stratum weights and equal-bird averaging.

| Original year | Matched strata | Raw observations in matched strata | Birds with both phases | Birds with faster ebb than flood | Mean ebb−flood log1p(km/h) |
|---|---:|---:|---:|---:|---:|
| 2009 | 786 | 8,446 | 7 | 7/7 | +0.07129 |
| 2010 | 4,486 | 47,774 | 21 | 21/21 | +0.10193 |
| 2011 | 2,992 | 32,105 | 11 | 11/11 | +0.11703 |

This is **39 bird-year contributions** summed across years, NOT 39 proven unique individuals or independent trials. The directional sign is a strong association, but it does not isolate changing exposure age, prey, weather, or other state-specific processes. No single universal movement rule inferred.

## What is now empirically supported and what is not
1. **Supported in same-site temporal prediction:** Absolute tide height is insufficient for these models. Flood/ebb phase information and trailing water-height rate provide a reproducible positive *incremental predictive association* on independent calendar years, with two different cluster units supporting the sign.
2. **Supported descriptively:** At matched tide height, bird, month and clock bin, ebb has higher observed average movement speed in all eligible bird-years in this three-year sample.
3. **NOT established:** Real dynamic intertidal area/exposure timing without an independently georeferenced NAP DEM and local hydrodynamic phase lag; prey abundance, organism energetic costs or selection; causal tide response vs correlated time/behavior; social steering/Boids coefficients or interspecific niche partition without synchronous neighbor-vs-ghost heldout controls.
4. **Source caution:** Native GPS clock UTC/GPS distinction remains unresolved despite 15s robustness. Tide is from a nearby named Waddenzee gauge, not proven exact water level or water arrival at every tracked fix; GPS data vary greatly in sample cadence and season by year.

## Direct next tests
- M2: geographic bathymetry/LiDAR in NAP and point-level inundation/exposure age (account for historical sediment and phase lag) and evaluate *independent-year M1→M2* gain, not just in-sample correlations.
- M3: 2010/2011 original near-neighbor pairs source-quality audit, actual contemporaneous partner versus matched ghost, while conditioning on the **M2** environmental null; control temporal sampling and GPS error and hold out bird-connected groups.
- Out-of-site and multiple shorebird species transfer is required before using a general cross-species niche claim.

All original animal GPS coordinates and identifiers were used only in ephemeral CI runners and have not been redistributed.
