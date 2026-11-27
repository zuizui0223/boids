# v61 completed — temporal fidelity, direction-specific residual effects, and coordinate support failure
2026-11-27 JST. Frozen protocol [V61_TEMPORAL_FIDELITY_FREEZE.md](V61_TEMPORAL_FIDELITY_FREEZE.md) at eaad00fac1f5fc0c50557842ab6dad07e10cca0d. Same original Liu & Burbano 2025 study (DOI 10.1098/rsos.250033), not independent of v55–v60. [Run 45940169908](https://github.com/zuizui0223/boids/actions/runs/45940169908); Dark job 140312429545 SUCCESS, Bright job 140312429863 SUCCESS. All 58 original members authenticated, 19 triads (9 bright,10 dark), three fixed balanced 8+8 training sets per trial, same native .2s grid, 8 replicates. 1207 original 10s starts (568/639 bright/dark); 398 separate 30s starts (189/209); zero safety stops. Original v60 stored score replay maximum absolute difference 0, 7128+7920=15048 fields. No source positions or coefficients exported.

## 10s: fixed primary temporal fidelity
Temporal loss is mean of six squared discrepancies of simulated vs observed RMS descriptor changes (speed, mean nearest distance, polarization; lags .2 and 1s), each divided by training descriptor SD before squaring. Not exact trajectory similarity, stationarity or full temporal covariance.
| Light | Noise | M0 | M3 | M0−M3 |
|---|---|---:|---:|---:|
| Bright | pooled iid | .01890320 | .01790493 | +.00099827 |
| Bright | light iid | .02220672 | .02117961 | +.00102711 |
| Bright | group | .02251514 | .02277435 | -.00025921 |
| Bright | block | .02740095 | .03683932 | -.00943837 |
| Dark | pooled iid | .03949843 | .03019366 | +.00930477 |
| Dark | light iid | .03407688 | .02569265 | +.00838423 |
| Dark | group | .03442246 | .02608942 | +.00833304 |
| Dark | block | .03144604 | .02536522 | +.00608083 |

Frozen primary M3 dark group-minus-block temporal loss +.000724200021183076 (8/10 positive; descriptive paired 95% [.0001268953,.0013437564], delete-one [.0005397801,.0009019339]). **BLOCK_TEMPORAL_FIDELITY_SUPPORTED_DESCRIPTIVE**, 2.78% reduction relative to group noise. Bright secondary -.0140649660 (0/9; [-.01904305,-.00921140]); 61.76% worsening. M0-to-M3 temporal gain in dark is positive in 10/10 trials for every fixed noise regime. Bright block M0-to-M3 temporal gain negative in all nine. Both mean/quantile vs temporal and bright/dark contradictions preserved.

## 30s: separate fixed longer-window support
| Light | Noise | M0 mean / quantile / temporal | M3 mean / quantile / temporal | M3 simulated rectangle excursion / observed |
|---|---|---|---|---|
| Bright | group | .495109 / .518758 / .025691 | .192873 / .252223 / .027039 | 18.4720% / .018812% |
| Bright | block | .359655 / .418589 / .030853 | .172584 / .313195 / .045846 | 23.4289% / .018812% |
| Dark | group | .185268 / .299566 / .037609 | .066817 / .104061 / .027407 | 21.9412% / .018114% |
| Dark | block | .145322 / .243633 / .033696 | .077347 / .113696 / .026183 | 21.2183% / .018114% |

Dark block M0-to-M3 temporal improvement +.0075134504, 10/10, descriptive interval [.00649635,.00887577]. Dark group analogous +.0102028870, 10/10, [.00883822,.01160097]. Dark M3 group-minus-block +.0012238514, 7/10, interval [.00026896,.00216753], FAIL frozen >=80% consistency criterion used descriptively; not a second primary pass. Bright M3 group-minus-block -.0188065688, 0/9, [-.02555526,-.01284822]. All longer runs finite. Observed near-zero rectangle excursion measured against identical training-only rectangle; simulated excursions orders of magnitude larger. This is a serious support mismatch, not physically calibrated wall violation. The occupancy constraint should be tested before tuning more noise.

## Actual independent postresult decomposition
For each fit, six squared standardized lag-error components/6, equal fits then equal trials. Group-minus-block temporal loss change:
| Light/window | .2s speed / distance / P | 1s speed / distance / P |
|---|---|---|
| Bright 10s | +.000076822 / +.000020500 / +.000742083 | -.015608151 / +.000490055 / +.000213725 |
| Dark 10s | +.000040419 / -.000000952 / +.000140681 | -.000066420 / -.000097759 / +.000708232 |
| Bright 30s | +.000095321 / +.000021299 / +.001122380 | -.021029976 / +.000442171 / +.000542237 |
| Dark 30s | +.000053887 / -.000002785 / +.000135532 | +.000308531 / -.000096583 / +.000825270 |
Bright worsening mainly excessive 1s speed variability; dark improvement mainly polarization fluctuations. Descriptive decomposition, not causal effect or independent tests. M3 30s 5s centroid displacement RMS native units (group/block/observed) Bright 1325.84/1481.58/1285.92, Dark 722.67/677.45/717.63. Good centroid displacement averages do not guarantee valid spatial support.

## Independently verified numerical evidence
Downloaded original artifacts Bright 15172436048 ZIP SHA256 71a8a33e23806d7eb6a622a3b5be67814ea850042f3e298048ac8e6ff23c7233, JSON 966d6dda83053b7081199fe592653443b8a0081ca0db83f9f4392def6aee8613; Dark 15172420995 ZIP 5e0d3a7ea014d662b959cc59d823bf95f16aa44425965531d1aa4c387f2d4016, JSON c0683870f5069f3dc4a139c1cb4b76832d2d221d10443236d3ea539f26387b58. Both ZIP and JSON digests verified locally, with v60 original pins. Executed independent reaggregation of every retained score from native means, quantiles, lag-change RMS and original training scales; exact prior-v60 field comparisons, trial-level summaries, all directional gates/bootstraps/delete-one ranges and new error decomposition. 30940 numerical assertions including 15048 v60 field comparisons, maximum absolute numerical discrepancy 2.2737367544323206e-13. Local executed audit script SHA256 b68486126c776c361ee21263eb518153ac2f5ed6fc2a8d11f1e9b83b4b523c08, JSON SHA256 b3638bc4e3cb67fd0b7f80e0523b6114e6ddf702bfdac387361f245636004e82. Reaggregation, not new fit. No physical calibration, independent population replication, or causal mediation established. Draft PR #262, main unchanged.
