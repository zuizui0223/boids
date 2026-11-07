# Bat echo memory timescale gate: static spatial walls vs moving target — 2026-11-07

**New dimensionless THEORY demonstration, NOT a new bat observation or a verified reproduction of Mazar & Yovel (2026).** Independent source code and prior art were inspected before this mathematical test. This is a general state-estimation tradeoff known in filtering theory; do not call the equation itself a new mathematical discovery or a confirmed bat control law.

## Why this source-anchored comparison is worth attempting

Mazar & Yovel 2026 *eLife* DOI `10.7554/eLife.105571` and original MIT source `omermazar/Colony-Exit-Bat-Simulation` pinned commit `a74fb61a8efb57ca37693893c3bd7b35fa94fa89`: original code's `ObsMemorySize` (default 5 calls), `ConfusionObs`, repeated-echo grouping and separate fast collision-avoidance decisions. **Published prior art already established that multiple-call integration facilitates cave exit under severe masking.** Original source files and model shapes were authenticated in boids CI `42339355443`; the original MATLAB simulator was NOT run.

Our earlier independently published observational `Molossus nigricans` 2024 *PNAS* source DOI `10.1073/pnas.2321724121`: in six same original bats high ambient call density associated with lower attack success, but original paper already reported that relationship. No actual prey-position state trajectories, receiver noise, memory parameter or animal sensory latency measured in this source.

**Distinct scientific question:** Can the same multi-call integration strategy be strongly helpful for *stationary spatial targets* yet neutral or harmful for *rapidly changing targets* without any change in the bat's auditory control architecture? If yes, a task-dependent memory horizon, rather than one universal bat jamming-avoidance strategy, is a falsifiable prediction.

## Prespecified minimal mathematical model

Use an allocentric ONE-DIMENSIONAL environmental target coordinate x(t), perfect correction of the bat's own motion. At each call x(t)=x(t-1)+eta(t) with independent `eta~N(0,q)` (per-call environmental change, **not measured prey displacement**). Each accepted sonic observation y(t)=x(t)+epsilon(t), independent `epsilon~N(0,r)`, and all K observations are available; `r` is **abstract measurement noise conditional on detection**, not a directly derived masking fraction. A bat's proxy memory estimator is the equal mean of the **current plus K−1 previous observations**, K integer 1..10:

`xhat_K(t)=(y_t + y_(t-1) + ... + y_(t-K+1))/K`.

The exact expected squared current-state prediction error is:
`MSE(K)=r/K + q (K-1)(2K-1)/(6K)`.

- first term decreases with more accepted echoes (noise averaging);
- second term increases with older environmental observations (state drift / stale-memory cost).
- `rho=q/r` defines the time-scale ratio; only dimensionless parameter. **No r or q calibrated to real bats**, no mapping to prey capture.

For r>0, q>=0 and K in 1..10, analytical continuous optimum for q>0 `Kc=sqrt(3*r/q + 1/2)`; choose integer minimum by evaluating the exact expression. With q=0, MSE=r/K decreases monotonically; more accepted echoes help. For original-paper illustrative memory K=5 vs one call: `MSE(5)<MSE(1)` iff `q/r<2/3`. For K=10 vs K=1: iff `q/r<6*(1-1/10)/((10-1)*(2*10-1)/10)` = `0.315789...`. (No claim these are bat thresholds.)

**Fixed parameter grid BEFORE output**: `rho ∈ {0,0.10,0.25,0.50,1.0,2.0,4.0}`, K 1..10, r=1 (only a dimensionless illustrative scale). Monte Carlo 40,000 IID synthetic past-echo histories for each rho (NumPy Generator PCG64, seed 20261107), compare empirical mean squared error to analytic MSE and accept maximum relative deviation ≤0.05 across all 70 conditions. Exactly these seven rho values and ten history lengths; no outcome-driven tuning. Include an off-grid rho=.6667 test of the K=5 crossing for numeric verification only, not another 'biological phase'.

## Stop / claim restrictions

- Simulated source Mazar code contains clustered **discrete obstacle detections**, obstacle geometry, masking *missing echoes*, adaptive pulse rates, multi-target sonar, allocentric movement plus fast obstacle reflexes; the present average-Gaussian estimator is NOT an original bat sonar receiver or original-paper code port. It cannot reproduce Mazar cave-exit success or collisions.
- A STATIC wall is q≈0 only in an allocentric reference frame; a moving bat experiences changing egocentric wall positions. We assume perfect motion compensation explicitly. A dynamic prey can have q>0, but its real movement variance has not been measured or assigned from the 2024 Molossus paper.
- 2025/2021 candidate independent empirical source supplements were checked and contain PDF/video but no original acoustic/trajectory tables; raw Mendeley downloads remain inaccessible. This theoretical contrast does NOT replace independent observational validation.
- All tests, formula, source DOI and original code licensing must be recorded in a new separate file on existing boids PR #36; do not merge/alter frozen batter manuscript or submit new bat ecology publication from synthetic success.
