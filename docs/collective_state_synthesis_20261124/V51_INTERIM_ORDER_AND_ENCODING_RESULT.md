# v51 interim actual results: order averaging and local feature representation expose an ayu counterexample

2026-11-25 JST. Frozen protocol at ee2c2fae85028eed0309be648f7616dc44726358; separate stickleback raw-local sensitivity frozen at 0e1026ba765d4907576f84de7969f504843afc5d before its new fits. Draft PR #254. Original run 45579308912: ayu and zebrafish SUCCESS at time of this note; tetra still in progress, no tetra v51 outcome claimed. Main unchanged.

## Primary order-averaged ratio R=100 mean(PhiL)/mean(PhiG)

All loss units within study. Residual L = nearest-three velocity minus other-fish mean; raw-local Lraw = nearest-three velocity minus focal velocity. B still contains group geometry. Joint model span same under both encodings, but fixed standardized Ridge10 can give different predictions and allocation; raw L shares information with global motion. No physical sensory or causal decomposition. Equal original evaluation units; stickleback true shoals, zebra within-size archived recordings (author states no within-size fish reuse), ayu biological independence not verified.

| Study | Residual short / delayed % | Residual delta pp; declines; gate | Raw-local short / delayed % | Raw-local delta pp; declines; gate |
|---|---|---|---|---|
| Stickleback 12 shoals (84 files) | 28.960399 / 18.597075 | -10.363324; 12/12; PASS (v50 primary) | 193.534394 / 157.001796 | -36.532598; 12/12; PASS descriptive sensitivity |
| Ayu 7 files | 3.681768 / 6.270520 | +2.588752; 1/7; FAIL | 82.968842 / 46.833160 | -36.135683; 7/7; PASS descriptive sensitivity |
| Zebrafish 8 files | 1.797700 / 1.496331 | -.301369; 6/8; FAIL delete-one | 50.398751 / 47.733209 | -2.665542; 6/8; PASS descriptive sensitivity (CI includes zero) |
| Tetra | pending | pending | pending | pending |

Ayu original global-first ratio decreases -6.431482 pp, but residual local-first increases +12.326369 pp, and symmetric residual increases +2.588752 pp (descriptive interval [1.300480,4.104515], delete-one [2.174265,3.310500]). This is a clear counterexample to a universal order-averaged residual hierarchy. Raw-local sensitivity shows the direction depends on how the local feature is defined; do not redefine primary or rescue the failed gate. Zebra residual fails delete-one (upper +.137880pp); raw-local passes predefined sign/leave-one gate but interval [-10.242768,3.407105] spans zero. Stickleback raw-local interval [-43.064379,-29.763506], delete-one [-38.351713,-33.300722]. Ratios may exceed 100% and are not proportions of a total.

## Polarization: low minus high polarization R, each horizon

| Study/encoding | Short pp; positive units | Delayed pp; positive units |
|---|---|---|
| Stickleback residual | +43.309734; 12/12 PASS | +24.470042; 12/12 PASS |
| Stickleback raw-local | +121.366160; 12/12 PASS | +66.980035; 12/12 PASS |
| Ayu residual | -.001085; 3/7 FAIL | STOP (6/7 high-state denominators positive) |
| Ayu raw-local | +3.927114; 3/7 FAIL | STOP (6/7 high-state denominators positive) |
| Zebra residual | STOP (4/8 low-state denominators positive) | STOP (5/8 low-state denominators positive) |
| Zebra raw-local | STOP (3/8 low-state denominators positive) | STOP (5/8 low-state denominators positive) |

Do not drop failed denominators. Stickleback low-polarization association robust to both feature representations in this dataset; no independent cross-species confirmation. Low-speed/low-P short stickleback ratio STOP under both encodings (11/12 positive PhiG); all state gains remain in receipts. Separate state-rank thresholds, no same physical velocity assumption.

## Actual source replay and numerical audit
Ayu artifact 15006310420 ZIP SHA256 2c788da11ebf374b31d61d399a5b0c110a9b06de575210df6c6faab65ace0278, JSON SHA256 9b0f55edf2751f4ad0fe434ba236014f65232eaa8964ccb1008c10546b50dd0c. Zebra artifact 15006056741 ZIP SHA256 0001885ee8914f09f3f778fdeeb66be492e860b0fd664b56ab4ba10826f8a714, JSON SHA256 3f04ffc96eef2dcb72289749a8a6875d99e74ce01f03649abb4d5cd1f0441e7d. Both downloaded ZIP hashes verified in local runtime. Every v48 full/state MSE replay exactly (max absolute 0); reduced B/BG/BGL replay max 7.27596e-11 / 3.46945e-18; state partitions max 1.04046e-9 / 1.45717e-14. Direct feature/moment parity fixtures passed in source jobs. Local independent score audit from saved per-unit losses checked 673 ayu / 587 zebra arrays/statistics/ratios (np.assert_allclose; gates and count assertions additional), not another fit. Fixed paired 10,000 bootstrap draws, descriptive only.

Stickleback executed locally on already downloaded 12 pinned v49 moment ZIPs and final v49 receipt. Re-executed v50 SHA-pinned script, all source/score replay gates passed; new BLraw/BGLraw fixed linear moment transforms and heldout fits across all nine states. Executed script SHA256 cf8cfd2e52966f52d88be1de883147538e2ee723a673fb5f57feba7395bae150. Local complete source-safe result JSON SHA256 2755ea333588f7a1484198c1862df9d098cd46a16d8947a59d61587d803cdb7a. Reproduce: python validation_fish_school_v51/stickleback_raw_local.py <directory-with-13-v49-ZIPs> validation_fish_school_v50/order_audit.py. No new raw coordinates or coefficients exported.

Conclusion ceiling: temporal shift in the *relative predictive allocation* is not universal under order averaging of the same residual block. Direct near velocity representation is a different question and is secondary. Preserve all earlier nonreplications. No biological claim of fixed social rule, no pooled effect, no arena/environment causal interpretation.
