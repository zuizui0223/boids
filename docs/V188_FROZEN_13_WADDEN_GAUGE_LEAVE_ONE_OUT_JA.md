# v188｜実測13観測所のLeave-One-Station-Out：潮位空間補間の独立予測検証

**FROZEN before opening any new v188 multi-site original RWS water-level comparisons.** After v185 5/15 SOURCE FAIL, v186 name-only audit, v187 **exploratory source repair 13/15** (Den Oever & Nieuwstatenzijl remain unavailable).

## Exact station cohort
The 13 native codes with genuine 2018 and 2019 WATHTE cm NAP Jun 1–3 in v187, unchanged:
DenHelder=`denhelder.marsdiep`, Kornwerderzand=`kornwerderzand.waddenzee.buitenhaven`, Harlingen=`harlingen.waddenzee`, Lauwersoog=`lauwersoog.waddenzee`, Eemshaven=`eemshaven.waddenzee`, Delfzijl=`delfzijl`, Huibertgat=`huibertgat`, Schiermonnikoog=`schiermonnikoog.waddenzee`, Wierumergronden=`wierumergronden`, Nes=`ameland.nes`, WestTerschelling=`terschelling.west`, VlielandHaven=`vlieland.haven`, Oudeschild=`texel.oudeschild`. No replacing a station on the basis of prediction error or source quality.

**Coordinates**: independent 2011 WEBTICS Appendix A Table A.1 published RD (EPSG:28992) reference points, NOT verified to equal original 2018/19 RWS modern instrument coordinates. RWS catalogue has ETRS89 but X/Y blank. As such geographic interpolation here is **exploratory, reference-coordinate-based** and cannot be claimed as a verified local GPS water field.

## Fixed original-source design
- Real official RWS DDAPI2 `WATHTE cm NAP`, 10-minute station observation, original UTC+01 timestamps, only 48h June 1–3 and September 1–3 **2018 and 2019** (four year×month windows). September checks are new out-month spatial SOURCE tests; cannot adjust pair/win after seeing errors.
- ≥200 genuine observations per station per window and ≥190 exact same UTC timestamps present at ALL 13; if source incomplete, `SOURCE STOP` for that window and **no dropping stations/observations based on model prediction**.
- Strict **Leave-one-station-out**: for each hidden target gauge, use only original simultaneous water levels from other 12 stations. No target series for fitting weights, input, calibration, or model selection. Fixed physical interpolators:
  - Baseline nearest other station by 2011 RD Euclidean distance, water height at same instant.
  - Primary: **3 nearest other stations, inverse-square-distance normalized weights**, same instant. No fitted parameters.
  - Secondary: Delaunay **triangle barycentric interpolation** from remaining 12 stations, only if target lies inside their convex hull; no extrapolation or fallback masquerading as triangle. Replicates known WEBTICS concept rather than claiming its invention.
- Per-station MSE (m²) over common original times; station-equal aggregate in each window and across 4 windows. Primary `MSE(nearest)-MSE(IDW3)`; positive = physical source-only gain. Source-only descriptive criterion ≥3 of four windows positive and pooled station-equal gain positive; no independent p-value from autocorrelated 10min observations. Report all station-level negative and positive effects, not merely significant stations. Triangle only on common interior stations.
- Original RWS response SHA256, native accepted count, source-safe MSE, station names and reference positions published. Do not publish raw gauge timeseries, individual GPS, bird ACC, or raw DEM. v182 DATUM+survey-day+local GPS-site tide STOP is unchanged. No new biological result.

Previous result v184 +30min Vlieland→West Terschelling is NOT applied globally here, because other station-specific lags are not independently calibrated. Spatial method is deliberately held to contemporaneous gauge heights so that tide travel cannot be silently optimized.

**Reference:** Rappoldt & Ens (2011), EcoCurves report 12 / SOVON 2011/05, Appendix A Table A.1 and A.1 method, <https://nam-feitenencijfers.data-app.nl/download/rapport/d360edf8-1955-4ee4-b0e9-58826d7e0a53?open=true>. Their ecological gauge interpolation pre-exists Boids.
