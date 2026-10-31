# When does sonar signal separability become foraging benefit?

**31 October 2026 — completed zero-new-measurements phase 2.** This is a repository source-reanalysis plus an **uncalibrated theoretical bridge**, not a replication of the 2020/2026 complete published models, nor an independent new bat experiment. No original per-bat rows, publisher MATLAB code or original audio files are redistributed.

## Research question

Why can a spectral jamming-avoidance response (JAR) decrease *potential acoustic misdetections* in a group-flight model yet fail to improve *prey detection/capture* in a predator–prey model?

The two studies have different biological response variables and different simulation architectures:

- **Mazar & Yovel 2020**, DOI 10.7554/eLife.55539: sensorimotor predator–prey simulator with correlation and filter-bank receiver pathways; published result: applying frequency JAR did **not** improve modeled insect sensing/capture. Publisher original archive downloaded transiently, **803,643 bytes, SHA256 `913dc06b606cecaeb33558de3ab97f8eca618eda302bd1cb720c2b11fc74baff`, 89 archive entries**. Safely listed source modules include `IsPreyDetected.m`, `IsPreyMissDetected.m`, `IsPhantomEchoesDetectected.m`, `Interfernce2DetectedPreys.m`, and `FilterBank_detector.m`. **Original MATLAB model has not been executed.**
- **Hase et al. 2026**, DOI 10.1098/rspb.2026.0921: sound-frequency leaky-integrator playback model and 2D group flight simulation. Figure 5f reports fewer possible cross-correlation-based misdetections under JAR; this does **not** count true prey captures. Public data DOI 10.6084/m9.figshare.30937379 is accessible and exposes 15 files, including the 2026 experimental `Data_jamming.csv` and R scripts. The complete group-flight simulator executable was not independently identified in this source manifest, so **Figure 5f has not been numerically rerun**.

Read-only primary source gates and inspections:
- [Publisher archive inventory run 41189765472](https://github.com/zuizui0223/boids/actions/runs/41189765472)
- [Source semantics 2020 MATLAB / 2026 R run 41190038624](https://github.com/zuizui0223/boids/actions/runs/41190038624)
- [2026 stimulus-only preflight run 41190147131](https://github.com/zuizui0223/boids/actions/runs/41190147131)

## Actual published 2026 data, reanalysed without new measurements

Source experimental table `Data_jamming.csv`: 12,308 rows, SHA256 `2998ad0e57cc51cb4a98f48de6444d543f925994600cd5574f25e40babcfa367`. The outcome-blind metadata inventory counted **11 original distinct bat-ID labels** across all experiments (not 11 new bats); original source ON/OFF row counts 6,841/5,467; 105 qualified within-bat design strata. After the frozen numeric eligibility and each condition's biological-sample aggregation, all three source stimulus families retained **7 bats each**, while low- versus high-IPI slopes overlap in only **four identical bat IDs**.

Under the [locked analysis contract](PUBLISHED_JAMMING_REANALYSIS_CONTRACT_V1.md), each eligible bat × stimulus condition has a within-context median ON−OFF terminal frequency response, and bat-level OLS response slope across at least three stimulus levels. TF was used in original dataset units (no speculative rescaling).

| 2026 source context | biological bats | per-bat slope result | equal-bat mean / 95% bat bootstrap | Status |
|---|---:|---|---|---|
| **IPIlow**: low-frequency jammer, slope vs log10(IPI ms) | **7** | **7 negative / 0 positive** | **−1.0060** [−1.4669, −0.7013] | Pre-specified slope direction supported under source sign test p=0.0078125 |
| IPIhigh: high-frequency jammer, slope vs log10(IPI ms) | 7 | 4 negative / 3 positive | +0.1091 [−0.1320,+0.4070] | Mixed / no common direction |
| SPLlow: low-frequency jammer, slope vs dB source | 7 | 0 negative / 7 positive | +0.04756 [+0.03310,+0.06179] | Descriptive secondary, source direction already known |

Robustness to replacing ON−OFF **median** with **mean** (same groups):
- IPIlow **7/7 slopes remain negative**, equal-bat mean −0.9559.
- IPIhigh changes to **2 negative / 5 positive**; no robust signed interpretation.
- SPLlow **7/7 positive**, equal-bat mean +0.04799.

Exact bat-level signs are **a secondary reanalysis of published outcomes**, not a new independent test of the source paper's already-known stimulus effects. The ON/OFF average cannot exclude trial/temporal drift and does not directly identify receiver SNR, 3D flight path, foraging target detection or any prey payoff. The source paper's published TF directions were inspected before this analysis; the contract was frozen before this branch's numerical TF opening, not before publication.

Reproducible read-only result: [GitHub Actions run 41190407233](https://github.com/zuizui0223/boids/actions/runs/41190407233), scripts `published_jamming_preflight_v4.py` and `published_jamming_response_v1.py`, aggregate `SOURCE_BOUND_RESULTS_LEDGER_V1.json`.

## A bounded capture-versus-misdetection theorem (not an empirical parameter estimate)

Let `F0` and `F1` be **potential** misdetections before/after JAR from the 2026 published model. Their ratio is `rho = F1/F0`. Suppose a hypothetical fixed fraction of those become costly false actions with recovery cost. Let `W0` denote their **unadjusted** false-alarm workload per unit active foraging time. Let JAR decrease true prey detection `d` by fractional `delta`. Hold prey encounter rate, capture-given-detection and handling time constant across JAR/no-JAR.

Under the explicitly assumed renewal-reward model
```
R0 = lambda*d*q           / (1 + lambda*d*h           + W0)
R1 = lambda*d*(1-delta)*q / (1 + lambda*d*(1-delta)*h + rho*W0)
```
it follows exactly that `R1 > R0` iff
```
(1 - delta - rho)*W0 > delta.
```
If `delta >= 1-rho`, no finite positive false-alarm cost improves capture under **this** model. If `delta=0`, `rho<1` and `W0>0`, capture strictly improves. If `W0=0`, lower potential misdetection cannot improve capture: there is no false-alarm handling burden to remove.

Published 2026 group-simulation means from Figure 5f (NOT data refitting) and resulting **arbitrary illustrative `delta=.02` thresholds**:

| Bat group size | Source mean potential misdetections no-JAR → JAR | relative reduction | `W0*` when fixed baseline workload across groups | `c*` when fixed cost per source-counted event |
|---:|---|---:|---:|---:|
| 4 | 0.14 → 0.01 | 92.9% | 0.022013 | 0.157233 |
| 8 | 1.37 → 0.12 | 91.2% | 0.022411 | 0.016359 |
| 16 | 5.98 → 2.49 | 58.4% | 0.035485 | 0.005934 |
| 32 | 15.77 → 10.01 | 36.5% | 0.057929 | 0.003673 |

**The important normalization sensitivity:** a common baseline false-alarm workload `W0` makes the *needed* workload increase with group size, whereas a common **per-source-event cost** `c` implies `W0=c*F0` and makes the threshold **decrease** with group size. Under fixed `c=0.01` and `delta=.02`, the toy predicts no benefit for 4 bats but positive benefit for 16 and 32. Under fixed `W0=.05` and `delta=.02`, the opposite density pattern is possible: improvement for 4–16 but not 32.

These are not contradictory mathematics; they are **different exposure and false-action mapping assumptions**. The published counts are *potential* misdetections, not verified independently time-standardized behavioral false alarms or actual false-response latencies, and no `c`, `W0` or `delta` has been calibrated to bats. Hence neither simulated ranking is a biological finding or evidence that a colony of a particular size benefits more.

The code is `endpoint_bridge_v2.py`, source `test_endpoint_bridge_v2.py` and the GitHub Actions full **31-test** synthetic + analytic suite. This theorem uses only the stated idealized assumptions, not the 2020 MATLAB dynamics.

## Best scientific conclusion today

1. **Empirically supported (published reuse):** real bats adjust emitted terminal frequency in an asymmetric stimulus-dependent way; the low-frequency IPI slope sign survives equal-bat and mean/median sensitivity, whereas the high-frequency IPI slope does not show one reproducible sign in this source reanalysis. No new independent species was tested.
2. **Computationally established:** a large reduction in potential misdetections does **not uniquely predict** prey-capture improvement. The sign and its group-size ordering depend on unmeasured detection penalty, false-alarm recovery, and which exposure unit is kept fixed.
3. **Not established:** the actual 2020-vs-2026 discrepancy has been explained causally. Different models/tasks/species and unmeasured conditional bridges remain. This is a **conditional theory and source-reanalysis**, not a publishable general bat law yet.

## Next action without any new bat measurement

Audit and port the original, source-frozen 2020 prey/phantom detector to a **paired fixed-physics forward model**, and implement the published 2026 leaky TF response as a *separate* module with declared source parameters. Predict BOTH (a) false acoustic detections and (b) actual target detections and post-detection capture in identical synthetic bat×prey scenes and hold out contexts. Keep pre-existing source code untouched and original source files outside public GitHub. Compare JAR/no-JAR on identical world seeds and receiver physics, with task context and frequency baseline separately controlled. If original 2020 MATLAB code cannot be replayed or its dependencies identified, explicitly STOP the original-model reproduction claim and label any new code as a novel independent approximation.

**Do not submit a third bat paper or claim the 2020 and 2026 numerical models have been faithfully merged until this source equivalence/replay gate passes.**
