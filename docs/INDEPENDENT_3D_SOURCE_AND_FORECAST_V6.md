# v6 — Independent synchronized 3D flight-pair observation gate and directional prediction

**Design frozen 2026-10-26 after viewing metadata and the *shapes* of the four MATLAB variables, before inspecting their numeric trajectories or model outcomes.**

## Core distinction

1. **Boids microdynamics**: steering as a function of own motion, observed neighbor position/direction, environment and uncertainty.
2. **Observed directional prediction**: can a *recorded partner*'s state predict the next directional change of a bat better than own-history and cross-trial ghost features?
3. **Emergent ecological niche**: long-term 3D use distributions and species/individual identity. **This third claim is not estimable from these 0.4–few-second segments.**

This lane is a novel, externally sourced bat-pair *prediction association* benchmark. It is not a confirmation of the previously published directional coupling, because both studies use the same Roy & Abaid archive, and it is not an independent sample from the original paper. It is independent of the older `Tadarida` GPS material in `batter` and `odsp`.

## Public candidate decision, fixed before numeric trajectory inspection

| Priority | Repository / DOI | Verified source semantics | Gate |
|---|---|---|---|
| 1 | Roy & Abaid bat pairs; `10.7294/W4639MWR` | Figshare `data.mat`, 577,806 bytes; MD5 `df055ac743fb2cc593a99c70a7afa15f`, four variables `XYZ_b1`, `XYZ_b2`, `Curvature_b1`, `Curvature_b2`, each cell vector 30×1; published pairs and obstacle/no-obstacle contexts | **Primary structural preflight and first exploratory directional prediction** |
| 2 | Watts et al. pigeon flocks; `10.5061/dryad.f9n8t` | 5 Hz GPS, 5- and 10-bird flock releases; official metadata 231,804,005-byte ZIP; direct raw GPS, no independent camera height calibration verified yet | Candidate independent *bird* validation only after own admission contract |
| 3 | Mehlhausen-Franks pigeon landscape; `10.5061/dryad.4tmpg4fp6` | 5 Hz position/flight habitat summary in 35.51 MB CSV; documented `Longitude`, `Latitude`, individual/flight time, but no confirmed bird-height field | Cannot assume full 3D use; valid for 2D/environment response only |

No source will be added after seeing candidate outcomes to rescue a negative result. Source 1 was selected for verified 3D paired trajectories and small checksum-pinnable public file, not for any favorable observed turning effect.

## Measurement and provenance warnings

- The source authors fitted a spline through bat trajectories and **resampled at 180 Hz**. The sample interval in `data.mat` is therefore **not evidence of independent camera measurements at 180 Hz**. The reported median flight duration is around 1.26 s.
- Recording used paired bat movement through a cave flight corridor. A partner can predict turning simply because both follow the same confined geometry or react to the same unobserved event. A predictive increment is not proof of copying, attraction, avoidance, echolocation, memory, or competition.
- `b1` and `b2` refer to ordering of entry in the tracking volume, not verified stable named individuals across the 30 episodes. No population-level biological replication count can be inferred from 30 segments. Flight-pair-resampling intervals condition on these **recording episodes** only.
- Original camera frame timestamps and independent 3D localization covariance are not available in the verified `data.mat` variable schema. Equal array index is assumed to imply within-pair temporal alignment per source description, but direct acquisition timestamp sync cannot be independently checked. Full separation/alignment/cohesion parameters **remain structurally unidentifiable**.

## Frozen source and quality gates

1. Fetch the official Figshare article 14097077 and source file ID 26581166, and require the expected 577,806 bytes and pinned MD5 before opening the MATLAB arrays.
2. Require *exactly* 30 cells in each of `XYZ_b1`, `XYZ_b2`, `Curvature_b1`, `Curvature_b2`. Load only `XYZ_b1` and `XYZ_b2` for prediction; never re-identify individuals based on their outcomes.
3. Require within-pair arrays of equal length with 3 columns, all finite coordinates, and non-zero steps. No interpolation to rescue missing coordinates or unequal lengths.
4. Predeclare numerical stride 6 from the interpolated 180 Hz series (nominal ~30 Hz). Require at least 12 downsampled positions per pair and at least 12 eligible flight episodes. **Do not change either gate based on observed support.**
5. Failure of the gate is `STOP`, not an invitation to re-bin or change a distance/time window. Report the failure and code receipts.

## Predeclared predictive estimand

At each admissible target time, compute from past/current downsampled positions an own heading `h_i,t` and previous heading change `h_i,t − h_i,t−1`. The outcome is next heading change `h_i,t+1 − h_i,t` (no absolute speed forecast). Each target role is independently predicted.

- **Own-history baseline M0:** current unit heading (3), previous 3D heading change (3), absolute current XYZ location (3), current speed (1), fractional time into paired recording (1). These variables attempt to control some, but not all, shared cave geometry and smooth spline dynamics.
- **Recorded partner model M1:** M0 plus partner heading perpendicular to own heading (3), and perpendicular unit vector toward recorded partner (3). This is a *predictive social-context feature set*, not an estimate of unique Boids force coefficients or a true interaction radius.
- **Ghost partner control Mghost:** same M1 feature definitions but the partner is taken from the fixed `(pair + 7) mod N` **other eligible flight trial**, skipping the held-out target trial as a possible donor for all training rows in each CV fold. Its path is interpolated onto the target trial's *normalized progress*. The held-out target pair is never read by any training-side ghost feature. It is not an ideal environment-matched control; its limitations must be shown.

Numerical update: the absolute path coordinates were not used to define a neighbor radius and no distance threshold is tuned. Fit multi-output ridge on turning vectors with alpha **10**, standardization from train rows only and pair-balanced training weights. Use leave-one-**whole-pair-recording**-out cross-validation with both bats evaluated and averaged within target episode; target records never appear in the training design or in ghost donor own features. The primary metric is equal-episode difference in 3D turning MSE:

`G_primary = MSE(Mghost) − MSE(M1_recorded)`.

Positive is predictive superiority of the recorded partner over the unmatched ghost for this particular design. Report also `MSE(M0) − MSE(M1)` and `MSE(M0) − MSE(Mghost)`. Bootstrap 5,000 whole-flight episodes (fixed seed 20261026) for descriptive percentile intervals; no claim of independent animals or causal social influence.

## Stop / decision rules

- No confirmed source MD5, no 30×1 schema, or fewer than 12 eligible pairs: `STOP` before fitting.
- A non-positive primary gain: **no positive predictive evidence for real-partner-specific information over the fixed ghost** at this temporal grain; retain as negative benchmark.
- A positive primary gain: **partner-specific held-out turning information conditional on a limited own-history/geometry baseline**. Cannot yet establish social force without measurement-error and common-cause control; no ecological niche or species-general prediction.
- A positive real-partner gain with poor ghost behavior is not proof of attraction/alignment; partner distance and shared spatial confinement remain confounders.
- Do not retrospectively change stride, ridge alpha, pair admission, ghost offset, or resmoothing based on results. No multiple alternative ghost choices as rescue.

## Reproduce

```bash
python validation_v6/source_preflight.py --out validation_v6/results/bat_pair_schema.json
python validation_v6/paired_trajectory_gate.py --out validation_v6/results/paired_eligibility.json
python validation_v6/social_forecast.py --out validation_v6/results/bat_pair_directional_forecast.json
PYTHONPATH=validation_v6 python -m unittest discover -s validation_v6 -p 'test_*.py' -v
```

Official source file and license: https://doi.org/10.7294/W4639MWR (CC BY 3.0 US); empirical paper Roy et al., *Entropy* 21:42 (2019), https://doi.org/10.3390/e21010042. This repository redistributes only manifest, code, output summary and tests, **not raw flight trajectories**.
