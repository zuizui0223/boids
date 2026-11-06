# v52: tide-related next-heading prediction — bearing change or vector-magnitude change?

**Frozen 2026-11-06 before any v52 angular/decomposition result.** Previous v43–v51 outputs are known. This is a post-result exploratory interpretation audit on the same historical oystercatcher cohorts, NOT independent field confirmation. Base commit: `23290eb35e1945265d6b85235708c105fbdd5bed` (v51).

## Question and alternatives
Return to the central tide-direction finding rather than extend the AHN2 missingness branch. The existing unconstrained 2D ridge predictor outputs a vector, not necessarily a unit direction. Its half-squared-vector error can improve through a better bearing, a changed magnitude, or both. A change of magnitude is NOT movement speed: the training targets are unit displacement vectors. It is also not automatically a calibrated concentration estimate, particularly when the fitted norm exceeds one.

Alternatives considered: extend terrain-mask matching; add nonlinear spatial baselines; inspect the original directional loss. This stage chooses the last because a claim about steering first needs direct evidence about angle, not only vector squared loss. No new predictors, outcome-dependent thresholds, tidal lag scans or habitat labels are introduced.

## Identical source, models and original-result replay
Use original publisher-MD5-verified 2010/2011 Zenodo `O_SCHIERMONNIKOOG` and `O_AMELAND` annual GPS files, frozen native-time-as-UTC primary convention, original local RWS measured `WATHTE meting` cm/NAP at `schiermonnikoog.waddenzee` and `ameland.nes`, fixed source UTC+01 and trailing 20-minute phase. Import v41 `original_three_fix_heading_episodes` and `forecast` unchanged. Same source first fix per hour, both A→B and B→C intervals 0.5–2 h and both horizontal speeds 0.4–120 km/h. No AHN2 filtering or new raster downloads.

Fit ALL admitted 2010 source triples and predict ALL admitted 2011 triples separately by site. Same M0 (water height and square, B location, daily/annual clock, own previous direction and log speed) and M1 (adds actual phase and phase×height), train-only standardization, equal-source-bird training weights, ridge lambda 10.

Mandatory pre-analysis replay to absolute 1e-9:
- Schier: 7,911 training rows, 4,948 test rows, 13 test birds; M0 = 0.4491437063035975 and M1 = 0.41370693859833235.
- Ameland: 3,753 training rows, 4,678 test rows, 5 test birds; M0 = 0.5107931836556263 and M1 = 0.43464618382116776.

Use exactly the same predicted vectors for every new endpoint. Preserve original GPS checksums and source water counts; never export raw bird IDs, coordinates, exact times or tracks. Source failure is not a negative biological result.

## Predeclared primary: length-normalized angular forecast
For observed unit direction y and model predictions m0,m1, let rj=||mj|| and uj=mj/rj. The PRIMARY outcome is paired improvement in cosine loss:

`G_cos = (1-y·u0) - (1-y·u1)`.

Positive means the predicted bearing itself is more accurate after tide-phase augmentation. Also report mean absolute wrapped angular error in degrees for each model and its paired improvement, using `atan2(abs(cross(y,u)), dot(y,u))` on [0,pi]. Degrees refer to one-step GPS displacement bearing error, NOT a physical bird turning angle caused by tide.

Require finite Nx2 arrays and observed unit norms within 1e-8. If either predicted norm is <=1e-12 for ANY row, report the original vector losses and mark angular attribution NOT_ADMITTED_UNDEFINED_BEARING; do not drop rows or invent a direction. Do not threshold on prediction confidence, select only highly directional birds, normalize observed mistakes, or tune model coefficients. Report prediction norm quantiles and count >1 rather than clipping them silently.

## Exact secondary decomposition, not a causal effect decomposition
Original per-row loss `L(r,u)=0.5||y-r*u||^2`. Compute all four hybrids L(r0,u0), L(r0,u1), L(r1,u0), L(r1,u1). Allocate the difference symmetrically:

`G_bearing = 0.5*((L00-L01)+(L10-L11))`

`G_magnitude = 0.5*((L00-L10)+(L01-L11))`.

Their sum must equal `L00-L11` for EVERY source row and every aggregate, to 1e-10. This is algebraic attribution between two fitted forecasts; it does not identify an intervention on actual tide or an animal steering force. Components can be negative or exceed the total; do not force a 0–100% biological attribution. The reference sample-statistics distinction between mean direction and mean resultant length is documented by SciPy `directional_stats` (https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.directional_stats.html); unconstrained regression norms are not equivalent to calibrated sample resultant lengths.

## Weighting, uncertainty and scope
For each site report paired mean gains for original vector loss, cosine loss, absolute angular error, bearing component and magnitude component. Primary is equal test bird, averaging all source rows within bird first; 10,000 paired whole-bird bootstrap draws, fixed seed 20261106. Separately summarize equal-week-then-present-bird means with 4,000 paired whole-week bootstrap draws. Do not use a weekly CI around a pooled-bird mean. Both axes/components share resampled clusters so the identity holds under resampling. Report positive-bird/positive-week counts. With 5 Ameland test birds, bootstrap uncertainty is descriptive conditional on this cohort, not population-wide or serial-dependence-proof inference. Tests are exploratory and multiple related endpoints are not independent confirmations.

## Execution plan and verification
1. Implement pure loss decomposition and paired cluster summaries test-first. Known-truth tests must distinguish magnitude-only from bearing-only improvements; verify scale invariance of cosine/degree metrics, exact four-hybrid identity, wrap-around, zero/NaN rejection and unequal bird/week weighting.
2. Add an original-source runner importing unchanged v41 functions, checking MD5, year split, counts and full v43 replay before new angular results.
3. Run the new pure tests and inherited v41/v43/v50 suites; report scoped test counts, not a full-repository claim. Execute both source sites once in a serialized workflow; preserve aggregate JSON.
4. Report both positive and null outcomes; save an integrated Japanese interpretation and mathematical bridge to an environmental directional policy, explicitly not physical acceleration or social Boids interaction.

A positive angular result supports tide-conditioned directional predictability beyond prior movement and simple spatiotemporal controls. It still does not establish local exposed-prey front tracking, behavioral state, a uniquely identified environmental force, cross-species generality or causal tide response. Previous source-mask limitations and all earlier positive results remain archived unchanged.
