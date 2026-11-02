# v33 — Observed tide-phase-only prediction survives slope ablation

**Status (2026-11-02 JST):** POST-RESULT EXPLORATORY original-field ablation. The v33 code was specified after viewing the v32 positive outcomes, so this result **does not replace or increase the number of independent validations in v32**.

## Model decomposition, original field sources

Original Zenodo v5 Schiermonnikoog Eurasian oystercatcher GPS 2009, 2010, 2011, all provider MD5 checksum matched and independent original gzip SHA256 pinned in source runners; RWS `schiermonnikoog.waddenzee` original monthly measured `WATHTE` in cm/NAP, native fixed UTC+01. One original first fix per hour per individual; observed subsequent 0.5–2h horizontal displacement outcome `log1p(km/h)`. Train year 2010 and hold out complete original 2011 (primary); also train 2009→2010 (secondary). Models replay `validation_v32/cross_year_tidal_transfer.py` to within numerical floating precision.

- **M0:** measured height + square, latitude/longitude, diel and annual sin/cos, intercept.
- **Mphase:** M0 + discrete ebb/flood and phase×height (no water rate).
- **Mrate:** M0 + continuous trailing 20-minute water rate (no discrete phase).
- **Mboth:** M0 + phase + phase×height + rate; **exact v32 M1**.

Same ridge penalty λ=10, training-only column normalization and equal source-bird total weighting for every model. Same original GPS data, source clock 0 (assume UTC) and -15s (GPS-UTC) cases. No post hoc sample selection. `M0` and `Mboth` predictions were checked against the complete original v32 predictor.

## Year-external MSE results (0-second source-clock scenario)

| Holdout | Variant | Equal-bird MSE | M0−model gain | % M0 error reduction | Whole-week bootstrap 95% of signed gain |
|---|---|---:|---:|---:|---|
| 2009→2010 (21 birds, 53 test weeks) | M0 | 0.172425161 | — | — | — |
| | **Mphase** | **0.170265038** | **+0.002160123** | **+1.2528%** | **[+0.001376, +0.002342]** |
| | Mrate | 0.171032933 | +0.001392228 | +0.8074% | [+0.000770, +0.001565] |
| | Mboth | 0.169997722 | +0.002427439 | +1.4078% | [+0.001474, +0.002559] |
| 2010→2011 (13 birds, 53 test weeks) | M0 | 0.163169228 | — | — | — |
| | **Mphase** | **0.158776139** | **+0.004393089** | **+2.6924%** | **[+0.001180, +0.003449]** |
| | Mrate | 0.161279126 | +0.001890102 | +1.1584% | [+0.000724, +0.002022] |
| | Mboth | 0.158718057 | +0.004451170 | +2.7279% | [+0.001211, +0.003450] |

**Positive year-external phase-only prediction:** 2009→2010 has 20/21 positive birds, 46/53 positive weeks; 2010→2011 has **12/13 positive birds, 49/53 positive weeks**. Both remain positive with original 2009–11 source clock shifted -15 seconds.

**Conditional incremental contrasts** (primary 2010→2011, 0-second):
- Phase on top of continuous rate: `Mrate−Mboth = +0.002561068` equal-bird MSE reduction, 12/13 birds; week-bootstrap 95% **[+0.0002223,+0.0017318]**.
- Continuous rate on top of phase: `Mphase−Mboth = +0.000058081`, 5/13 birds; week-bootstrap 95% **[-0.0003283,+0.0002904]** (not robustly separated from zero).

The predictor components are correlated; percentages are not independent or additive causal contributions. These post-result tests show that **phase-only retains most of the full-model year-external predictive increment** under this fixed representation. Do not say discrete phase is the sole physical cause.

## What remains uncertain

1. Original GPS source metadata say native timestamps are UTC **or GPS time**. Analyses assuming UTC and -15s yield the same sign and similar magnitude, but fixed +1h/-1h errors, local hydrodynamic tide lag, and historic clocks are not completely adjudicated.
2. The RWS source station is a spatial proxy; precise local exposed-mudflat elevations, reef/channels and freshwater conditions are not joined. There is no demonstrated individual tracking of the moving wet-dry boundary, food exposure or seasonal patch choice.
3. Observational same-height ebb/flood matched comparisons are positive 7/7 (2009), 21/21 (2010), 11/11 (2011), but can also reflect commutes or differential routes instead of time-varying prey.
4. Cross-year transfer still comes from the **same species and study site**, with possible repeated individuals. M3 social-force and cross-species generality not supported.
5. This is **explicitly exploratory post-result ablation** and should be followed by an independent site/species, or untouched GPS acquisition period, before treating it as separate confirmatory evidence.

## Reproducibility

- [v33 passing real-source Actions 41410102440](https://github.com/zuizui0223/boids/actions/runs/41410102440)
- [v33 fixed before v33 outcome, after v32 outcome protocol](V33_POSTRESULT_TIDAL_PHASE_RATE_ABLATION.md)
- `validation_v33/phase_rate_ablation.py` and `test_phase_rate_ablation.py`, numerical replay checks PASS.
- [v32 original predeclared annual transfer result](V32_OBSERVED_TIDAL_PHASE_CROSSYEAR_RESULT.md)
- [Original Zenodo GPS v5](https://zenodo.org/records/22296922); [Dryad independently published 2014 AHN DEM and historical NAP water reference](https://doi.org/10.5061/dryad.wm37pvmth).

The output stores only aggregate source manifests and model scores; no raw GPS coordinates, bird identifiers or raw RWS station time series are committed.
