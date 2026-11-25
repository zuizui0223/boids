# v58 balanced pooled selective illumination rules — completed, conditional near primary not supported
2026-11-26 JST. Frozen [protocol](V58_SELECTIVE_ILLUMINATION_RULES_FREEZE.md), commit b124d4004339e1acd8f39e645e2ccaaedc936a1e. Same Liu & Burbano 2025 original study (DOI 10.1098/rsos.250033), not an independent replication of v55–v57. Retain v56 common-state support STOP (.0713485 < .20), v57 short dark local coefficient-transplant directional support, and all original adverse results.

## Execution and verification
Original [run 45720329192](https://github.com/zuizui0223/boids/actions/runs/45720329192), job 139576755969 SUCCESS. Artifact 15071223342, original ZIP SHA256 0114ab958c67ade8dd389335cbfcacc5b4020a9f2ab03d1eeb6ddaa783b0d750, JSON SHA256 090e2a6856e6808c601befe67b833013bf613421830d1726411e80e81116d0fe. Downloaded and verified actual ZIP and original score payload locally. All 58 original source files reauthenticated, same native .2s grid, 19 triads. Exact v56 separate-fit NEAR replay max abs 8.312781574204564e-10; v57 stored subset endpoint comparison max 8.276401786133647e-10. All 405 unique balanced 16-recording sets (8 bright +8 dark) and 1215 eligible heldout-fit pairs per encoding; 6480 pooled fits and 19440 heldout-fit evaluations for two encodings × eight masks. Neither number represents independent biological units. No source coordinates or fitted coefficients exported. No model-specific training subset selection or threshold tuning.

Every pooled model includes original B/G/N features and shared slopes. Binary mask bits B,G,N enable condition-specific slopes; B bit also enables illumination-specific intercept. M0 shared; M1 B-specific; M2 G-specific; M3 B+G-specific; M4 N-specific; M5 B+N-specific; M6 G+N-specific; M7 all specific. Same train-only StandardScaler and fixed Ridge10, and heldout rows. Each result is equal-original-trial mean of 100*(MSE_M0-MSE_Mmask)/MSE_M0 after averaging losses over eligible fits. This is a supervised forecast, NOT a physical Boids simulation or causal estimate of vision/social interactions.

## All model results
| Model | Bright short | Bright delayed | Dark short | Dark delayed |
|---|---:|---:|---:|---:|
| M0 | 0 | 0 | 0 | 0 |
| M1 B | .445296 | 1.532121 | .865511 | 3.355110 |
| M2 G | .276345 | .824480 | .344851 | 1.670081 |
| M3 BG | .853491 | 2.361239 | 1.619513 | 5.150814 |
| M4 N | .041273 | -.020655 | .012473 | -.024862 |
| M5 BN | .526412 | 1.621915 | .873258 | 3.336254 |
| M6 GN | .341495 | .883021 | .439448 | 1.786580 |
| M7 BGN | .934076 | 2.470228 | 1.703278 | 5.240403 |

Primary short dark M3−M7 normalized by M0 = +.0837646613 pp, descriptive bootstrap [.01188981,.17246853], delete-one [.05620355,.09640174], **6/10 positive, 4 negative**. Frozen >=8/10 sign gate FAIL; **CONDITIONAL_NEAR_SPECIFICITY_NOT_SUPPORTED**. Even a positive bootstrap interval is not enough under the frozen joint criterion. Geometry-polynomial sensitivity also 6/10, [.01125472,.17295212]; retain primary failure. M4 alone provides little mean improvement and its delayed mean is negative in both lights.

## Secondary contrasts (base encoding)
All signs retained. Same 10,000 paired whole-trial resamples seed 20261126, descriptive (overlapping training sets). These contrasts were prespecified secondary, not independent replications or replacements for primary.

| Dark-test contrast | Short pp (positive/10; 95%) | Delayed pp (positive/10; 95%) |
|---|---|---|
| M7 vs M0 | 1.703278 (8; [.828483,2.541286]) | 5.240403 (10; [3.027761,7.494078]) |
| M6 vs M0 | .439448 (8; [.140539,.735795]) | 1.786580 (7; [.322943,3.259200]) |
| M7 vs M6 (B added after G,N) | 1.263830 (8; [.524356,1.953331]) | 3.453823 (8; [1.407567,5.330667]) |
| M7 vs M1 (G,N added after B) | .837767 (10; [.644790,1.051832]) | 1.885293 (10; [1.388725,2.448230]) |
| M7 vs M5 (G added after B,N) | .830020 (10; [.674572,.990045]) | 1.904149 (10; [1.468372,2.380438]) |
| M7 vs M3 (N added after B,G) | .083765 (6; [.011890,.172469]) | .089589 (5; [-.037382,.246140]) |

All bright-test base model comparison bootstrap intervals contain zero, including M7 vs M0 at short [-1.436339,2.688514] and delayed [-2.938886,6.346102]. Do not claim treatment-asymmetric improvement established by directly comparing these means/intervals; that would need a separate test. 

Signed order-average (Shapley) allocation of M0−M7 improvements, percentage points of shared M0:
| Test | Horizon | B | G | N |
|---|---|---:|---:|---:|
| Bright | Short | .523007 | .346072 | .064997 |
| Bright | Delayed | 1.569664 | .846397 | .054167 |
| Dark | Short | 1.065688 | .588453 | .049137 |
| Dark | Delayed | 3.409952 | 1.792601 | .037850 |

Dark B and G mean allocations have descriptive 95% intervals above zero both horizons; N interval spans zero (short [-.005889,.116215], delayed [-.049111,.144529]). All eight model scores and factorial interactions retained in artifact. M3 mean performance close to M7 in dark, but no equivalence margin was frozen: cannot declare noninferiority or prove N specificity unnecessary. B includes geometry and condition-dependent intercept, so it is not an exclusively intrinsic individual mechanism. M6 (collective-specific with common B) does not capture most mean full specificity improvement. v57 transplant loss and v58 conditional benefit are different estimands: substituting separately trained coefficients can be costly even when pooled selective extra slopes are not consistently helpful. Original v57 support not overturned; neither test establishes a causal social channel. Common-state support failure and day/tracking/behavior distribution differences still limit interpretation.

## Independent local score audit
Executed independent reaggregation of original per-trial MSEs (not an independent refit), verifying 1040 numeric or gate assertions, maximum abs error 2.248201624865942e-14; factorial contrasts, closed-form subset-weight Shapley (rather than permutation enumeration), bootstraps, leave-one means and exact primary verdict. Local script SHA256 ec88231e871b9003f404d0c90aa5d3248a052d32ce7583e9ab6bbde0d8c3aa05, audit JSON SHA256 7373ff63f8fe80259852937f1dcf8897854979834fc1dfb787abbc4193b04120. Full v58 artifact is canonical result. Main unchanged; [draft PR #259](https://github.com/zuizui0223/boids/pull/259).

Next empirical direction (not yet executed): test a genuinely transportable rule across heldout recording date blocks with reduced balanced training, and test continuous covariate-conditioned rules across support rather than assuming vision-only treatment effects. Do not retrofit v56 overlap threshold or v58 primary. For Boids synthesis, use illumination-dependent self-history and collective velocity blocks as model candidates, then test an integrated dynamic simulation on heldout group-level statistics; short-horizon regression alone is not a validated generative model.
