# v44 — PRE-OUTCOME matched-episode tidal speed versus next-heading information

**2026-11-05 JST, fixed BEFORE opening any v44 joint-episode scores.** Existing original speed results v32–v40 and original heading results v41/v43 have already been opened, including positive v43 2011 direction results in both Wadden islands. This is therefore **post-result EXPLORATORY** for the same species/animals, not a new independently confirmatory study.

## Question and comparability

Does the same measured tide ebb/flood phase provide additional heldout predictive information for (i) the next **horizontal GPS displacement speed** and (ii) the next **horizontal unit displacement direction**, on the EXACT SAME original three-fix bird movement episodes, beyond the exact same historical bird-specific heading, prior speed, tide height, location, time of day and season?

In previous studies speed models often included stationary intervals; direction models required ≥0.4 km/h, resulting in noncomparable cohorts. This study **must preserve the v41/v43 original 3-fix direction inclusion gate for BOTH outcomes**. Therefore it cannot be construed as a representative all-activity speed effect. This explicitly tests moving three-fix source opportunities only.

## Frozen site/year source admission

- Two original Zenodo O_SCHIERMONNIKOOG v5 and O_AMELAND v6 original GPS annual gzip, publisher MD5 pinned for 2010/11/12; independent SHA256 calculated; actual original local RWS WATHTE meting in cm above NAP, fixed UTC+01 all seasons at `schiermonnikoog.waddenzee` and `ameland.nes`.
- Source three consecutive **original** GPS fixes A,B,C; one earliest original visible fix per UTC hour/individual, both original A→B and B→C steps in 30–120min, 0.4–120km/h, original site frozen geographic envelope, genuine source timestamps and valid source measured tide phase at B using trailing 20min gradient ±0.012m/h. **Import v41 source parser unchanged** and attach B→C speed from the same earliest-in-hour original GPS fix pairs by exact original bird+time keys. Fail hard if any v41 source-qualified row cannot be uniquely matched to original same B→C start+next fix (including target heading consistency). Do not silently discard unmatched rows, change eligibility, or use interpolated GPS fixes.
- Native GPS source timestamp UTC-vs-GPS unresolved. Primary interpret native source time as UTC (0s). Secondary fixed -15 seconds; note GPS−UTC changes to 16s July 1, 2012. No clock search or outcome-driven choice.
- Two temporal holdouts **per island**, ALL eligible birds included: **(A) train 2010 → test 2011**, and **(B) train 2010+2011 → test 2012**. All 2010–2012 outcomes have previously been examined in different representations; these are internally heldout fits, not untouched source populations.
- Pre-frozen gate separately for every (site, heldout year, clock): ≥1,000 original training *and* testing three-fix episodes, ≥3 original test birds and ≥4 independently sampled test ISO weeks. If source fails, **NOT_ADMITTED**, no outcome for either axis. In particular Schiermonnikoog 2012 had 869 source-valid headings at v41 and is expected to fail; do not lower the threshold or report same-row speed-only gain as though its direction were evaluable.

## Exact common models, endpoints and scoring

At middle fix B, the source site location, absolute observed water height h(B), h(B)², daily/annual clocks, private A→B unit east/north heading and log1p(A→B km/h) are baseline **M0** features. **M1** adds measured falling/rising phase(B) coded -1/+1 and its interaction with h(B). No additional predictors, species-specific hyperparameters, frequency bin re-selection, social other-bird information, or any lag scan.

- Import original v41 `vector(row, level)`, use train-only feature mean/SD, training bird-equal total weights, fixed ridge L2=10 with unpenalized intercept.
- Predict **three outcomes** from the exact same X design/weights: target next log1p(B→C horizontal km/h), and the target next east/north unit vector from original B→C. Future C and any `target_*` field must never influence features.
- For speed scalar: squared error `(truth−predicted)^2`. For direction: half squared unit-vector error `0.5*((trueEast−predEast)^2+(trueNorth−predNorth)^2)`. The absolute MSEs have different physical/metric units, and must not be directly subtracted or quantitatively equated.
- Within each response, equal-weight over birds of per-bird average heldout loss; M0 and M1 are assessed on exactly the same bird episodes. Define fractional error reduction `R_axis=(MSE0_axis−MSE1_axis)/MSE0_axis`. Primary comparison **paired relative-skill difference** `D=R_direction−R_speed` on exact same original test rows. A positive D means a greater *fraction of that axis's own baseline prediction error* was removed by phase, **not** stronger causal steering or ecological selection.
- For each axis and D: retain paired per-test-bird means of all 4 error columns (speed M0/M1, direction M0/M1), resample whole birds **10,000** times with fixed seed 20261105, recompute ratio-of-means for each draw and report matching equal-bird 95% percentile bootstrap. Separately compute equal-week-then-present-bird averages of those 4 errors, then 4,000 whole-week resamples and **separate matching week-point values**. Do NOT put a week bootstrap CI around a pooled-bird point.
- Report positive-bird and positive-week counts for each axis, sample size, original checksum and tide gauge counts, same episode guarantee, and v41 heading forecast replay `np.allclose` on same source rows within ≤1e−9 for both models. Never silently omit an unfavorable clock scenario/year/site.
- **No original GPS bird identifiers, raw coordinates, exact timestamps or RWS tide time series committed to GitHub**, only aggregated source receipts and scores.

## Interpretation guards

Positive R_direction or speed is evidence of tide-state-associated **predictive information** on moving 3-fix segments. D>0 is a relative predictive axis gap conditional on the different losses and baseline skill, **not a directly comparable biological effect size**, let alone proof tide “causes direction more than speed.” A null or negative D does not undo previous v32/v39/v40/v41/v43 source-backed positives under their own cohorts. One taxon/two nearby islands, shared historical observations; original GPS clock, gauge-to-local-water travel, mudflat elevation, prey/feeding state, and actual social forces remain unknown. Prior v47 same-location/tide-phase sham explained most apparent neighbor alignment; do not assert social Boids as verified.

This stage contains no exposed-mudflat GPS join; independent 2014 Dryad NAP LiDAR coastline download was HTTP 401 (v42), so front tracking remains a mathematical hypothesis. No selection of future model based on this test's direction or significance.
