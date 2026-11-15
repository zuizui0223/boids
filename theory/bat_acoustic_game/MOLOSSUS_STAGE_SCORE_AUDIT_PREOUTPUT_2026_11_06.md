# Molossus source stage-score audit — 2026-11-06

## Scope and prior exposure
Continue PR #36 using ONLY Krivoruchko et al. 2024 PNAS DOI 10.1073/pnas.2321724121, original Dataset S01, workbook SHA256 `92acbc36cce42028bfd5a07ad1ec8aa8062121575d6d665dc7392b47222f562d`. Ten original bats, 4,299 observed five-second rows; nine-bat complete-sec_group sensitivity. No new animal measurements. Existing full capture outcomes and density summaries have already been examined. This is a POST-OUTCOME diagnostic, not preregistration, independent confirmation, or model selection.

Question: Does poor held-out TOTAL capture prediction arise because density provides no transferable information about attack attempts, success conditional on an attack, or both? The published article already discusses those stages; neither the decomposition nor its average social-foraging trade-off is a new discovery.

## Frozen comparisons before new stage scores
Reuse the unchanged corrected E=1 parser and original `model_rates` M2 fits, same log1p(calls)/log1p(100) predictor, ridge 0.1, fitting routine, and leave-one-whole-bat-out folds. No added covariates, cutoffs, curves or parameter tuning.

For every withheld bat:
1. Attack stage: Poisson deviance per observed five-second row for the existing M2 attack rate vs a constant attack rate `(sum(A_train)+0.5)/(N_train+1)`.
2. Conditional capture stage: binomial negative log likelihood per observed attack for existing M2 success probability vs `(sum(Y_train)+0.5)/(sum(A_train)+1)`. Rows with A=0 contribute zero, not a missing or failed attack. An individual with no attacks has no conditional score and is reported missing, never assigned zero.
3. Total capture stage: existing M2 vs M0 Poisson deviance per row, as already reported. This is a retained outcome, not a new primary win.
Report equal-bat mean scores, paired differences, wins/losses, whole-bat bootstrap intervals (5,000 draws, seed 20261106). Publish all three stages for all-ten and nine-clean cohorts. Intervals are descriptive, small-n and not multiplicity-adjusted; the same nine bats are reused in sensitivity. The units differ between stages: do NOT add their score changes or compare their absolute sizes.

Keep four source-prior density categories 0, 1–25, 26–75, >=76 calls/5s only for pooled held-out calibration: observed and predicted attacks/captures, actual attack count, supporting bat count, and predicted successes conditional on observed attacks. No new tail threshold or response-conditioned subset. Prediction using observed attacks is explicitly CONDITIONAL; it cannot be called forward total-capture prediction.

## Reproducibility defect investigation
The previous verifier failed on the archive's package SHA, after the workbook SHA check passed. Fetch the official Europe PMC supplementary package twice, record package hashes and member hashes. Test whether the analytic XLSX bytes and full member contents are unchanged even when ZIP serialization changes. Retain the original expected XLSX hash as a strict stop; record transport ZIP hashes as provenance, not as data-identity proof. Do not assert a changed ZIP is harmless until inspecting its members. No raw workbook, bat IDs or original five-second records are committed or uploaded.

## Interpretation boundaries
One source/study, 10 bats each with one tracked flight: no longitudinal individual-memory or cross-species inference. Call counts are not independently counted neighbors. Density, prey availability and behavioral state are observationally associated. Success conditional on an attack is selected on attempting; a predictive improvement is not proof of sonar jamming or a causal social cost. Preserve the previously invalid numel-exposure V1 quarantine and previous failed complete-capture forecasting. A result showing one stage transfers would refine, not erase, that failure. Freeze all choices now; do not choose a new model based on this audit.
