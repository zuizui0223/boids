## v183｜2018・2019年の独立した二つのRWS実測潮位比較（SOURCE ONLY）

This physical pilot is **frozen before opening the 2018/2019 two-gauge comparisons**, stacked after v182. No bird outcome, raw GPS or environmental exposure estimates are allowed.

### Fixed source, pair, years

- Authoritative RWS DDAPI2 metadata and observations; station A exact code `vlieland.haven`, station B unique officially named West Terschelling (normalized name WestTerschelling or TerschellingWest). Ambiguous station → STOP; never select by outcomes or correlations.
- Same fixed 48-hour windows June 1–3, **2018 and 2019**; only genuine WATHTE, cm, NAP original Aqua metadata, original constant +01 timestamps, >=200 original observations at each station and >=190 exact UTC timestamp pairs.
- Report West Terschelling minus Vlieland Haven observed height median and p05/p95, absolute difference median/p95, same-time correlation and descriptive peak ±120 minute (10-min-step) cross-correlation. The best correlation shift is descriptive and must never be treated as an independently validated local tide-transfer model.
- Preserve provider response SHA256; publish no raw tide series, bird GPS, ACC outcomes, DEM pixels or individual locations.

### Interpretation gates

Different water levels at two stations would show the harbor observation does not equal a second station at the same instant. It would **not** prove or identify bird-cell-specific tidal propagation, net water depth, usable mudflat area, feeding, a social Boids force, or tide-by-sun causality. Even equal heights at two gauges would not establish uniformity. 48 hours cannot validate an entire season, let alone 2018→2019 model transfer.

If the exact primary station pair is absent, the original RWS source is down or the records do not match the frozen quality rules, source STOP rather than silently switching dates or stations. v182 physical-source STOP remains binding even after a positive two-station comparison.

Reproduce synthetic exclusion tests: `python -m unittest discover -s validation_v183 -p 'test_*.py' -v` with `PYTHONPATH=validation_v110`. Real-source run: `python -u validation_v183/original_RWS_two_gauge_comparison.py` with the same path.
