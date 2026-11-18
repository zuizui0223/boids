# v184｜6月校正のみで7〜9月を予測：2018・2019年RWS独立二観測所（原本SOURCE / 生物行動なし）

**Frozen before viewing any July–September true tide values for the two-station transfer.** Stacked after v183 #201, which found a descriptive best lag of +30 minutes (West-Terschelling behind Vlieland Haven) on June 1–3 in 2018 and 2019. That pilot selected the positive lag, so this is not a from-scratch independent hypothesis.

## Fixed physical test

* Two original Rijkswaterstaat DDAPI2 stations only: Vlieland Haven exact code `vlieland.haven` and unique original-catalogue West Terschelling.
* Train OLS `West(t) = a + b * Vlieland(t-shift)` **only 2018 June 1–3** original `WATHTE` `cm` `NAP` measurements; independently fit each prespecified lag `0, +30, -30, +90` min using the exact same time-index outcomes across all models.
* For heldout comparison, **do not refit** on 2018 or 2019 July 1–3, August 1–3, September 1–3, six fixed 48-hour windows. No June 2019 reused as an alleged untouched holdout.
* The primary physical contrast is heldout `MSE(lag 0) - MSE(lag +30)`. Positive means 30-min phase correction improves West-station water-height prediction **relative to contemporaneous Vlieland water height**, not evidence for bird GPS-specific h(s,t). Reverse -30 and +90 minutes are prespecified controls; report all six blocks, and aggregate over exactly equal target instants for each lag.
* SOURCE gate ≥200 records per original station for each 48h window and ≥200 common paired targets for all four lags. All original data `cm NAP` and +01:00 timestamps or fail closed. No shifting dates, stations, data windows or interpolation to rescue any positive result.
* A simple **descriptive** robustness threshold is ≥4 of 6 heldout windows with positive primary MSE gain and positive all-window pooled gain; failing threshold is a meaningful limit. Given shared coastline and only two years, report no independent six-sample p value and no causal inference.
* Output original publisher response SHA, station identity, coefficients, aggregated heldout MSE and source validity counts only. **No raw measured tide series or individual bird GPS, ACC or DEM grids.**

The original 10-tile DEM vertical datum and exact local GPS tidal correction from v182 remain STOP. Even a strong v184 pairwise station transfer **does not** establish local mudflat exposure or tide/solar niche mechanism.
