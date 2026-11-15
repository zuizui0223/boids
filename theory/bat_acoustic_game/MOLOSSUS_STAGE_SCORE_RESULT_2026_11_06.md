# Where the held-out capture prediction fails

**2026-11-06 — post-outcome diagnostic of a previously published dataset; no new animal measurements.** Source: Krivoruchko et al. (2024), PNAS, DOI 10.1073/pnas.2321724121; original supplementary workbook SHA256 `92acbc36cce42028bfd5a07ad1ec8aa8062121575d6d665dc7392b47222f562d`. Ten bats, 4,299 observed five-second rows, 1,354 attacks, 1,006 successful captures. The original paper already established the social-foraging trade-off. This analysis diagnoses the existing model's out-of-bat predictions, not a new discovery of that trade-off.

## Finding

**In the pre-existing high-call-density category (>75 other-bat calls per five seconds), the unchanged M2 model predicts the number of attacks approximately correctly in aggregate but substantially overpredicts successful captures.** Predictions are genuinely bat-held-out: each animal's entire record is predicted from the other animals. The category was inherited from the original study, not optimized here.

| High-density source subset | Observed | Held-out M2 prediction |
|---|---:|---:|
| Attack attempts | 36 | 38.856 |
| Successful captures, forward attack-rate × success model | 10 | 24.471 |
| Successful captures, conditional on the ACTUAL 36 attacks | 10 | 22.555 |

This subset contains **112 five-second rows from eight bats**, not 112 independent biological replicates. Even replacing predicted attacks with observed attacks leaves overprediction of success: the attack-weighted predicted success fraction is about 62.7%, versus 27.8% observed. Therefore the high-density calibration failure is not merely an error in how many attacks occur. It persists in the success-given-attack component of this particular model.

The nine-bat sensitivity, excluding the original animal with seven missing sec_group indices, yields 108 high-density rows from seven bats: 36 observed attacks and 10 captures, versus 36.862 predicted attacks and 23.709 forward-predicted captures (23.050 conditional on observed attacks). These are overlapping sensitivity data, not an independent reproduction.

## Complete stage assessment, not just a favorable subset

The analysis retained **exactly the prior M2 models**, covariates, ridge penalty, source eligibility and bat-held-out folds. It added stage-specific baselines and scoring, without selecting a new curve. Lower scores are better.

| Endpoint, all ten bats | Constant baseline | Density model | Density minus baseline | Bats with lower error | Descriptive paired-bat 95% interval |
|---|---:|---:|---:|---:|---|
| Attacks: Poisson deviance per 5s | 0.865795 | 0.867240 | +0.001444 | 8/10 | [-0.004600, +0.011458] |
| Success given an attack: binomial NLL per observed attack | 0.572300 | 0.567221 | -0.005079 | 7/10 | [-0.014412, +0.004200] |
| Total captures: Poisson deviance per 5s | 0.762319 | 0.765162 | +0.002843 | 3/10 | [+0.000259, +0.006608] |

Most bats' attack predictions improve slightly, but larger deterioration in two bats makes the equal-bat mean worse. Conditional success has a small average predictive gain, yet its interval includes zero; **reliable overall conditional predictive improvement is not established**. The earlier negative total-capture prediction result remains unchanged. Stage loss units differ, so their changes are not additive and their raw magnitudes should not be compared.

Nine-clean-bat mean differences are +0.002272 for attacks, -0.002981 for conditional success, and +0.003654 for total captures. Intervals for the first two include zero. The bootstrap uses 5,000 whole-bat resamples with seed 20261106; earlier total-capture point estimates are reproduced, while interval endpoints differ slightly from the earlier bootstrap seed.

## Interpretation limits

The result identifies an **out-of-bat calibration problem of the chosen model** in dense acoustic conditions. It does not distinguish interference with sonar, physical avoidance, prey conditions, individual behavioral state, observation processes, or inadequate functional form. No neural receiver or causal jamming effect was measured in this reanalysis. Conditioning on having attacked is not an experiment on attack selection. Call density is an acoustic proxy, not a direct count of neighboring bats. One flight per bat cannot establish persistent personality or learning.

This was specified after earlier source outcomes were examined. All stages, both cohorts and all four density categories are reported. No additional models were tuned after the diagnostic. The new result should refine the previous prediction failure, not turn it into a claim of a universal ecological law.

## Reproducibility repair

The previous original-source verifier failed because it required the outer download ZIP's checksum to remain constant. Two new official downloads have **different ZIP timestamps/checksums but identical content hashes for all seven member files**, including the original analytical XLSX. ZIP packaging is recorded as a transport receipt; XLSX identity remains a strict SHA gate.

A second verifier problem used cohort names that did not exist in the permanent result ledger. This lookup was corrected without changing data or numerical results. A subsequent run exposed only a 3.17e-12 cross-run numerical difference from the fitted model. Numerical comparisons now use an explicit 1e-9 absolute tolerance and print the largest observed discrepancy; source hashes, count denominators, original code identities, cohort membership and direction counts still require exact agreement. The tolerance is far below reported scientific precision and does not alter model fits. Prior invalid E=numel_5swindows results remain quarantined.

## Saved evidence

- `MOLOSSUS_STAGE_SCORE_AUDIT_PREOUTPUT_2026_11_06.md`: frozen post-outcome diagnostic specification.
- `molossus_stage_score_v1.py`: unchanged-model stage scoring and two-download member audit.
- `MOLOSSUS_STAGE_SCORE_LEDGER_2026_11_06.json`: permanent complete aggregate results, including all density categories.
- GitHub Actions run **42183498629**: original-data stage analysis, previous total-score reproduction, 56 targeted tests and full acoustic-component discovery of **145 passing tests** before adding four verifier-specific regression tests.
- Artifact **13485828445**: full aggregate output and complete component test log, no raw source records.

Only this acoustic research branch is changed. PR #36 remains Draft; no merge, journal submission, or frozen batter manuscript modification.
