# v24 frozen protocol — decay of collective-motion predictive information across five predefined delays

**2026-11-24 JST. Freeze this specification in the repository BEFORE running any v24 original behavioral outcomes.** v5–v9c and v22 predictions have already been inspected, so v24 is a prospectively specified *secondary analysis of known data*, **not independent biological replication**. No new fish/audio field records are introduced.

## Question and hypotheses

Does information carried by other fish's movement **at time t** dissipate continuously as one uses increasingly old measurements of those other fish, while the focal's self-state, currently measured geometry and all target outcomes remain *exactly unchanged*?

Let \`G_i(t)\` be exactly the frozen v22 geometry and focal-state features, and define
\`R_i(t; ell) = (1/(N-1)) sum_{j!=i} v_j(t-ell) - v_i(t)\`,
where \`v_i(t)\` is **always the current focal velocity**, even when the other fish are measured at \`t-ell\`. Do not change the focal's current self predictor or use fish positions at stale times to recompute spatial geometry.

**Six predetermined other-fish measurement ages** \`ell ∈ {0, 0.1, 0.2, 0.5, 1.0, 2.0}\` **seconds**, plus exactly the v22 geometry-only \`G_i(t)\`. These clocks are converted to integer original source frames: Puy black neon tetra 50Hz → 0,5,10,25,50,100 frames; Niizato ayu 30Hz → 0,3,6,15,30,60 frames. A stale group velocity at age ell always uses two strictly past original frames \`[t-L-s, t-L]\` where \`s=5\` tetra and \`s=3\` ayu; the zero age uses \`[t-s,t]\`. Averages are *other N−1 fish*, not including the focal. All predictors are ≤t even if source publishers performed noncausal smoothing.

## Original sources, fixed support and reproducibility

**Tetra:** re-acquire all 6 original Puy 2024 8-fish Zenodo 10890112 source CSV files, verify provider MD5 before inspecting movement. Preserve v22 \`tetra.tetra_one\` source/target indexes and two horizon-specific target cohorts exactly, including v22 original v7 model replay. Use identical original \`G_geometry\`, \`G_global\`, future 0–0.2s and future 0.5–0.7s velocity targets for the exact same original fish×frame rows. 2s history is already present in original v5 support (\`GHOST_LAG=100\`).

**Ayu:** exact upstream Git commit \`158e8d7ebdef73752da63192ee36e3a099dd5dfa\`, all 7 provider Git blob SHAs/sizes. Original \`source_data\` 30Hz true native TXT clocks, original 10-fish X/Y column mapping. Use the same v22 2-second eligible source index \`t>=66\`, same geometry/global and short/delayed Y rows. No new cohort rescue or source-time reinterpretation.

For each original entire-recording heldout split: training-only StandardScaler, fixed Ridge(alpha=10), no coefficients tuned to v24 results. Evaluate both 2D velocity components and all 7 panels (geometry + 6 ages) on the same exact original heldout fish×frame rows. **Do not resplit fish×frames or use any test file to fit scaler/coefficients.** No source-level scores or original animal positions are committed.

## Original replay before new results (hard scientific STOP)

Before any v24 contrasts, the exact v22 **original all-recording equal means** for \`current\` and \`2s-old\` must replicate **to absolute 0.001 original source squared units**, using original source-authorized source cohort and the same v22 fitting implementation:

| Source / horizon | v22 current original MSE | v22 2s old original MSE |
|---|---:|---:|
| Tetra 0–0.2s | 11.352981111900112 | 13.740122954303708 |
| Tetra 0.5–0.7s | 54.62586752465776 | 64.89291742289119 |
| Ayu 0–0.2s | 6343.970137459749 | 7061.387488140268 |
| Ayu 0.5–0.7s | 25687.490647693074 | 30463.936132138184 |

If replay fails, retain source-safe STOP receipt; never tune model, parameters, cohort, lags or scale to force a positive result. Same exact \`G_geometry\` columns, \`current\` relative vector and \`2s\` vector must be byte-wise array-equal to v22 where represented identically.

## Frozen inference metrics and counterclaims

1. For each source and each horizon, report **mean of per-recording MSE** at geometry and all six lags, all positive/negative per-recording signs for each delay versus current, paired whole-recording bootstrap 95% with exactly 5,000 draws and seed 20261124. Do not pool Puy cm/s or ayu unknown units; do not count two horizons as independent samples.
2. Primary *operational information-retention curve*:
  \`I_s,h(ell) = [MSE_s,h(geometry)−MSE_s,h(ell)]/[MSE_s,h(geometry)−MSE_s,h(0)]\`,
  using equal-recording means. This is not mutual information, a biological signal lifetime, or a universal timescale: it is normalized incremental predictive MSE in this specified model, source and horizon. If the denominator ≤0, retention is NOT_DEFINED, with no posthoc alternative.
3. A discrete operational "half-retention threshold" is the smallest **observed sampled lag** \`ell∈{0.1,0.2,0.5,1,2}\` with \`I(ell)≤0.5\` *if it exists*. If non-monotone, retain the full curve and label threshold **not a dynamical half-life**. No interpolation or continuous exponential time constant fit.
4. Secondary *direction/temporal null* claims: current versus 0.5s, 1s, 2s individually; signs across whole recordings. Even with all signs positive, conclude only conditional time-specific **shared movement-state prediction**, not evidence of causal neighbor response, transfer entropy, communication or fish calling.
5. Known-truth Gaussian common-driver null with **no fish→fish arrows** predicts the same general current>stale pattern when an unmeasured shared driver is time-varying; see [v22 source-independent counterexample](V22_COMMON_INPUT_NULL_AND_IDENTIFICATION.md). This alternative is **not** defeated by group-velocity decay alone. Original paper's smoothing/interpolation can also create retrospective temporal information unavailable to fish in real time. Explicitly report inability to calibrate biological sensory timescale.
6. Fish chorus remains untested: no time-aligned individual calls, sender localization, acoustic fields or playback in either full movement source.

**No merging.** All outcomes reported whether positive, negative or null. PR #248 stays Draft, main unchanged.
