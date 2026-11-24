# v22 — Two independent original fish taxa: the present collective velocity matters more than a 2-second-old collective state

**2026-11-24 JST — OBSERVED RETROSPECTIVE FISH MOVEMENT, NOT SOUND OR SOCIAL CAUSALITY.**

## Main preregistered question

Given the same current focal movement, wall/spatial geometry, same entire held-out recording and the same future velocity outcome, does **the mean velocity of other fish observed NOW** predict the focal better than that same set of other fish observed **2.00 seconds ago**? The focal's self velocity is always **current** in both relative-global predictors.

Methods were frozen before these new numerical results at [v22 pre-result freeze](V22_CONTEMPORANEOUS_COLLECTIVE_VELOCITY_FREEZE.md), commit [f90d14e7](https://github.com/zuizui0223/boids/commit/f90d14e7c49e7de38c1d7ba9ae09d89a3088f471). All original v5–v9c source data and prior outcome models were previously inspected, so this is a preregistered *incremental diagnostic within known source populations*, not a pristine independent study or newly measured fish vocal behavior.

## Source-verified executed results

| Study, full original recording as heldout | Prediction window | MSE with CURRENT other-fish vector | MSE with 2s STALE other-fish vector | STALE − CURRENT MSE | Relative improvement vs STALE | Recording signs | Paired-recording descriptive bootstrap 95% of absolute gain |
|---|---|---:|---:|---:|---:|---:|---|
| **Puy et al. black neon tetra**, 8 fish per recording, **6 original files**, 50fps | 0.0–0.2 s | **11.352981** | 13.740123 | +2.387142 | **17.3735%** | **6/6 positive** | [2.0215, 2.7375] |
| Same 6 original recordings | 0.5–0.7 s | **54.625868** | 64.892917 | +10.267050 | **15.8215%** | **6/6 positive** | [9.6510, 10.7217] |
| **Niizato et al. ayu**, 10 fish per recording, **7 original files**, 30fps | 0.0–0.2 s | **6343.970137** | 7061.387488 | +717.417351 | **10.1597%** | **7/7 positive** | [479.8213, 963.0529] |
| Same 7 original recordings | 0.5–0.7 s | **25687.490648** | 30463.936132 | +4776.445484 | **15.6790%** | **7/7 positive** | [3962.1096, 5593.8172] |

Absolute MSE units are **(cm/s)^2 for Puy tetra** and squared original numeric coordinate units/second for ayu, whose spatial scale has *not* been established. **Never pool, subtract, or compare their absolute MSEs across sources.** Relative percentages are conditional on each fixed model, source and horizon. There are **two studies/taxa, not 13 independent populations**; 6/6 and 7/7 recording signs may share the same fish and common tank/experimental setting. The two horizons within each recording are correlated, so 26/26 is not a valid independent sample size.

### Secondary controls frozen before observing v22 outcomes

- CURRENT vector versus **current vector MAGNITUDE only**: mean MSE improvement relative to magnitude-only is **17.354% / 15.810%** for tetra short/delayed (6/6 recording signs each) and **10.139% / 15.707%** for ayu short/delayed (7/7 each). These signed, two-dimensional spatial vectors are informative; a scalar magnitude alone does not replace them.
- Old **geometry-only** versus CURRENT: tetra MSE 13.735379 → 11.352981 short, 64.867789 → 54.625868 delayed. Ayu revised 2-second history eligible cohort MSE 7060.251274 → 6343.970137 short, 30474.431421 → 25687.490648 delayed. STALE and MAGNITUDE scores remain close to the geometry-only baseline across these source-specific comparisons.
- No fish audio, acoustic source localization, group-call occurrence, playback, or external flow measurement enters these models. Do not relabel the magnitude-only control as experimental particle-motion phase or an auditory stimulus test.

## Reproducibility and source provenance

- **Puy et al. 2024 PNAS** original [Zenodo 10890112](https://doi.org/10.5281/zenodo.10890112) 6 × 8-fish original source files, all provider MD5 reverified and original v7 current-global short-horizon leave-one-recording-out scores replayed before new v22 score. Full original runs: [Actions #45311753355](https://github.com/zuizui0223/boids/actions/runs/45311753355) SUCCESS, [source-safe exact per-recording JSON artifact](https://github.com/zuizui0223/boids/actions/runs/45311753355/artifacts/14883633016).
- **Niizato et al. 2024 Scientific Reports** seven original 10-ayu TXT Git blobs independently reverified at frozen upstream commit `158e8d7ebdef73752da63192ee36e3a099dd5dfa`. Native 30fps raw time mapping (not the source paper's downstream 20Hz analysis) and v9c original global/geometry features exactly replayed, with a fixed eligibility subset `t>=66` source frames for the 2s-old comparison. Full runs: [Actions #45311757386](https://github.com/zuizui0223/boids/actions/runs/45311757386) SUCCESS, [source-safe exact per-recording JSON artifact](https://github.com/zuizui0223/boids/actions/runs/45311757386/artifacts/14883790757).
- Each Actions job: **8/8 synthetic source-free tests PASS**, verified whole-recording numeric model training/test isolation, frozen ridge alpha=10 with training-only standardization, original data hashes, 5,000 **recording-unit** descriptive bootstrap replicates for each contrast. Both workflows have strict scientific result gates; an unavailable source or replay mismatch fails the job rather than giving a scientific PASS. No animal coordinates or original individual traces are committed.

## What is supported

**In two independently published fish taxa, present-time other-fish directional group motion has a repeatable, source-conditional predictive advantage over 2-second-old other-fish motion, when added to each focal's current movement and spatial state.** This holds for both short and delayed future-motion targets within the original source contexts. A useful ecological label is **the temporal specificity of shared collective motion information**, not established social signal transfer.

Neither nested-model improvement nor the current–stale contrast identifies a biological information-flow direction between fish. In particular, the independently constructed **zero-social-interaction common-driver Gaussian counterexample** in [v22 non-social identifiability proof](V22_COMMON_INPUT_NULL_AND_IDENTIFICATION.md) produces the same qualitative current-group superiority because many fish jointly sample one time-varying external driver. The existing records may also contain noncausal source smoothing/interpolations with future support. No external driving flow was experimentally blocked; no causal Reynolds alignment, acoustic hearing, cognitive memory, 3D ecology, contact calling, or school↔chorus feedback effect is established.

This is **not a formal cross-study meta-analysis** at n=2 taxa, and bootstrap intervals are only descriptive source-recording variability. The result can motivate a larger, fully source-audited multi-taxon synthesis and a controlled fish acoustic/motor experiment, without inflating the evidence.

## Next falsification and third-study eligibility

1. Extend to a **third independent fish taxon with complete source trajectories and more than one nonselected school**, comparing exact time-specific 0s versus 2s other-fish state (with source-specific measured clocks/geometry). The 2026 *Hemigrammus rhodostomus* study has two openly available, hand-selected high/low maneuverability examples but requires the authors' original broad 5/10/15-fish tracks; [v23 source-only gate](V23_THIRD_FISH_SPECIES_SOURCE_GATE.md) refuses to count two examples as independent reproduction.
2. To distinguish common external motion from social information, measure water/environmental motion, record independent whole schools, add common-driver and position-matched nulls, and identify a social cue intervention. Individual transfer and common environmental response are observationally non-identifiable from the current predictors alone.
3. Full **Boids→fish chorus** needs the same schools' synchronized individual movement and **source-attributed vocal events** with acoustic stimuli and adequate quiet intervals, a task none of Puy, Niizato, Veith or curated Zheng pairs currently fulfills.

**Decision:** positive cross-taxon predictive recurrence, **no positive fish social-causal or vocal-mechanism claim**, keep [PR #248](https://github.com/zuizui0223/boids/pull/248) Draft and main unchanged.
