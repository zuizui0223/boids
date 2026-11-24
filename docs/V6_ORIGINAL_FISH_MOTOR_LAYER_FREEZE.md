# v6 preregistered post-v5 exploratory motor-layer decomposition

Date: 2026-11-20. **Do not treat as a new independent experiment or mechanism discovery.**

## Core scientific question
Original 2024 black neon tetra (8-fish, 6 recordings, source original SHA/MD5) gave heldout-trial Boids-feature advantage of +2.5797952516 (cm/s)^2, 6/6 recordings. That full predictor simultaneously changed information about nearby fish **positions** (separation/cohesion/count) and **velocities** (alignment). Which component of *predictive information* transfers to a previously unseen recording?

## Locked models
Reuse `validation_fish_school_v5/forecast_transfer.py` literally for original source acquisition, original train/test recording groups, original 0.2s future Cartesian velocity target, 50fps, 100cm/2745px, 25cm perception, 8cm avoidance, 10-frame stride, train-fold standardization and ridge alpha=10. This is an exploratory post-v5 design, not untouched source.

Nested layer predictors, each with exactly same M0 own-state/wall terms:
- **Geometry-only G:** repulsion vector (x,y), cohesion vector (x,y), neighbor count = 5 social features. No neighbor-velocity information.
- **Alignment-only A:** mean neighboring relative velocity vector (x,y). No neighbor positions beyond eligibility of its original fixed 25cm neighborhood, so proximity still influences this feature.
- **Full F:** repulsion+alignment+cohesion+count = 7 social features, byte-exact the original v5 full feature array.
- **No-repulsion N:** alignment+cohesion+count = 5 social fields; test unique incremental repulsion information.
- **No-cohesion C:** repulsion+alignment+count = 5 social fields; test unique cohesion information.
- **Faster-neighbor M2:** full+relative velocities of faster neighbors & number; byte-identical original v5 version.

**Required primary new decomposition**: G vs F on same 6 complete heldout recordings. The MSE(G)−MSE(F) improvement asks whether neighbor velocities carry *incremental predictive information* beyond known neighbor geometry.
**Secondary**: M0→G, M0→A, N→F (repulsion), C→F (cohesion), F→M2 (speed-selective original replay).

## Source and output gates
- Download original six CSVs only via official Zenodo 10890112; all published MD5 checked before opening movement numerical outcomes. Never upload raw tracks.
- Recompute M0, F, and M2 and stop if any differs from **v5 archived source Actions run #44743721112** by >2×10^-5 in original MSE.
- Record whole-recording MSE separately (six recording units), exact one-sided directional sign, and descriptive fixed 5000 whole-recording bootstrap. Do not count ~500,000 fish×frames as independent populations.
- No post-outcome rescue via feature-radius, time-horizon, sample cutoffs, nonlinearity, or best panel selection.

**Claim limit:** Predictive alignment information is not identification of an alignment *force*. Source trajectories use partly future-symmetric Gaussian smoothing, and six recordings may share fish. One species/study is not macroecological universality. None of these 2024 original fish datasets contains synchronized fish calls. Fish chorus mechanism **NOT TESTED**.

## Implementation
`validation_fish_school_v6/ablate_schooling.py`, `test_v6_layers.py` and GitHub Actions `fish-school-v6-layers.yml`. Keep PR draft and main unchanged.
