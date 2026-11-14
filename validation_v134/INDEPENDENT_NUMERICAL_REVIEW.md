# Independent scientific and numerical review — v134 penguin analysis

**Verdict: no P0/P1 implementation bug or contradiction with the stated exploratory interpretation found in the reviewed snapshot.** The original shared-mask mutation is fixed and covered by a passing regression test. Scientific interpretation depends on retaining the limitations below; the result does not establish useful tide-specific prediction, nor does it establish absence of a tidal effect.

Reviewed the v131 frozen protocol, v134 IPD specification, prefit specification, postfit log, both penguin implementation modules, tests, saved results/derived inputs, original penguin/current CSVs, source minute table, and author workflow/metadata. No project files were edited. Final narrative report was not yet reviewed.

## Scientifically consequential qualifications

1. **Relative improvement is not demonstrated predictive utility.** Primary animal→week weighted cross-entropies are M0 0.804310, M1 0.808294, real M2 0.771751, best shifted current (−12 h) 0.770989. Thus Δcurrent=+0.036543 but Δphase=−0.000761; real current ranks third of nine. Every primary fitted model performs worse than fixed p=0.5 (0.693147) and training-only animal-balanced prevalence (0.706177). Both comparators belong beside the headline delta. Adding them as explicitly postfit diagnostics is appropriate and does not change the frozen models.

2. **The shifted speed controls have weak ability to distinguish the real clock.** Across the exact 3,334 primary bins, real versus −6/+6 h modeled speed has Pearson r=0.99136/0.99164; −12/+12 h has r=0.96592/0.96778. Corresponding RMSEs are about 0.051 and 0.100 m/s. Scalar speed discards current direction; repeated speed phases make these clocks very similar. These are descriptive exposure diagnostics, not independent samples or hypothesis tests. The comparison is scientifically interpretable as a stringent matched predictive ranking, but failure to beat these clocks cannot show that tide is unimportant, and even a tiny first-place sensitivity result cannot establish unique tidal timing. Do not replace the frozen offsets after inspecting the ranking.

3. **The source-clock ambiguity remains material.** The raw Timestamp is naive; author metadata describes DateTime as UTC, but the released R workflow parses DateTime without specifying timezone, while it explicitly sets the current origin to GMT. Primary UTC localization is an interpretation, not an encoded timestamp fact. Prespecified ±3 h results should remain visible: the +3 h setting ranks real current first but still loses badly to simple baselines. This cannot be used to select a preferred timezone from the outcome.

4. **Only one coast, one species, two weeks.** There are 27 unique animals and 32 observed animal/week combinations, with 9/23 animals in the two folds and 5 animals shared. Neither 3,334 bins nor approximately 3 million source seconds is an independent-study count. The folds combine temporal and animal transfer and do not establish eight-week confirmation. The animal-cluster intervals condition on the two observed weeks and already fitted models; they are neither refit-bootstrap intervals nor uncertainty across weeks/coasts and must not become meta-analysis SEs. Best wrong-clock selection uses held-out outcomes as explicitly documented, so its selected score is not an unbiased performance estimate or a randomization p-value.

5. **Endpoint/exposure scope remains narrow.** This is observed submergence share (>2 m primary), not prey capture or foraging success. A mean coordinate/time represents each 15-minute bin; the spatial bounding-box diagonal is median 1.16 km, 95th percentile 2.17 km, maximum 3.69 km. This is a consequential approximation already disclosed in the prefit design, not a replication of the original per-second vector/navigation analysis. It warrants retention as a limitation, not outcome-driven model repair.

## Reproducible numerical evidence

- `python -m unittest validation_v134.test_penguin_analysis -v`: 11 tests pass, including conflicting duplicates, observed denominators, interpolation origin/bounds, masked nodes, whole weeks, hierarchical scoring, analytic gradient, and shared-input mutation.
- `python /workspace/scratch/b1f1c33bd747/v134_review/independent_verify.py`: independently sums the audited minute source to exactly reproduce all 3,400 eligible bins, observed denominators and all 1/2/5 m threshold counts. A separate reread of original Penguins.csv reproduces mean times, coordinates/ranges and trip elapsed times (coordinate serialization differences ≤5.1e−11 degrees).
- The same script rereads original Ocean_Currents.csv, verifies every original hourly Time/TS against 2019-11-22 01:00 GMT and Hours, then uses a separate `LinearNDInterpolator` path. All 81 clock×shift×interpolation columns agree within 4.3e−9 m/s. The 22,930 grid nodes include 6,157 all-hour zero nodes; 3,373 bins have common support, and 3,334 survive the conservative zero-node mask. The retained-zero sensitivity correctly has 39 more bins.
- Independent collapse of saved animal/week scores matches published hierarchical scores within 2.3e−13 nats. Fractional CE and ridge derivative agree with their definitions; row multiplicity is not used as uncertainty precision.
- `OPENBLAS_NUM_THREADS=1 python /workspace/scratch/b1f1c33bd747/v134_review/independent_refit.py`: a separate Newton/Hessian optimizer, training weighting/standardization and score calculation reproduces all 11 primary model scores within 9.1e−7 nats. It reuses inspected production feature construction and week labels, so this is an independent optimization/scoring check, not a wholly separate feature implementation. Primary ranking and scientific conclusion are unchanged.
- Inspection of penguin_analysis.py:60–88 and :120–159 confirms scaling, outcome fitting and diagnostic prevalence use training rows only. Test-only animal indicator columns remain zero in training and receive zero fitted effects. Predetermined time/current/solar/location construction uses no behavioral labels. No target leakage found. Shared animals are explicitly disclosed, so this is not leave-animal-out validation.

Machine-readable verification is in `independent_verification.json` and `independent_refit.json`. No recommendation to tune thresholds, offsets, penalties or model form from these outcomes is made.

## Follow-up: quantify mean-location exposure approximation

Regrouped the independent minute table's per-second-derived current-speed means into the **same 3,334 primary bins**, weighting each minute by its observed unique seconds. All 3,000,423 source seconds have matched current values. No response model was refitted and no setting was selected.

| Hour convention | RMSE (m/s) | 95th percentile absolute error (m/s) | Maximum absolute error (m/s) | Pearson r |
|---|---:|---:|---:|---:|
| Floor | 0.004163 | 0.003224 | 0.094401 | 0.999947 |
| Nearest | 0.004382 | 0.003225 | 0.094401 | 0.999940 |

The mean-location exposure is higher on average by only 0.000266/0.000297 m/s; RMSE is about 1.0–1.1% of the corresponding source exposure SD. These checks indicate small changes for typical floor/nearest inputs, with some localized larger errors. They do not independently validate the primary linearly interpolated exposure or quantify effect on model estimates.

The source-position diagnostic also finds **27 retained bins containing 5,980 seconds whose original interpolation triangle touches an all-hour zero node**. The frozen primary mask is applied to the bin's mean-location triangle; passing it does not imply every original position inside the bin passes the same mask. This is consistent with the implementation and documented exposure approximation, but the final report should avoid the stronger interpretation. Per-second source means retain those original values; no retrospective mask was introduced.

Reproduce with `python /workspace/scratch/b1f1c33bd747/v134_review/exposure_approximation.py`. Detailed results are in `exposure_approximation.json`; bin-level differences are in `exposure_approximation_bins.csv`.
