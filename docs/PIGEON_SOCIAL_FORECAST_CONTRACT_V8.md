# v8 — frozen novel field prediction of Boids-style neighbor information

**Status: frozen before inspecting 3D GPS headings, speed-dependent eligibility, social steering values, or held-out prediction scores.** The earlier source-only v7 and time/position-only v8 gates have passed and are fixed. The original public data are CC0 (Zenodo record 5010830, original archive DOI `10.5061/dryad.53f4b`); the archive is not redistributed. This study does not reopen the Roy/Abaid bat v6 or batter/ODSP/mina/louis endpoints.

## Supported observational unit and question

The outcome-blind v8 gate admitted **197 synchronized paired flights** with **320,723** matched 3D fixes among **17 site×dyad units** from the 199 v7 file-matched flights. Within the admitted sample, the observed GPS cadence median is **1 second**, despite the archive being described as nominally 5 Hz. All 197 admitted flight pairs have at least 10 recorded fixes within 100 m. Three-dimensional synchronization alone does not calibrate altitude error or prove acoustic/visual interactions. The primary response is therefore **one-second horizontal steering/turning**, not 3D vertical Boids coefficients.

## Models and precommitted features

A derived row uses two bird tracks matched by at most 0.11 seconds (as in v8 gate), with consecutive sampling intervals 0.8–1.2 s for three prior/current/future intervals and the partner's 10-record-lag interval. Current and preceding ground speeds must be >=4 m/s for both birds. **Eligibility does not condition on future response speed**. The participant identities and complete flight stay grouped. Require >=20 role-level predictand rows per animal pair (>=40 total), 30 positions per flight and 5s coverage. Cap any bird role at 500 deterministic evenly spaced records per flight. No interpolation of unsynchronized timestamps; source timestamp and altitude columns retain original semantics.

Response for each bird is the signed change in horizontal heading in radians between the already-observed displacement and the next displacement. Predictors are restricted to values at or before that time:

- **M0 own/route:** intercept, previous heading turn, log(current horizontal speed/12), sine/cosine components of current flight heading, horizontal displacement from *first observed own GPS fix* at the time of the prediction, and elapsed time since first observed GPS fix (never fraction of **future total** flight duration).
- **M1 actual-neighbor:** M0 plus body-frame longitudinal and lateral relative partner position (cohesive displacement), inverse-cubic separation-like displacement kernels (fixed +5 m regularization), and relative velocity components, all measured from the actual synchronously tracked partner. No physically interpreted sign is assigned a priori to fitted regression coefficients.
- **Mghost 10-second-stale neighbor:** same number and type of regressors as M1, but partner GPS/velocity from exactly ten existing matched samples earlier. Allow only 8–12 seconds of actual lag; retain identical responses and valid M0 rows across models. This negative control preserves the same partner and homeward flight context but breaks strict present-time coordination.

All models use ridge regression with **fixed alpha=30**, standardizing numerical features on training folds only (non-intercept SD floor 1e-4). Training uses all other individual components, no target bird or its other flights ever enters training. The graph of bird IDs linked by flight dyads, **across both sites**, defines fully connected independent holdout components. Require at least 5 such components to evaluate. Each held-out flight scores both roles; two roles are one paired flight. Average MSE first within flights then within held-out bird-connected components, giving equal weight to the latter, not to GPS rows.

The primary contrast is **MSE(Mghost) − MSE(M1)**, with positive values favoring actual live-neighbor information. The secondary contrast is **MSE(M0) − MSE(M1)**. Report 10,000 seeded whole-component bootstrap percentile 95% intervals for all contrasts, exact one-sided component sign-test p, positive-group count and structural design condition number for two lateral neighbor kernels (training data only). A positive *primary* result requires its full bootstrap interval above zero **and** the secondary actual-vs-own interval above zero. Otherwise the new prediction is unsupported; the chosen 10s ghost timing, 4m/s speed, model features and ridge alpha may not be tuned after results. Even a positive contrast remains a *predictive association*: shared routing decisions, simultaneous exposure to spatial cues, pseudoreplication within a component, unobserved habitat and GPS position error can create correlations.

## Boundaries and next ecological link

This test does not identify the causal force of attraction, separation, alignment, biosonar or any specific communication. A two-kernel design may remain ill-conditioned, in which case reliable prediction cannot establish a unique Boids coefficient. Vertical niche shape identity is not tested by short homing flights, and a single pigeon species does not establish interspecific niche partitioning. If the movement prediction transfers across independent bird components, the next preregistered study must compare the *multiday spatial-state probability distribution* and niche information conditional on horizontal position before attempting connections with batter/ODSP/louis/mina.

## Reproduce

```bash
PYTHONPATH=validation_v8 python -m unittest discover -s validation_v8 -p 'test_pigeon_social_forecast.py' -v
python validation_v8/pigeon_social_forecast.py --out validation_v8/results/pigeon_social_forecast_v8.json
```
