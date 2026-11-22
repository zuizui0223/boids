# v16 frozen prospective test — pre-stimulus susceptibility gate

Status: SYNTHETIC_ONLY_NOT_FIELD_RESULT. This is a new-seed holdout of the same simulator, not wild fish evidence.

## Discovery versus test
The old v15 seeds 2000–2095, already observed, suggested that at the update-1000 boundary, groups whose last completed calling fraction was < 0.90 (5/96) carried 99.56% of positive finite pulse effect mass. That is exploratory training, and could reflect a bounded response with near-ceiling controls. Do not reuse those 96 as confirmation.

## Frozen before independent outcomes
- Simulator: validation_fish_boids_v15/simulation.py exactly as SHA256 a7720cd1a482bbaff49edc9d1b15e4493bc7614cd9715e8e116cd94f583a4bdb, default 32 agents, PCG64 original updates.
- Independent, uninspected model seeds **3000–3191 inclusive, n=192**. No seed exclusion/enrichment or threshold tuning.
- At t=1000 completed updates take q_i = calling fraction of last completed update (trace index 999). Define at-risk q_i < 0.90; already-high q_i >= 0.90. Membership fixed before playback.
- From the same pre-cue state and RNG, simulate two natural histories until t=6000 completed: no cue control and cue 0.8 on update indices [1000,1040). Same native weights audio=5, heard=3. No state transplant or motor cut.
- Primary seed response D_i = mean(pulse minus control calling fractions at global update indices [1040,4040)). Primary holdout contrast = mean(D_i | q_i<0.90) minus mean(D_i | q_i>=0.90), in unit calling fraction.
- Report at-risk/already-high n, means, primary contrast, seed-paired within-stratum 10,000 bootstrap percentile95% interval with fixed seed 2026112220, and all sign counts. If either stratum has fewer than 2 seeds, report no interval/confirmation.
- Secondary descriptive outcomes fixed now: full-192 mean D; [1040,1240) and [5000,6000) contrasts; fraction of positive effect mass in at-risk stratum; proportion D_i > 0.005 per stratum (0.5 percentage points); control future headroom H_i=1-mean(control call fraction, [1040,4040)); ratio sum(D_i)/sum(H_i) per stratum if H>0; first 200-update moving window >=.90 confirmation and explicit censoring at t=6000.
- Save all seed values and full common prefixes [0,1000) and both arm traces [1000,6000) with receipts/hashes. Include pre-cue mean [800,1000), initial q, and no-pulse future means; never use the latter for cohort assignment.
- Use Python3.12 pinned numpy2.3.5/scipy1.17.0, common RNG, data validation, exactly two parallel CI workers. No post-hoc changes to model or seeds.
- A replicated positive risk-high contrast alone cannot rule out the 0..1 ceiling. Headroom normalisation is only descriptive and not a pre-cue predictor. No stationary or biological memory/social-causation claim.
- The v15 result is training; new v16 seeds are the prospective holdout. Keep PR248 Draft, main unmodified.
