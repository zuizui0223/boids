# v7 known-truth rank test: Does next-step prediction identify a Boids force?

**Scope:** numerical known-truth structural diagnostic, not wild-animal inference. This is separate from the frozen v6 bat-pair observed-data negative prediction result and the v7 independent pigeon source header-only preflight.

## The issue

Let \(r_{ij}(t)=x_j(t)-x_i(t)\), and specify an explicit local Boids basis

\[
S_i(t)=-\frac{1}{n_i}\sum_{j\in N_i}\frac{r_{ij}(t)}{\lVert r_{ij}(t)\rVert^3},\qquad
C_i(t)=\frac{1}{n_i}\sum_{j\in N_i}r_{ij}(t).
\]

The steering component is \(a_i(t)=\alpha S_i(t)+\gamma C_i(t)+\varepsilon_i(t)\). This exact functional form is a **model choice**, not an empirical finding.

With only one neighbor at fixed distance \(d\), \(S_i(t)=-C_i(t)/d^3\) for every observation: the two design columns are rank-one even if the response can be predicted nearly perfectly. With three neighbors all fixed at the same distance, the same proportionality holds. Varying distances across observations or among neighbors may break the collinearity and permit identification **under the assumed kernels and observation model**. More observed animals without geometric/scale excitation do not resolve the ambiguity by themselves.

## Executed fixed synthetic experiment

- Predefined scenarios: one observed neighbor at fixed distance 10 (2-bird system); one at uniform distance 6–18; three observed neighbors all at fixed 10 (4-bird system); three at varying 6–18.
- 60 independent seeds per scenario, each with 100 3D snapshots for training and 60 independent 3D snapshots for testing. Unit is an independently generated local-neighbor configuration, **not an empirical biological individual**.
- Force bases scaled only with training RMS. Known coefficients: (0.70, −0.25) in standardized design space, additive Gaussian response noise SD 0.10. Recovery via unregularized least squares with a fixed singular-value threshold; this gives the minimum-norm solution when not identified.
- Observables: fraction of full-rank designs, mean L2 coefficient recovery error, held-out MSE compared with oracle noise floor. `validation_v7/social_force_rank.py` and `test_social_force_rank.py` contain all generation and scoring decisions.

| Configuration | Full rank across 60 runs | Mean coefficient L2 error | Mean test MSE | Oracle test MSE |
|---|---:|---:|---:|---:|
| 2 birds, fixed distance | 0/60 | **0.3182** | 0.0102 | 0.0101 |
| 2 birds, varying distance | 60/60 | **0.0084** | 0.0100 | 0.0100 |
| 4 birds, equal neighbor distances | 0/60 | **0.3182** | 0.0099 | 0.0098 |
| 4 birds, heterogeneous distances | 60/60 | **0.0096** | 0.0100 | 0.0100 |

**Central result:** an excellent held-out forecast can coexist with a mathematically underidentified separation/cohesion coefficient pair. Conversely, a variable-distance design can identify the coefficients in known-truth simulations but this does **not** establish that an organism actually follows these kernels.

## What this changes for field study design

1. Before fitting a social Boids coefficient, fix and document the interaction kernels and observation error model; test local steering design rank, smallest singular value, and condition number under declared scaling.
2. Record variation in neighbor distances, bearings, speeds and social context; synchronized individuals alone do not guarantee excitation. Retain fully time-aligned observations with biologically validated sampling intervals (spline-resampled points are not independent sensor samples).
3. Score next-step own-history, environment-only, and own-plus-social predictors on independent pairs/flights/individuals, with a genuine out-of-context held-out test, plus physically matched negative controls when available.
4. Quantify environmental 3D niche use and individual repeatability only where longer tracked periods and independent contexts exist. An identified local steering equation is **not** equivalent to predicting long-term use probabilities or species niche partition.
5. Treat multiple parameter sets yielding the same observed forecasting distribution as an identified set, not a unique inferred animal rule. Extend to stronger behavioral response models only after independent data, not by adjusting a failed frozen v6 endpoint.

## Reproduction

```bash
python validation_v7/social_force_rank.py --seeds 60 --out validation_v7/results/social_force_rank_known_truth_v7.json
PYTHONPATH=validation_v7 python -m unittest discover -s validation_v7 -p 'test_*.py' -v
```

Outputs are synthetic; no copyrighted or protected field records are copied.
