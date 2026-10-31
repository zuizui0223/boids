# v33-D — fixed within-day tide-height–movement association

**Exploratory, after v32 opened the GPS data, and independently fixed before computing a GPS×tidal-height–stratified movement association.** This is distinct from the daily RWS astronomical RANGE forecast v33-C and must not be combined into a new confirmatory claim because both are explorations of the same Schiermonnikoog birds.

## Ecological distinction and prediction

The v33-C day-ahead forecast tests **spring–neap changes in daily predicted tide amplitude**, and may have little power even if the biological behavior is strongly tied to individual **low-water/high-water events roughly every 6 h**. This new v33-D question tests **subdaily** association explicitly.

Use only the original v32 source `O_SCHIERMONNIKOOG` seven GPS-year archives (source MD5/SHA pinned by v31, unchanged visible/manual outlier, original UTC parser, all duplicated exact bird×timestamp fixes dropped), and independently verified RWS 10-minute **astronomical tide** (`ProcesType=astronomisch`, station `schiermonnikoog.waddenzee`, NAP, cm → meters), 2008–2014. No actual future measured tide enters this analysis. Station center is the official original catalog **53.468937N, 6.202908E**, and only GPS steps with both endpoints within a **25 km** great-circle buffer of this site are used; no post-outcome radius tuning or migration site choice.

## Independent response, high-vs-low water

- For each original bird, sort valid fixes by UTC date-time, with no track interpolation and source outlier flags. Retain **consecutive** observed GPS pairs whose elapsed UTC time lies between **5 and 180 minutes**; exclude any pair where either endpoint lies beyond the fixed 25km local tide site radius. This is a conditional, retrospective analysis of actually observed movement (NOT day-ahead movement destination forecasting).
- Haversine displacement `D` (km) across two GPS fixes, `v=D/Δt_hours`, response `log(1+v)`. Report original observations, pairs rejected by time, geography and tide matching, and extreme raw speed diagnostic (>100 km/h; do not tune exclusion to outcome).
- Attach **astronomical** RWS tide height at the UTC midpoint using nearest original 10-minute time (≤5min; deterministic rounding, tie to earlier measurement). Missing observation / unsupported source year => pair unadmitted, no imputation.
- Determine **source-only** RWS tidal level quartiles Q25 and Q75 from all valid original 2008–2014 10-minute astronomical tide heights, before looking at any GPS-conditioned response. Assign low tide quartile `h ≤ Q25` and high tide quartile `h ≥ Q75`. Middle 50% excluded from high-vs-low contrast by design. This is a *relative tide water-level category*, not measured mudflat availability or true peak-water turn time.
- To control 24h diurnal schedule and coarse season, create strata by **original bird × calendar year-month × UTC clock-hour**. A stratum is paired only if it has **≥2 original steps in EACH high and low category**. Take within-stratum mean `log(1+v)` high minus low, then equal-weight these paired strata within each bird, then equal bird weight across accepted birds.
- **Single fixed primary association:** signed high-water minus low-water difference in `log(1+km/h)`; **report both signs, do not pick high/low after results**. 10,000 paired whole-bird bootstrap (RNG seed 20261031), exact one-sided sign p for a positive difference plus two-sided bootstrap CI. Report cross-bird heterogeneity and sample effort.
- Pre-result support gate **≥20 birds each with ≥8 matching paired strata**, and ≥200 total paired strata. If not met, **NOT_ADMITTED** and no behavior/tide association or p-value exported. No fallback to a clock-unmatched pooled analysis.
- This is an *observational association*: local water level at one station is only a tidal-accessibility proxy; GPS displacement speed does not distinguish feeding vs roost flight or local prey. Same bird×UTC-hour×month matching controls only simple clock/season strata, not wind, storms, predator disturbance, tidal basin geometry, or GPS duty schedule. Results do NOT identify Boids social forces, cognitive memory, or causal habitat selection.

## Reproducibility

Publish frozen code and known-truth unit tests for original GPS source checksums, pair time and distance, UTC tide matching, clock×month strata, equal bird weights, and source-only Q25/Q75 before opening joined movement-by-tide results. Source tide and animal GPS downloaded ephemeral; no original positions or bird IDs redistributed. Keep v33-C daily forecast and v32/v31/v30 independent results unchanged.
