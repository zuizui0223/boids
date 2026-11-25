# v54 initial source stop and singleton-control counterexample

2026-11-25 JST. Original independent study Liu & Burbano 2025 DOI 10.1098/rsos.250033; author release exact commit 2eb7fdd4172fff870224b7cbc4d7bdb086b5fbf0 and CC0 license confirmed. Main and previous results untouched.

Initial run 45585192596, job 139104881243. Author clone and synthetic grid/target isolation/standardized Ridge backend/global-preserving label-swap fixtures passed. Real scoring never started: first source CSV failed pre-outcome TRIAL_DURATION_STOP (expected published 10min ×30fps, allowed 17000–18001 rows). Source STOP artifact 15007678981 ZIP SHA256 f91e600077fa4050f72ff96729cd1cce84d30bcaf80413c451fe02c2ed36c292 verified after download. Singles.zip Git blob b1aa7ec2c673cf351593b9c661fb556a7fa2cc2a SHA256 bf0c6bbfa5b7fea4e1b89d2a3ef84be6bf4d3e10f7d05a198d97597b4b1b5086, 20 CSV member paths, first explicit header Frame;Time;X_Arena0_Ind0;Y_Arena0_Ind0 confirmed. Actual row count not logged by first run. Separate schema_diagnostic.py retrieves all original files' actual row counts and clock/coordinate structure without fitting or exporting raw trajectories. No changing the scientific endpoint based on prediction scores, no inferred source semantics. Initial STOP retained.

## Executed no-social-edge counterexample for independent singleton controls

Frozen before calculation at 6dc00f189a04a16357aa4a3c44d5cd7cf650aa91. Code validation_fish_school_v54/singleton_control.py, local SHA256 b070d9d98f1dde3a8f9be0e30c10f17b38684c9290affd53e77a0838da1ced50; result singleton_control.json SHA256 8ac794355dc4c28b280de217ba9a69e077eb1cfaf3c0a6161ea3a5935e355546. Exact population linear covariance projection. Three static sites, no interindividual edges; shared global field, patch field shared between nearest sites, independent individual process. Conditions X/Y differ solely in external patch variance (.5/2), NOT real light treatments. Independent-single pseudo triads have same marginal individual process but independent realizations of external fields; score the same real-trained coefficients. Random sign control preserves global predictor, erases local cross-covariance in population.

| Condition | Horizon | Co-observed triad A (%) | Independent-single pseudo triad A (%) |
|---|---|---:|---:|
| X | Short | +.07792813 | -.52427498 |
| Y | Short | +.29025784 | -2.43034267 |
| X | Delayed | +.00307667 | +.04347580 |
| Y | Delayed | +.00095047 | +.05630971 |

Short real A change Y−X = +.21232970 pp, pseudo change = −1.90606770 pp. Oracle loss from true present latent states has analytically zero neighbor increment. Pseudo negative short gains are domain-transfer errors, not proof of real social causality; delayed pseudo gains can even be positive. All results synthetic, not empirical estimates. Even a light-associated real-versus-pseudo difference in the eventual experiment could reflect changes in geometry or common environmental responses, and darkness does not eliminate mechanosensory channels. This strengthens interpretation guardrails without changing v54 frozen primary. Draft PR #256.
