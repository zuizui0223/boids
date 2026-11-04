# v40 source admission and fixed field holdout implementation (2026-11-03)

Source-only ORIGINAL GPS [run 41564939899](https://github.com/zuizui0223/boids/actions/runs/41564939899) passed provider MD5 on both 2012 files before opening any 2012 GPS × measured tide outcome.

- Schiermonnikoog: 27,873 original 2012 fixes, 5 source birds, 9,165 original hourly 0.5–2h displacement candidate steps, 36 ISO weeks.
- Ameland: 12,080 original 2012 fixes, 3 source birds, 10,646 eligible original source steps, 50 weeks.
- Both exceed the frozen admission gate (≥3 birds, ≥4 weeks, ≥1,000 steps); actual tide joining may reduce these sample counts.

The previous v40 frozen [protocol](V40_FROZEN_2012_TIDE_SOURCE_GATE.md) had already fixed the only primary test: train original 2010+2011 and hold out all 2012, compare Mphase0 with pre-selected Mphase−120min using identical original GPS and original 10-minute RWS NAP water heights and complete common lag-source rows. Same v33 standardized ridge penalty10, equal bird scoring, separate bird/week bootstrap point estimands. This is a temporal validation of a lag selected after 2011 results, not clean discovery or a measured physical delay.

2012 year RWS original source uses fixed quarterly original meting WATHTE cm/NAP +01:00, as in v39 source transport. 2012 GPS native UTC or GPS-time clock unresolved; a fixed -15s sensitivity is approximate during the leap-second change of 2012-07-01 (15→16s). Never claim exact corrected 2012 GPS clock. No DEM, prey or social Boids coefficients inferred.
