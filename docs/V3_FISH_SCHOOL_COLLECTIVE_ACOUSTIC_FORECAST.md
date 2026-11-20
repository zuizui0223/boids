# Fish school × fish chorus v3 — source-gated collective prediction

Status (2026-11-20): **synthetic experiment executed, field data not fitted, review-only Draft.**

## Research question

Does information about a moving **collective acoustic source centre and velocity**, reconstructed from multiple hydrophones, improve online prediction of next observed receiver intensity beyond the same receiver's previous measured intensity?

Reference schooling implementation: https://github.com/SebLague/Boids (MIT, Sebastian Lague, 2019). Its separation / alignment / cohesion forces motivate the movement problem but **are not estimated from five hydrophone chorus intensity records**.

## New known-truth result (not ecology)

20 independent simulation training days, 16 untouched test days, five receivers and synthetic Gaussian source attenuation. Fixed train-only Kalman velocity hyperparameter selection. Equal receiver and t+1 audio MSE: M0 clock 0.4973203; M1 previous intensity 0.0057197; M2 inferred centre/velocity 0.0052366; M3 wrong receiver geometry 0.0057790. M2 improves MSE versus M1 by +0.0004831 (8.4%), in 15/16 test days, synthetic-day bootstrap interval [0.0003025,0.0006796]. This is *not* an estimated fish effect; bootstraps resample simulator days.

Full executable Python known-truth suite, unit tests, exact result JSON and source-only gate are packaged in the conversation's fish_school_chorus_v3.zip artifact. Numeric data are summarized under validation_fish_school_v3/results/known_truth_summary.json; **the full suite is not yet committed into this repository branch**. Do not claim GitHub CI replay of the full numeric benchmark.

## Official Dryad source gate

Source: Ota et al. (2025 archived, 2026 Methods in Ecology and Evolution), https://doi.org/10.5061/dryad.zkh1893qn . Target: five-hydrophone original chorus-cropped acoustic intensity q25_autoChorusDetect4.zip and mic_location_xycoordinate.csv. Branch script validation_fish_school_v3/dryad_source_gate.py uses only official public Dryad API; source stops on HTTP 401/403, changed membership/digests, unsafe ZIP and fewer than five coordinate rows.

**A source-only success is not an ecological effect.** Acoustic outcome values are never opened in this gate. No animal records or raw sound are redistributed.

## Empirical task frozen before opening data

- Verify original receiver IDs/times, actual recording-effort overlaps, ≥7 complete source recording dates and ≥2 whole-day holdouts; else SOURCE_SUPPORT_STOP.
- Use only prior-in-time observations to infer collective state. Published MCMC summaries may contain future observations and must not be used as independent next-step truth or predictors.
- Primary target: log sound intensity *conditional on publisher-selected chorus-positive observations* at five receivers. Not true chorus onset or absence.
- Fit M0 clock+source-time-known environment, M1 previous acoustic intensity, M2 prior-only multireceiver inferred collective state and inertia, M3 wrong-receiver layout. Exact matched targets and training-only tuning.
- Days, not audio windows or synthesized posterior samples, are replicate units for uncertainty.
- A field M2 advantage would show group-level predictability, not separation/alignment/cohesion or social vocal triggering.

Do not merge or publish a fish-mechanism claim without independently verified original source and out-of-day numerical holdouts.
