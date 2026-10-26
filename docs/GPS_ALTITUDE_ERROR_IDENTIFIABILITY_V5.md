# v5 — Does a predictive climb-state transition identify a movement rule?

**Status:** 2026-10-26, synthetic known-truth negative-control study. No new real-animal data were used, and previously frozen `batter`, `odsp`, `mina`, and `louis` results remain unchanged.

## Question and why it matters

The exploratory observed *Tadarida teniotis* v4 result found that previous climb class predicts held-out next climb class slightly better than the unconditional class model (**M1−M0 = +0.01383 nats/transition**, equal-individual mean; 7/8 individuals positive). That is a **prediction association**, not yet a validated physical inertia coefficient or evidence of Reynolds alignment, separation, or cohesion.

If measured GPS altitude is \(z_t^\mathrm{obs}=z_t^\mathrm{true}+e_t\), and \(v_t^\mathrm{obs}=(z_{t+1}^\mathrm{obs}-z_t^\mathrm{obs})/\Delta t\), then adjacent estimated vertical velocities share the error at their common altitude fix with opposite signs:

\[
\mathrm{Cov}(v_t^\mathrm{obs},v_{t+1}^\mathrm{obs}) = \mathrm{Cov}(v_t^\mathrm{true},v_{t+1}^\mathrm{true}) - \sigma_e^2/\Delta t^2.
\]

Under stationary AR(1) true vertical velocities with variance \(\sigma_v^2\) and autocorrelation \(\rho\), independent zero-mean altitude errors of variance \(\sigma_e^2\), and regular cadence:

\[
\rho_{1,\mathrm{obs}} = \frac{\rho\sigma_v^2-\sigma_e^2/\Delta t^2}{\sigma_v^2+2\sigma_e^2/\Delta t^2},\qquad
\rho_{2,\mathrm{obs}} = \frac{\rho^2\sigma_v^2}{\sigma_v^2+2\sigma_e^2/\Delta t^2}.
\]

Consequently **a useful previous-class predictor can arise even when successive true velocities are independent**. It may learn a negative correlation induced by shared measurement error. Conversely, genuine true velocity persistence can be hidden by observation error at lag one. These are theoretical consequences of the stated error model, not observations about bat GPS devices.

## Test design, fixed before examining synthetic outcomes

- 8 simulated individuals, 3 nights each, 240 true vertical-velocity steps per night at exactly 30 s resolution; 30 prespecified independent simulation seeds starting at 20261027.
- True velocity SD 0.8 m/s; AR(1) \(\rho=0\) (no true step persistence) or \(\rho=0.7\) (positive true persistence).
- Position-level independent Gaussian measurement error SD 0, 10, 20, or 40 m. These are **illustrative stress-test settings**, not estimates of actual accuracy in the observed *Tadarida* archive.
- Reconstruct climb classes down / level / up using the **same ±0.5 m/s** threshold as v4; evaluate whole-session held-out M1−M0 log-score gain using the **same v4 Jeffreys 0.5 and conditional 12 pseudocount definitions**, and equal-individual weighting.
- Inspect observed velocity lag-one and lag-two correlations separately. A lag-two association could help distinguish white position-error effects from true AR(1) persistence **under the assumptions above**, but it is not a universal diagnostic for correlated device errors or nonstationary behavior.
- The new synthetic test is independent of, and must not be used to refit/relabel, the frozen empirical v4 outcome.

## Results (30 simulated seeds per scenario)

| True velocity process | GPS altitude error SD | Mean held-out M1−M0 (nats/transition) | Mean observed lag-one \(r\) | Mean observed lag-two \(r\) |
|---|---:|---:|---:|---:|
| IID (no persistence) | 0 m | −0.00039 | −0.006 | −0.008 |
| IID (no persistence) | 10 m | **+0.00483** | −0.132 | −0.007 |
| IID (no persistence) | 20 m | **+0.02623** | −0.290 | −0.006 |
| IID (no persistence) | 40 m | **+0.05301** | −0.421 | −0.005 |
| True AR(1), \(\rho=0.7\) | 0 m | **+0.20070** | +0.684 | +0.465 |
| True AR(1), \(\rho=0.7\) | 20 m | −0.00044 | −0.010 | +0.191 |

In each IID-with-position-error scenario, all 30 simulated repeats had **positive held-out M1−M0** despite **no true serial dependence** between successive vertical velocities. The positive score does not identify the **sign** of autocorrelation, let alone a motor mechanism; the predictor can exploit either a positive or negative class relationship.

The observed wild-bat gain +0.01383 falls within the *range of gain magnitudes attainable* in these illustrative measurement-error worlds, but **this is not a fit to that dataset and does not estimate its error variance**. No conclusion about actual GPS-error dominance follows.

The persistent-velocity-with-error example illustrates a second limitation: lag-one correlation becomes near zero while lag-two correlation remains positive. A true movement policy may therefore be obscured by coarse, noisy observations. No universal inference follows from comparing just lag-one and lag-two correlations without a validated observation model.

## What is now supported and what is not

**Supported, mathematical/known truth:** The existing M1−M0 forecast score is not an identifiable estimate of physical vertical inertia unless a position-error model or independent movement sensor supplies additional constraints. Previous-state prediction and true movement persistence are separable phenomena.

**Not supported:** A bat-specific GPS altitude-error SD, a wild-bat social-interaction rule, a causal influence of annotated wind, an inferred collective Boids coefficient, a species-general behavior law, or an observed niche forecast in an independent taxon.

## Prespecified next real-data gate (new source or independently acquired validation)

1. **Observation model:** establish instrument height-error variance/correlation from stationary tags, calibration flights, dual independent sensors, or matched high-quality 3D localization, with terrain-relative versus MSL semantics retained.
2. **Synchrony and proximity:** quantify near-neighbor track pairs at species-specific sensory distance and response times. v4 found zero <=5 s / <=100 m pairs, so full social Boids coefficients remain blocked in that dataset.
3. **Candidate comparisons:** score error-aware inertia-only, environmental/resource, individual-history, and full social-Boids transition models on exactly the same held-out individuals/sessions. Keep whole-individual weighting and calibrated night-block nulls where used.
4. **Ecological forecast:** compare next-night 3D use probability distributions and niche-axis information \(I(S;XY)\), \(I(S;Z\mid XY)\), not merely one-step class accuracy, with spatial grid sizes and rare-state smoothing frozen in advance.
5. **Stop condition:** if no independently measured height error and no synchronous neighbors exist, report the structural non-identifiability and do not tune distance/cadence windows after observing the outcome.

## Reproduction and integrity

```bash
python validation_v5/altitude_error_audit.py --seeds 30 --out validation_v5/results/gps_altitude_error_known_truth_v5.json
PYTHONPATH=boids3d_empirical_v4:validation_v5 python -m unittest discover -s validation_v5 -p 'test_*.py' -v
```

`validation_v5/test_altitude_error_audit.py` explicitly checks the frozen M0/M1 probability definitions against `empirical_transition_benchmark.probs_from_counts`, verifies negative-control behavior and a positive-persistence control, and checks deterministic replay. The output JSON reports all 30-seed means and distributions. No animal tracks are bundled in this test.
