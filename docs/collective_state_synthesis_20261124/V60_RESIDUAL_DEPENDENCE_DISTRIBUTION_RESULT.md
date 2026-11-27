# v60 completed: condition-dependent rules improve heldout distributions; temporal residual dependence does not universally help
2026-11-27 JST. Frozen [protocol](V60_RESIDUAL_DEPENDENCE_DISTRIBUTION_FREEZE.md), commit 6aa553b4635b53d0862eff24de826ff7a5856d82. Same Liu & Burbano 2025 study; no independent replication. [Run 45759872351](https://github.com/zuizui0223/boids/actions/runs/45759872351), Bright job 139707101976 SUCCESS and Dark job 139707102335 SUCCESS. Authenticated 58 original files; same 19 triads, 1207 starts, three fixed 8+8 training sets per trial, .2s steps, 8 stochastic replicates, M0/M3/M7, 4 residual regimes. Zero safety stops across 684 trial×trainset×mask×regime runs. Native coordinates not calibrated; no wall constraint.

## Actual heldout distribution results
Loss = mean of nine squared discrepancies of observed vs generated 10th/50th/90th percentiles of group speed, mean nearest-one distance, polarization, divided by train descriptor SD before squaring. Equal trial weights. All same source, shared training folds. Averages:
| Light | Residual regime | M0 | M3 | M7 | M0−M3 | Positive trials | Descriptive paired 95% |
|---|---|---:|---:|---:|---:|---|---|
| Bright | pooled iid | .372343 | .176401 | .179315 | .195942 | 8/9 | [.097584,.281668] |
| Bright | light iid centered | .382148 | .175149 | .176507 | .206999 | 8/9 | [.108960,.294873] |
| Bright | light group centered | .380177 | .181011 | .182586 | .199165 | 8/9 | [.097498,.290357] |
| Bright | light block centered | .306793 | .206890 | .206930 | .099904 | 7/9 | [-.000239,.190008] |
| Dark | pooled iid | .214517 | .093036 | .093354 | .121481 | 10/10 | [.084529,.156335] |
| Dark | light iid centered | .211637 | .089357 | .090094 | .122280 | 10/10 | [.087610,.154861] |
| Dark | light group centered | .213130 | .088595 | .089069 | .124536 | 10/10 | [.089844,.157016] |
| Dark | light block centered | .176936 | .095054 | .096257 | .081882 | 9/10 | [.049948,.114035] |

Frozen primary (dark, 10s light-block M0−M3) **BLOCK_DISTRIBUTION_M3_SUPPORTED_DESCRIPTIVE**, reduction 46.28% of M0 mean, delete-one means [.071101,.092071]. Bright block secondary does not pass the sign/interval gate. Other three regimes support positive mean reduction in both lights under the same descriptive criterion. Do not declare M3 equivalent to M7 (no equivalence margin). All eight earlier forecast models and prior adverse endpoints retained. Noise includes observed residual covariance, not a mechanistic estimate of social forcing.

## New postresult decomposition (descriptive, independently reaggregated)
At 10s, M3 quantile loss relative to M0, signed descriptor contributions in speed / nearest distance / polarization (each 1/3 of total descriptor quantile squared loss):
| Regime | Bright | Dark |
|---|---|---|
| pooled iid | +.025434 / +.163379 / +.007130 | +.035927 / +.021774 / +.063780 |
| light iid | +.010880 / +.186741 / +.009378 | +.017810 / +.038516 / +.065955 |
| group | +.007153 / +.183848 / +.008164 | +.018086 / +.039465 / +.066985 |
| block | -.018975 / +.129204 / -.010326 | +.007903 / +.027892 / +.046086 |

Bright improvements mostly nearest distance; Dark mostly polarization. In bright block, speed and polarization errors worsen. These are error components, not independent effects or causal attribution.

Holding M3 fixed, postresult paired group-minus-block quantile-loss contrast bright -.025878 (4/9 positive, descriptive CI [-.070901,.013838]); dark -.006460 (2/10 positive, [-.011323,-.001241]). Thus 1s blocks do not universally improve even distributional summaries; in dark the observed quantile loss is higher. Same-light iid-minus-group contrast bright -.005862 (3/9, [-.013180,-.000287]), dark +.000762 (4/10, [-.000825,.002709]). Pooled-minus-light-iid contrast crosses zero both lights. Not a frozen noise-selection test; retain all regimes. Same-light blocks alter both time dependence and finite marginal sampling weights. Marginal quantile loss cannot test temporal sequence fidelity. That requires a separately frozen trajectory-dynamics endpoint.

Training rectangle excursions M3 pooled/group/block bright .155096/.173344/.204024; dark .228665/.202603/.199411. In dark M3 block still exceeds M0 block .134430. These are NOT calibrated tank-boundary violations; observed rectangle-excursion baseline absent in v60. Cannot claim a physically valid generative model.

## Provenance and independent numerical audit
Original downloaded and SHA-verified artifact Bright 15089297415 ZIP f6fdc48a02705635ccb2b12303ae3e0c84a6b5685bba9ff4a42d9af41e335ac9, JSON 2017fdade0cd6d075d64acf0efbd423a4b4efb711e626abd519b3aa8a73c431c; Dark 15089077349 ZIP 1e7a99bb8f74777e11af03d7a17149b202d96eea9084aad90af89c7f18f20e19, JSON 3bc74db14eddd51ab8bd9dfcb62b8a3a39e77e34d706875eeaff4587ac3c419f. Independent local reaggregation from source-safe per-fit metrics, not a new fit: 15708 numeric assertions, 3591 exact prior v59 score comparison checks, maximum abs discrepancy 2.7853275241795927e-12, verified trial identities and no heldout leakage, all primary and secondary gate statuses. Audit JSON SHA256 8feb2fc56bd4458bbca9be6766e4364ecfe8444d9726e207a9d7167eba704e30. No original positions, coefficients or individual residuals exported. Main unchanged; draft PR #261.
