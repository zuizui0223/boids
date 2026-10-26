# 3D Boids: individual rules, niche differentiation and cross-repository ecology

**Date:** 2026-10-25  
**Status:** synthetic known-truth and mechanistic ablation tests only; no new field-data analysis and no updated claim in any frozen manuscript.

## Executive conclusion

The same generative framework supports four *distinct* ecological endpoints: persistent individual movement states, species-specific 3D occupancy, conditional vertical-state differentiation, and experience of an environmental state. They are **not interchangeable**. Crucially, shared-resource depletion **decreases** global 3D spatial segregation in this implementation while **increasing** species-conditioned vertical information. Strongly reduced spatial overlap is therefore neither necessary nor sufficient for species-specific vertical organization.

### Current study design

- 2 constructed 'species' × 7 agents, 3 independent model nights and 480 agent time steps per night, 180 warm-up steps; repeated in 5 random worlds (seeds 17, 23, 47, 71, 101).
- 16 ecology treatment arms = 80 model simulations. Two renewable resource types have different vertical structure. Movement changes resources through consumption every time step; resources regenerate with fixed rate. Agents steer on resource gradients, conspecific-neighbor alignment, collision avoidance across species and (in separate arms) an environmental-state mismatch gradient. No output-space height shifts are applied.
- Competition identification uses **paired shared versus private-resource** worlds. The private-resource control maintains resource depletion by one's own behavior but disables consumption externalities among agents. It is a designed counterfactual rather than a field-realistic population.
- Independent-validation arm: 7 treatment types × 5 seeds = 35 additional complete synthetic runs; unseen-individual transfer, horizontal versus conditional-vertical information, and 3 spatial grid sizes.
- Individuality arm: 5 ablations × 5 seeds = 25 further synthetic runs, each with 4 nights and 800 time steps, whole-night identity permutation (199 reps) restricted to conspecifics, after session-median centering on voxel-unit z bins.
- 15 local regression tests PASS. Simulated generations cannot establish that these mechanisms generated the empirical bat, bird or penguin patterns.

## Dynamical definition

For species s and individual i, write the vector of movement-control parameters as

\[
\theta_{si}=\mu+u_s+v_{si},\qquad
\dot{x}_{si}=v_{si}^{motion},\qquad
\dot{v}_{si}^{motion}=F_{social}+F_{resources}+F_{experienced\ state}-\zeta v_{si}^{motion}+\epsilon.
\]

Resource stock k in each voxel follows a discrete-time bounded approximation to

\[
\partial_t R_k(x,t)=\rho_k(K_k(x)-R_k(x,t))
-\sum_i c_{ik}R_k(x_i,t)\,\delta(x-x_i).
\]

The last term is actually evaluated in each time step. Resource preferences are assigned to two *pseudotaxa*; there is no claim that these parameter values represent any empirical bat/bird species. Conspecifics alone align, whereas collisions repel individuals of both groups.

## Major result A: the sign of spatial partition and conditional-state information can diverge

Averaged over five independent simulation seeds:

| Mechanism | Species spatial-segregation index (16×16×8) | I(Species;XY), nats | I(Species;Z\|XY), nats | Species held-out *new individual* conditional-height gain, nats/point |
|---|---:|---:|---:|---:|
| No species difference or social alignment | 0.001 | 0.054 | 0.018 | −0.045 |
| Social alignment, identical resource preferences | 0.002 | 0.063 | 0.019 | −0.063 |
| Species-specific resource preferences only | 0.268 | 0.685 | 0.008 | +0.010 |
| Preferences + **shared depletion** | 0.094 | 0.137 | 0.402 | +0.445 |
| Preferences + **private depletion** | 0.147 | 0.222 | 0.351 | +0.374 |

**Attention to binning:** Spatial-segregation column above uses the original fixed 16×16×8 grid with 0.06 smoothing; information and unseen-individual numbers come from independent-validation calculations. They are distinct estimators, not directly comparable numeric scales. All conditional-information and held-out-transfer comparisons are computed on the same 4×4×8 conditional observation grid.

Original paired 5-seed contrasts at fixed resolution: `shared_depletion - private_depletion` is −0.0523 for spatial segregation in **5/5** seeds, and −0.0400 for realized mean resource uptake in **5/5**. This is evidence about this known-truth simulation, **not a field effect size**, ecological competitive exclusion, or a discovered threshold.

In the independent-validation assay with identical smoothing across resolutions, the spatial segregation index from preferences only versus shared depletion changes:

- 4×4×4: 0.594 → 0.452
- 8×8×4: 0.484 → 0.309
- 16×16×8: 0.187 → 0.069

All show the same direction. Even while spatial distinction declines, independently held-out species-conditioned vertical state becomes much more predictive. A single niche-overlap metric loses this information.

The 5-seed depletion sweep is continuous: spatial segregation decreases from 0.268 (no depletion), to 0.166 (depletion 0.04), to 0.094 (0.20), to 0.081 (0.35). **No discontinuity, phase transition, or critical threshold has been demonstrated.**

See `fig_spatial_vs_vertical_information.png`, `eco_dynamics_factorial_results.json`, and `eco_dynamics_independent_validation.json`.

## Major result B: the louis-type buffering mechanism requires local options

Define a model-specific, same-time, locally matched environment mismatch reduction:

\[
B=1-\frac{E[|E_{used}-E^*|]}{E[|E_{local\ alternative}-E^*|]}.
\]

This is **not** louis's hydrological response-slope reduction, nor its temporal SRI; it is an experimental analogue with a known target state and nearby alternative samples.

At the same resource regime, average B over five seeds:

- Spatially homogeneous environmental state, state tracking OFF or ON: **0.000** in both (negative control).
- Locally heterogeneous state, state tracking OFF: **0.138**. Nonzero baseline may arise from resource-state covariance and comparison architecture, not purposeful habitat-state tracking.
- Heterogeneous state, weak tracking: **0.443**.
- Heterogeneous state, strong tracking: **0.612**.
- More locally heterogeneous state, strong tracking: **0.692**.

The within-seed strong-versus-off tracking contrast is **+0.474** in 5/5 worlds. This is an experiment on an explicitly constructed policy; *it is not a fitted explanation of King Rail movement*. To test actual movement-mediated buffering one needs event-matched positions or movement-feasible counterfactual local trajectories, precisely the linkage unresolved in louis.

See `fig_local_portfolio_tracking.png`.

## Major result C: a stable behavioral-state mixture can preserve centered individual identities

An individual-specific foraging/transit duty cycle was added as a *persistent* personal parameter. State switches follow a Markov transition mechanism; the trajectory is still generated each time step by Boids/environmental forces. Neither different height offsets nor route maps are imposed as outputs.

After centering each synthetic night and evaluating self versus **conspecific** vertical shapes, with within-species whole-night permutation calibration (199 shuffles):

| Arm | Mean null-calibrated self-identity gain, nats/fix | Independent model worlds passing p≤0.05 |
|---|---:|---:|
| Shared policy; no personal behavioral mixture | +0.0003 | 0/5 |
| **Stable personal foraging/transit mixture** | **+0.1297** | **5/5** |
| Same mixture *swapped among individuals each night* | +0.0027 | 1/5 |
| Stable personal mixture + shared resource depletion | +0.0690 | 5/5 |
| Resource depletion without personal mixture | −0.0003 | 0/5 |

The partial false positive in the night-swapped negative control is retained, not discarded. Mean same-species *coarse spatial* overlap remains ~0.822 in the stable-mix arm and ~0.877 under shared depletion; the agent rules contain no active within-species exclusion rule except short-range collision avoidance.

This provides a **mechanistic possibility** for batter's persistent centered vertical-use shapes without exclusive spatial partitions. It does **not** prove that observed bats exhibit personal foraging/transit mixtures, nor that experience or memory carries their strategies.

A preceding scratch audit accidentally reused metre-scale centered-height bin edges on voxel-unit simulated heights (all points fell into one bin), producing invalid constant results. Those 12 audits were removed from `eco_dynamics_factorial_results.json` and superseded by the corrected, within-species assay and its negative controls. The error, its cause and replacement are recorded in that JSON's `centered_shape_audit_correction`.

See `fig_personal_mixture_identity.png` and `eco_dynamics_behavioral_mixture.json`.

## Major result D: a separate annual breeding-space gate (mina comparison)

A new independent `breeding_patch_bridge.py` evaluates the inverse-Simpson **effective number of breeding components** under an externally specified declining population trajectory. It uses six invented monitored breeding components, with population totals fixed at 900 → 120. A null simulates **4,999 fixed-share multinomial draws for each world**, conditioned on the exact same total abundance endpoints. Scenarios differ only in heterogeneous local substrate vulnerability and an explicit probability of choosing/re-targeting more suitable breeding components.

Across 20 stochastic worlds per scenario:

| Annual-scale scenario | Mean change in breeding-component effective number | Worlds with excess contraction against fixed-share null (p≤0.05) |
|---|---:|---:|
| Fixed-share decline, no substrate differentiation | −1.7% | 1/20 |
| Homogeneous substrate deterioration, strong retargeting | −1.2% | 0/20 |
| Heterogeneous substrate, weak retargeting | −11.4% | 6/20 |
| **Heterogeneous substrate, strong retargeting** | **−35.9%** | **20/20** |

Thus, **a population can maintain or seek suitable environmental state by concentrating breeding decisions in fewer patches**, even while total abundance declines for externally imposed reasons. This connects a louis-like *move to stay in state* process to a mina-like change in spatial composition, but only at the level of a **constructed two-timescale mechanism**. No short-term Boids trajectories were used as annual breeding choice; they are separate modules requiring linkage by individual state, accessibility and habitat suitability data. This toy does not establish why Adelie or chinstrap penguins experienced the documented contraction.

See `annual_breeding_patch_bridge.json` and `fig_annual_effective_components.png`.

## Empirical evidence bridge: four repositories

| Repo and actual observed result | What the current model demonstrates | Boundary not crossed |
|---|---|---|
| **[batter](https://github.com/zuizui0223/batter/tree/prospective/decentralized-route-theory-v1)**: centered-height identity retained in 5 comparative panels; terrain-relative strategies persist in 4/4 fruit-bat panels, whereas additional vertical segregation is supported in 0/4 | Stable behavioral-state mixtures can yield centered individuality across bouts while spatial use remains largely shared | No bat behavior-state classifier or experimentally tested learning, morphology, memory, wind/echolocation mechanism |
| **[ODSP](https://github.com/zuizui0223/odsp)**: bat effective vertical states ~4.02, but the frozen cross-individual bat x-y-z conditional-state transfer fails; Serengeti species-time differentiation I(S;T\|site)=0.224 nats with positive gains in 3/3 held-out folds | Separate occupancy overlap, H(Z\|XY), I(S;Z\|XY), and individual/nights-out transfer. Resource effects can change these in opposite directions | Simulated model pseudotaxa are not a replication of wild bat/predator patterns; no measured time-of-day niche partition in present model |
| **[mina](https://github.com/zuizui0223/mina)**: inverse-Simpson breeding-component effective number contracts 19–83% across five populations, beyond a fixed-share finite-count null | A separate year-scale patch-choice gate shows that declining total abundance + heterogeneous breeding-substrate quality + retargeting can produce excess concentration against a count-conditional null | **Not derived from Boids.** Site vulnerability and retargeting are imposed toy rules; no wild colony parameters, births/deaths or breeding polygons are estimated |
| **[louis](https://github.com/zuizui0223/louis)**: 10/10 King Rails show hydrological buffering, local-availability coupling reduction 83.8%; displacement as the cause unresolved because coordinate/event keys cannot be safely joined | State tracking needs a locally heterogeneous reachable environmental portfolio; the no-portfolio control correctly blocks the intended benefit | Our relative mismatch is not SRI or coupling-slope reduction, and no matched wild water-depth trajectories are fitted |

The four results form a common set of *questions*, not one demonstrated empirical law: how much environmental freedom is reachable; whether individuals move to preserve experiences; how use differs among identities; and how movement and habitat access couple to population dynamics.

## Research thesis after this round

**Working question:** Under which resource, accessible-state and memory constraints do persistent individual movement rules become spatial, temporal or functional niche differences—and when can distinct strategies coexist without segregation?

A concise causal ladder to test is:

`movement and sensing policy → behavior-state mixing and state experience → P(x,y,z,t,resource | identity) → competitive externalities and realized payoff → (if breeding habitat and demography are modeled) population spatial composition`.

**Next new-data/next-model gates:**

1. An honest model of synchronously observed multi-individual position would enable identifying social separation/attraction strengths; asynchronous GPS cannot identify neighbor forces.
2. Multiple prey/food proxies or independently observed behavior states are needed to distinguish true resource differentiation from a geometric height shape.
3. Valid time-of-day state partitioning must model observation/detection effort; don't lift ODSP's camera-time results into Boids without activity schedules.
4. The separate annual component-count null is now implemented as a toy. The missing *causal bridge* is linking identified trajectories or individual accessibility to actual breeding-site choice, survival and suitable nest substrate. Do not treat the toy as a penguin fit.
5. Validate independently in birds and bats with species-appropriate speed, wind, altitude-datum and location-error models. No model parameters can be inferred from these synthetic experiments alone.

### Run locally

From the `boids3d_research` directory (Python 3.10+, `numpy`, and optionally `matplotlib`):

```bash
python -m unittest discover -p 'test_*.py' -v
python run_ecological_bridge.py
python validate_ecological_bridge.py
python validate_behavioral_mixture.py
python breeding_patch_bridge.py
python make_ecological_figures.py
```

Note: runner outputs will be overwritten with the same fixed seeds; they contain exploratory synthetic data. Historical M3–M6 files in this directory use **post-hoc occupancy transformations** and should never be cited as evidence from the new integrated resource-consumption dynamics.
