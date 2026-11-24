# v30 frozen protocol — fully harmonized 3-taxon fish movement age forecast

**Frozen 2026-11-24 JST before ANY v30 original heldout future-velocity outcome values.** v24–v29 original-source results are already known, so this is a source-locked **post-earlier-results harmonization sensitivity test**, NOT a newly independent test of a previously unknown ecological effect.

## Primary question

Earlier Puy (black neon tetra), Niizato (ayu) and MacGregor (stickleback) whole-recording source tests suggested the benefit of other-fish CURRENT directional movement over aged movement differed among taxa. But each source used a different focal/geometric feature set, native recent-velocity intervals and future delayed target. v30 holds all these *physical measurement definitions identical* across all three ORIGINAL datasets. Do the age-predictive-retention curves still differ, and is age=0 always the best predictive group vector under this shared, retrospectively fitted supervised model?

Three source-specific numerical models are trained/evaluated independently; **no cross-species transport of coefficients**, no standardized species pooling and no genuine cross-taxon population meta-analysis. Original study/sampling biases remain.

## Exact biological sources and admission

- Puy et al. 2024 black neon tetra: original six 8-fish 50fps source recordings, Zenodo 10890112, all source provider MD5 reverified BEFORE any XY opened; original author pixels→centimeters unchanged. Source filename and original native Time [frame] strictly validated at all used rows (no interpolation or repaired frames).
- Niizato et al. 2024 ayu: exact published seven 10-fish 30fps original TXT at Git commit 158e8d7ebdef73752da63192ee36e3a099dd5dfa, every Git blob SHA/byte size checked BEFORE original XY opened; original source column X3:12 / Y13:22, original frame/rounded time crosscheck; native coordinate units UNKNOWN.
- MacGregor & Ioannou 2021 stickleback: exact 3 PRESELECTED native 25fps eight-fish EIDC files 01.txt,02.txt,105.txt with source SHA256/byte sizes from v26 source gate; original first16 alternating XY (source header x.1,x.9,...x.16), last 17th column literal frame, missing original XY NA. The original 84 filenames are NOT mapped to 12 fish shoals, so three file tests CANNOT be called three independent shoals. [Source identity #249](https://github.com/zuizui0223/boids/issues/249) remains unresolved.

## Predeclared universal physical model

For any ORIGINAL source with native FPS F∈{50,30,25}, use fixed **0.2s velocity estimation window** = F/5 frames: s=10/6/5 for tetra/ayu/stickleback, and native group-state ages **ell={0,0.2,0.4,1.0,2.0}s** → frame offsets respectively (0,10,20,50,100), (0,6,12,30,60), (0,5,10,25,50). All frame offsets integral; no interpolation and no extra rounding.

Candidate source cohort time IDs t start at 2.2s original file onset, stride EXACT 0.2s, and stop before future t+0.8s. In native frame units, starting t0=110/66/55, strides=10/6/5; require entire **same** set of past timestamps t−(2.0+0.2), t−(1+.2), t−(.4+.2), t−(.2+.2), t−.4, t−.2,t and future t+.2,t+.6,t+.8 with ALL fish native XY finite, original frame ID differences exactly equal native frame offsets. This ensures no predictor/response-specific missing-row subsets; allow ONLY the stated listwise finite filter, never fill NA or use an original future time as predictor. Source target horizon t+0.6 to +0.8 is matched across all source taxa (unlike original v24 .5–.7).

At each t, for every focal fish i, define native G_i(t) with identical 14 numeric covariates in each source: current position XY (2), focal current 0.2s velocity (2), focal previous 0.2s velocity [t−.4,t−.2] (2), current minus previous velocity as finite-difference acceleration proxy (2), own speed (1), current school centroid minus focal position (2), focal→3 nearest fish *mean displacement* (2), and mean distance to the current 3 nearest fish (1). No tank-wall covariates, taxa indicator, fish ID or absolute age/sex; source-specific original coordinate units retained, training-only z-score handles dimension. Group size 8/10 is recorded but not used as a per-fish predictor. Nearest three purely geometry, NOT velocity.

Define same additional 2-vector for each group age ell:
R_i(t;ell)=mean_{j≠i} v_j(t−ell) − v_i(t),
where v_j is the exact same 0.2s backward original velocity, and **focal subtraction is ALWAYS current v_i(t)** even in stale arms. G is bitwise identical across all age arms, group-state vector direction retained; scalar speed-only panel not used. Exactly six model panels = G-only + FIVE fixed group age levels.

Two response outcomes share EXACT SAME test fish/time rows and training files: (short) future mean velocity [t,t+0.2]/0.2; (delayed) future mean velocity [t+0.6,t+0.8]/0.2. Both are original XY units/s, in source-native physical scale (Puy cm/s, Niizato unknown source units/s, stickleback pixels/s). Never compare or pool absolute source MSE. The 4 response coordinates can be stacked in a multi-response linear Ridge fit since identical train/test rows and alpha apply to all four.

**Fitting**: StandardScaler on training source FILES only, fixed Ridge(alpha=10) multi-response 4D, source-specific leave-one-original-FILE-out, use each fish×frame row in the test original file once to score equal-coordinate 2D MSE for each horizon. No cross-species training, label-dependent filtering, hyperparameter tuning, output-based source selection, or test-file leakage into scaling or fitting. Publish file-level and equal-FILE mean outcomes, all sign counts; no bootstraps claiming independent schools/populations (only 3 MacGregor files).

## Frozen tests and decision criteria

For each taxon/horizon define G-only MSE_B and age0 MSE_0. If MSE_B <= MSE_0 (no positive incremental group gain), report normalised I(ell) as NOT_DEFINED, retaining raw signed MSE contrasts. Else report normalized incremental retention
I(ell)=[MSE_B−MSE_ell]/[MSE_B−MSE_0] for ell≥0 (I(0)=1). Negative values allowed. Give all five age MSEs and age-specific equal-file sign counts for age ell MSE minus age0 MSE. First sampled age ell in {.2,.4,1,2} at which I≤0.5 is a **discrete sampled threshold**, not a measured animal neural half-life; no continuous interpolation.

Primary methodological test: with same G/velocity/target, is current group velocity better than 0.2s-old velocity in **each** of the three original taxon sources? Report yes/no and each recording sign. Secondary: is stickleback I(.2) higher than BOTH tetra and ayu for both horizons? Report any failure, do not change cohort/age/model. Even if supported, cross-source differences may reflect source tracking/autocorrelation, food context, missingness, original test school overlap, environmental common drivers or camera filters. Original observed previously reported age0.2 retention from v24/v26d is background only and NOT an immutable numerical target for v30 because model/horizon/cohort changed by design.

## Interpretability/causal limits

This is a new common-spec **retrospective prediction**, not experimentally demonstrated Reynolds Boids fish-fish force. A common time-varying external driver, upstream future-symmetric video tracking, positional constraints and focal-source observation noise can generate current>stale and taxa differences with **zero active fish influence**. No time-aligned individual acoustic calls in any source. The source verified MacGregor EIDC three files remain **not known independent shoals** and 3 original species do not support population-wide ecological universal conclusions.

Original-source samples may be large, so source numeric runs may optimize linear regression algebra but may NOT change source row cohort, coefficients, alpha, features, target, coordinate frame or normalization. All results including null/adverse retained. PR #248 stays Draft, main unchanged.
