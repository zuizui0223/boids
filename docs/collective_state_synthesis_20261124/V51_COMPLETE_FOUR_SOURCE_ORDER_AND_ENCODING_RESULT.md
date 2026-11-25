# v51 complete: four-source order-averaged hierarchy is representation dependent

2026-11-25 JST. All three new original source jobs in run [45579308912](https://github.com/zuizui0223/boids/actions/runs/45579308912) SUCCESS. Tetra job 139085014238, ayu 139085014233, zebra 139085013706. Stickleback v51 alternative representation executed locally on the pinned v49 sufficient statistics, exact prior v50 replay. Frozen protocol at ee2c2fae85028eed0309be648f7616dc44726358 and supplementary stickleback freeze 0e1026ba765d4907576f84de7969f504843afc5d. This supersedes pending tetra status in V51_INTERIM_ORDER_AND_ENCODING_RESULT.md; original v46, v48/v49 failed tests and v51 primary failures preserved. Main unchanged, draft PR #254.

## Full cohort

R = 100*mean(PhiL)/mean(PhiG). B is focal history and geometry, G = other-fish mean velocity minus focal current velocity. Residual L = near3 mean minus other-fish mean. Alternative Lraw = near3 mean minus focal current velocity = G+L. PhiG/PhiL are the two-order averaged signed incremental predictive gains, with sum B−BGL. Neither block is a causal/sensory information measure. B includes group geometry, and Lraw overlaps G. Same joint linear span, but standardized Ridge penalty is basis dependent. All same 0.2s kinematics, whole original evaluation unit holdouts, equal file scores (84 recordings averaged inside 12 stickleback shoals). No pooling of native MSE.

| Study | Residual short/delayed % | Residual change pp (decrease units); frozen directional gate | Direct near-focal short/delayed % | Direct near-focal change pp (decrease units); secondary directional gate |
|---|---|---|---|---|
| Tetra (6 recordings) | 3.928570 / 3.185360 | -0.743209 (5/6); PASS | 102.725220 / 62.670417 | -40.054802 (6/6); PASS |
| Ayu (7 recordings) | 3.681768 / 6.270520 | +2.588752 (1/7); FAIL | 82.968842 / 46.833160 | -36.135683 (7/7); PASS |
| Zebrafish (8 archived trials) | 1.797700 / 1.496331 | -0.301369 (6/8); FAIL leave-one | 50.398751 / 47.733209 | -2.665542 (6/8); PASS |
| Stickleback (12 original shoals; 84 files) | 28.960399 / 18.597075 | -10.363324 (12/12); PASS | 193.534394 / 157.001796 | -36.532598 (12/12); PASS |

Directional gate: all denominators positive, ratio of equal-unit mean gains decreases, at least ceil(.75*n) within-unit decreases, every delete-one existing test-score reaggregation decreases. Descriptive paired bootstrap 10000 draws, seed 20261125, NOT independent-population inference (overlapping training folds). Residual intervals: tetra [-1.795623,.054365], ayu [1.300480,4.104515], zebra [-2.010975,1.155121], stickleback [-12.104413,-8.458546]. Direct near-focal intervals: tetra [-43.382664,-36.259678], ayu [-43.725677,-25.424108], zebra [-10.242768,3.407105], stickleback [-43.064379,-29.763506]. All four secondary raw-local directional gates pass (31/33 evaluation units decrease), but zebra interval includes zero. No pooled sign test, no universal law claim; tetra/ayu individual shoal independence unverified. Primary residual gate passes two of four studies only. Ayu is a positive opposite-direction counterexample. Global-first decline is not robust to order averaging of residual features. Tetra residual local-first change +6.565087 pp (0/6 declines); ayu +12.326369 pp (0/7). Both residual-order dependence and representation dependence matter. Do not promote the secondary raw-local sensitivity to replacement primary.

## Fixed polarization contrast: lower minus higher P ratio (pp)

| Study | Residual short | Residual delayed | Direct near-focal short | Direct near-focal delayed |
|---|---:|---:|---:|---:|
| Tetra | +1.451204 (6/6; PASS) | +.253170 (3/6; FAIL) | +5.223331 (4/6; FAIL) | -9.183149 (2/6; FAIL) |
| Ayu | -.001085 (3/7; FAIL) | STOP | +3.927114 (3/7; FAIL) | STOP |
| Zebrafish | STOP | STOP | STOP | STOP |
| Stickleback | +43.309734 (12/12; PASS) | +24.470042 (12/12; PASS) | +121.366160 (12/12; PASS) | +66.980035 (12/12; PASS) |

STOP: at least one within-state PhiG denominator nonpositive; retain signed gains, no denominator rescue or omission. Tetra direct delayed contrast is negative, descriptive bootstrap [-17.334227,-3.037505]; not universal positive low-P relation. State ranks based on present/past covariates in each original recording; not causal manipulation. All state-specific scores retained in original artifacts. The low-P association is robust to both encodings and horizons in stickleback only, not established across studies.

## Actual numerical audit and provenance

Downloaded original three v51 score ZIPs and verified their original GitHub artifact digests. Independent local reaggregation from source-safe per-file model losses (no training) reproduced signed gains, per-unit ratios, descriptive bootstrap quantiles, delete-one ranges, direction/denominator gates: 725 tetra, 673 ayu, 587 zebra numerical array/summary checks, 1985 total, plus status and counts. Original source scoring replayed every v48 state and full-model MSE; reduced panel and state partition checks passed, synthetic transformed-moment/direct-design parity passed.
- Tetra artifact 15005287825; ZIP SHA256 406a8366fe63172355b73f2fd555b72c81014234c076b1f285ef599604d148a4; JSON SHA256 d7f02450acfdafc8b18394d1b4ad35d16235067a27abbfe5b9ebefb07aee9a30. Max original replay 7.31859e-13; reduced replay 0; partition 1.66267e-12.
- Ayu 15006310420; ZIP 2c788da11ebf374b31d61d399a5b0c110a9b06de575210df6c6faab65ace0278; JSON 9b0f55edf2751f4ad0fe434ba236014f65232eaa8964ccb1008c10546b50dd0c. Max replay 0; reduced 7.27596e-11; partition 1.04046e-9.
- Zebra 15006056741; ZIP 0001885ee8914f09f3f778fdeeb66be492e860b0fd664b56ab4ba10826f8a714; JSON 3f04ffc96eef2dcb72289749a8a6875d99e74ce01f03649abb4d5cd1f0441e7d. Max replay 0; reduced 3.46945e-18; partition 1.45717e-14.
- Stickleback source-safe moment audit and script in V51_INTERIM_ORDER_AND_ENCODING_RESULT.md. Actual new fits from same authenticated moments, no raw position exports. 

## Scientific interpretation

The robust statement is narrow: comparing directly observed near-focal velocity block against whole-school velocity block, the order-averaged relative predictive ratio falls at the longer of the two forecast windows in these four datasets by the prespecified descriptive criterion. This is not the same estimand as the residual local deviation. A decomposition of shared and unique predictive gain is required to understand why residual and direct blocks differ. Test the change in conditional predictive overlap and genuinely unique contributions using the fixed existing loss panels, without pretending shared information is a causal common field. Future genuinely independent data are needed to validate the direct-block result, and raw-local ratios should not be interpreted as percentage of all information. Existing failed primary gates remain intact. 
