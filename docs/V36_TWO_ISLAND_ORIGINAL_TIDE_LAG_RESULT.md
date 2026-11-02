# v36 — Original two-island measured tide phase lag grid (post-result exploratory)

**2026-11-02 JST.** Original GPS provider-MD5 sources and RWS measured NAP tides, 2010 train and completely held-out 2011. This grid was chosen after v32–v34 outcomes, so **none of the five offsets is an independently confirmed optimum**. Only the source tide phase is evaluated at t+lag; original observed tide height h(t), bird GPS outcome and original row inclusion are fixed across all five lag variants.

## All five original-clock-UTC lag results, no winner selection

| Phase proxy timestamp | Schiermonnikoog M0−Mphase mean equal-bird gain | Schier % reduction | Schier positive birds/weeks | Ameland M0−Mphase mean equal-bird gain | Ameland % reduction | Ameland positive birds/weeks |
|---|---:|---:|---|---:|---:|---|
| t−120min | +0.01036646 | **+6.343%** | 12/13, 46/53 | +0.00408092 | **+2.349%** | 5/5, 49/53 |
| t−60min | +0.00759307 | +4.646% | 12/13, 50/53 | −0.00002822 | −0.016% | 3/5, 22/53 |
| t | +0.00443445 | +2.713% | 12/13, 49/53 | +0.00000528 | +0.003% | 3/5, 25/53 |
| t+60min | +0.00312945 | +1.915% | 13/13, 42/53 | +0.00138787 | +0.799% | 5/5, 40/53 |
| t+120min | +0.00167156 | +1.023% | 9/13, 37/53 | +0.00064809 | +0.373% | 5/5, 34/53 |

Sample support held constant across lags at a site: 2010 Schier training 70,542 and 2011 test 46,635 rows (13 test birds); 2010 Ameland 30,852 and 2011 test 31,212 rows (5 birds). Original GPS timestamps treated provisionally as UTC; -15s GPS→UTC sensitivity gave same general patterns (e.g. Ameland t−120min +2.375% vs +2.349% at 0s). No original raw GPS or tag IDs committed.

## Important inferential caution: distinguish estimands in uncertainty estimates

The numerical output's **equal-bird** main point estimates use per-bird pooled prediction error differences across all withheld observations. The output's **whole-week bootstrap** resamples equal-bird-per-week effects and therefore estimates a **mean equal-bird-week difference**, not the same pooled equal-bird estimand when weekly bird counts differ. Its 95% intervals must **NOT** be misrepresented as confidence intervals for the headline equal-bird point estimates. For example Schier t−120min pooled equal-bird +0.01036646 lies above its original whole-week interval [+0.00257252,+0.00884575]. This is not a CI paradox; it is an estimand mismatch needing an explicit aligned-unit reanalysis. Week-sign counts remain descriptive. Bird-level resampling must also account for few independent animals and shared tide cycles.

## Interpretation

The Ameland lag-0 small increment does not establish absence of tidal control, because fixed shifted-phase models show other positive predictive associations. However a 120min shifted proxy does **not** identify a 120min animal response delay: astronomical periodicity, measurement site, local propagation, activity routines and GPS original UTC/GPS clock ambiguity can all generate cross-lag predictive patterns. Lag grid was fixed only **after** earlier outcomes. Neither island has field-joined patch elevation, independently measured prey-exposure time or causal Boids social-force estimates.

The scientific defensible result is: tidal dynamic associations with GPS displacement are **context and time-reference dependent**; the strongest fixed site-level comparisons have positive cross-year predictive information in original data, but physical local-front tracking and cross-species mechanism remain hypotheses.

## Reproduce

- [Run 41412749762](https://github.com/zuizui0223/boids/actions/runs/41412749762) original source-backed v36 PR workflow, all test/source gates success.
- Code `validation_v36/two_island_phase_lag_grid.py` and tests. All raw positions and individual tokens remain external to GitHub.
- [Original post-result v36 lag-grid pre-outcome-of-v36 contract](V36_POSTRESULT_TWO_ISLAND_TIDAL_LAG_GRID.md). It is **not** preregistration before earlier observed source outcomes.
