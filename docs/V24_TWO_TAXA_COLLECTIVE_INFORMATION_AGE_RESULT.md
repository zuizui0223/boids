# v24 — Original two-fish-taxon collective-state predictive age curve (2026-11-24)

**ORIGINAL OBSERVED FISH MOVEMENT, RETROSPECTIVE PREDICTION ONLY. Not fish contact calls, a social-interaction estimate, neural response latency, acoustic sensing, or a formal cross-study meta-analysis.**

## Frozen original source and model

The exact six group-state ages {0, 0.1, 0.2, 0.5, 1, 2} seconds, source-specific 50/30 Hz frame correspondence, **current focal self-state in ALL models**, currently observed geometry, both existing future-velocity horizons, ridge alpha=10, full recording holdouts, original SHA/MD5 source admission, historical v22 current+2s MSE replay tolerance, and 5,000 recording-level descriptive bootstraps were [frozen in a commit before any v24 observed effects](https://github.com/zuizui0223/boids/commit/4966d94aa80643b5b2256d72df776b6063550d14). The first two CI attempts failed on a **synthetic fixture sharing a short/delayed Python dict reference** before any original source behavior was opened; we corrected that fixture only and reran. The successful source-locked numeric model and all original biological cohorts were not retuned.

We define a **conditional predictive retention index**, not mutual information or physical interaction strength:
\[
I(\ell)=\frac{MSE(G)-MSE(G+\mathbf{v}_{-\!i}(t-\ell)-\mathbf{v}_i(t))}{MSE(G)-MSE(G+\mathbf{v}_{-\!i}(t)-\mathbf{v}_i(t))}.
\]
Here \(G\) has the same focal's CURRENT motion and CURRENT geometry in every arm, \(\mathbf{v}_{-\!i}\) means mean of the **other** fish, and the future target is the focal's 2D velocity (0–0.2 or 0.5–0.7 seconds). Values below zero mean that lagged vector is slightly worse than G-only. The index is normalized **within** a source/study/horizon, not an estimate of the biological fraction of information transmitted.

## Authenticated actual field/laboratory trajectory results

| Original independently published source | Future motion target | I(0.1 s) | I(0.2 s) | I(0.5 s) | I(1 s) | I(2 s) | First sampled lag I≤0.5 |
|---|---|---:|---:|---:|---:|---:|---:|
| **Puy et al. 2024**, 8 black neon tetra in each of 6 original recordings | 0–0.2 s | **0.6332** | **0.3224** | 0.0242 | −0.0042 | −0.0020 | **0.2 s** |
| Same 6 tetra recordings | 0.5–0.7 s | **0.5190** | **0.2209** | −0.0069 | −0.0136 | −0.0025 | **0.2 s** |
| **Niizato et al. 2024**, 10 ayu in each of 7 original recordings | 0–0.2 s | **0.6836** | **0.4321** | 0.1021 | 0.0263 | −0.0016 | **0.2 s** |
| Same 7 ayu recordings | 0.5–0.7 s | **0.6741** | **0.4396** | 0.1315 | 0.0345 | 0.0022 | **0.2 s** |

All 6/6 tetra recording-level current-speed models score better than the models using group state aged 0.1,0.2,0.5,1,2s, for **both targets**. All 7/7 ayu recordings show the same signs for all five aged-current contrasts, for **both targets**. That is **13 recording files in 2 independently published fish species**, not 13 independent fish populations and not 26 independent confirmatory tests. It is a same-file secondary comparison on already-studied original populations. Recording-unit descriptive 95% bootstrap intervals of each age-vs-current MSE contrast are in the original source-safe numeric receipts, and are not independent-population confidence intervals.

### Original equal-recording MSE by age (different source units: **do not pool**)

| Source–target | Geometry G | age 0s | age 0.1s | age 0.2s | age 0.5s | age 1s | age 2s |
|---|---:|---:|---:|---:|---:|---:|---:|
| Tetra 0–0.2s, squared cm/s | 13.7354 | 11.3530 | 12.2269 | 12.9672 | 13.6778 | 13.7455 | 13.7401 |
| Tetra 0.5–0.7s, squared cm/s | 64.8678 | 54.6259 | 59.5518 | 62.6053 | 64.9390 | 65.0068 | 64.8929 |
| Ayu 0–0.2s, squared unknown original XY units/s | 7060.2513 | 6343.9701 | 6570.6349 | 6750.7543 | 6987.1027 | 7041.4461 | 7061.3875 |
| Ayu 0.5–0.7s, squared unknown original XY units/s | 30474.4314 | 25687.4906 | 27247.3649 | 28370.1892 | 29844.8204 | 30309.2979 | 30463.9361 |

Ayu's **equal-recording average MSE** rises monotonically with source-state age across the six recorded lags. Tetra's MSE is *not perfectly monotone* in its near-zero-information 1–2 second tail; no monotonic law is claimed at every lag and every recorded school.

## Scientific interpretation, including falsifiable alternatives

**Positive observed pattern:** the incremental advantage of using the current, signed/directional movement vector of *other fish* decays sharply as that predictor is replaced by older information, even though the focal's own latest motion and spatial relationships are unchanged. Both taxa already lose **more than half of their model-specific incremental predictive advantage at the first predefined sampled lag of 0.2 seconds**. This is a *discrete operational predictive age threshold*, neither a precise continuous 0.2s biological half-life nor the delay of a specific visual, mechanosensory, or auditory signaling pathway.

This pattern does **not** independently identify social forces: a single unmeasured common stimulus/water flow can generate correlated fish velocities whose *current* value predicts focal future responses better than its delayed value, even when fish never respond to each other. The existing analytical [zero-social-influence common-driver null](V22_COMMON_INPUT_NULL_AND_IDENTIFICATION.md) already establishes the confounding. Also, authors' original trajectories may have future-informed interpolation/smoothing; we have performed source-retrospective heldout recording predictions, **not** proven an ex-ante online forecasting device.

Relevant published prior evidence includes [Herbert-Read et al. (2011) PNAS](https://doi.org/10.1073/pnas.1107583108), which analyzed direction-specific fish-pair temporal responses, and [Peterson et al. (August 2026)](https://doi.org/10.1093/icb/icag151), which manipulated lateral-line function in schools of 60 rummy-nose tetra, already reporting shorter acceleration response latencies for intact flow sensing. Our v24 is **not the first fish temporal coupling or sensory latency analysis**, and it does not supersede causal experiments.

## Exact original-source verification

- [Tetra observed original Actions #45316701006](https://github.com/zuizui0223/boids/actions/runs/45316701006) SUCCESS, 9 source-independent unit tests, provider MD5 for all six original Puy source files re-checked, v22 old source rows and exact current/2s original MSEs replayed. [Original aggregate+per-recording source-safe receipt](v24_verification/TETRA_SIX_AGE_ORIGINAL_AGGREGATE_RECEIPT.json). ZIP source artifact SHA256 f6aec331d0ac7d1810fd8ec533f71f5b37f6a6ad5873a8bda812034551bcd3c3.
- [Ayu observed original Actions #45316706567](https://github.com/zuizui0223/boids/actions/runs/45316706567) SUCCESS, 9 source-independent tests, all seven original Niizato Git blobs at pinned upstream commit \`158e8d7...\` verified, native ~30 Hz source time and exact original v22 forecast MSEs replayed. [Original aggregate+per-recording source-safe receipt](v24_verification/AYU_SIX_AGE_ORIGINAL_AGGREGATE_RECEIPT.json). ZIP source artifact SHA256 2ed2d2b044faf2b93cafd1e6c3ca5f5a71a507517d6cf682ab2469cbe812d656.
- No original animal locations, individual trajectory time series or audio were redistributed to the branch. CI regression tests reject source-digest drift, time-schema drift, unequal future target rows and non-original MSE replays.

## Next actual mechanistic test / limits

The strongest next empirical design tests whether the conditional age curve changes when an independent sensory pathway is blocked, **separately in acceleration and deceleration phases**. Peterson et al. 2026 already report a lateral-line intervention and official [Dryad DOI 10.5061/dryad.gxd25482b](https://doi.org/10.5061/dryad.gxd25482b), so that original source is scientifically more valuable than adding more synthetic Boids seeds. A source-only [v25 frozen schema gate](V25_LATERAL_LINE_2026_DRYAD_SOURCE_FREEZE.md) is underway. No independent original intervention treatment-by-frame score has been admitted so far.

Even a successful sensory test of school motion does not establish group vocal–motor feedback without simultaneous call sources; fish chorus mechanism remains NOT_TESTED. Preserve PR #248 Draft, main unchanged.
