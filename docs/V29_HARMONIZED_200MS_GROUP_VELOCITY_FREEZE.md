# v29 preregistration — harmonize original fish group-state velocity averaging to exactly 0.2 seconds

**2026-11-24 JST; frozen before any new v29 original source C(age) scores.** The v27 original measured source-specific group-speed vectors used **different temporal differencing windows**: Puy 5/50=0.1s, Niizato 3/30=0.1s, MacGregor stickleback 5/25=0.2s. The longer stickleback window can smooth higher-frequency motion, potentially increasing apparent raw group velocity autocorrelation. v27's stickleback highest source-level C therefore did **not** directly control measurement-window length. Do not retroactively erase v27; label its cross-source rank *native-pipeline conditional*.

## Frozen strictly common physical speed measurement

For ALL three published original datasets, define group velocity from the **same 0.2-second native source difference**:
\[
U^{(0.2)}(t)=\frac{1}{N}\sum_i [XY_i(t)-XY_i(t-0.2)]/0.2.
\]
Frame supports: Puy 10 frames at 50fps, Niizato 6 frames at 30fps, stickleback 5 frames at 25fps. Compute centered 2D vector Pearson/cosine correlation between U(t) and U(t-age) on exactly the same original source time roster, for ages **0.2, 1 and 2 seconds** (respectively 10/50/100, 6/30/60, and 5/25/50 frames). Use **zero smoothing or interpolation beyond original published source**, and never use later original frame for a past predictor.

All ORIGINAL cohorts identical to source-verified v27:
- Puy six original 8-fish Zenodo CSV files, provider MD5, v8 original_indices fixed current+2s source support. Min t allows t−100−10=0.
- Niizato seven original 10-ayu TXT files, author-pinned commit and 7 Git source blobs, v24 t>=66 source roster. Min t−60−6=0.
- EIDC stickleback three original files 01,02,105, SHA256 locked; v26d roster 6,966 / 8,015 / 5,567 source group times, native last-frame +1 and NO original fish NA imputation; t>=55 supports t−50−5=0. School identities still unknown.

All original source X/Y and test group time indices must match frozen original source. Stop on any provider checksum, native 0.2sec integer frame, source case, group roster, nonfinite data or trivial variance mismatch. Report per original *file* and equal-file study mean of each C(age), source C_native(original v27) shown separately as previous *methodologically non-harmonized* estimates, not new fish biology. Never fit any fish future velocity target, causal force, social transfer or fish vocal effects.

## Locked diagnostic comparisons

1. **Primary:** does harmonized stickleback C(0.2s) still exceed harmonized Puy **and** Niizato C(0.2s)? If no, state that v27 apparent stickleback persistence rank was **NOT robust to common measurement interval**, not a universal taxon effect.
2. **Secondary:** at ages 1 and 2s, compare study-level C order. A qualitative consistent ranking is descriptive only; no direct inference of species difference with 3 studies, source smoothing, contexts, environments and stickleback repeated group IDs unknown.
3. The original v24/v26d future velocity age-retention I used source-specific current self/geometries and prediction intervals; harmonizing this C curve does **not** also harmonize I. Do not retroactively claim cross-source I is fully adjusted for frame-rate and sampling differences.

Explicit null: an autocorrelated common environmental drive can cause all group autocorrelation patterns with no fish-fish social influence. **A v29 support result is only a source-specific movement-persistence result**, not information transfer or acoustic chorus.
PR #248 remains Draft and main unchanged.
