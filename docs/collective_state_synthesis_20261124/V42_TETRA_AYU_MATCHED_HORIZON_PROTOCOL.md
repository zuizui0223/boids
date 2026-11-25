# v42 protocol — cross-source replication of forecast-horizon dependence of proximity vs information age

2026-11-24 JST. Frozen after the exploratory 12-shoal stickleback result, BEFORE opening any v42 outcome. Tetra and ayu were already analyzed in v5–v30 for related but different endpoints; this is a new same-source retrospective endpoint, NOT untouched independent confirmation. No new species or experimental manipulation is implied.

## Sources and frozen cohort

- Puy et al. 2024 original Zenodo 10890112, six 8-fish recordings at 50fps, exact provider MD5/bytes plus v28 recorded SHA256 for all six; names and per-recording source cohort match v30.
- Niizato et al. 2024 original Git repo at 158e8d7ebdef73752da63192ee36e3a099dd5dfa, all seven 10-fish files and original Git blob SHA1/size, native 30fps, same v30 cohort.
- No replacement recordings, interpolation or new time masks. Whole recording leave-one-out, training file only StandardScaler, Ridge alpha=10, equal recording weights. Source authors' distinct biological shoal IDs for these two studies are not established, so 6 and 7 files are NOT declared independent shoals. No cross-study pooling of native MSE or nominal p-values.
- Reuse v30 G14, 0.2s velocity differencing, exact common eligible source times, short future 0–0.2s and delayed 0.6–0.8s. Require per-file count and source G/GLOBAL equal-file MSE match to v30 within 1e-6 relative + 1e-8 absolute before admitting additional outcomes. Source gate failure is not a null effect.

## Six frozen matched models (v33 analog)

G_geometry (14), GLOBAL (G + current mean all other N−1 fish velocity minus focal current velocity), NEAR_TRUE (GLOBAL + current nearest-three velocity mean minus all-other mean), FAR_TRUE (same for farthest-three), NEAR_ROT1 (one fixed cyclic assignment of other-fish velocities onto other-fish positions in original fish index order, preserves exact multiset and global average), NEAR_STALE_0.2S (current nearest IDs, 0.2s old velocities minus 0.2s old all-other mean; current G and GLOBAL unchanged). All same support/Y. N=8 or 10, nearest/farthest 3 unchanged, no thresholds selected postoutcome. Note different group size changes the fraction of neighbors, and position ties follow the existing NumPy ranking.

## Registered contrasts and result gates

For each file and future window: D=loss(GLOBAL)−loss(NEAR_TRUE); report all signed MSE contrasts incl near vs far, near vs rotated, near vs stale. Primary first gate: D>0 for every original file in BOTH horizons, otherwise report signed gains, ratio-of-means only when mean D>0, all-file mean within-file ratios and paired ratio test NOT ADMITTED. No dropping nonpositive-denominator files or assigning arbitrary ratio.
When admitted, for each file define Qdist=(loss(FAR_TRUE)−loss(NEAR_TRUE))/D, Qage=(loss(NEAR_STALE_0.2S)−loss(NEAR_TRUE))/D, Qmap=(loss(NEAR_ROT1)−loss(NEAR_TRUE))/D. Report every file and equal-file means, 1−Q retention, ratio-of-means separately. Q may be negative or >1; no clipping.
Primary joint descriptive replication: within same original file, delayed minus short Qdist<0 AND delayed minus short Qage>0. Report number with both signs, each mean contrast, and source-recording resampling intervals (10000 draws seed 20261124; descriptive ONLY). Support label for a study requires both average signs predicted AND >=5/6 tetra or >=6/7 ayu individual files both predicted. Stronger original all-12 stickleback result reported separately. Otherwise retain nonreplication; do not rescue by horizon, distance, lag or alternate denominator.
Secondary: delayed minus short Qmap, and Qmap greater than Qdist and Qage in each window; full signed results. Different controls alter different structures, not equivalent interventions, causal percentages or physical signal propagation. Shared spatial external field, tracking smoothing, group size and study-specific environments remain rival explanations.

Execution: exact original source workflow, synthetic parity tests against original v33 for 8 fish, 10-fish nonself/disjoint and rotation/age checks. Outcome JSON retains source identities/hashes, all source-level scores/contrasts, source QA, no raw XY or future target arrays. No main merge. No new biological finding until original source runs and numerical gate completed.
