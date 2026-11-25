# v49 completed and v50 feature-order sensitivity — original 84 stickleback trials / 12 shoals

2026-11-25 JST. [v49 frozen protocol](V49_STICKLEBACK_POLARIZATION_TRANSFER_FREEZE.md). Original [run 45575582497](https://github.com/zuizui0223/boids/actions/runs/45575582497), all 12 source jobs and score job 139075074730 SUCCESS. Original v49 aggregate artifact 15004761090 ZIP SHA256 422b42d5d69623b88c17adb0c8be0ea1c01f46562c692f7111e6650ac64fe6cc; JSON SHA256 012a0eef459fe6d5efbdc3b3888bbffff86b6b54093d223bdd231fbb28296383. All 84 original file hashes, sizes and actual author shoal IDs checked against v33b. Cohort unchanged: 3,147,771 native rows, 570,360 eligible group times, 4,562,880 eligible fish-times, 57,968 omitted group times. All speed×polarization cells admitted. Exact six model prior replay max absolute 2.18279e-11, state partition error 6.51198e-10. No new biological independent population or causal interpretation.

## v49 original result
K=(F_highP-F_lowP)_delayed-(F_highP-F_lowP)_short, F=100*(MSE_NEAR-MSE_FAR)/MSE_GLOBAL at each shoal/state/horizon; equal trials within original shoal, then equal shoal means.

| Contrast | Mean pp | Positive shoals | Descriptive paired 95% interval |
|---|---:|---:|---:|
| All speed states | +.023431854 | 6/12 | [-.009678,.057745] |
| Low speed | -.029707778 | 4/12 | [-.061196,.001144] |
| High speed | +.133124454 | 11/12 | [.070107,.195176] |
| Equal speed-stratum K | +.051708338 | 8/12 | [.011770,.090799] |
| High minus low speed | +.162832231 | 11/12 | [.103428,.220550] |

**Frozen primary TRANSFER_DIRECTION_NOT_SUPPORTED** (6/12<9/12). Secondary speed moderation all four scale point estimates positive: state-global +.162832 pp, full-global +.038538 pp (6/12 positive, interval includes zero), state-geometry +.145420 pp (11/12), native MSE +22.403536 (12/12). Thus the sign of the mean speed contrast is insensitive to these scales, but consistency and intervals are not. Prior tetra and ayu negative speed contrast, zebra and stickleback positive; species/study/arena/measurement confounded. No absolute speed equivalence or universal rule.

## New v50: order-averaged predictive gain audit
Frozen before new reduced-panel outcomes at commit c2bc3a1572f55cd2e51a203d3551c3a75673503b, [protocol](V50_FEATURE_ORDER_SENSITIVITY_FREEZE.md). Downloaded all 12 source-safe v49 moment ZIPs (artifact names v49-original-shoal-1 through 12) and completed v49 aggregate; SHA256 exactly matched GitHub artifact digests. Locally executed [order_audit.py](../../validation_fish_school_v50/order_audit.py), independently centered normal equations, fixed Ridge10, train-only scaling; all nine strata and six original panels replayed max absolute 2.09184e-11; all 20 v49 interaction arrays and interval quantiles reproduced (max interaction error 2.13731e-11). Same 11-train-shoal, 1-test-shoal folds. Verified each reduced original model score matches original to max 7.09406e-11. No fresh raw trajectory acquisition. New BL model fit from selected columns of original 18D moments; fitted coefficients never exported.

Let B=geometry/own history, BG add whole-school velocity, BL add nearest3 deviation from mean other-fish velocity, BGL both. Denote model MSE with same letter. G0=B-BG, L1=BG-BGL, L0=B-BL, G1=BL-BGL. Symmetric predictive gains PhiG=(G0+G1)/2, PhiL=(L0+L1)/2. Exact sum PhiG+PhiL=B-BGL checked. Local block is defined RELATIVE TO whole-school mean, not information exclusively available to nearby fish. Order averaging allocates predictive improvement, NOT causal variance partition or sensory contributions.

| Ratio (%) | Short | Delayed | Change pp | Declining shoals | Descriptive 95% interval |
|---|---:|---:|---:|---:|---:|
| Global first L1/G0 | 47.160329 | 31.487374 | -15.672956 | 12/12 | [-18.647267,-12.615991] |
| Local first L0/G1 | 14.766720 | 8.008514 | -6.758206 | 12/12 | [-7.870633,-5.402952] |
| Order-averaged PhiL/PhiG | 28.960399 | 18.597075 | -10.363324 | 12/12 | [-12.104413,-8.458546] |

All primary full-cohort denominators positive. **Frozen v50 direction gate PASS**: all 12 decrease, all delete-one changes negative [-10.826558,-9.427997] pp. Ratio of equal-shoal mean gains. 10000 paired whole-shoal resamples seed 20261125; descriptive, overlapping training folds. Order-averaged native gain PhiG short/delayed 70.921998/493.403890; PhiL 20.539293/91.758690. Both gains increase with horizon; local-to-global ratio decreases, not local absolute loss. Baseline-normalized mean within-shoal gains PhiG 2.208732%/5.800767%; PhiL .603535%/1.050500%.

Secondary state-specific order-averaged ratios:
| State | Short % | Delayed % | Change pp | Declining shoals | Gate |
|---|---:|---:|---:|---:|---|
| P low | 54.133820 | 32.503848 | -21.629972 | 11/12 | PASS |
| P high | 10.824086 | 8.033806 | -2.790280 | 9/12 | PASS |
| V low | 37.413214 | 20.529223 | -16.883992 | 12/12 | PASS |
| V high | 26.279186 | 17.098340 | -9.180846 | 12/12 | PASS |
| V low P low | NA | NA | NA | NA | STOP (11/12 positive short PhiG denominators) |
| V low P high | 11.390604 | 7.783333 | -3.607272 | 12/12 | PASS |
| V high P low | 46.321110 | 31.895962 | -14.425148 | 11/12 | PASS |
| V high P high | 11.033202 | 8.172138 | -2.861064 | 6/12 | FAIL sign threshold |

No substitution of denominators or dropping adverse units. Results condition on same observed study and overlapping training folds. State stratification uses within-trial covariate ranks. All state-specific analyses secondary, not independently validated. v50 does not rescue v46 or v48/49 failed universal transfer. Next replicate this exact four-panel order audit in tetra, ayu and zebrafish (source-safe moments not retained in their previous state workflow; requires new source reauthentication and reduced-model fit). Connect to earlier studies only as a methodological hypothesis about conditional predictive hierarchy, not a pooled ecological meta-effect.

## Reproducibility
From run 45575582497, download the 12 source artifacts named v49-original-shoal-N.zip and final aggregate as v49-stickleback.zip into one directory. Run python validation_fish_school_v50/order_audit.py <directory>. Script pins all 13 ZIP SHA256s. Local executed script SHA256 da97d9252ac7841e7305db7ccb66bf568ea1d5b991f737186a2d7aca18fe41f8, Git blob a07a9baefe59fa5b7182456ab76da87017ea83b3. Local result JSON SHA256 45363c583170d866aacf80295aefa496c1edee8dc31c451cb44437996d372b45 (290155 bytes); regenerate using same script (floating precision may differ by CPU). No original trajectories or fitted coefficient arrays republished. Draft PR #253, main unchanged.
