# v134 penguin prefit analysis — conditional exploratory current–diel test

Recorded after the structural source audit and **before any v134 outcome relationship/model fit**. Source: Gunner et al. (2025), `10.1371/journal.pbio.3002981`; versioned original data `10.6084/m9.figshare.28517873.v1`. The audit found 27 animals, 3,072,835 source records, 26 exact duplicate rows, one 2,582-second gap, and two ISO weeks. These structural facts, published methods and source column definitions are the only data-dependent choices below.

## Scope and estimand

Ask whether local modeled tidal-current speed improves held-out prediction of **observed submergence time share** after clock, solar, individual and spatial controls. Pressure depth is independently measured; neither reconstructed swimming speed, heading-derived travel efficiency nor unavailable prey-pursuit event labels is the response. Submergence is not prey capture, foraging success or energetic benefit.

This is one colony/coast and one species. Nine observed dates / two calendar weeks fail the frozen eight-week confirmatory gate. All estimates are exploratory, conditional on the author-metadata timestamp interpretation and the released current model. No result can establish causal tidal entrainment or global temporal-niche partition.

## Source interpretation and observations

- Read original `Timestamp`, `ID`, `Depth_sm`, `DR_longitude`, `DR_latitude`. Confirm all 26 duplicate keys are exact full-row duplicates before dropping repeated copies; conflicting duplicates are a hard failure. Preserve original bytes, counts and duplicate/gap audit.
- Interpret the naive `Timestamp` as UTC using the repository description of its renamed `DateTime` field; retain this qualification. Repeat the entire analysis after **−3 h and +3 h** shifts of animal timestamps relative to the explicitly GMT current grid. These are predetermined clock sensitivities, not alternative timestamps selected for a better result.
- Aggregate unique observed seconds into non-overlapping source-clock 15-minute bins. Require at least **720 of 900 seconds** with finite depth and coordinates. Do not insert missing seconds or zero behavior. Preserve counts above **2 m** (primary), **1 m** and **5 m** (threshold sensitivities).
- Covariate location and time are the mean recorded longitude/latitude and mean observed timestamp within each bin. This is an explicit 15-minute exposure approximation, not an exact replication of the paper's per-second travel-vector analysis. Retain within-bin geographic ranges so the approximation can be assessed.
- Current `Hours=0` means **2019-11-22 01:00:00 GMT**, and there are 240 hours. Verify every grid node/hour/time key and no nonfinite original current component. Use the original eastward U and northward V values in m/s.
- Spatial interpolation is linear within a Delaunay triangle of the original longitude/latitude grid, without extrapolation. Temporal interpolation is linear between adjacent original hourly U/V outputs (primary). A nearest-hour and a floored-hour alignment are prespecified sensitivities because manuscript and released workflow differ.
- The model has grid nodes with identically zero U/V over all 240 hours. Their interpretation as land is unverified. The conservative primary analysis excludes bins whose interpolation triangle touches **any such node**, and reports the number excluded. A sensitivity retains those original zero nodes. Never describe them as observed slack water.
- At the same original location evaluate current times shifted by **−24, −18, −12, −6, +6, +12, +18, +24 hours**. No wrapping, extrapolation or synthetic periodic extension. Real and all eight wrong-clock models must use exactly the same bins. Use common temporal support across the three timezone interpretations as well, so their comparisons do not silently change the source cohort. Mask sensitivity is separately labeled.

## Models fixed before outcomes

Use a fractional logistic model for each observed share `y = submerged_unique_seconds / observed_unique_seconds`. Optimize cross-entropy with ridge penalty `0.01 * sum(beta_non_intercept^2) / 2`. Continuous features are centered/scaled **using training rows only**; zero-variance columns become zero. The intercept is unpenalized. Training windows are weighted so each training animal has equal total weight. No hyperparameter selection from held-out outcomes.

**M0:** intercept; animal indicators (unseen held-out animal coefficients remain zero); local clock sine/cosine at 24 and 12 h; elapsed days from the fixed current origin; elapsed hours from that animal's first recorded timestamp; observation fraction; longitude, latitude and their quadratic/product terms. Local civil time/week follows UTC−3, with no seasonal offset during the source period. Spatial and trip-time controls reduce straightforward habitat/trip confounding but do not make currents randomized.

**M1:** M0 plus solar elevation sine, positive solar elevation sine and a night indicator (solar center below −0.833°). Use NOAA's documented fractional-year/equation-of-time/declination approximation at the recorded location/time. Over this short period solar geometry and local clock are strongly related; distinguish their incremental prediction from causal light effects.

**M2:** M1 plus modeled speed `sqrt(U^2+V^2)`, speed squared, and speed × night. Each wrong-clock model has exactly these three added features, evaluated at its shifted original model time. This tests the speed pathway; it does not exhaust directional-current navigation mechanisms.

Prespecified penalty sensitivities: **0.001 and 0.1** with the primary endpoint/time/interpolation/mask. Prespecified threshold, clock, hour-alignment and mask sensitivities change one condition at a time; no preferred setting will be chosen after looking at results.

## Holdout, score and uncertainty

Hold out each entire local calendar week; fit on the other week. No individual-minute random split. Report animal overlap between train/test, observed animal counts and night/day coverage in each fold. Since there are only two source weeks and many animals may be new in a held-out week, this tests a mixture of temporal and animal generalization and cannot estimate temporal population uncertainty.

Score held-out fractional cross-entropy, first averaging windows within each animal/week, then animals within week, then the two weeks with equal weight. Report M0, M1, real M2 and every wrong-clock score in nats per observed behavioral trial. Also report Brier-style squared error of the predicted share as a descriptive calibration measure, without pooling unlike scores.

`Delta_solar = L(M0) - L(M1)`; `Delta_current = L(M1) - L(M2)`; `Delta_phase = min_shift L(Mwrong) - L(M2)`. Positive means improvement by the named real model. The best wrong shift is selected on held-out scores as a deliberately strong descriptive comparator; it is **not** an unbiased selected-model performance estimate or a randomization p-value. Give the rank among all nine clocks.

For the primary score differences only, a 2,000-draw animal-cluster bootstrap (seed 134) resamples whole animal IDs and retains each sampled animal's weeks; score aggregation still weights the observed weeks equally. This is a **conditional resampling interval for these fitted folds**, not a refit bootstrap, not uncertainty across independent weeks/coasts, and not a confirmatory confidence interval. Do not manufacture a standard error for meta-analysis from it.

## Output and checks

Save input source SHA256s, aggregation/exclusion counts, matched derived windows, held-out animal/week scores, complete sensitivity results, fold counts and prefit specification SHA256. Derived penguin data can be redistributed only under the verified original license with attribution; restrict output if license validation fails. Test source identity, duplicate conflicts, observed denominator, hour origin, out-of-range/masked interpolation, no train/test week overlap, equal hierarchical scoring and fractional-likelihood derivatives before running the analysis. Inspect results for remaining source contradictions and retain null or wrong-clock-favored results unchanged.
