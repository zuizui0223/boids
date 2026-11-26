# v59 completed — selective illumination rules improve 10-second closed-loop group summaries

2026-11-26 JST. Frozen protocol [V59_CLOSED_LOOP_ROLLOUT_FREEZE.md](V59_CLOSED_LOOP_ROLLOUT_FREEZE.md), commit 813320b5d778556d3015365a48bd4e97e97c9504. Same Liu & Burbano 2025 study (DOI 10.1098/rsos.250033), not new independent validation. All previous adverse results retained.

## Execution and audit
Original [run 45758356187](https://github.com/zuizui0223/boids/actions/runs/45758356187), job 139702223944 SUCCESS. Artifact 15088179956, ZIP SHA256 e1c6ab2dcdba2da341aee914c69c51e4229d7ad0e19fb303d18cec7a3a075ecf, member rollout.json SHA256 e20a7115cd82442a5160c13be240491ccd45a5f3024c40306e361740992dda75. All 58 original members authenticated, 19 original triads (9 bright, 10 dark). All 405 balanced training combinations replayed for each of eight base models, max prior v58 loss error 7.894414011389017e-10. Three fixed hashed training sets per heldout trial. 1,207 distinct admissible 10-second starting windows (62–70 per trial), 912 trial×training-set×model×regime runs, zero safety stops. These are not 912 independent biological groups. No future observation used as an input after the initial three positions. Observed future positions used only for support and evaluation. Primary noise uses iid draws from pooled M0 training residuals, paired across model masks. No wall/speed clipping. Native coordinate units remain uncalibrated.

Independent local recomputation from downloaded original per-trial/per-fit scores, replicate means and training scales: 9,628 numerical checks, max absolute error 2.2737367544323206e-13. Verified all loss components, whole-trial summaries, bootstrap quantiles, delete-one gates, counts and no heldout overlap. Not an independent refit. Local executed audit script SHA256 80f01764b1843e625cb579bb2d6bf9f82c242b3568b1d595466bbb57f96c0ad4; JSON SHA256 83a5d3150aba04b6c45cb43499b6769e4a9781c00e584cf2dd76f12131b95815.

## 10-second scalar group descriptor error
Loss is mean squared discrepancy of three descriptor MEANS divided by pooled training standard deviations. Equal 3 training fits within trial; equal trials. It does not evaluate complete trajectory distributions, stationarity, or physical wall compliance.

| Light | Model | Deterministic loss | Stochastic loss |
|---|---|---:|---:|
| Bright | M0 | 1.021811 | .350171 |
| Bright | M3 | .857812 | .144388 |
| Bright | M7 | .868582 | .147112 |
| Dark | M0 | 1.154932 | .123364 |
| Dark | M3 | .996636 | .056553 |
| Dark | M7 | 1.013822 | .058175 |

M3 vs M0, primary dark stochastic loss reduction .0668102062 (9/10 positive, descriptive paired bootstrap [.0326738334,.1006798820], delete-one [.0555580586,.0772985628]). **ROLLOUT_M3_DIRECTION_SUPPORTED_DESCRIPTIVE.** Relative reduction of equal-trial mean loss 54.16%. Bright secondary .2057834299 (8/9, [.1206576391,.2788574541], delete-one [.1851659468,.2398489849]), 58.77% reduction. All other masks retained in original score artifact. M3 minus M7 stochastic 10s: bright -.002724 (4/9 positive, interval crosses zero); dark -.001622 (3/10 positive, descriptive interval [-.0032924,-.00003268]). No equivalence/noninferiority margin and no best-subset selection. M3 is fixed candidate, B includes geometry/intercept, not pure intrinsic self rule.

## Key limits and exploratory decomposition
At 10 s, observed descriptor means vs generated M3:
| Light | Regime | Speed (native/s) | Nearest distance (native) | Polarization |
|---|---|---:|---:|---:|
| Bright | observed | 416.67 | 288.12 | .79571 |
| Bright | deterministic | 256.46 | 104.96 | .95572 |
| Bright | stochastic | 383.60 | 387.60 | .81150 |
| Dark | observed | 308.85 | 736.86 | .56129 |
| Dark | deterministic | 144.59 | 372.17 | .62518 |
| Dark | stochastic | 307.42 | 806.79 | .56530 |

Adding pooled training residuals improves M3 descriptor-mean loss in all 19 trials; deterministic minus stochastic bright .713425, 9/9, [.571550,.857687], dark .940082, 10/10, [.784846,1.095942]. Mean-loss reductions 83.17% and 94.33%. Deterministic model suppresses speed and over-compresses groups. Stochastic M3 remains too spread out. Fraction of simulated fish positions outside pooled train rectangle: bright .15510, dark .22867; stochastic M0 .20832/.16470; deterministic M3 .01148/.00673. This is a coordinate-support check, not a verified physical tank boundary. Better group means can coexist with worse extrapolation; no physically valid long-term model claim.

Signed contribution to M0-minus-M3 mean loss change (computed per fit as one-third difference of squared standardized mean errors, then equal trials):
| Light/regime | Speed | Nearest distance | Polarization |
|---|---:|---:|---:|
| Bright deterministic | +.248100 | -.048511 | -.035589 |
| Dark deterministic | -.148567 | +.120572 | +.186290 |
| Bright stochastic | +.043418 | +.157001 | +.005364 |
| Dark stochastic | +.006719 | +.002215 | +.057877 |

In stochastic runs, bright improvement mostly nearest distance, dark improvement mostly polarization. This is a postresult error decomposition, not causal mechanism attribution. v60 should compare fixed alternative train-only residual dependence structures and descriptor distribution quantiles, with exact v59 replay, without changing the prior primary or using test behavior to tune noise. Main unchanged, draft PR #260.
