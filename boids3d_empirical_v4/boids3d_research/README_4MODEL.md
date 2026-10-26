# 3D Boids → bat/bird movement → vertical-niche geometry (synthetic proof of concept)

**Status 2026-10-25:** working toy simulator and testable hypothesis, **not fitted to empirical bat or bird tracks**. This is post-freeze prospective work, separate from the frozen JAE manuscript and the old Movebank eligibility search.

## Hypothesis and what this experiment can establish

A generative sufficiency question: can a shared environment, local flight coordination and *persistent individual differences in response to that environment* yield persistent, median-centered vertical space-use shapes while individuals strongly overlap horizontally?

This script contrasts four exactly specified treatments:

- `independent_shared` (M0): shared environmental movement rule; no Boids social force; no individual gain differences.
- `boids_shared` (M1): separation, alignment and cohesion; all individuals have equal environmental vertical-response gain.
- `boids_personal` (M2): same Boids forces and same external height field, but gain varies persistently across individuals. **No individual-specific preferred flight altitude, forage site or goal is encoded.**
- `boids_personal_swapped` (M3): same between-agent response-gain heterogeneity as M2, but gain assignments are permuted independently each night; stable rules no longer follow identities.

All treatments also contain a shared horizontal attractor, time-varying terrain/resource-related target height, bounded acceleration and airspeed, a vertical-climb bound, common horizontal wind and process noise. These are deliberately illustrative—not species-calibrated. Social interaction graph is topological k-nearest by default for this benchmark; `metric` is also implemented. The fixed six-nearest choice does not assert that bat groups use six neighbors.

### State and mechanism

At every time step, 3D positions and velocities are updated synchronously:

```
acceleration_i = a_sep * separation_i + a_align * alignment_i
               + a_coh * cohesion_i + a_patch * (patch_xy(t) - x_i, y_i)
               + e_z * [gain_i * (height_resource(x_i,y_i,t) - z_i)
                        - damping * v_z_i]
               + stochastic_acceleration_i
position_i(t+dt) = position_i(t) + dt * [air_velocity_i(t+dt) + wind(t)]
```

Acceleration, airspeed, climb, and vertical domain are bounded in code. The simulator is a *steering approximation* and does not solve wing aerodynamics or acoustic sensing. In this implementation the wind advects the animal horizontally; it does not change the vertical acceleration directly.

Individual specialization of **movement response** is intentionally distinct from an explicit preferred-altitude parameter.

### Evaluation endpoint

Each synthetic night is median-centered separately, and a fixed-height-bin histogram is created for each individual/night. Leave-one-night-out mean log score contrasts a self-training profile with pooled-other profiles. Whole-agent-night identity-label permutations provide a pipeline-specific null, which is generally *not zero*. Biological individuals are equal-weighted.

A separate coarse horizontal-overlap statistic is the mean pairwise Bhattacharyya coefficient of 7x7 x-y histograms, smoothed with pseudocount 0.5. **This is not a 3D segregation statistic and does not establish a lack of close-range avoidance or competition.**

### Recorded result (5 prespecified demonstration seeds × 199 permutations each)

| Seed | M0 excess / p | M1 excess / p | M2 excess / p | M3 excess / p | M2 horizontal overlap |
|---:|---:|---:|---:|---:|---:|---:|
| 17  | +0.0009 / 0.235 | +0.0022 / 0.025 | +0.0258 / 0.005 | +0.0020 / 0.230 | 0.9967 |
| 23  | -0.0029 / 0.990 | -0.0004 / 0.630 | +0.0228 / 0.005 | +0.0043 / 0.035 | 0.9956 |
| 47  | -0.0015 / 0.890 | +0.0017 / 0.045 | +0.0310 / 0.005 | +0.0015 / 0.250 | 0.9964 |
| 71  | +0.0013 / 0.095 | +0.0018 / 0.055 | +0.0261 / 0.005 | +0.0003 / 0.440 | 0.9953 |
| 101 | +0.0002 / 0.400 | +0.0014 / 0.150 | +0.0241 / 0.005 | -0.0002 / 0.475 | 0.9953 |

Data: `benchmark_5seeds_199.json` (full precision). Four nights, 14 agents, 288 retained steps per agent per night; artificial units/constraints per code. P values are individual Monte Carlo tail proportions with a lower resolution limit of 0.005, **not five independent field validations**. M3 loses the M2 fingerprint under gain-to-identity reassignment. Individual M1/M3 small-p results emphasize stochastic false positives, null calibration and replication; their positive sign is not evidence for built-in individual rules. Model M2 is a **constructed positive control**: its stable individual response gains are inputs, not an ecological inference.

## How to run

```bash
python -m pip install numpy
python -m unittest -v test_boids3d_bridge.py
python boids3d_bridge.py --seed 17 --reps 199
```

## Connection to batter and ODSP

The frozen `batter` endpoint describes held-out individual identity in distributions of flight height (after coarse x-y standardization and centering). This prototype asks a *different*, forward-model question: which low-dimensional policy parameters, if any, suffice to generate such signatures when projected into `P(z | x,y, individual, context)`? ODSP measures 3D niche organization and transfer, while this model provides candidate dynamics and observable predictions.

The paper reports durable self-history and little support for added contemporary segregation in evaluable fruit-bat panels, but does **not** establish memory, learning or environmental reaction norms. Do not read the synthetic M2 result as the missing empirical cause.

## Prospective empirical testing hierarchy

1. **Screen temporal support without outcome fishing.** Social separation/alignment/cohesion parameters need synchronized multi-individual 3D positions at seconds/subseconds scale. Interpolating sparse GPS positions to fabricate neighbors is not admissible. Without simultaneous fixes, estimate only independent agent movement/environment terms.
2. **Estimate kinematic quantities with explicit error models.** Ground versus airspeed requires wind and positioning uncertainty. Species-appropriate speeds, turn/climb envelopes and terrain/height datum must be documented.
3. **Freeze model ladder before opening held-out responses:** (i) bounded movement null; (ii) common environmental response; (iii) local interactions if supported; (iv) persistent personal-response parameters; (v) time-varying learned-route memory. Use meaningful parameter recovery on synthetic data, and falsify excess complexity.
4. **Predict independent nights/individuals:** held-out one-step-to-many-step trajectory log likelihood, angular velocity/turning autocorrelation, 3D occupancy, median-centered height-profile score; additionally score overlap/segregation against concurrent-position permuted nulls. Do not optimize solely to matching a marginal height histogram.
5. **Use matched birds as generality tests** rather than presume parameters transfer between taxa. For birds, topological-neighbor models are a reasonable candidate; bats may require species-, context-, and echolocation-specific interaction kernels. Shared mathematical *structure* is not evidence for equal coefficient values.

## Existing evidence and boundaries

- Reynolds (1987), *Flocks, Herds, and Schools*: https://doi.org/10.1145/37401.37406
- Ballerini et al. (2008), starling topological interactions: https://doi.org/10.1073/pnas.0711437105
- Bat sensorimotor response during group emergence: https://pmc.ncbi.nlm.nih.gov/articles/PMC12002023/
- The time sampling challenge for social GPS inference: https://doi.org/10.1111/2041-210X.13999

## Next technical work (not executed here)

- Fit only structurally identifiable terms to empirically synchronized 3D data and perform parameter recovery on observation-cadence-matched simulations.
- Add latent behavioral states and a memory kernel to distinguish stable policy from different mixtures of commuting, feeding and return.
- Quantify real `P_i(x,y,z,t)` spatial overlap and simultaneous vertical separation independently, with tagged-device error propagation.
- Test out-of-sample transfer and alternative mechanisms instead of declaring Boids to be a fitted biological law.

## Follow-up: observation cadence and approximate parameter recovery

`kinematic_identifiability.py` estimates a vertical environmental-response gain from synthetic sampled tracks using finite-difference acceleration, a known environmental field, and a known damping constant. It **does not fit social Boids coefficients**. Run `python kinematic_identifiability.py`; recorded results are in `cadence_recovery_seed17.json`.

For the personal-gain positive control (seed 17), correlations between true and estimated individual gains remain about 0.982–0.984 at 2.5, 5, 10 and 20 second sampling intervals, but estimated across-individual gain standard deviation decreases from 0.0547 to 0.0239 (true SD 0.134). The rank relationship can survive while the absolute gain magnitude is strongly biased by acceleration/velocity clipping, smoothing and finite differences. In the shared-gain control, apparent estimated SD is only about 0.0011–0.0016. This is a single synthetic scenario with a known environment, no positioning error, and no uncertainty intervals. It is not a proof of parameter identifiability on wild tracking data.

**Next falsification:** add realistic position error and wind/height-field misspecification; test held-out prediction, not just gain correlation, and repeat across independent seeds.
