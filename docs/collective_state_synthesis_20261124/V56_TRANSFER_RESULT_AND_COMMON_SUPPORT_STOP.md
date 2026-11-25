# v56 completed — illumination model transfer and strict common-state support STOP

2026-11-25 JST. Frozen protocol [V56_COMMON_STATE_AND_CROSS_LIGHT_FREEZE.md](V56_COMMON_STATE_AND_CROSS_LIGHT_FREEZE.md), commit 80aee399a39114b8bc2543e8c49ea60bcbb2e4d2. New endpoints in the same original Liu & Burbano 2025 study as v55, not independent replication. Original run [45588323875](https://github.com/zuizui0223/boids/actions/runs/45588323875), job 139115574606. Original result artifact 15009722292 ZIP SHA256 fdefee8d9927286f3c61953b11a5967bef8aa5603e2c16a17bfb67f43114a8ca, JSON SHA256 dbe0f7d18184e3b2af977db6f19aff60f09ae8282e69551962a69803ee731411. Downloaded and verified archive hash locally. Original 58 files and v55 full source QC reauthenticated, 9 bright and 10 dark triads, exact native 0.2s grid. All same-light v55 scores replayed max absolute error 8.312781574204564e-10; cell partition score reconstruction max error 6.439222488552332e-10. All 8-training-recording combinations balanced (9 bright combinations,45 dark combinations), no training-subset selection. No raw tracks or fitted coefficients exported.

## Primary common-state standardization: STOP

Fixed pooled median thresholds mean group speed 341.071272 (native coordinate units/s), mean nearest distance 478.472342 (native units), polarization 0.709581975. All 19 trials retained. Three of eight cells (codes 0,1,7; binary high-speed/high-distance/high-polarization) have at least 30 group times in every trial. Sum of minimum per-trial occupancy proportions in those cells = .07134854587209223, below pre-fixed .20. Fractions of individual recordings lying in supported cells range .0973676–.4467099; this differs from the common minimum mass. **COMMON_STATE_SUPPORT_STOP.** No standardized outcome or causal adjustment reported. Do not relax thresholds or omit trials after seeing support. The stopped endpoint is not evidence that adjustment removes or preserves the light association. This reveals restricted joint covariate overlap, not a measured physical treatment effect.

## Secondary: cross-illumination prediction

Relative excess (%) = 100*(opposite-light trained MSE−same-light trained MSE)/same-light trained MSE, equal original trial mean, same heldout rows. Whole trial holdouts, eight-trial training for every fit, averaged losses across all eligible train subsets. Shared fitting folds; percentile bootstrap intervals are descriptive. Bright test means dark-trained models compared with bright-trained; dark test is reverse.

| Test | Horizon | B excess % | GLOBAL excess % | NEAR excess % | NEAR minus B excess pp (positive trials; descriptive 95%) |
|---|---|---:|---:|---:|---|
| Bright | Short | 2.601519 | 4.956845 | 5.318031 | 2.716512 (7/9; [1.139362,4.066975]) |
| Dark | Short | 7.426627 | 9.694509 | 10.745862 | 3.319234 (9/10; [1.918653,4.764615]) |
| Bright | Delayed | 7.011002 | 13.052219 | 13.599550 | 6.588548 (8/9; [3.438821,9.227741]) |
| Dark | Delayed | 22.417736 | 30.900428 | 32.736745 | 10.319009 (9/10; [5.875196,14.879643]) |

NEAR excess positive in 8/9 bright and 10/10 dark at both horizons; NEAR model's cross-light excess greater than B in 7/9 and 9/10 short, 8/9 and 9/10 delayed. Extra cost above B includes both GLOBAL and local feature blocks, not isolated social/near causality. Native polynomial sensitivity confirms direction (NEAR−B excess short bright 2.714011, dark 3.332188; delayed bright 6.603404, dark 10.346133). Relative excess for both B and NEAR larger when testing dark with bright training than reverse in point estimates. Do not directly compare native MSE scales across conditions or claim statistically established asymmetry without dedicated test.

### Correct local velocity-to-position assignment
A=100*(MSE_ROT−MSE_NEAR)/MSE_GLOBAL; normalized within test trial/training regime. Negative = randomized local assignment model predicts better. Equal original trial means.
| Test | Horizon | Same-light A % | Other-light A % | Other−same pp (descriptive 95%) |
|---|---|---:|---:|---|
| Bright | Short | .460112 | .129882 | −.330231 [−.591127,−.066703] |
| Dark | Short | .029415 | −.920141 | −.949556 [−1.321624,−.616194] |
| Bright | Delayed | .609873 | .141415 | −.468458 [−.851321,−.126672] |
| Dark | Delayed | .046889 | −1.336654 | −1.383542 [−2.044324,−.802481] |

Bright-trained applied to dark: cross-light A negative in 10/10 short and 9/10 delayed, other−same A negative in 10/10 both. Same-light contrast replay +.430697626 pp short, +.562984798 delayed. Fixed native polynomial results similar. This is a stronger prediction-transfer diagnostic, not identification of a visual mediation pathway. Within-condition training cohorts differ in state and behavioral distributions, filming date, unmeasured environment or tracking. A pooled state overlap gate failed, so cannot rule out distribution shift. v54 synthetic no-edge counterexamples preserved.

## Filename date-token sensitivity
04062024 3 bright/1 dark, 04092024 6 bright/1 dark; within-date short A contrasts +1.002994 and +.157512 pp, delayed +1.912712 and +.037944 pp. 04072024 and 04082024 only dark 4 each. Date codes as in filenames, not verified randomized blocks. Eight same-light training recordings unavailable when either mixed-date block is entirely held out (bright remaining 6 or 3). No claim date adjusted or independent replicate.

## Independent numerical audit
Recomputed all original same-light losses against v55 artifact, overlap admission and all transfer and assignment trial vectors, bootstrap quantiles and signs from source-safe MSE. 268 assertions passed (no independent refit). Audit JSON SHA256 8c88facfd44dccdda3a07c1ef68c36c080a2461d3c3ce4368251895806b8f7f0; executed local script SHA256 e3994abc295c0a1000e997304336e8070b22a1955648c0c32386d1df3732a7fe. Bootstrap uses fixed seed 20261125. All source result and gate failures retained. Main unchanged, draft PR #257.
