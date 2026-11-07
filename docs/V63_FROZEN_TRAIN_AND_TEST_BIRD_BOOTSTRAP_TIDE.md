# v63 — Training-bird uncertainty for the already-positive Schier real tidal-heading result

**Frozen 2026-11-07 JST BEFORE opening any v63 training-resample or leave-one-training-bird scores.** Based on v62's previously examined original data and positive T=+0.17641912034715593 on all 211 observed opposite-phase GPS pairs, and T=+0.03815442590078731 on the pre-established seven-bird/204-pair source-supported subset. This is **post-result exploratory uncertainty analysis on the same historical animals**, not a fresh independent experiment. Preserve v59–v62 analyses, thresholds and outcomes unaltered.

## Scientific gap

The v62 "whole-bird 95%" intervals resample the **2011 evaluation birds** while holding the **2010 fitted coefficients fixed**. The latter come from just **8 different 2010 Schiermonnikoog source birds / 1,508 three-fix movements** after excluding every literal 2011 evaluation identity. If training-bird variation changes predicted phase-difference direction, test-only intervals can exaggerate certainty.

**Question:** Does the genuinely observed 2011 rising-minus-falling next-heading difference align with the 2010 source-learned phase direction *after propagating uncertainty in which source birds supplied that directional rule*?

## Frozen source and original checks (no tuning)

- Original Zenodo Schier GPS original provider MD5/pinned SHA256: 2010 **7,911 source three-fix movements from 21 bird IDs**, 2011 **4,948 original three-fix movements from 13 IDs**. Original official RWS `schiermonnikoog.waddenzee` WATHTE NAP measured 2009–2011 each **52,561** readings. Use unchanged `load_site('schiermonnikoog')` to reproduce previously published full-source heading model.
- Exactly reproduce v59/v61 pre-registered, response-unseen 2011 same-bird, same native B 1km cell, measured opposite tide-phase matching and seven sequential source admission counts **[1784,1294,1276,969,572,277,248]**, **211 distinct real paired episodes**, **10 original birds with pairs**, **7 birds with >=10 pairs**, **204 pairs among those 7**, **45 weeks**, **12 months**. All strict source gates must pass before reading B→C next-heading labels or fitting the v63 analysis.
- Remove from 2010 all 2011 evaluation literal bird IDs, keeping exactly **8 source birds / 1,508 training trips**, **zero literal training/test identity overlap**. Do not replace with a within-bird row bootstrap or restore omitted training birds.
- Reproduce old full-training v61 primary T=**0.22867885497020074** exactly within 1e-9 and old identity-disjoint fixed-training v62 primary T=**0.17641912034715593** and separately source-qualified T=**0.03815442590078731**, each within 1e-9. Do not change v41 lambda=10 weighted ridge, fixed features, per-fit training-only scaling, GPS timing, phase threshold, geographic alignment, matching, or any 2011 animal/episode.

## Frozen estimator and re-fit variation

Use v60's exact same real two-GPS-outcome paired primary:
`T_pair = ((y_real_rising - y_real_falling) · g_model) / 4`,
where `g_model` is the average of the difference between predicted *unit* next-direction vectors at each of the two **actually observed** B covariate states when the same trained model is given rising vs falling phase. The model-input sign contrast only defines a comparison direction; the `y` vectors are *two real observed separate 2011 animal movements*. T is in [-1,+1] and **does not identify causal tidal steering**.

Freeze **B=1,024** source-bird cluster bootstrap draws using independent NumPy PCG64 RNG seed **20261107**. In each draw sample **8 of the original 8 distinct 2010 source birds with replacement**; include all original 2010 source rows for each sampled block. If a source bird appears in several draw slots, clone that bird's entire block into distinct, ephemeral **pseudobird IDs by draw slot** so that the unchanged v41 `forecast` correctly assigns equal mass to every sampled bird block, rather than letting repeated blocks silently merge into one original ID. Re-fit **once per draw** with the unchanged weighted ridge lambda 10 and **training-only** mean/SD; no 2011 outcome/identity enters refitting. Predict both signs for all 422 real 2011 B endpoints of the same 211 frozen pairs, without fitting on those endpoints. No data-dependent resampling exclusions and no favorable parameter selection. If a predicted norm is <=1e−10 or nonfinite for a draw, hard `ESTIMAND_STOP`: do **not** remove unlucky draws or produce a positive figure.

Primary two uncertainty distributions (both computed on **the same fixed 211 genuinely observed GPS pairs**):
1. **Train-only uncertainty:** for each source-bird resampled model, compute T for all source-matched pairs and average by the *ten original 2011 matched birds equally*, without resampling test birds. Report across 1,024 re-fits mean, median, 2.5/97.5 percentiles, fraction positive, min/max.
2. **Train-and-test uncertainty (primary v63 admission decision):** in each of the same 1,024 re-fits, independently draw **ten matched 2011 birds with replacement**, average that bootstrap's resampled bird-wise mean T (8 and 10 are distinct train/test sample counts), and report mean, median, percentile 95%, fraction positive. Test-bird resampling uses a **separate NumPy PCG64 stream with seed 20261108**, never a row/pair bootstrap.
3. **Pre-existing source-qualified sensitivity:** repeat both distributions at each same training re-fit restricted to the **same seven 2011 birds with >=10 original v59 matches and their same 204 pairs**. For nested test uncertainty independently draw seven test birds, with PCG64 seed **20261109**, one draw per same source-model re-fit. This is pre-existing source-only subset, NOT outcome-selected, and is **secondary, not substituted for all-pair primary**.
4. **Leave-one-training-bird-out stress check:** train eight additional models, each excluding exactly one of the 8 2010 source birds (7 training source birds, no 2011 overlap) and score same fixed 211 and 204 pairs; report 8 anonymous T values summarized as min/max/mean and number positive, **never list original source IDs or bird-specific outputs**. No confidence interval or automatic override from these eight nonindependent runs.

Confidence intervals here are empirical **cluster bootstrap percentiles** from only eight source birds and ten/seven test birds, with fixed matched field outcomes; they do not represent new wildlife replication, hydrodynamic tide intervention, or independent model discovery. Values over draws are correlated; do not claim 1,024 biological replicates.

## Fixed interpretation and status

Primary v63 training-uncertainty-robust positive **ONLY IF** the all-211 original pair equal-bird T still replays positive and the **train-and-test 95% lower percentile is >0**. If it crosses 0, label `TRAINING_UNCERTAINTY_POSITIVE_NOT_ESTABLISHED` regardless of train-only, source-qualified or leave-one-out positivity. If the 204-pair source-qualified secondary 95% lower >0, report separately; if not, explicitly note that lack of robustness. Do not discard prior v62 positive conditional result or reweight bird data.

Do not call any bootstrap interval a confidence interval for tide causation. No social Boids forces, exposed prey-front, local hydrodynamic velocity, other species, multi-taxon niche differentiation, or 3D motor coefficients are tested here. Historical source GPS native UTC-vs-GPS clock and local tidal phase lag remain uncertain.

## Safe execution and artifacts

New immutable source spec here, and implementation/tests in `validation_v63` only. Dedicated GitHub Actions original field run stores only aggregate bootstrap distributions, source checksum/replay receipts and sampled counts. **Never persist original bird IDs, raw coordinates, exact time, per-pair GPS/next directions, per-bird scores, raw station time series, bootstrap pseudobird IDs, or original source fitted coefficients.** Existing v59–v62 code/PRs untouched. Draft PR stacked on v62; main unchanged. Report both favorable and unfavorable outcomes.