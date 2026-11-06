# v51: matched bird × destination cell × month × clock comparison

2026-11-06. EXPLORATORY AFTER v50. This protocol is fixed before opening any v51 matched-stratum losses. It is not an independent population confirmation. Base commit: f4915fdd083762639ff626368ff43033a83498b9.

## Question and immutable source
Does v50's larger tidal-phase heading-prediction gain in AHN2-masked destinations survive comparison within the SAME original bird, SAME 2010-selected 2km destination cell, SAME calendar month, and SAME six-hour UTC clock bin?

Reuse v50's original MD5-verified 2010/2011 GPS and original measured RWS NAP source, unchanged v41 full-2010-trained M0/M1 forecasts, and original 2011 test rows. No model refitting on terrain or matched strata. Exactly replay the prior whole-year losses/counts before scoring new matched contrasts. Select the same eight 2km RD cells using 2010 GPS only. Require successful reads of ALL eight AHN2 source tiles; a failed network request is never a missing-height label. Require each source raster SHA256, three-way partition counts, and unadjusted same-bird v50 effect to replay. Do not accept source drift silently. No new patches or clock-offset search.

The AHN2 label concerns historical terrain DATA OBSERVABILITY, NOT measured water, intertidal habitat, exposure or prey. Native GPS clocks are provisionally UTC; the original uncertainty remains.

## Matching fixed before new outcomes
Primary stratum = (bird identifier, destination C's fixed 2km RD cell, B-time year/month, floor(B-time UTC hour/6)). Compare only C_AHN2_VALID versus C_SELECTED_CELL_AHN2_MISSING; outside selected cells are excluded from the matched estimand, but counted in the unchanged whole-cohort replay.

Retain a stratum only if BOTH source groups have at least THREE original episodes. Retain a bird only if it has at least TWO such strata. Use ALL episodes within retained strata; no favorable-row selection or random downsampling. Compute each group's mean M0 and M1 squared-direction loss within each stratum. Weight the SAME retained strata equally within a bird for BOTH groups, then weight birds equally. Thus place/month/clock distributions are identical between groups within each bird, regardless of their unequal episode counts.

Admission: at least THREE retained birds, TWO distinct destination cells, FOUR distinct ISO weeks in EACH group, and at least TWO HUNDRED original episodes per group across retained strata. Report support and attrition even on failure, but do not estimate a primary effect if the gate fails. Never loosen gates or merge bins after seeing results.

Secondary prespecified sensitivity: add actual ebb/flood sign at B to the stratum key, retaining the SAME thresholds and weighting. This additionally standardizes phase composition; it is not independent replication and cannot replace the primary result if favorable.

## Estimands
Let L_g,m be equal-bird/equal-within-bird-stratum mean loss for source group g and model m. R_g = 1 - L_g,1/L_g,0. Primary D = R_masked - R_valid. Positive means larger relative PREDICTIVE improvement in the masked source domain, not a stronger biological causal effect. Resample whole birds, carrying all four paired loss columns together, 10,000 times with seed 20261106; recompute ratios of means per draw. Report matched point and percentile interval, sample counts, positive-bird counts, and leave-one-bird-out D range. Five birds can yield unstable intervals; do not call weeks independent populations.

Secondary absolute-error contrast A = (L_masked,0-L_masked,1) - (L_valid,0-L_valid,1), using the same loss units/weights and paired bootstrap. This checks whether the relative comparison is dominated by unequal baseline denominators. No weekly confidence interval is substituted for the equal-bird estimand.

Run BOTH islands. Report primary and phase-conditioned sensitivity even when negative, inconclusive or NOT_ADMITTED. Conditioning on the observed destination is descriptive outcome-domain analysis, not causal habitat selection. Residual subcell location, activity state, serial correlation, historical survey date, source auxiliary-band semantics and GPS/gauge uncertainty remain.

## Implementation / verification plan
1. Add a pure NumPy matching/scoring module and regression tests: synthetic composition-only contrast disappears after matching, true within-stratum contrast survives, asymmetric strata are excluded, low support stops, paired weights and empty groups are checked, optional phase matching is exact.
2. Add a source runner importing existing functions unchanged; replay v43 full forecasts, v50 partitions and same-bird contrast; verify all eight raster hashes; compute matching on in-memory source rows only.
3. Run local synthetic tests before committing executable workflow; run one serialized two-island GitHub Actions source evaluation. Do not trigger a second duplicate field run from PR creation.
4. Save only aggregate JSON, source hashes, tests and an honest result document. Never publish original bird IDs, GPS positions/timestamps, tile coordinates, or raw tide/DTM values. Leave existing evidence and main unchanged.
