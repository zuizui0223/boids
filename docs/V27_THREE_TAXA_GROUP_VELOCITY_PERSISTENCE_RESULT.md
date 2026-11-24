# v27 observed result — group-motion persistence coincides with slower decay of predictive group-state information in stickleback

**2026-11-24 JST — ORIGINAL OBSERVED FISH MOVEMENT; NOT fish-to-fish causality, neural latency, synchronous acoustic calls or meta-analytic pooled effects.**

## Why run this additional test?

The source-authenticated two-taxon v24 result had normalized model-specific incremental predictive retention I(0.2s)=.322/.221 (Puy black neon tetra short/delayed) and .432/.440 (Niizato ayu); third-taxon *Gasterosteus aculeatus* v26d exploratory three-source-file forecast retained .783/.777 at 0.2 seconds. This post-result-motivated independent diagnostic tests whether a *source-level shared-motion persistence* can account for at least the **highest** predictive retention in stickleback.

[Pre-v27-result source-locked protocol](V27_GROUP_MOTION_AUTOCORRELATION_FREEZE.md), committed at [2fdf88d7](https://github.com/zuizui0223/boids/commit/2fdf88d7058327c8f6b4a4ded0c2aeda96fdee01), fixed exact original source cohorts and frame-based age grid before all v27 original correlation numbers. **Explicit falsification rule**: stickleback mean C(0.2) must exceed *both* tetra and ayu means. No need to optimize lag, reuse predictive outcomes, select schools or adjust any correlation after inspecting v27 results.

## Source-authenticated real fish observations

For each study recording, U(t) is the **observed whole-school mean two-dimensional velocity vector** based only on current/past original XY positions, using each study's existing source speed difference (Puy 5/50 seconds; Niizato 3/30 seconds; MacGregor 5/25 seconds). The metric C(age) is the **centered 2D vector autocorrelation** of U(t) and U(t−age) on exactly the same original source-time cohort as the earlier age-prediction study. This is not the MSE-retention index I, and not fish-to-fish information transfer.

| Published original fish source | Original files | C(0.2s) | C(1s) | C(2s) | I(0.2s) short / delayed (previous models) |
|---|---:|---:|---:|---:|---:|
| **Puy et al. 2024** black neon tetra, 8 fish | 6 files | **0.965553** | 0.580486 | 0.153962 | 0.322423 / 0.220901 |
| **Niizato et al. 2024** ayu, 10 fish | 7 files | **0.958512** | 0.595210 | 0.247052 | 0.432089 / 0.439580 |
| **MacGregor & Ioannou 2021** stickleback, 8 fish | 3 files, **distinct shoals unverified** | **0.985309** | **0.869427** | **0.646431** | 0.782893 / 0.777077 |

### Exact recording/source-quality checks

- **Tetra:** original [Actions #45334241176](https://github.com/zuizui0223/boids/actions/runs/45334241176) SUCCESS: all six Puy Zenodo 10890112 provider MD5 original files verified, v24 original short cohort exact replay, source-free known-truth unit tests; [per-file original receipt](v27_verification/TETRA_GROUP_VELOCITY_CORRELATION_RECEIPT.json). C(0.2) per-file range **0.959071–0.970493**; original group time events per file 8,288 / 8,988 / 8,988 / 8,988 / 17,988 / 11,488.
- **Ayu:** original [Actions #45334246172](https://github.com/zuizui0223/boids/actions/runs/45334246172) SUCCESS: all seven Niizato pinned Git blobs SHA verified, exact v24 2-second eligible t≥66 roster, native 30Hz original clock; [per-file receipt](v27_verification/AYU_GROUP_VELOCITY_CORRELATION_RECEIPT.json). C(0.2) per-file range **0.936306–0.976492**.
- **Stickleback:** original [Actions #45334249760](https://github.com/zuizui0223/boids/actions/runs/45334249760) SUCCESS: 3 EIDC original SHA/byte-authenticated source files, exact v26d native 25Hz time, NA omissions and original 6,966 / 8,015 / 5,567 source-time prediction cohort replay; [per-file receipt](v27_verification/STICKLEBACK_GROUP_VELOCITY_CORRELATION_RECEIPT.json). C(0.2) per-file range **0.982631–0.990372**. Three source filenames do **not** prove different original shoals. All three C(1) ≥0.832, all three C(2) ≥0.549.
- In each original workflow **6 synthetic known-truth tests passed** (validation of sample support, native fps, constant velocity null, nonfuture source positions and source-cohort STOP). Each receipt was independently recomputed from source-safe per-file correlations, with no original individual XY time series redistributed.

## Frozen decision and important contrary pattern

**Fixed stickleback-highest prediction: SUPPORTED.** The source-conditioned ordering at 0.2 seconds is C(stickleback)=.985309 > C(tetra)=.965553 > C(ayu)=.958512. At 1–2 seconds stickleback retains much more group directional motion than the two 2024 sources. This agrees qualitatively with the stickleback age-0.2 *predictive* retention I≈.78 exceeding the others I≈.22–.44.

**BUT: raw group-velocity persistence alone does NOT perfectly order all three original source results.** At 0.2s, tetra has marginally HIGHER raw C than ayu (.9656 > .9585), yet its incremental predictive MSE retention is LOWER (.322/.221 vs .432/.440). This source-level rank inversion contradicts a simple assumption that measured C(age) by itself uniquely determines normalized predictive retention across datasets.

Moreover C(0.2) is high in **all three original taxa** (≥0.959), even though predictive I(0.2) ranges .221–.783. This alone prevents equating C with model-retained unique predictive information or a fish sensory transmission coefficient. The 0.2s difference in C between tetra and stickleback is only ~0.02; their predictive I difference is far larger and may involve conditional redundancy with own state, spatial geometry, asymmetric observation noise or trial circumstances.

### Interpretation ceiling

The data are **consistent** with an effect of source group-movement persistence on age-predictive value, but they do **not establish a causal or sufficient explanation**, nor an animal's perception/network or an evolutionary species-specific clock. Original fish trial sessions, aquaria, video tracking/interpolation, source fps and precise future target horizon differ. No independent new fish behavioral manipulation was made. A time-correlated common water/current/environmental stimulus can cause both high C and I without social communication (see [postresult known-truth counterexample](V24_NON_SOCIAL_AUTOCORRELATED_COMMON_DRIVER_COUNTEREXAMPLE.md)). n=3 source studies with missing verified school IDs is not a valid population-wide cross-taxon meta-analysis.

## Next falsifiable axis — conditional innovation instead of raw common-state persistence

**New candidate, not yet tested:** the decay of **model-unique school-velocity *innovations conditional on each focal's own movement and present geometry***, rather than unconditional U(t), may account for the large variation in I(0.2). Lock the original per-recording past/target rows and compute, using training recordings only, the component of current other-fish relative motion not already predictable from fixed G/own-state; then assess if stale residual information survives without confusing the local group velocity with a latent shared external driver. Compare per-recording correlation and time-aged out-of-sample prediction **without choosing smoothing or time constants after seeing outcomes**. More decisive empirical identification still requires independently measured common motion/flow or randomized sensory manipulation.

**No fish vocal data:** None of the three verified movement sources include time-aligned individual vocalization/source localization. Boids↔chorus feedback remains untested. Maintain [Draft PR #248](https://github.com/zuizui0223/boids/pull/248) unmerged; main untouched.
