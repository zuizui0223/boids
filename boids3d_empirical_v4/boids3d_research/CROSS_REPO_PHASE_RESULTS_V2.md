# Boids movement → niche-axis redistribution: four-repository bridge (v2)

**Date:** 2026-10-25  
**Scope:** fully synthetic, known-mechanism test-bed. No wild bat/bird/penguin telemetry was newly fitted, and no frozen manuscript was modified. Units of flight time, resource density and space are arbitrary and **not** calibrated to real species.

## Executive outcome and correction

An ecologically consequential distinction emerged: **a pseudotaxon difference in resource preference can initially appear as horizontal sorting, but depletion and habitat-state tracking can redistribute observable differences between horizontal and conditional-vertical niche axes without preserving the same global spatial-overlap values.** This is a controlled *generative possibility*, not evidence that direct interspecific competition causes wild bats to segregate.

**Major quality correction:** strongly smoothed fine-resolution Bhattacharyya overlaps were misleadingly high. At resource contrast=0.30 and depletion=0.30, 16×16×8 between-group BC is **0.013 without smoothing** but **0.642 with pseudocount 0.06/voxel**. Unsmooothed fine-grid estimates themselves are downward biased by finite spatial sampling. Report a resolution/smoothing sensitivity rather than “high 3D overlap.” At 4×4 horizontal resolution without smoothing the between-group overlap is 0.653; this is evidence for *coarse horizontal sharing*, not actual close-range 3D sharing.

## 1. Source evidence, which must be kept separate

| Repository | Verified empirical/descriptive status in GitHub | Test-bed counterpart (NOT proof of explanation) |
|---|---|---|
| [batter](https://github.com/zuizui0223/batter) | Same-identity vertical-shape repeatability across multiple bat panels. A prospective maintenance synthesis reports 4/4 evaluable fruit-bat panels retain individual strategies at 500 m, while 0/4 supports positive added terrain-relative segregation. Repeatable individual strategy does **not** entail exclusive spatial niches; learned memory remains unproven. | `validate_behavioral_mixture.py`: fixed personal foraging/transit duty cycle yields centered-z self-history, while nights with shuffled duty cycles largely remove it. |
| [ODSP](https://github.com/zuizui0223/odsp) | Native bat `H(Z|XY)=1.392` nats (~4.02 effective states) but frozen bat-to-new-bat conditional transfer failed. Separate Serengeti species-time organization `I(S;T|site)=0.224` nats and three held-out site folds all positive. Descriptive thickness, identity-conditioned partition and transfer are three distinct endpoints. | `cross_repo_phase_scan.py`, `crossover_resolution_audit.py`: estimate `H(Z|XY)`, `I(S;XY)`, `I(S;Z|XY)` and held-out *new-individual* gain at frozen grids. Beware resolution dependence. |
| [louis](https://github.com/zuizui0223/louis) | King Rail: 10/10 birds with positive temporal water-depth retention, hydrological availability coupling reduced 83.8%. Geographic displacement as a causal mechanism is **not** verified because the coordinates lack joinable event IDs. | `state_tracking` moves agents down a known environmental mismatch gradient; control `state_tracking=0` isolates its added value. It is NOT the rail hydrological slope estimator or a matched local pseudo-trajectory. |
| [mina](https://github.com/zuizui0223/mina) | Five Adélie/chinstrap monitoring units have excess contraction of inverse-Simpson effective breeding-component number (19–83%) beyond the fixed-share count-error null. This is breeding-component composition, **not** habitat area nor Boids flight. | Separate `breeding_patch_bridge.py` and `density_breeding_patch_bridge.py` apply explicitly synthetic annual abundance-conditional patch-choice nulls. Do NOT interpret aerial voxels as breeding sites. |

## 2. Forward 3D dynamical mechanism and 90-condition scan

`eco_dynamics.py` simulates two pseudotaxa, seven individuals each, over 3 nights. All animals share a 3D landscape with two renewable prey/resource fields. Conspecific alignment and inter-individual collision repulsion operate within each time step; individuals use species-labeled prey preferences. Three resource-stock counterfactuals are implemented: `shared` (all agents reduce the same stock), `species` (only conspecifics share), and `private` (self-only depletion). Zero depletion returns **bit-for-bit identical tracks** across these stock structures.

`cross_repo_phase_scan.py`: 3 preference contrasts × 3 depletion levels × 2 habitat-tracking levels × 5 seeds = **90 simulations**. At strong resource preference (0.30), no habitat tracking:

| Resource consumption | I(S;XY) nats | I(S;Z\|XY) nats | Mean new-individual vertical predictive gain nats/record | Between-pseudotaxa smoothed 3D BC* |
|---:|---:|---:|---:|---:|
| 0.00 | 0.686 | 0.007 | +0.012 | 0.567 |
| 0.30 | 0.107 | 0.436 | +0.473 | 0.642 |

\*BC column uses 16×16×8 plus 0.06 symmetric pseudocount and **cannot be interpreted literally as physical niche-sharing strength**. Across five seeds, depletion 0→0.30 lowers `I(S;XY)` by 0.579 and raises `I(S;Z|XY)` by 0.429 nats; all five contrasts have those signs. Species-conditioned `Z|XY` also predicts previously unseen individuals better. This supports a model-specific *redistribution of the dimension carrying identity*; it does NOT imply an observed reversal of competitive displacement or ecological equivalence of flight modes.

With strong preference **and** strong depletion, state tracking 0→0.8 increases the local mismatch-buffering advantage by **0.418**, but reduces `I(S;Z|XY)` by **0.195** nats in the five paired seeds. In this generating system, maintaining a similar *experienced state* partially offsets species-encoded vertical differentiation. No blanket trade-off law is inferred from these parameter values.

## 3. A crossover exists in one grid but is not a universal ecological threshold

`crossover_and_competition.py`: 9 depletion levels, five seeds, 85 worlds including three resource-stock counterfactuals at four levels. At `4×4×8`, the descriptive equality `I(S;XY) = I(S;Z|XY)` appears at interpolated consumption values **0.072–0.084** across five seeds. It is a smooth operational information-crossover, not a discontinuity or a phase transition.

`crossover_resolution_audit.py`: the **identical trajectories** yield radically different crossovers as XY grids change:

- `2×2×8`: `I(S;Z|XY)` exceeds horizontal identity information **even at zero depletion**; there is no internal crossing.
- `4×4×8`: one crossing in each of five seeds at approximately 0.072–0.084.
- `8×8×8`: crossings occur later, between **0.08 and 0.15** depending on seed.

Therefore report only **scale-conditional** crossover curves, with all grids visible. Coarse XY conditioning fails to separate original geographic sorting from within-place vertical sorting; very fine XY conditioning reduces joint support and has sparse-sample limitations. Stronger data and methods are required before a predictive real-world threshold can be estimated.

## 4. Competition versus depletion: direct counterfactual

For depletion=0.30:

- Shared by both pseudotaxa: `I(S;Z|XY)=0.436` nats.
- Shared only within pseudotaxa: `I(S;Z|XY)=0.408` nats.
- Self-only private stock: `I(S;Z|XY)=0.401` nats.

The **shared-minus-species** vertical-information difference is only +0.028 nats (positive in 4/5 seeds), compared with the +0.429 no-depletion-to-all-shared contrast. Thus most of the generated shift is **not attributable uniquely to heterospecific stock-sharing effects**. Shared/species/private treatments alter realized resource capacity and can affect trajectory length/quality; they are not instrumented real-world removals of competitors. Additional density-controlled interventions would be needed to identify competitive displacement or resource-mediated coexistence.

## 5. Simultaneous local co-use is distinct from occupancy overlap

`synchronous_local_test.py`: compare actual same-clock local horizontal proximity (within 2 model units) and pairwise absolute vertical separation against circularly time-shifted pseudo-synchrony (99 null replicates, five seeds). Results require sufficient nearby pairs.

- With strong preference **but no depletion**, no heterospecific pair meets the frozen minimum local co-use criterion in the five simulations. Heterospecific matched vertical separation is **not estimable**, not zero.
- With shared depletion, heterospecific proximity is evaluable. Its synchrony-calibrated vertical separation is not consistently positive or significant across seeds (**0/5** p≤0.05 in the run). This experiment cannot establish synchronized competitive repulsion as the cause of the conditional distribution differences.
- A positive conspecific shift is also possible due to social movement or common environmental state, so synchrony alone is not aggression/competition proof.

## 6. batter-type individuality and louis-type state buffering

`eco_dynamics_behavioral_mixture.json`: a stable personal foraging/transit duty cycle, explicitly supplied as a model parameter, produces mean **+0.130 nats/record** of null-centered centered-height identity (5/5 synthetic seeds at Monte Carlo p≤0.05). Swapping that personal duty cycle between nights reduces mean gain to **+0.003** (1/5 passes); shared-pool consumption without personal duty-cycle differences produces approximately zero mean centered identity. This proves sufficiency within this simulator, not learned memory in field bats.

`eco_dynamics_factorial_results.json`: the local-state buffering score with heterogeneous available states is ~0.138 under no tracking and ~0.613 under strong tracking, a paired difference **+0.474**. A spatially homogeneous environment cannot provide alternative local states, so tracking cannot improve this metric. Note nonzero no-tracking buffering is produced by source covariance and matched-alternative selection, not a purposeful strategy. The score differs from both the louis SRI and the used-on-available hydrology regression slope.

## 7. mina-type annual contraction: separate model class

`annual_breeding_patch_bridge.json` shows that a prescribed demographic decline (900→120 animals in six invented components) with spatially heterogeneous substrate filtering plus high patch retargeting yields **−35.9%** mean inverse-Simpson component change and **20/20** synthetic worlds below the fixed-share multinomial null (4999 null replicates). Fixed-share and spatially homogeneous worsening-habitat controls show no systematic excess contraction. This is an *input-defined* habitat/patch-selection scenario, not a derived explanation for Palmer/Signy penguins and not continuous Boids flight.

An independently coded `density_breeding_patch_bridge.py` uses density-dependent patch settlement and Gamma-Poisson observation noise with separately prescribed 600→60 decline. With crowding coefficient 4.0, mean observed contraction is **−29.9%** and stronger than the model-matched fixed-composition null at p≤0.05 in **7/10** worlds; fixed-quality proportional baseline passes only **1/10**. Thus more than one generative route can produce compositional contraction, but neither has been fitted to penguin site histories.

## 8. Reproducibility, limitations and next empirical filter

```bash
cd boids3d_research
python -m unittest -v test_boids3d_bridge.py test_eco_dynamics.py test_breeding_patch_bridge.py test_cross_repo_extensions.py
python cross_repo_phase_scan.py
python crossover_and_competition.py
python crossover_resolution_audit.py
python overlap_smoothing_audit.py
python synchronous_local_test.py
python breeding_patch_bridge.py
python density_breeding_patch_bridge.py
```

Twenty-one regression tests passed as of 2026-10-25. The scientific inference from simulations is conditional on the explicit rules and chosen scales, not on a real population or a known universal law. Key falsification tasks:

1. **Individual strategy (batter)**: compare independently classified foraging/transit states with matched-night centered vertical identity, then distinguish persistent duty-cycle mixture from within-state personal responses using untouched validation nights. Sparse non-synchronous GPS cannot identify simultaneous social Boids coefficients.
2. **Multi-axis generality (ODSP)**: preregister XY grid, vertical datum, observation effort, and held-out *new individual/site* transfer. Do not retune a completed ODSP empirical endpoint.
3. **State stabilization (louis)**: obtain event-ID-to-coordinate joins or independently linked time series before inferring measured displacement into similar water depths. Current SRI/coupling results are evidence of experienced-state buffering, not its specific movement mechanism.
4. **Demography (mina)**: use georeferenced, persistent breeding-patch identities and environmental covariates to test whether patch quality/accessible capacity predicts excess effective-component contraction conditional on the abundance path; do not substitute 3D flight voxels for monitored breeding components.

**Conclusion:** the attractive research programme is not “Boids proves competitive niche segregation.” It is a **cross-taxon generative framework in which policy persistence, environmental state buffering, ecological-state information, space sharing and demographic concentration are distinct, sometimes opposing outputs.**
