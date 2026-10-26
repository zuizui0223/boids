# From 3D Boids movement rules to predictive ecological patterns (v3)

**Date:** 2026-10-25  
**Scope:** an explicitly synthetic forward model, independent of frozen `batter`, `ODSP`, `mina`, and `louis` manuscripts. It is **not an empirically fitted movement law** for any real bat, bird, or penguin species.

## Main answer

Yes: mathematically specified movement rules can generate 3D probability distributions of use, and functionals of those distributions define measurable ecological patterns. This is a **micro → meso → macro forward map**, not a proof that real animals use uniquely identifiable Boids rules:

```
individual movement policy + social interaction + resource/environment dynamics
                       ↓ stochastic trajectories
          individual/species P(x,y,z,t,behavior)
                       ↓ explicit observation process
  repeatability | species XY and Z partition | transfer | state buffering
                       ↓ forecasting, if input parameters and environments are identified
         new environment/density/competition → distributions of patterns
```

## Model

For each agent i of species s:

- State: r_i(t)=(x,y,z), velocity v_i(t), latent behavioral mode h_i, and history m_i.
- Policy: theta_{s,i}=mu+u_s+w_{s,i}, with shared, between-species, and within-species components.
- Movement (stochastic acceleration approximation):

  dr_i = v_i dt

  dv_i = [a_sep,i S_i + a_align,i A_i + a_coh,i C_i
          + a_food,i ∇R(r_i,t) + a_state,i ∇E(r_i,t)
          + a_memory,i M_i(t) − gamma_i v_i] dt + Sigma_i dW_i(t).

- Depleting resource k:

  partial_t R_k(r,t) = rho_k(K_k(r,t)-R_k(r,t))
                      − R_k(r,t) sum_i c_{ik} K_eat(r-r_i(t)).

- Generate occupancy as a probability distribution from the simulated trajectories:

  p_{si}(r,t | theta, E, R, initial conditions)

This is numerically evaluated by agent simulation. With appropriate approximations, a mean-field density PDE can be derived; it is **not** yet a mathematically validated exact closure of the present stochastic ABM, especially with finite k-nearest neighbors and memory.

## Distinguish endpoints

| Endpoint | Definition | Why distinct |
|---|---|---|
| Within-species individual repeatability | held-out logscore of person-matched centered Z versus conspecific baseline; after XY control | The same person may use a repeatable vertical strategy without exclusion |
| Horizontal species partition | I(S;X,Y) | Species may use different regions |
| Conditional vertical species partition | I(S;Z | X,Y) | At the same XY spatial grain, species can use different heights |
| Temporal partition | I(S;T | X,Y) | Species can occupy the same physical space at different times |
| Vertical niche thickness | exp[H(Z | X,Y)] | Thickness is not identical to species partition |
| Predictive transfer | independent night/animal log-score gain | In-sample identity information does not imply persistence |
| Habitat-state buffering | temporal used-state stability relative to matched availability | State retention is not the same as staying in place |
| Effective breeding component count | 1/sum_j p_j(t)^2 | This is a separate demographic/settlement layer, not a flight voxel |

All information metrics depend on observation grain, sampling and detectability. For empirical studies, set them **before outcomes are inspected** and use cross-validation/permutations at biological-replication units.

## Current code's true Boids content (important correction)

- Original `boids3d_bridge.py`: all three classic rules separation, alignment, cohesion.
- `eco_dynamics.py` through previous v2 runs: *only separation and alignment* plus food-resource steering and environmental tracking. **It did not have cohesion.**
- v3 adds `separation_strength` and optional `cohesion_strength` (default zero, so all v2 simulations unchanged). All old 21 tests and 3 new prediction tests now pass.

### Social forces ablation, 60 synthetic worlds (4 ecological contexts × 3 arms × 5 seeds)

Neutral resource environment, no between-species preference difference:

| Social rule arm | Pooled I(S;XY), nats | Held-out other-night XY log gain, nats/point |
|---|---:|---:|
| No local social forces | 0.060 | −0.176 |
| Separation+alignment | 0.076 | −0.238 |
| Separation+alignment+cohesion | **0.391** | **−1.038** |

Strong stable species-specific food preference, no resource depletion:

- Boids full arm: pooled I(S;XY) ≈ **0.678** nats and held-out-night gain ≈ **+0.644** nats/point.

Interpretation: *conspecific cohesion can produce apparent per-night species spatial sorting even with identical resource preference, but that spatial geometry failed transfer to another fresh-initialization night*. Adding a persistent species-coded resource preference produced repeatable out-of-night prediction in this artificial system. This is a mechanistic **possibility**, not a universal species rule. No causal exclusion/fitness gain is inferred from the information score.

The depletion-driven reduction in horizontal species information and increase in conditional vertical information persisted in the no-social and separation/alignment arms. Resource/environment dynamics produced much of this pattern; the mere presence of Boids forces was **not necessary** in this toy system. With strong cohesion, the results change quantitatively.

### Forecast model tested on unseen synthetic conditions

First model: multilinear interpolation over the original **90 known-truth training simulations**, with fixed 3 × 3 × 2 ecological parameter grid, 5 seeds each. It predicts niche metrics for intermediate ecological parameter values. Novel challenge 1: **24 worlds** with 8 parameter cells not present in training and 3 never-used random seeds.

| Pattern | Model RMSE | Nearest-known-setting baseline | Global-mean baseline |
|---|---:|---:|---:|
| I(S;XY) | **0.0414** | 0.0745 | 0.1306 |
| I(S;Z|XY) | **0.0331** | 0.0754 | 0.0748 |
| Habitat-state buffering index | **0.1203** | 0.2411 | 0.1810 |
| Simulated resource uptake | **0.0197** | 0.0378 | 0.0552 |

*Critical failure:* uncertainty bands derived solely from seed-to-seed variation on the training cells covered **0/24** novel worlds for buffering and uptake. They omitted structural interpolation error. Point prediction success is not uncertainty calibration.

The first 24-world challenge was used as an **explicit calibration** set for an absolute-error interval. A second set of **24 new worlds**, with disjoint novel parameter cells and random seeds, was then opened without refitting the mean predictor:

| Pattern | Second-test model RMSE | 90%-error-band empirical coverage |
|---|---:|---:|
| I(S;XY) | 0.0314 | 23/24 |
| I(S;Z|XY) | 0.0223 | 24/24 |
| Buffering | 0.0936 | 24/24 |
| Uptake | 0.0153 | 24/24 |

These deliberately structured synthetic scenarios are not exchangeable IID field draws, so the resulting bands have **no formal distribution-free coverage guarantee**. The good empirical coverage indicates conservative error bands for these particular 24 new tests, not a biological predictive interval.

The within-training-domain prediction command is:

```bash
python predict_niche.py --preference 0.21 --depletion 0.16 --tracking 0.65
```

For the example, the four synthetic predictions are: I(S;XY) ≈ 0.1851 nats, I(S;Z|XY) ≈ 0.2251 nats, state buffering ≈ 0.4755, resource uptake ≈ 0.4642. These are not species-calibrated unit values. The API refuses parameter values outside the trained grid; extrapolation is untested.

### Contrasting scenarios (illustrative forward forecasts)

Fix species resource-preference contrast 0.21 (arbitrary simulator unit):

| Scenario (depletion, state tracking) | I(S;XY) | I(S;Z|XY) | Buffering | Uptake |
|---|---:|---:|---:|---:|
| Baseline (0.04, 0.30) | 0.417 | 0.175 | 0.295 | 0.590 |
| Higher consumption (0.16, 0.30) | 0.194 | 0.275 | 0.266 | 0.477 |
| Higher consumption + stronger state tracking (0.16, 0.65) | 0.185 | 0.225 | 0.476 | 0.464 |

In this simulator: with other assumptions fixed, increasing resource depletion shifts species information away from XY toward conditional Z while lowering uptake; stronger state tracking then increases experienced-state buffering while lowering vertical species information. This makes **quantitative counterfactual predictions**, not claims about actual ecological change.

## Four repository evidence bridge

1. **batter** ([prospective research branch](https://github.com/zuizui0223/batter/tree/prospective/decentralized-route-theory-v1)): personal vertical strategy persists in 4/4 evaluable fruit-bat panels at 500 m without positive added terrain-relative segregation in 0/4. The synthetic repeated behavior-mode mixture reproduces a possible *pattern*, not empirically inferred memory, stable policies, or social Boids coefficients.
2. **ODSP** ([main](https://github.com/zuizui0223/odsp)): bat H(Z|XY)=1.392 nats, exp(H)≈4.02, while new-bat spatially conditional prediction fails. By contrast, Serengeti temporal species partition I(S;T|site)=0.224 nats transfers across 3 held-out site folds. Our cohesion versus stable resource preference comparison directly probes the difference between in-sample structure and out-of-night transfer.
3. **louis** ([main](https://github.com/zuizui0223/louis)): ten King Rails show stable used water-depth state relative to nearby matched alternatives; a geo-displacement causal claim remains unresolved due to missing event-coordinate join keys. Our ecological-state tracking is a toy mechanism and does not estimate the published State Retention Index or hydrological coupling slope.
4. **mina** ([main](https://github.com/zuizui0223/mina)): effective monitored breeding components contract 19–83% across five penguin monitoring populations beyond an abundance-conditional fixed-share error null. It requires a demographic/settlement component on a different timescale: flight Boids cannot directly predict annual breeding-component concentration without explicit reproduction/survival/site-choice rules and georeferenced habitat.

## What could be forecast for wildlife, and the decisive missing measurements

- **Directly feasible next**: conditional ecological-state distributions and held-out individual-night/species transfer, if event-level GPS/vertical state and environmental layers are accurate; condition on observation effort and individual IDs.
- **Needs better telemetry**: short-horizon 3D flight path distribution, speed/turn/climb changes and state-switching rates. Need error-aware time intervals, wind, species-appropriate flight bounds, repeated individuals and new nights.
- **Not currently identifiable**: simultaneous social interaction coefficients from non-synchronous GPS. Need simultaneous multi-animal 3D positions and speed, preferably second-scale or higher cadence, plus experimental/independent environmental variation.
- **Needs more ecology**: causal competitive displacement requires actual resource supply/depletion/competitor intervention or credible quasi-experimental design; cross-species niche segregation from GPS alone does not establish diet, direct competition, fitness or coexistence.
- **Requires separate annual module**: penguin breeding-site response to habitat loss/demographic decline; feed output from movement+settlement into natal/breeding location and population transition, then evaluate years out.

A rigorous field forecast must include observed location/height error and false detections in `p(y | true state)`, and incorporate posterior uncertainty in parameters, site and weather rather than only random simulator seeds.

## Source and implementation

Run tests:

```bash
python -m pip install numpy scipy
python -m unittest -q test_boids3d_bridge.py test_eco_dynamics.py test_breeding_patch_bridge.py test_cross_repo_extensions.py test_forward_prediction.py
# 24 tests PASS
```

Reproducible scripts and output:

- `eco_dynamics.py` — micro movement/resource dynamics + optional cohesion.
- `boids_ablation.py` → `boids_ablation.json` — 60 synthetic social-force ablations.
- `boids_horizontal_transfer.py` → `boids_horizontal_transfer.json` — 45 synthetic other-night tests.
- `forward_prediction_validation.py` → `forward_prediction_validation.json` — 24 never-seen-world first tests.
- `prediction_uncertainty_revalidation.py` → `prediction_uncertainty_revalidation.json` — 24 new uncertainty tests.
- `predict_niche.py` → `example_prediction.json` — bounds-checked command-line predictions.

The existing older artifact files are included separately and retain their original meanings. Neither the frozen bat JAE manuscript nor the penguin manuscript is modified.
