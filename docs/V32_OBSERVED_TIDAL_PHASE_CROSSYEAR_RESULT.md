# v32 observed tidal dynamics: cross-year transfer and same-water-height hysteresis

**Date:** 2026-11-02 JST. **Source:** original Zenodo v5 2009–2011 GPS and contemporaneous original RWS measured Schiermonnikoog Waddenzee WATHTE, cm/NAP, fixed UTC+01. **Status:** OBSERVED POSITIVE PREDICTIVE ASSOCIATION, clock/shore-front not independently calibrated.

## Positive results, frozen BEFORE 2010–2011 outcome in `V32_PREOUTCOME_THREE_YEAR_TIDE_TRANSFER.md`

The pre-specified cross-calendar-year model was frozen with hourly first-fix per bird and within 0.5–2h observed great-circle horizontal displacement (log1p km/h). Water height, square, source latitude/longitude, diel and annual cycles form M0; M1 adds ebb/flood phase, its interaction with water height and 20-minute prior water-height rate. Train-time standardized ridge with L2=10 and equal total per-bird weight; score every bird equally in the unseen complete calendar year. Raw coordinates and bird identifiers were not published.

| Train → completely withheld test year | Test steps | Test birds | Test weeks | M0 equal-bird MSE | M1 equal-bird MSE | Gain M0−M1 | Gain/M0 | Positive birds | Positive weeks | 95% bird-bootstrap gain CI | 95% week-bootstrap gain CI |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 2009 → 2010 | 70,561 | 21 | 53 | 0.172425161 | 0.169997722 | **+0.002427439** | **+1.4078%** | **19/21** | **45/53** | [+0.001879799, +0.002931679] | **[+0.001472982, +0.002568498]** |
| **2010 → 2011 (PRIMARY)** | 46,653 | 13 | 53 | 0.163169228 | 0.158718057 | **+0.004451170** | **+2.7279%** | **12/13** | **47/53** | [+0.002549349, +0.006673264] | **[+0.001200905, +0.003460766]** |
| 2009+2010 → 2011 | 46,653 | 13 | 53 | 0.164665686 | 0.160399648 | **+0.004266038** | **+2.5907%** | **12/13** | **48/53** | [+0.002502968, +0.006339430] | **[+0.001150083, +0.003358034]** |

The prescribed -15-second 2009–2011 GPS/UTC time interpretation gives the same **positive signs and nonzero bird/week intervals** for all three transfer directions. In particular, 2010→2011 becomes +0.004476958 (+2.744%), 12/13 birds, 47/53 weeks, week CI [+0.00122143,+0.00348380]. This is a *same-site cross-year predictive transfer result*, not a different population, species-general behavior or verified tidal causal mechanism.

## Independently interpretable observational descriptive contrast

Original GPS is matched within bird, calendar month, water level (0.15 m bins) and 6-hour clock bin, with at least three ebb and three flood observations per stratum.

| Year | Matched strata | Total used records within matched strata | Ebb-faster birds | Mean ebb−flood log1p(km/h), equal bird |
|---|---:|---:|---:|---:|
| 2009 | 787 | 8,440 | **7/7** | **+0.06675746** |
| 2010 | 4,493 | 47,766 | **21/21** | **+0.09843962** |
| 2011 | 2,994 | 32,122 | **11/11** | **+0.11407964** |

These are *descriptive matched* associations, not raw speed differences, experimental manipulations, independent bird-year replication, or proof of movement toward newly exposed prey. The 2009–2011 contrast survives the -15s clock sensitivity with same directional bird counts.

## Distinct prior tests must not be conflated

Separate v31/v32 direct/high-cadence within-calendar-year model (2min–1h fixes, identity intercepts, M1 adds phase and phase×height but **not** rate) gives within-year signed MSE error reduction **+0.68% (2009, 3 test birds), +0.33% (2010, 15), −0.17% (2011, 6)**. Week intervals all cross zero. This does not contradict the separate, hourly, cross-year model; **different endpoint representations and extra rate term mean the observed positive v32 result cannot yet be exclusively attributed to ebb/flood phase**.

## Limits and next exploratory challenge

- Original `timestamp` is documented as **UTC or GPS time**, not independently decided; 0 vs -15s checks only this ambiguity, not every station-vs-bird tide propagation lag, timezone misannotation or clock drift.
- Source water level is at `schiermonnikoog.waddenzee`, identity with the exact Dryad instrument not established. The field birds use a spatially complex intertidal system, so local ebb/flood timing can differ from station timing.
- Water elevation at a patch, exposure age, prey abundance and actual moving shore boundary are **not observed** here; M2 resource-front hypothesis NOT_ESTABLISHED.
- No observed social response vs synchronized ghost negative control was fitted; Boids social M3 NOT_ESTABLISHED.
- The full-year external prediction contains the water-rate variable along with tide phase. A **post-result, explicitly exploratory** feature ablation and rigorous local tidal lag/clock negative controls are necessary before making any claim about the unique phase-only mechanism.
- Heldout weeks are not fully statistically independent of seasonal or site drivers; bootstrap intervals reflect the chosen test-week and test-bird resampling units, not a causally identified effect.

## Reproduce and exact receipt

- [GitHub Actions original three-year run 41409144120](https://github.com/zuizui0223/boids/actions/runs/41409144120) — original 2009, 2010 and 2011 Zenodo GPS provider MD5 rechecked, 2009–2011 RWS NAP source data joined, frozen year-external scoring, and matching.
- [Original zenodo dataset v5](https://zenodo.org/records/22296922), species `Haematopus ostralegus`.
- Code `validation_v32/cross_year_tidal_transfer.py`, previous preregistration `docs/V32_PREOUTCOME_THREE_YEAR_TIDE_TRANSFER.md`.
- The complete machine-readable aggregate run receipt was captured by the GitHub Actions output; raw source tracking coordinates are never redistributed in this repository.
