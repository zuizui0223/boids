# v8 original school velocity–neighbor assignment diagnostic, plus source-smoothing delay

Frozen 2026-11-20, **after v5–v7 positive outcome access**. This is a post hoc mechanism *stress test*, not an independent confirmatory animal study.

## Scientific trigger

Original 8-fish×6 recording Puy 2024 trajectories (Zenodo 10.5281/zenodo.10890112), v7 MSE G+Global=11.352981, G+Global+TrueLocal=11.320852, unique local +0.0321295 (cm/s)^2. The difference is small relative to overall +2.5798 self→full Boids. A current local velocity field might be a proxy for generic shared momentum. Also the original publication describes a Gaussian σ=2 frame smoothing truncated at 5σ (up to ±10 frames), and Zenodo CSV may have already been filtered/interpolated. Hence v5–v7 forecasts were correctly labeled *retrospective*, not true online.

## Locked two validation components

**A. Spatial–speed crosswalk negative control (primary diagnostic, unchanged original 0.2s endpoint)**

For every focal fish i and original 50fps frame t, keep: all eight exact positions, focal fish own velocity/state, all seven other fish instantaneous velocities as a multiset, school global average, local 25cm neighbor mask, the actual heldout target. Only **rotate which other-fish velocity is assigned to which other-fish position** among the seven other fish at the same t, two fixed nonzero shifts 1 and 3 in original index order. The local mean relative velocity changes when not all other fish are inside the 25cm neighborhood. Other-fish mean is numerically identical for every focal and frame. This is an adversarial diagnostic (assignment exchangeability NOT assumed and no experimental animal perturbation).

Compare four models on exactly the same source-target fish frames, with 5 entire recordings train/6th withheld, training-only scaling, fixed ridge alpha=10, same 25cm/8cm geometry:

- G+Global (same original v7).
- G+Global+TrueLocal (original v7 combined model).
- G+Global+Rot1Local (same dimension, 1-position rotation of others).
- G+Global+Rot3Local (same dimension, 3-position rotation).

Precondition: exact original v7 G+Global and G+Global+TrueLocal six test-recording MSEs must replay within 6e-5 before accepting a novel result. Primary diagnostic effect MSE(Rot1)−MSE(True); Rot3 secondary. All source-recording negative results retained.

**B. Delayed 0.5–0.7s future trajectory (separate endpoint)**

Original input features at t unchanged. Predict *post-gap velocity* from raw record positions at t+25 and t+35 frames, with 10-frame/0.2s target difference. If published source positions were symmetric Gaussian-smoothed using original ±10 frames, this separates the non-overlapping raw observations underlying features at t and delayed positions at t+25 onward. However any unknown spline interpolation may be non-causal and the actual original CSV filtering state is unverified. **Do not call strict prospective online.** Compare the G+Global, G+Global+TrueLocal, G+Global+Rot1Local on identical support after eligibility. This is a different and harder target than v5–v7 short-step prediction. No cross-target MSE percentage attribution.

Additionally report original neighborhood counts (0–3,4–6,7 of seven other fish) and trials to assess how much of the source feature can even change when velocity-position assignments are rotated.

## Scientific claim boundary

No observed fish vocalizations are synchronized to these Puy 2024 trajectories. Results cannot identify separation/alignment/cohesion as distinct causal forces, fish call propagation, individual cognition or cross-species generality. Six original recordings may contain recurrent fish; signed tests conditional on treating whole recordings as independent are not population-level p-values. No rescue by scanning lags, permutation seeds or radii after opening v8 outcome scores.

Original source acquisition: same provider SHA/MD5 six originals. No fish positions redistributed. Keep Draft and original v5-v7 conclusions frozen. Run: `validation_fish_school_v8/assignment_and_delay.py`.
