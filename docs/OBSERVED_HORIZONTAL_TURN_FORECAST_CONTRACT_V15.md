# v15 frozen exploratory contract — original GPS horizontal next-turn forecast

**Frozen 2026-10-28 JST before calculating v15 turning forecasts.** This is a *new observed-data exploratory* test on the independent 2026 Zenodo source; original v6/v8 negative outcomes, v13 synthetic outcome, and v14 source-quality receipts remain frozen and unchanged.

## Data and exact source

Huang et al. (2026), DOI [10.5281/zenodo.21092705](https://doi.org/10.5281/zenodo.21092705), version 1.0.0, CC BY 4.0. ZIP filename `pigeon_homing_public_trials_v1.0.0.zip`; **126,588,691 bytes**, published MD5 `5c1e9b386bff5794e177b122b1fcb244`; independently observed ZIP SHA256 `756eed718ad13c14233e60b19009ce0916f183eb540b1262ba030ebc25a0ab03`. The ZIP has three independent flock-flight episodes (7/11/10 bird files, 13 distinct identities). Enforce these exact bytes and the published 56 original member SHA256 checks before fitting. Download original in a temporary runner directory; never commit raw tracks.

## Question, outcome and causal boundary

**Does a bird's presently co-observed nearest partner better predict its 1-second-ahead GPS ground-track heading change than that *same* partner's state 10 seconds earlier, after the focal bird's own history and route-state variables are included?**

- Outcome: `wrap_radians(course_over_ground[t+1s] - course_over_ground[t])`. Use *measured* original NMEA `$GNRMC` heading, not IMU-derived turn and not inferred physical acceleration. Score wrapped angular squared error (rad²) on **identical held-out target records for each candidate**.
- Experimental unit for trial transfer: entire **source flock-flight episode**. Exactly 3 leave-one-trial-out folds. Repeated birds across trials mean this is not independent bird-identity transfer. Report every held-out trial separately and equal-weighted across the three trials. An exact trial-level one-sided sign test has minimum `p=0.125` for 3/3 positive; a positive mean is **not confirmatory**.
- No altitude, no feeding-resource measurement, no manipulated contact-network membership; therefore *no* Boids-force recovery, v13 acquired-niche mechanism, competition or 3D niche claim.

## Outcome-blind flight and observation admission

- Parse original valid NMEA RMC; validate any provided NMEA checksum and reject mismatch, but explicitly count records without a CRC field. Reject void fixes, invalid date/time, out-of-domain coordinates, missing ground speed/heading, and duplicate raw UTC timestamps (all duplicate rows). Convert RMC speed knots → m/s with `0.514444`. Use GPS heading compass degrees → radians.
- A valid **airborne run** consists of consecutive observations with raw GPS speed **6 ≤ speed ≤ 35 m/s**, positive time spacing **≤0.5 s**. Break on every dropped/bad observation or invalid/slow speed; retain runs spanning **at least 12 s** and containing **at least 60 fixes**. These conservative cutoffs are preselected without reading any turning-model performance.
- Sample focal anchor **every 5 seconds on the absolute UTC grid**. A focal event at `t` requires valid GPS fixes nearest (not interpolated) to `t−10s`, `t−1s`, `t`, `t+1s`, each within **≤0.2 s** and within the *same* uninterrupted airborne run. It must have a partner measured at `t` and `t−10s`, also within ≤0.2 s and inside the same partner airborne run. For partner B, choose the latest recorded raw fix **at or before the actual focal A fix time** (never future partner measurements); earlier partner lag ≤0.2 seconds. Current partner is selected deterministically as the **closest measured bird other than the focal animal within 100 m at `t`** (ties: lexical ID); partner choice never examines the target `t+1`.
- Compute social features as *relative geometry between B and focal A at the same respective time*: present `A(t),B(t)` and stale `A(t−10),B(t−10)`. Do **not** compare stale `B(t−10)` to present `A(t)` (this would create artificial time-displacement leakage).
- The original RMC time stamps are not synthetically filled, spline-resampled or repaired. The validity of device UTC synchronization remains a limitation, and observations cannot be treated as independent rows.

## Fixed predictors and regularization

**M0 (own+route)**: intercept; sin/cos focal compass heading at t; focal speed/15; own signed course change t−1→t; own speed change t−1→t divided by 5; time since **start of currently admitted flight segment** divided by 300; east/north coordinate displacement from the segment's **observed first point** divided by 1000 (only historical route information). All features observable no later than time t.

**M1 (present actual partner)**: M0 plus six social features computed from same-time A(t), B(t): along-heading separation/50, lateral separation/50, log1p(distance_m)/5, sin and cos relative heading difference, (B_speed−A_speed)/10.

**M2 (stale actual partner)**: same M0 plus the identical six social features computed at A(t−10), B(t−10); partner ID must be exactly the one chosen for M1 at t. The focal's own historical speed/heading at t−10 is *not* otherwise supplied in M0; both feature vectors carry the same number of columns. Historical partner/own geometry is an imperfect control for route and time—**not proof of social causation**.

**M3 (30-s time-shifted surrogate; secondary)**: M0 plus social features computed from A(t−30), B(t−30) for the same partner, if both are observed in the same uninterrupted flight runs; explicitly a 30-second *lagged surrogate*, **not** an independently observed ghost bird. M3 and M0/M1/M2 are retrained and re-evaluated on the **identical subset requiring 30-s history**. Do not compare this secondary subset directly with primary means.

**Zero-turn** (descriptive only): predict no heading change.

- Models are separate linear ridge regressions, fixed `alpha=30` penalizing standardized non-intercept coefficients; the intercept is unpenalized. Apply training-only mean/scale to all predictors. Fold training data are weighted to contribute **equally per source trial** regardless of fix count; heldout trial is never used to standardize or tune.
- No hyperparameter optimization, threshold redefinition, extra candidate features, test-driven exclusion, or post-hoc subgroup rescue. All eligibility rules apply identically to primary models.
- Required structural admission: **≥60 primary anchors and ≥3 distinct focal bird IDs in *each* of the three trials**, otherwise stop with a fully reported **not admitted** outcome. M3 secondary is reported only if each of the three trials also has ≥30 anchors on the restricted matched subset.
- Report by trial: raw fixes, airborne segments, eligible anchors, final matched targets, held-out MSE of zero-turn/M0/M1/M2, primary (M2−M1) MSE advantage, secondary (M0−M1) MSE advantage, paired M1 vs M3 subset contrast, and sign counts. Trial equal-weighted mean and min one-sided sign-test p bound; no row bootstrap CI advertised as ecological uncertainty.

## Primary interpretation and stop rule

- The **primary** descriptive target is `Δ_current_vs_stale = MSE(M2) - MSE(M1)` on the same held-out trial. Positive favors present partner information. It can also reflect shared stimuli/route or measurement error; does **not** uniquely identify separation/alignment/cohesion or interaction causality.
- A nonpositive primary result or lack of structural admission stays negative. No refitting frozen thresholds on that same source to rescue it.
- If positive in all 3, describe only **directional exploratory transfer within three source trials**, not `p<0.05`, field-validated flock law, or generalizable niches.
- Save aggregate-only JSON and logs to GitHub Actions; never publish raw GPS/IMU, individual routes or coordinates. Cite full source and acknowledge CC BY 4.0.

## Reproduction

```bash
python -m pip install "numpy>=1.26,<3"
PYTHONPATH=validation_v14:validation_v15 python -m unittest discover -s validation_v15 -p 'test_*.py' -v
python validation_v15/forecast.py --out validation_v15/results/frozen_turn_forecast_v15.json
```
