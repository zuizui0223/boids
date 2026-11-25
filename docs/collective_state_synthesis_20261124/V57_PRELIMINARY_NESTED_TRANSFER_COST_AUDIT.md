# v57 preliminary: common-denominator nested-model transfer costs

2026-11-26 JST. Verified original v56 artifact 15009722292 ZIP SHA256 fdefee8d9927286f3c61953b11a5967bef8aa5603e2c16a17bfb67f43114a8ca, JSON SHA256 dbe0f7d18184e3b2af977db6f19aff60f09ae8282e69551962a69803ee731411. Local independent reaggregation of existing per-trial losses, not new prediction fit. v56 COMMON_STATE_SUPPORT_STOP unchanged.

Let E_M=100*(MSE_other-light,M - MSE_same-light,M)/MSE_same-light,B, with the SAME denominator for every model within test trial/horizon. Define costs B=E_B, global increment=E_GLOBAL-E_B, local increment=E_NEAR-E_GLOBAL. Exact sum E_NEAR verified for every original trial and both encodings/horizons. Equal-trial means, all signed differences, descriptive trial-resampling bootstrap (10,000 draws, seed 20261126) with shared training folds.

| Encoding | Test | Horizon | B | Global increment (positive trials; descriptive 95%) | Local increment (positive trials; descriptive 95%) | Total |
|---|---|---|---:|---|---|---:|
| base | Bright | Short | 2.601519 | 2.088676 (7/9; [.828080,3.129438]) | .304211 (8/9; [.049935,.543481]) | 4.994405 |
| base | Dark | Short | 7.426627 | 2.262127 (9/10; [1.180466,3.327409]) | 1.049415 (10/10; [.668736,1.477755]) | 10.738170 |
| base | Bright | Delayed | 7.011002 | 4.746722 (7/9; [2.165161,6.822241]) | .408209 (6/9; [.108401,.732805]) | 12.165933 |
| base | Dark | Delayed | 22.417736 | 8.424302 (9/10; [4.634023,12.202225]) | 1.821728 (10/10; [1.002661,2.749955]) | 32.663766 |
| native polynomial | Bright | Short | 2.666283 | 2.082465 (7/9; [.825373,3.120861]) | .305426 (8/9; [.055362,.542611]) | 5.054174 |
| native polynomial | Dark | Short | 7.417004 | 2.284058 (9/10; [1.199019,3.356343]) | 1.040325 (10/10; [.660889,1.469108]) | 10.741387 |
| native polynomial | Bright | Delayed | 7.104577 | 4.750841 (8/9; [2.171259,6.823018]) | .406059 (6/9; [.112606,.725742]) | 12.261477 |
| native polynomial | Dark | Delayed | 22.400832 | 8.475858 (9/10; [4.677606,12.279633]) | 1.795079 (10/10; [.977802,2.726719]) | 32.671769 |

All entries percentage points relative to same-light baseline B; not the prior v56 excess with separate model-specific denominators. Both incremental costs positive in all eight mean comparisons, but these are NOT block-specific coefficient allocations, because nested models were fitted independently and shared coefficients can change. No isolated social/visual causal claim. Native polynomial does not supply physical calibration. Same source and day/state-distribution confounding retained.

Local executed script SHA256 485011d9d60e6059c3a016c034fdd5e1192ab2e831457783a8f0825f1c98e25d, JSON SHA256 29f8a633ab4a77ffa5fa9da32bdb28834ae8d6bbdcf3a78cbcc8960b4701eb7f. All per-trial scores retained in local result JSON. Next: frozen v57 coefficient-block transplant in [PR #258](https://github.com/zuizui0223/boids/pull/258), [run 45719717449](https://github.com/zuizui0223/boids/actions/runs/45719717449). No new transplant outcome claimed before successful source replay and score receipt.
