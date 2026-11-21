# v13 Acoustic Boids: persistence and mechanism audit protocol

**Status:** SYNTHETIC_ONLY_NOT_FIELD_RESULT. Protocol written before the v13 seed sweep.
**Date:** 2026-11-21 JST.
**Baseline:** zuizui0223/boids at 609dfac2fdf87fca8767c6836cdb1ce254b71f55; v12 source is preserved.
**Authority:** continuation of the existing Boids research task. PR #248 stays Draft; no main update or merge.

## Question and interpretation

Does the v12 playback contrast remain after a much longer observation period, and after delaying the same pulse until the group has already evolved? Which explicitly programmed acoustic links are necessary for the contrast? A finite pulse response is not by itself evidence of bistability. The mean-field and microscopic models are distinct; their gains are not numerically identified with each other.

This is a prospective computational sensitivity audit of an already exploratory, deliberately chosen v12 model, not a preregistered biological test. Seeds are simulator replicates, not fish shoals. No model parameters will be fitted to these results or to published effect sizes.

## Fixed numerical experiment

- Preserve the v12 equations, update ordering, initial-state distribution, RNG consumption, 32 individuals, dt=0.06, stimulus magnitude 0.8 and duration 40 steps.
- New seeds: 1000 through 1023 inclusive (24 independent simulator initializations).
- Horizon: 4000 steps, or 240 arbitrary model-time units. These time units are not calibrated to fish seconds.
- Four mechanisms (audio steering weight, hearing-to-call weight): full (5,3), no acoustic steering (0,3), no hearing-to-call response (5,0), neither link (0,0).
- For every mechanism and seed: no pulse and pulse at steps [1000,1040). The full mechanism additionally receives the original early pulse [80,120).
- Reuse the same no-pulse full trajectory for both timing comparisons. Total: 216 trajectories, 864000 individual simulation steps across trajectories.
- Use matched initial states and matched random draws at every time step across arms of each seed. Independent seeds remain the unit of uncertainty.
- All four v12 parameters determining movement/hearing remain exploratory design constants; no tuning after outcomes.

## Outcomes and uncertainty

Primary numerical contrast: warmup-pulse minus no-pulse call fraction averaged over terminal steps [3000,4000).
Secondary: corresponding convex-hull area difference in arbitrary squared-distance units.
Report all five contrasts: full early pulse and each of four warmup mechanisms.

Also report pre-pulse [start-200,start) where available; during [start,end); immediate post [end+10,end+50); intermediate [end+120,end+320); penultimate [2000,3000); terminal [3000,4000).
For the early pulse, pre-pulse window is [0,80). For the original v12 replay only, retain [130,170) and [240,280).
Report no-pulse and pulse levels as well as differences, per-seed values, sign counts and paired bootstrap 95% intervals over the 24 seeds (10000 resamples, RNG seed 20261121). Reuse the resampling index matrix across contrasts.
These intervals describe Monte Carlo variation in the stipulated model. They are not animal-population confidence intervals, formal equivalence tests, or multiplicity-adjusted discovery tests.

Report warmup factorial interaction of the two acoustic links: delta_full - delta_no_motor - delta_no_hearing + delta_neither, paired by seed. This is an interaction between model interventions, not a mediation estimate for real fish.
No p-value discovery gate. Do not infer absence of a biological effect from a near-zero contrast.

## Implementation and checks

- Replay original v12 seed 2 and all original 12-seed summary endpoints before making comparisons. Preserve the original source and keep long-run output separate.
- Meaningful tests: matching v12; no acoustic steering implies identical movement across pulse arms; no hearing response implies identical calls immediately after pulse; no future pulse effect; invalid inputs rejected.
- Analytic audit: derive exact fold bounds and full two-state discrete-time stability; root solver must handle tangent and critical roots; perform converged increasing/decreasing theta continuation.
- Produce figures directly from saved numerical arrays. Inspect rendered figures.
- Independent review of code and scientific interpretation before final commit.

## Literature and claim audit

Check van Oosterom et al. 2016 (10.1038/srep19098) for units, design and post-stimulus observations. Check earlier primary fish-playback literature for post-stimulus calling and context dependence. Correct historical prose where an effect unit or novelty claim is inaccurate, while preserving numerical v12 results.
Do not claim new field evidence, universal logistic threshold, fitted individual fish forces, or observed motion-call feedback.

## Deliverables

New v13 simulator extension, mathematical audit, executable runner, tests, workflow, results summary, complete per-seed data/figures in a reproducible bundle, and a Japanese scientific report with primary citations. Add results to existing Draft PR #248 using a guarded branch update.
