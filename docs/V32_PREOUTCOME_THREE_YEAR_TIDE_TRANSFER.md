# v32 — Pre-outcome independent-year original GPS × RWS measured tide transfer

**2026-11-02 JST. Evidence is not yet evaluated at creation of this protocol.** v29 toy simulation, v30 seven-year original source inventory, and v31 2009 exploratory heldout are not retroactively changed.

## Scientific question
Does measured flood/ebb phase improve prediction of shorebird horizontal speed beyond water height, location, solar clock and season **in an independent calendar year at the same Wadden Sea site**? Can the same-height ebb/flood contrast recur in 2010/2011?

## Original 3-year data
- Original [Zenodo GPS annual gzip provider MD5](https://zenodo.org/records/22296922): 2009, 2010, 2011, all previously independently byte pinned in v30 (46,826; 282,920; 200,348 real source GPS rows, respectively). Original observed source timestamp explicitly says UTC **or GPS time**; it is *not* independently verified by this script. Use a clock interpretation 0 sec as UTC versus minus 15 sec as GPS time (valid 2009–2011 GPS−UTC leap-second differential), keeping the result labeled exploratory.
- Original historical instrument [RWS WATHTE](https://github.com/Rijkswaterstaat/wm-ws-dl) station `schiermonnikoog.waddenzee`, `meting`, cm/NAP, fixed UTC+01. Never apply Dutch DST; fetch all 12 months for each original calendar year and require >12k valid measurements. Verify provider MD5 GPS every execution, and never commit raw animal fixes/IDs.
- Reuse already defined frozen v31 processing: one first local GPS fix per UTC hour per individual, 0.5–2h displacement, 120kmph speed cap and source region, log1p(km/h), gauge WATHTE NAP with trailing 20-min flood/ebb and rate. Backwards tide rate at position start avoids using future tide phase, though RWS interpolation and station-level tide are retrospective observations.
- **M0** = water height + quadratic + position + 24-hour and seasonal terms. **M1** = M0 + ebb/flood phase, ebb/flood × water height and trailing rate. Train-weight each individual equally with fixed ridge and train-only normalization; compare identical withheld observations. There is NO per-individual fixed identity covariate in this annual-transfer model.

## Frozen tests (before any v32 outcome)
1. Main **train 2010, test 2011**. Independent heldout calendar year, not necessarily individually new birds. Primary signed gain (\Delta=\mathrm{MSE}(M0)-\mathrm{MSE}(M1)\), equally averaging heldout bird MSE; positive means phase improves independent-year speed prediction.
2. Replication **train 2009, test 2010** and **train 2009+2010, test 2011**, with exact same features and no outcome-based model selection.
3. Primary 2011 result is shown for source clock at 0 and -15s. The sign should agree across these two nearby clock choices; these are **sensitivity analyses** not independent replication.
4. Whole-individual and whole-week resampling (4,000 replicates each). Positive effect should have both the equal-individual and equal-week confidence intervals above zero to support temporal and individual reliability; a paired bird bootstrap alone is not sufficient.
5. Descriptive same bird/month/0.15m height/6h clock-bin ebb minus flood in each year; required >=3 records per phase/stratum. Replication across years is stronger than a post-hoc 2009-only pattern but still not evidence of tidal front, prey or physical forcing.
6. Report test sample count, heldout independent bird count, week count, birds and weeks with positive increments, month/source counts, original MD5/SHA256 and gauge source checks; no individual identifiers or raw animal geolocations in report.

## Interpretation thresholds
- If 2011 external year transfer gain >0 and both bird and week CIs exclude 0 under 0s and -15s, declare **predictive association transferred across the same site**, *not* a causal tidal rule or species-general Boids principle.
- If improvement is directional but either uncertainty interval spans 0: **suggestive only, transfer not robustly established**.
- If an original source, measurement datum, unit, or clock gate fails: **SOURCE_STOP**, not ecological zero.
- M2 resource-front needs real local DEM + sea-water propagation/exposure; M3 social response needs independently group-heldout synchronous pair vs ghost controls and clock-error audit. Both remain not admitted here.

## Reproduce
```bash
python -m pip install 'numpy>=1.24,<3'
PYTHONPATH=validation_v32:validation_v31:validation_v30:validation_v29 python -m unittest discover -s validation_v32 -p 'test_*.py' -v
PYTHONPATH=validation_v32:validation_v31:validation_v30:validation_v29 python validation_v32/cross_year_tidal_transfer.py --output /tmp/boids_v32_transfer.json
```
