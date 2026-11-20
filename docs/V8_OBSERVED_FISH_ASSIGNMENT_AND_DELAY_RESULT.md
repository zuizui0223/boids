# v8 original schooling: velocity-to-neighbor mapping, radius saturation, and delayed prediction

**2026-11-20 genuine original data**: 6 author-published, provider-MD5 verified 8-fish black neon tetra recordings, [Actions 44757948554](https://github.com/zuizui0223/boids/actions/runs/44757948554). Full original result JSON is retained at [artifact 14640941036](https://github.com/zuizui0223/boids/actions/runs/44757948554/artifacts/14640941036). All 7 independent known-truth tests succeeded. Source v7 G+Global and G+Global+Local MSEs on the same native 0.2s target replayed before novel comparisons (absolute difference <6e-5). No original fish track coordinates redistributed.

## Core result: fixed 25cm local radius mostly spans the **entire school**

Number of other fish within 25cm (of 7 available): mean across recording×focal×time **6.67–6.97**. Fraction having **all seven** in radius by recording 0–5 is **0.984179, 0.969696, 0.980154, 0.920241, 0.810436, 0.955454**. Equal-recording mean = **0.936693 (93.6693%)**.

Where all 7 neighbors are within 25cm, v7 'local alignment' is algebraically identical to the other-seven whole-school mean velocity. Thus the very large v5/v6 predictive alignment gain should **not** be advertised as a uniquely local steering effect, because the selected original neighborhood is near-complete in nearly every observed focal-time row.

## Fixed within-time velocity-to-position reassignment negative controls

For each focal/time, keep the exact same focal own history, eight positions, 7 other-fish velocities as a multiset, and other-seven **global velocity mean**. Rotate the *assignments* of these seven velocities among the fixed seven positions by fixed shifts 1 and 3; retrain and test identical recording-level splits with fixed ridge and identical target rows.

Short 0.0–0.2s future mean-velocity MSE (cm/s)^2:

| Frozen contrast | Equal-recording mean reduction in MSE | Positive recording-level signs | Trial-bootstrap descriptive 95% |
|---|---:|---:|---|
| Real local beyond known global (v7 replay) | +0.03212948 | 6/6 | [0.016504,0.052940] |
| Correct velocity-to-neighbor mapping vs fixed rotation by 1 | **+0.03319641** | **6/6** | [0.016910,0.054935] |
| Correct mapping vs fixed rotation by 3 | **+0.03215270** | **6/6** | [0.015427,0.055438] |

**These are NOT exchangeable animal interventions and no permutation p-values are claimed.** The effect can occur only when the 25cm mask omits some neighbors. Among six recordings, incomplete-neighborhood fraction and local increment have exploratory recording-level correlation **+0.904** (n=6, post hoc), not an independent ecological effect or strong mechanistic test.

## Delayed, disjoint-ish source window: 0.5–0.7s after current frame

Original 2024 paper describes Gaussian sigma=2 frame, support about ±10 frames, for its processed kinematic analysis. The published CSV's smoothing state is not independently verified. Delayed outcome is defined from source positions t+25 and t+35, while predictors only use values at or before t in our code. This reduces the potential overlapping support of a symmetric ±10-frame smoothing window. Original source occlusion interpolation may have longer, noncausal support; therefore this is **NOT fully prospective** and is a new target distinct from v5–v7 0.2s.

| Delayed comparison | Mean MSE difference | Positive recordings | Descriptive 95% |
|---|---:|---:|---|
| Global vs global + true local | **+0.03041068** | **4/6** | [−0.000484,0.062348] |
| Correct vs 1-rotation velocity assignment | +0.03161425 | 4/6 | [+0.004106,+0.062809] |

The delayed locally incremental advantage **did not consistently recur across all six recordings**. A positive mean is not sufficient to establish a transportable rule, and this is not a general biological null.

## Scientific conclusion and next falsification

The strongest supported field result remains: **collective velocity predicts focal fish locomotion**. Unique local alignment information is small, and its measured increment depends on restricted neighborhood topology and forecast horizon. No individual causal Reynolds force, acoustic signaling, fish chorus, cross-species universality or independence of repeatedly filmed fish is established.

Independent ayu (*Plecoglossus altivelis*) source: Niizato et al. (2024) Scientific Reports, [public source](https://github.com/t-niizato/Information-structure-of-heterogeneous-criticality), seven 10-fish recordings. Already source-only [v9 source run 44758472999](https://github.com/zuizui0223/boids/actions/runs/44758472999) verified 7 Git blobs and 22-column rectangular tables; original MATLAB importer maps source columns 3–12 to X of 10 fish, 13–22 to Y. The next behavior test should adopt **fixed k-nearest-neighbor topology** rather than an arbitrarily oversized radius, use a heldout recording, and avoid post-outcome threshold rescue.

**Review-only Draft PR #248, main unchanged.**

