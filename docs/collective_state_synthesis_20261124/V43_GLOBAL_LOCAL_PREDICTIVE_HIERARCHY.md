# v42 completion and v43 cross-study hierarchy (2026-11-25 JST)

## Original v42 completion
Both source-verified workflows completed successfully ([run 45404183787](https://github.com/zuizui0223/boids/actions/runs/45404183787)). All source-authentication and v30 baseline replay gates passed. The frozen v42 joint ratio test is NOT ADMITTED for either tetra or ayu because at least one file has nonpositive incremental near gain. This is an honest STOP, not a positive replication. Retain all negative observations.

| Dataset | Short near gain (% of GLOBAL MSE) | Delayed near gain (% of GLOBAL MSE) | Positive files short / delayed |
|---|---:|---:|---|
| Tetra, 6 files | 1.762360 | 0.002776 | 6/6; 3/6 |
| Ayu, 7 files | 0.822353 | -0.006778 | 6/7; 3/7 |
| Stickleback, 12 original shoals, 84 recordings (v33b) | 0.876270 | 1.652469 | 12/12; 12/12 |

## NEW v43: global-to-local predictive hierarchy
Post-result exploratory reaggregation, NOT a preregistered or independent confirmation. Define B = MSE of G_geometry (own motion and geometry); G = MSE of GLOBAL; N = MSE of NEAR_TRUE. Global increment Dg = B-G; local increment Dl = G-N. On the same held-out observations in each study, calculate R=100*mean(Dl)/mean(Dg). This is a ratio of nested predictive improvements, not social information flow, variance explained, or a causal fraction. All source files/shoals retained including negative Dl. Every Dg is positive in both horizons across the 25 scored units, so no ratio denominator exclusions.

| Dataset | Global gain short / delayed (% of B) | R short / delayed (%) | R change (percentage points) | Descriptive paired 95% bootstrap interval | Units with R decrease |
|---|---|---|---:|---|---|
| Tetra | 17.714741 / 12.599232 | 8.186193 / 0.019259 | -8.166933 | [-8.896790,-7.588890] | 6/6 |
| Ayu | 11.405929 / 13.359527 | 6.387523 / -0.043959 | -6.431482 | [-9.233631,-2.451897] | 6/7 |
| Stickleback | 1.824171 / 4.986350 | 47.160329 / 31.487374 | -15.672956 | [-18.717515,-12.544360] | 12/12 |

Leave one existing evaluation unit out of the aggregation (NO model retraining): change ranges tetra [-8.375439,-7.884068], ayu [-7.151363,-4.882920], stickleback [-16.484069,-14.167822] pp. All 10,000 paired unit-resampling draws have positive global denominators per study. In all three datasets and 24/25 scored units, the local-to-global increment ratio decreases with prediction horizon. This does NOT mean absolute local predictability always decreases: stickleback local gain increases, but global gain grows faster. It also does NOT establish independent groups among tetra or ayu recordings, or a universal fish law.

The additive total improvement B-N is exactly Dg+Dl. Its order-dependent local share (%) also decreases: tetra 7.566763 to 0.019256, ayu 6.004015 to -0.043978, stickleback 32.046904 to 23.947070. Negative estimates are kept as adverse predictive increments, not physical negative information. Ratios are formed within each dataset/horizon, not pooled across native MSE units.

## Source and audit
- Tetra artifact 14925460476, ZIP SHA256 1d98e9ec844d742e9f4ebf8427bdb6004d2dbaf9687719bcf098721275ac866f; JSON SHA256 356102aab4e2afddbd14ae9421e07f8d23eed1aaff577875e8d866ec8eaa49b4.
- Ayu artifact 14923998689, ZIP SHA256 ab935d966b2bca6c54b56a68b8908004b24f625143ffc6f26bf410310466749b; JSON SHA256 84e30c425ec498b0474ea6be78de506514331f0f49038ce4cf0ebcc3a6676119.
- Original v33b stickleback artifact 14906668781, ZIP SHA256 4aa514578f04b850c977070fb49bc0773aec831fed0b7260efb7dc73bdffed7a; JSON SHA256 a409e041e0f8b3392836ff256c6edf75a1d2c29ded425a52383f1ac2f1801386.
- Reaggregation code: [validation_fish_school_v43/reaggregate.py](../../validation_fish_school_v43/reaggregate.py). Executed locally on the three actual downloaded source-safe artifacts with matching ZIP hashes, fixed NumPy RNG 20261125, paired 10,000 evaluation-unit draws, equal-file or equal-shoal means. No new model fitting and no raw coordinates redistributed. Intervals are descriptive and do not account for dependence from overlapping training folds or potential reuse of individual fish.

## Ecological integration and next independent test
Evidence supports a narrower hierarchy hypothesis: local and aggregate predictive increments can have different persistence, and the aggregate increment becomes relatively more important at longer prediction horizons in these three existing datasets. The cross-system extension to choruses, birds and tidal opportunities remains an analogy/hypothesis, since spatial neighborhood and temporal activity states are different measurements. A spatially correlated external field can also create these patterns. For a genuinely new study, freeze the same six panels and both horizons plus the R contrast, use independently identified held-out shoals, check trajectory filtering does not use future targets, evaluate matched external-field/identity controls, and report both absolute and relative gains. Preserve v42 STOP, all prior results, and draft PR #252; no main merge.
