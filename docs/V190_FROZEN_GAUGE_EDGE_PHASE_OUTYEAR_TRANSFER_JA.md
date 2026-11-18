# v190｜2018年6月だけで観測所間位相差を校正し、2018年9月・2019年6/9月に係数固定で転移

**EXPLORATORY PHYSICAL SOURCE analysis, designed after seeing v188's 7/13 positive sites and 6/13 negative sites.** Frozen **before opening the v190 holdout results**.

## Scientific motivation
v183/v184 showed a reproducible +30min sea-level transfer from Vlieland Haven to West Terschelling. v188 13-site same-time interpolation improved global station-equal MSE but had strong influence from Eemshaven and sign reversals at six sites. A direct, falsifiable physical candidate is **phase shifts of the tidal wave between fixed sites**, not Euclidean station distance alone. The two-station pilot cannot supply 30min to all of the Wadden Sea.

## Source cohort, true clock, and split
Exactly v187's fixed 13 source-audited RWS station codes (exclude Den Oever, Nieuwstatenzijl). Original RWS `WATHTE` `cm` `NAP` genuine timestamps, 10-minute native, fixed source metadata and prior source SHA checks. 2011 independent WEBTICS RD geometry used to select each target's **three geographically nearest other gauges**, frozen before water. Their exact station codes cannot be changed based on correlations.

Train **2018 June 1–3 only** (48h), selecting each target–predictor edge phase lag from fixed grid −120 to +120 minutes every 10min by maximal **Pearson** correlation, tie resolved by smallest absolute lag then signed lag. The lag is defined so that prediction for target at time `t` uses neighbor observation at `t−lag`. Need ≥200 exact native UTC matched original 10-minute pairs for every edge; otherwise SOURCE STOP. This phase training **uses the target's June observations** and therefore does **not** constitute station-holdout out-of-site interpolation. Claim only **calibrated station-pair transfer** to different months/years.

Test with all trained lags locked and no refit on: **2018 September 1–3, 2019 June 1–3, 2019 September 1–3**. All target instants used by every model must be exactly the same and have the available frozen shifted source neighbor and target observations. Source gate ≥200 target instants in each target×window. If any source fails, do not replace original station or shift dates.

## Fixed models and controls
- **M0**: 3 nearest RWS gauge heights at the same UTC time, 2011 RD distance-based IDW (1/d²).
- **M1**: same 3 gauges and **identical weights**, each 2018-June-fitted edge lag `h_j(t−lag_ij)` (phase-only correction, no fitted amplitude or intercept).
- **M−**: negative-control reversed lag `h_j(t+lag_ij)`, identical weights/time/cohorts.
- Secondary context: nearest single other RWS gauge at same time.
- Primary `MSE(M0)−MSE(M1)` on untouched test months, summarized by **equal station weight** across all 13 targets in each window. Positive supports cross-month **station-calibrated physical phase-transfer**, not source calibration at bird GPS. Descriptive support only if ≥2/3 windows positive and pooled equal-station gain positive. Report all site signs, median/mean, delete-one-site influence, missingness, and raw source response SHA (not raw water levels). Negative effects are retained; no new lags, geographic weights, or lag intervals chosen after seeing holdout.
- This post-v188 physical model is **exploratory** even if test years were not previously read by this v190 phase model, because the entire design was motivated by v188 observed station errors. No p-values from serially correlated original 10-minute points.

## Scope
A strong result would establish a reproducible, location-specific physical time delay in station-to-station tide propagation. It would **not** establish 2018/19 RWS exact instrument positions (original catalogue X/Y missing), local `h(s,t)` at the birds' GPS coordinates, DEM `z` NAP vertical reference and exact field survey days, wet/dry ground exposure or tide×sun animal niche causation. v182 SOURCE STOP is unchanged. The known WEBTICS 2011 geometric interpolation is prior art.
