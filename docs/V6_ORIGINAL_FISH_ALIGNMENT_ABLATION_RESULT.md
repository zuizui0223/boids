# v6 observed black neon tetra schooling: local alignment is the principal predictive information

Completed original numerical run on **2026-11-20**: [Actions #44750162263](https://github.com/zuizui0223/boids/actions/runs/44750162263), [full source-safe result artifact](https://github.com/zuizui0223/boids/actions/runs/44750162263/artifacts/14634564142).

## Source / validity
Original Puy et al. (2024) PNAS 8-fish × 6 recordings, 50 fps Zenodo DOI 10.5281/zenodo.10890112. All published MD5s 6/6 verified before new values opened. The **same** original focal fish future 0.2s velocity, same exact valid rows, train on 5 entire recordings, test on 6th, train-fold standardization, ridge alpha=10 and preselected 25cm/8cm neighborhoods as frozen v5. v6 first source-run passed 5 known-truth tests and recomputed each of the six v5 original own/full/faster-neighbor MSEs to within 2×10^-5. Original source sample/threshold or scoring not retuned.

## Exact original six-recording heldout scores

MSE unit: (cm/s)², lower is better. Source values rounded here; exact decimals are in the Actions artifact.

| Entire heldout recording | Self M0 | Neighbor *geometry* (G) | Alignment-only (A) | Full classic Boids (F) | F + faster-neighbor |
|---:|---:|---:|---:|---:|---:|
| 0 | 15.27100 | 15.14133 | 12.16923 | 12.11560 | 12.01489 |
| 1 | 13.19111 | 13.03683 | 10.65980 | 10.58197 | 10.51858 |
| 2 | 12.42779 | 12.26727 | 10.20441 | 10.12057 | 10.06225 |
| 3 | 13.06379 | 12.88236 | 10.65660 | 10.55974 | 10.51311 |
| 4 | 13.70523 | 13.56780 | 11.97206 | 11.87967 | 11.88255 |
| 5 | 15.75943 | 15.51668 | 12.80646 | 12.68202 | 12.56739 |
| **Equal-recording mean** | **13.90306** | **13.73538** | **11.41143** | **11.32326** | **11.25979** |

### Frozen scientific comparisons
- **Full F vs self M0, original v5 replay**: +2.579795 (cm/s)², 6/6 recordings positive.
- **Geometry G vs self M0**: +0.167679, 6/6 positive. Descriptive whole-recording bootstrap 95% [0.141500, 0.200231].
- **Full F vs geometry G (primary new decomposition)**: **+2.412116**, 6/6 positive, trial-level bootstrap [2.049454, 2.752235], exact one-sided sign p=.015625 **only under independence of the 6 recordings**.
- **Alignment A vs own M0**: +2.491630, 6/6 positive, even though alignment-only still implicitly depends on which fish are inside 25cm neighborhood.
- **Repulsion unique increment beyond alignment+cohesion**: +0.035526, 5/6 positive; exact sign p=.109375, not robust across recordings.
- **Cohesion unique increment beyond alignment+repulsion**: +0.082684, 6/6 positive, descriptively small relative to alignment information.
- **Faster-neighbor selectivity beyond F**: +0.063468, 5/6 positive, sign p=.109375; not a robust newly transferable rule in this test.

A decomposition of **incremental predictive improvement under nested fitted ridge regressions** yields 2.412116 / 2.579795 ≈ **93.50%** for the velocity-alignment addition beyond geometry. This fraction is **not a causal variance attribution or unique behavioral force**: the effects depend on model ordering, collinearity, training sample and spatial neighborhood definitions.

### Biological interpretation / limitations
Multiple fish in a small tank share momentum and latent environmental fluctuations. Other individuals' current velocities may improve forecasting without *causally exerting* alignment steering. The paper already demonstrated selective speed-alignment patterns (prior art), and source trajectory coordinates used Gaussian smoothing/interpolation that can include future frames. Trial-holdout is retrospective transport, not untouched online realtime forecasting. Recordings may reuse animals (not independent fish populations). No matched individual fish calling, habitat resources, stable 3D niches or causal Reynolds coefficients were estimated.

**Next necessary model-competition test:** compare the current local within-25cm alignment features with whole-school other-fish mean velocity (a shared school-motion baseline) on exactly the same original targets and heldout recordings. A positive local-minus-global gain is needed before proposing that neighborhood-scale alignment is special. If only the global term transfers, the correct empirical result is *collective school motion is informative*, not local social influence.

**No merge to main or field chorus claim.** Keep PR #248 draft.

