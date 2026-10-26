# v6 frozen observed bat-pair result — real partner has no reliable held-out advantage

**Date:** 2026-10-26.  **Status:** COMPLETED EXPLORATORY EXTERNAL-ARCHIVE ANALYSIS, primary predeclared endpoint *not supported*. Original analyzed archive was distinct from older *Tadarida* GPS panels but this is **not** an independent replication of Roy et al. 2019 on their own dataset.

## Reproduction and provenance

- Public source: Roy & Abaid, *3D trajectories and corresponding curvatures of 30 bat pairs*, [DOI 10.7294/W4639MWR](https://doi.org/10.7294/W4639MWR), Figshare file `data.mat`, 577,806 bytes, MD5 `df055ac743fb2cc593a99c70a7afa15f` (verified directly in GitHub Actions). Data published under CC BY 3.0 US; **raw source is not redistributed**.
- Prospective code and source gates: [predeclared v6 study contract](INDEPENDENT_3D_SOURCE_AND_FORECAST_V6.md). The commitment to use 30×1 pairs, 180-Hz-spline numerical stride 6, exact accepted 3D arrays, and minimum 12 eligible pairs was made after reading only the MAT variable *shapes*, before viewing trajectory coordinate values and outcomes.
- Confirmed four arrays: `XYZ_b1`, `XYZ_b2`, `Curvature_b1`, `Curvature_b2`; 30 episodes each.
- Eligibility pass: **28/30 flight-pair episodes**; #8 and #20 excluded for `FAIL_TOO_SHORT` under the *unchanged* predeclared 12-point-after-decimation rule. No pairs excluded for unaligned length or nonfinite positions.
- Observation premise: published cubic-spline reconstructed flight paths, resampled to **180 Hz**. Downsampled computationally by a factor of 6 (nominal 30 Hz), which **does not create or verify independent 30-Hz raw camera observations**. The source archive lacks verified independent height-error estimates and explicit original acquisition-frame timestamps.
- Github Actions: [held-out forecast run](https://github.com/zuizui0223/boids/actions/runs/40277563862). Complete replay artifacts: `validation_v6/results/paired_eligibility.json`, `validation_v6/results/bat_pair_directional_forecast.json`.

## Primary endpoint: actual recorded bat versus unmatched ghost partner

Fit ridge models (alpha=10, train-only feature standardization, flight-trial balanced training) predicting the *next three-dimensional heading-change vector*. Held out **entire flight-pair episodes** (both target roles) and averaged errors equally across episodes. Compared only frozen own-history baseline, actual-pair extra features, and other-flight ghost extra features. Do not treat time steps as independent animals.

| Measure | Observed equal-pair mean | Whole-pair bootstrap 95% interval |
|---|---:|---:|
| Own-history MSE | 0.0251675 | — |
| Own + recorded partner MSE | 0.0249940 | — |
| Own + ghost partner MSE | 0.0255488 | — |
| Recorded partner improvement beyond own | +0.0001736 | −0.0004980 to +0.0009481 |
| Ghost partner improvement beyond own | −0.0003813 | −0.0007759 to −0.0000158 |
| **Recorded over ghost (primary)** | **+0.0005548** | **−0.0000919 to +0.0012760** |

The actual-partner model improved on the ghost model in **16/28** episodes. A descriptive one-sided exact sign test on the 28 episodes is p=**0.286**, computed *after* primary analysis only as a diagnostic, **not** a post-hoc new primary gate. The own-only to recorded-partner decrease in mean MSE is ~**0.69%**, not an ecological variance-explained quantity.

**Decision:** The primary difference is positive as a point estimate, but its pair-level bootstrap interval crosses zero and the sign of improvement is heterogeneous. **The frozen study does not establish a robust held-out prediction advantage of the actual partner.** This is a result, not a source-screen failure.

## Interpretation and constraints

The literature reports curvature transfer entropy / convergent cross mapping evidence for coupling in these bat recordings under a specific environment control (Roy et al., *Entropy* 21:42, 2019, https://doi.org/10.3390/e21010042). Those are different **in-sample/dynamical informational questions** from the present **held-out 3D heading forecast with other-pair ghost control**. Failure of the latter does not overturn the former, and reported literature effects do not validate this new predictor.

Neither a positive *nor* a negative MSE gain identifies the biological mechanism. The 30 recordings may re-observe the same unknown bat individuals; the biological replicate remains unresolved. Common cave geometry and spline smoothing affect the conditional dynamics, the ghost trajectories are not physically geometry-matched, and short windows cannot separately identify alignment, separation and cohesion force parameters (the two positional attraction/repulsion vectors are close to collinear for a pair).

The trajectory segments are **inadequate for batter-type multi-night individual 3D-niche repeatability, species overlap or niche-axis transfer testing**. The v1–v3 synthetic ABM and surrogate forecasts remain demonstration/known-truth results; v4 `Tadarida` GPS persistence remains an error-confounded short-step association (see v5).

## Explicit closure and forward path

**Close this source/model/grain for post-hoc tuning.** No changing the stride, ghost offset, predictor set, ridge penalty, smoothing, or thresholds on this same data to rescue the primary result. Prospective next step should use an *independent tracking system* with measured positioning uncertainty and real multi-individual synchrony (e.g. high-cadence raw synchronized 3D images or 5-Hz raw pigeon flight GPS with an observation-error audit), *before* fitting or comparing 3D niche-space predictions.
