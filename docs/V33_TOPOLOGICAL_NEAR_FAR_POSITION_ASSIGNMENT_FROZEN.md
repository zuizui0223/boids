# v33 preregistration — does nearest-neighbor velocity contain additional fish-specific predictive structure beyond whole-school velocity?

**2026-11-24 JST, after published v32 outcome but BEFORE ANY v33 original source local/far/surrogate numeric outcome.** This is a retrospective source-heldout *model discrimination* sensitivity test, NOT an independent experimental fish-neighbor intervention.

## Background and nonduplication

- Earlier v8 **black neon tetra** and v9c **ayu** ran source-file-heldout true local vs rotated neighbor velocity contrasts; these are pre-existing, not novel methods or experimental source interventions. They used original sources, native 0.1s/other geographic geometry windows. **v33 adds a distinct dataset**: the source-verified 2021 *Gasterosteus aculeatus* original 84 videos, 12 genuine experimental shoals matched by original author Trial→Group ID, and exactly 0.2s velocity/0-.2 and .6-.8 horizons. No novel algorithm claim.
- Original v32 all-84 source, complete 12-original-group heldout baseline: G-only short MSE **3407.0695372716236**; G+all-other-current-velocity short MSE **3344.9187577732027**; delayed G-only **8925.030228272999**; G+global current **8479.996942316231**. All four must replay to absolute native MSE ≤ **0.02** with exactly the same original rows, source hashes, G14 and Ridge10 train-only fitting before v33 comparisons are admitted.
- [Original source-locked Trial→Group map](v31_verification/EIDC_84_ORIGINAL_FILES_TO_12_AUTHOR_SHOALS_VERIFIED.json) Git blob 57ea77c604414cb484f4abd1dd6637eecb2fdf90. Author CSV SHA256 f642200bfcd0741e80969981b0a7358462f63ac816bd93dba1b95983855ea3f3, EIDC original index SHA256 270ae039d690ca4dc315416a5390b3cd3cbfa14e9dcbc1e456ec8e8302158ddc. All 84 EIDC published native files and per-file sizes must authenticate, previous 3 original SHA pins must replay. Do not infer shoal identities from filename order. No missing value imputation.

## Frozen new heldout prediction panels, same common 0.2s source rows as v32

Each original source trial has 8 tracked fish, 25fps, exact published original XY and frame index. Use unmodified [v30 14-dimensional focal current/self/geometry model](../validation_fish_school_v30/harmonized_forecast.py): focal position (2), its current and previous 0.2s velocity (4), difference (2), speed (1), group centroid displacement (2), current nearest three neighbor mean relative position (2) and nearest-three mean distance (1). Common source XY finite cohort includes every v30 required source lag and the two source future outcomes; all panels share identical train/test fish×timestamps.

At each eligible focal i,t let:
- v_i(t) = [p_i(t)−p_i(t−0.2)]/0.2 (2D velocity); global other-fish mean = average velocity of the other seven; **B_i(t)=mean_{j≠i}v_j(t)−v_i(t)**, 2 features.
- **Nearest3(t)** = three fish with smallest present original Euclidean distance to focal, no distance cutoff; **Farthest3(t)** = three fish with largest present distances among the other seven (excluding focal), deterministic tie broken by original fish column order. Both have exactly three fish, same source t/focal geometry.
- Residual local deviation **L_near(t)=mean_{j∈Nearest3(t)}v_j(t)−mean_{j≠i}v_j(t)**; far deviation **L_far(t)=mean_{j∈Farthest3(t)}v_j(t)−mean_{j≠i}v_j(t)**. They have the same units and two predictor dimensions, and **global is already present** in every comparison.
- **Same-nearest3 assignment surrogate** L_perm(t): among the 7 other-fish original velocities in ascending original fish ID order, cycle the vector values forward by exactly **one position**; assign rotated velocities to the unchanged original seven positions. Compute the mean of the velocity values now assigned to the same nearest3 identities minus the unchanged seven-fish global mean. For every focal and frame this explicitly preserves the true seven-vector multiset/global mean and current focal XY/G14; it destroys the true velocity-to-position assignment only. This is a nonphysical *predictive null*, NOT fish without interactions, and may retain correlations due to rotation geometry. No random seeds, no tuning or multiple rotations.
- **Stale nearest3** L_near_age02(t) = mean velocity of fish in the **present nearest3 set** measured at t−0.2, minus average of all other seven measured at t−0.2. Current neighbor *membership* and geometry held fixed, only age of other-fish velocity differs; source velocity difference [t−0.4,t−0.2]. This is neither biological latency nor a past-nearest3 historical network reconstruction. Focal current self velocity and present global vector stay unchanged.

Five preregistered model panels, all standardize on train groups only and use Ridge(alpha=10):
(1) G14 alone [14];
(2) **GLOBAL** = G14 + B_i(t) [16];
(3) **NEAR_TRUE** = GLOBAL + L_near(t) [18];
(4) **FAR_TRUE** = GLOBAL + L_far(t) [18];
(5) **NEAR_ROT1** = GLOBAL + L_perm(t) [18];
(6) **NEAR_STALE_0.2S** = GLOBAL + L_near_age02(t) [18].
All source original target Y 4D is identical to v30/v32: short focal 0→0.2s and delayed 0.6→0.8s future velocity. No outcome- or timestamp-dependent source selection; no new source preprocessing allowed. Original code must check that G and GLOBAL panels EXACTLY reproduce v30 numerical values (bitwise/prediction numerical tolerance).

## Heldout groups, inference and stopping rules

Re-use v32 source-independent source moment Ridge backend, whose 8 offline known-truth tests passed. For each of the twelve original Group IDs, **hold out every source file from that shoal**, train on other 11 groups, calculate each heldout trial file's MSE then equal-file mean per group, equal-12-group mean across groups. No within-shoal leakage. Short/delayed outcomes are correlated and not 24 independent tests. Abort on mismatch of original 84 files, source SHA/size/clock/NA, grouped fold mapping, G/global v32 baseline or original three Puy-analog source test fixtures. No results are retuned or selected.

Primary *two contrasts* for each future horizon:
A) **Independent local predictive increment beyond global = MSE(GLOBAL)−MSE(NEAR_TRUE)**, per true original group and equal-12 mean. Positive means true nearest three provide predictive value after all-fish mean and fixed geometry; negative means local extra harms forecast.
B) **Original velocity-to-position specificity = MSE(NEAR_ROT1)−MSE(NEAR_TRUE)** on the same heldout group, same predictor dimension, original global preserved. Positive suggests the real local assignment is more predictive than this single fixed surrogate; negative is opposite. If either contrast nonpositive on mean or fewer than **9/12** true original groups positive, DO NOT call a robust positive near-neighbor association; still report all signs.

Secondary prespecified comparisons: **FAR_TRUE vs NEAR_TRUE** = MSE(FAR_TRUE)−MSE(NEAR_TRUE); **NEAR_STALE_0.2S vs NEAR_TRUE** = MSE(NEAR_STALE)−MSE(NEAR_TRUE); **GLOBAL vs FAR_TRUE** = MSE(GLOBAL)−MSE(FAR_TRUE). Report per-group signs and all original file/test-group MSEs. For first two primary contrasts only compute 5000 whole-shoal descriptive bootstrap resamples with seed **20261124**, and no nominal population p (12 fold training sets overlap). No unregistered source/permutation hyperparameter choice after results.

Do not call a local effect if it is not distinguishable from fixed rotation or farthest3. A positive local association conditional on global is still NOT proof of fish-fish causal effect because positions and velocity may reflect common heterogeneous flow, orientation, enclosure and source tracking smoothing. Original time-series need not be online/causal. No individual sound/call source is available, so Boids fish chorus remains hypothetical. Preserve pre-existing v8/v9c precedence and biological caveat.

Original source raw XY, original individual time-series and original future target rows never redistributed to GitHub. All original 84 per-trial hashes and 12 author group IDs preserved in source-safe receipt. PR #248 stays Draft; main untouched.