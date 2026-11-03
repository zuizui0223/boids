# v32 FROZEN INDEPENDENT-YEAR TEMPORAL VALIDATION: 2010 and 2011
2026-11-02 JST. Freeze before seeing 2010/2011 movement-model outcomes.

Motivation: v31 real original 2009 had M0−M1 equal-bird test MSE gain +0.001047997 (+0.6804%) on 3 held-out birds and 8 weeks, but the held-out-week bootstrap 95% interval included zero. Thus an independent annual check in the **same Schiermonnikoog study** is needed.

No tuning or endpoint switching. All inclusion thresholds, retrospective gauge assumptions, original position-to-displacement calculation, within-year 70% chronological training / one-week embargo / last weeks holdout, M0/M1 feature design, phase threshold, equal-bird ridge, 4000× bird/week bootstrap, and four native-clock offset scenarios are imported directly from frozen `validation_v31/tidal_observed_2009.py`. This extends data years without refitting v31 or changing its outcomes.

Two new original annual GPS objects:
- 2010 original Zenodo v5 GPS (provider MD5 pinned in v30); 2010-01-01..2010-12-31
- 2011 original Zenodo v5 GPS (provider MD5 pinned in v30); 2011-01-01..2011-12-31
RWS same observed `schiermonnikoog.waddenzee`, WATHTE, NAP, cm, fixed UTC+01:00. For each year request from Dec 30 of previous year to Jan 2 of following year in 14-day windows, verifying units and no gap for each joined step. No DEM/habitat elevation, so M2 remains NOT_ADMITTED; no social Boids force fitted, M3 remains NOT_ADMITTED.

Each year is analyzed **separately** using its own chronological holdout and equal bird weighting. Do not pool raw records, fish for seasonal windows, or select time offsets based on scores. Report direction, magnitude, held-out birds, held-out weeks and whole-week uncertainty for **both years even when negative**. A cross-year same-sign result is temporal replication **within one species/site**, not evidence of multiple independent populations or a causal tide-front mechanism.

All original-animal GPS fixes/IDs and raw gauge data exist only on ephemeral Actions runners. Only aggregate manifests and model scores are saved. Position clocks remain UNCERTAIN: original timestamp documentation says GPS or UTC, which is not fully resolved by ±15s/±1h sensitivity.
