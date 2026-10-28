# v16 observed result II — Present neighbor state predicts short-horizon pigeon turns across seven of eight independent flocks

**2026-10-28 JST. Exploratory independently held-out original-GPS prediction; no social-force coefficient or ecological niche mechanism inferred.** This is a distinct source from the negative v15 2026 GPS benchmark, and the published 2016 paper's treatment contrasts are not represented here as new findings.

## Source, frozen design and exact reproduction

- Watts et al. (2016), *Misinformed leaders lose influence over pigeon flocks*, *Biology Letters*, DOI [10.1098/rsbl.2016.0544](https://doi.org/10.1098/rsbl.2016.0544). Original 8-flock GPS archive [Zenodo 4943714](https://zenodo.org/records/4943714), dataset DOI `10.5061/dryad.508j2`, **CC0**. Exact source: **272,270,105 bytes**, published MD5 `ab0950ffebd924950632f727cd487c27`, verified SHA256 `7380feccd8c2e4e1675679411d1ee8075cd29ccbd2dada98e317ca88053ffbfa`.
- The [outcome-blind joint protocol](DUAL_TIMESCALE_ROUTE_PREDICTION_CONTRACT_V16.md) was committed before any fast-turn or slow-route effects were calculated. [Full observed GitHub Actions run 40615273961](https://github.com/zuizui0223/boids/actions/runs/40615273961) passed all **8 fast-model synthetic/no-time-leakage tests** and every actual-source execution/receipt gate. [Executable script](../validation_v16/fast_turn_forecast.py) and [machine-readable per-flock extract](../validation_v16/results/fast_turn_aggregate_v16.json) are saved. Original workflow aggregate-artifact ZIP digest `sha256:9ff445e4b585eab633c1e5387027e5b6cacf4a45eaf5845c5b1a89ed1553f4de`; digest refers to the workflow artifact ZIP, **not** the original source or inner JSON.
- Only the **559 true raw GPS CSVs** were used; 178 AppleDouble `._` resource-fork metadata sidecars were excluded. Original GPS records supply UTC date, UTC time, milliseconds, measured lat/lon and heading; no positions or timestamps were interpolated. Flight was restricted to the observed first outbound 500–4,500m radial corridor with spatial steps ≤50m, gaps ≤1s, runs ≥12s and ≥60 fixes. Only source GPS partners measured **at or before** focal time and within ≤200ms and 100m were eligible.
- **Training** for each heldout flock used historic releases **5–8 from the other seven flocks only**. **Test** used releases **9–15 of the heldout flock**, without individual overlap between training and test flocks. All eight folds used the same rows for each tested model and training-only scaling. The estimated physical GPS measurement error has **not** been independently calibrated.

## Held-out GPS turning forecast — numerical results

Target: wrapped **1-second-ahead original GPS course-over-ground change**. F0 = own prior motion + progress/cross-track route state; F1 = F0 + present nearest-neighbor relative position/heading; F2 = F0 + the same neighbor's 10-second-stale relative geometry, where BOTH focal and partner are evaluated at that historical time. All models use the fixed training-only standardized linear ridge alpha 30. MSE in rad² (**lower is better**).

| Held-out flock | Future matched anchors | F0 own | F1 present | F2 stale 10s | Δfast = F2 − F1 |
|---|---:|---:|---:|---:|---:|
| 01 | 1,219 | 0.035854 | **0.033642** | 0.035814 | +0.002172 |
| 02 | 1,043 | 0.033578 | **0.031984** | 0.033593 | +0.001610 |
| 03 | 1,341 | 0.039807 | **0.037430** | 0.039750 | +0.002320 |
| 04 | 1,514 | 0.037565 | **0.035453** | 0.037583 | +0.002130 |
| 05 | 1,018 | 0.026803 | **0.024621** | 0.026826 | +0.002205 |
| 06 | 1,249 | 0.037348 | **0.035538** | 0.037370 | +0.001832 |
| 07 | 950 | 0.022688 | **0.021809** | 0.022669 | +0.000860 |
| 08 | 945 | **0.026430** | 0.027476 | 0.026421 | −0.001055 |
| **Equal-flock mean** | **9,279 total** | 0.032509 | **0.030994** | 0.032503 | **+0.001509** |

- **Prespecified primary**, `MSE(F2)−MSE(F1)`: **+0.0015091850000559575 rad²**, positive **7/8** independent flocks, flock-resampling bootstrap 95% **[+0.0006797277,+0.0021096195]**.
- **Prespecified own-only secondary**, `MSE(F0)−MSE(F1)`: **+0.0015150729425521805 rad²**, also **7/8** positive; 95% **[+0.0006798005,+0.0021197334]**.
- F1 reduces equal-flock mean MSE by **4.64% relative to the stale-10s control**, and **4.66% relative to own-only**. These are ratios of the eight-fold equal-flock mean MSE, not flock-internal percentages. An exact independent-flock one-sided sign-test for 7/8 gives `9/256=0.03515625` *if independent exchangeable flock signs are accepted*; the study shares one population/experimental protocol and has two registered contrasts. Treat this as an **exploratory group-level probability**, not proof of a general species-level mechanism.

## Cross-timescale interpretation with the independently run v16 slow endpoint

The [v16 slow-route predeclared benchmark](OBSERVED_EIGHT_FLOCK_ROUTE_RESULT_V16.md) using the same source instead showed:
- **Group prior-route history**, population/global other-flock template vs same-flock history: **+0.003543 rad²**, **4/8** positive, whole-flock bootstrap **[−0.01817,+0.02696]**, generalizable improvement not supported.
- **Individual prior-route history**, group vs personal template: **+0.002932 rad²**, **5/8** positive, **[−0.00284,+0.01219]**, also not supported.

Thus the two registered predictive levels yield a **positive fast current-neighbor contrast** and **non-robust transfer of static earlier-route templates**. This is a genuinely interesting **difference in predictive organization across targets and time horizons**, but the target variables (1-second heading change versus future-release geographic bearing) and training comparisons differ. **Non-significant slow effects do not establish slow-model equivalence to a null**, and subtracting the two MSE gains cannot identify a universal fast/slow hierarchy parameter.

## Key scientific limits

1. Real flight data with short-step current-neighbor predictive information **do not prove birds follow neighbors**, because shared route, environmental cues, receiver error, and common unobserved variables can supply correlated features. No Reynolds separation/alignment/cohesion coefficient was recovered, nor can attraction be uniquely separated from avoidance from these data.
2. The different v15 2026 observed dataset found an opposite result (no current-partner improvement in any of three trials), but model feature sets, sensor semantics, birds and group design differ. Their contrast is **consistent with heterogeneity**, not a controlled causal test of context-dependent effect.
3. This dataset's recorded `ALTITUDE` field exists, but instrument-specific vertical error was not calibrated; neither present work nor v15 validates wild **3D** niche partition. No actual food patches or reward observations were modeled.
4. The 2016 original experiment manipulated solar-compass information, but our observed predictive model did **not** register a complete independent release-wise treatment ledger. No new causal conclusion about clock shifting or the direction of navigational decision transfer is made.
5. The v13 endogenous niche-hierarchy findings remain **synthetic mechanism demonstrations**, not biological validation. A future independent dataset with measured social contacts, resources and repeated long-term trajectories is necessary for cross-taxon niche generalization.

**Scientific advance:** An independently checksum-verified eight-flock GPS source supports **real held-out incremental short-step prediction from contemporaneous partner state**, even though the same source does not support stable transport of static personal/flock route templates to later releases. This qualifies as observed **predictive information**, not discovered Boids behavioral forces or ecological competition.
