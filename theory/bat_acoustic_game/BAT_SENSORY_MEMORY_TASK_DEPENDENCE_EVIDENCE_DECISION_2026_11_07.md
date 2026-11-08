# Bat acoustic flight and task-dependent memory — 2026-11-07 evidence decision

**Scope: no new animal measurements. Scientific status: original-source architecture audit + mathematically exact source-motivated filtering examples, NOT a new bat ecological law or a source-exact Matlab replication.** Keep `boids` Draft PR #36 separate from original `batter` frozen JAE/BE manuscripts.

## Status of actual independent bat sources

- `Goldshtein et al. 2025`, *PNAS* DOI [10.1073/pnas.2407810122](https://doi.org/10.1073/pnas.2407810122) — published simultaneous on-board sonar and group-emergence spatial spreading for `Rhinopoma microphyllum`. Europe PMC original `supplementaryFiles` retrieved with provider authorization, 11 members: 1 PDF, 2 MP4, 4 JPG, 4 GIF; **zero machine-readable synchronized source measurements**. Original Mendeley `10.17632/k7pt2j84f7.1` was source-catalogued in earlier work, but original data bytes NOT admitted due provider API HTTP401/404. **Source-empirical transport STOP.**
- `Gilmour et al. 2021`, *J Exp Biol* DOI [10.1242/jeb.242715](https://doi.org/10.1242/jeb.242715) — published acoustic-deterrent flight/feeding-buzz behavior with experimental site×night blocks; Europe PMC original ZIP 19 members: 9 GIF, 9 JPG, 1 PDF; **no original raw acoustic+flight table**. Original Mendeley DOI `10.17632/gb45nfkkk5.1` not admitted. **Source-empirical transport STOP.** Its 1167 trajectories cannot be declared 1167 distinct biological bats.
- These two original studies cannot be pooled with 2024 *Molossus nigricans* natural capture interactions as if same acoustic intervention or common experimental unit; published scientific outcomes are distinct prior art. [Verifiable original archive member inventory](https://github.com/zuizui0223/boids/actions/runs/42338871309).

## Verified *source code*, not source animal data, of a third independent study

**Mazar & Yovel (2026), *eLife*, DOI [10.7554/eLife.105571](https://doi.org/10.7554/eLife.105571)**, original source [omermazar/Colony-Exit-Bat-Simulation](https://github.com/omermazar/Colony-Exit-Bat-Simulation), original MIT commit `a74fb61a8efb57ca37693893c3bd7b35fa94fa89`. Seven original Git blobs independently checked (SHA and sizes) including sonar/flight/maneuver decision MATLAB scripts, `Pipistrellus kuhlii` / `Rhinopoma microphyllum` default XLSX and one model MAT file. [Original code verification](https://github.com/zuizui0223/boids/actions/runs/42339355443). Original actions include `ConfusionObs`, `ObsMemorySize`, acoustic masking, repeat-echo clustering and fast steering; authors ALREADY demonstrated that recent observations plus multi-call sensor memory help simulated bats exit a densely occupied cave.

**Do not falsely describe this as our numerical replication.** The original code uses absolute Windows paths, MATLAB table/GUI, `polyshape` and MATLAB-specific signal processing, so the original source model and its published figures have NOT been executed here. `Swarm_200bats_New_1.mat` was verified only as original one `curr_strct` 1×1 MATLAB STRUCT, NOT an independent observation of 200 real animals. Our `boids` original synthetic flock models similarly omit calibrated acoustic echo receivers.

## Closed exact mathematical contrast (source-motivated but not a bat source-effect estimate)

Take a ONE-dimensional allocentric target location random walk `x_t = x_(t-1)+eta_t`, q = per-call target change variance, r = per-call independently measured echo-location noise variance. Under *all echoes accepted*, equal-averaging K most recent echo coordinates estimates current target position with
```
MSE(K) = r/K + q*(K-1)*(2*K-1)/(6*K).
```
This is a standard filtering-theory bias/variance trade-off, NOT a new theorem. Mazar paper's original five-echo memory `ObsMemorySize=5` is only a reference to the original source architecture; its original algorithm is NOT this arithmetic moving average. With K=5 compared to a single accepted echo, **accuracy is improved iff q/r < 2/3**. For `q=0`, longer memory is more accurate provided perfect self-motion compensation. A fast-changing target can instead favor a short memory. Fixed seven q/r settings × ten K, 40,000 simulated synthetic independent histories per setting verified exact formula to max 2.01% relative MC error (within frozen 5%), 12 tests passed. [First exact formula CI](https://github.com/zuizui0223/boids/actions/runs/42339580008).

Extended with independent Bernoulli accepted-echo probability `p` for each of K emitted pulses. **Condition on at least one accepted echo**; the all-missing event is a separate outcome `P(no usable echo)=(1-p)^K` and cannot be assigned error zero. Conditional on accepted lag subset S and `n=|S|>0`,
```
MSE(S)=r/n + q/n² * sum_{h=1}^{K-1} [count(j in S with j>=h)]².
```
Exact enumeration of all received subsets for p={1,.75,.50,.25}, q/r={0,.25,.50,1,2,4}, K=1..10 yields **240** cases. The p=1 formula replays the prior exact all-echo formula with zero discrepancy; 11 regression tests passed. There is no arbitrary fitness cost for no returned echoes. [Exact source-inspired availability CI](https://github.com/zuizui0223/boids/actions/runs/42339782477).

**Post-output analytical corollary** from the frozen model: for five emitted calls vs single call, the condition where MSE(K5 | echo available) is still lower becomes more restrictive as p falls:

| Probability an echo is usable p | q/r break-even threshold (memory 5 vs 1 conditional accuracy) | P(all five are missing) |
|---:|---:|---:|
| 1.00 | 0.6667 | 0 |
| 0.75 | 0.5467 | 0.000977 |
| 0.50 | 0.3542 | 0.03125 |
| 0.25 | 0.1528 | 0.237305 |

This is NOT a real-bat numeric threshold, and the last column represents **missing position estimate**, not a behavioral failure or an observed feeding attempt. With a mobile target and strong masking, longer memory reduces all-missing risk but can make the accepted-position estimate stale and less accurate. The Pareto frontier correctly reports potentially many non-dominated K, not one uncalibrated “ecologically optimal K.” [Frozen 310-case analytic/MC exact source ledger](BAT_ECHO_MEMORY_TASK_CONDITIONED_THEORY_LEDGER_V1.json) and [fail-closed replay script](verify_bat_echo_memory_theory_ledger_v1.py). Original unmasked analytic outputs fixed and source SHA-checked.

## Relation to previously published positive and negative *Molossus* findings

Krivoruchko et al. (2024), *PNAS* DOI `10.1073/pnas.2321724121`, ORIGINAL already observed the rise and subsequent decline of successful capture as conspecific calls become dense. Using that same original published source after correcting the `numel_5swindows` exposure mistake, we found 10 successes/36 attacks under ≥76 other-bat calls per 5s vs 119 successes/173 attacks under 26–75 calls, **in six same original bats**; five had lower high-density success and one tie. Within-bat coarse flight-time thirds retained all 36 high attacks in nine matched bat×third strata. [2024 source within-bat CI](https://github.com/zuizui0223/boids/actions/runs/42334035042). The source authors' original bat-ID GLMM ALREADY controlled individuality; this is narrow descriptive robustness and NOT a newly discovered ecological pattern.

**No mechanistic bridge currently exists:** *Molossus* data do not record actual prey displacement `q`, source-aligned echo-location error `r`, or independent accepted-echo probability `p`. The *Mazar* original source is a simulated cave-exit task, not a measured hunt. Consequently the filtering model does NOT explain the observed 2024 attack-success effect; **do not use the same record count 36 or 10 to estimate p, q or r**. Data on conspecific emitted call rate are NOT independent counts of receiver-lost echo returns, and acoustic sound density is not the number of neighboring bats.

## Publication/next-test decision

**What is supported:** a precise standard filtering-theory prediction that a task-dependent echo memory horizon trades off all-echo-missing risk against stale-coordinate error. Source original 2026 MATLAB architecture supports this as a relevant model comparison but does not validate numerical parameters or behavioral payoffs. Mathematical model and published papers are separate evidence tiers.

**What is not supported:** real bat task-conditioned memory strategy, prey capture payoff for q/r, biological inversion of sensory mixing, source-independent species replication, a new mathematical law, the claim that the original 2026 echo-memory benefit was our finding, or a general 3D niche partition principle.

**Genuine source threshold for a publishable follow-on without new observations:** identify an independent, authorized original archived dataset with synchronized received echo-level detection/masking, bat/flight ID, bat self-motion correction and environmental-target motion (or actual task) to estimate `p, q/r` *before* opening held-out obstacle/prey performance outcomes. Run same 1-versus-5 echo rule on independent bats and separately held-out static walls vs mobile prey. True agent-level q/r, original source signal reliability and reward must be calibrated without tuning to the signs. Otherwise retain PR #36 as a **replicable source-audited prospective theory demonstration**, not a bat-specific original empirical manuscript.

No new field/lab work, source redistribution, journal submission, `batter` modification or merge was performed.
