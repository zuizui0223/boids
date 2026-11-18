# v182 | 局所干潟アクセスの物理的出典ゲート（SOURCE ONLY）

Status: **STOP until independent original-source verification**. Stacked after v181 #198. Tracking issue #199.

## Observed original-data provenance (not a mechanism)
v181 original-source CI passed twice: 2018 149446/157863, 35 birds; 2019 119778/125241, 27 birds; all valid native isource filenames have labels before bird observation years. This is exploratory parser repair after v179 failed. Filename year does **not** verify actual field survey date, local elevation datum or tidal phase at bird location.

v169 2018-fit→2019 heldout original bird ACC: harbor HEIGHT incremental MSE gain +0.007430798 beyond observed prior behavior; shifted tide date advantage was not robust at week-block CI. No demonstrated endogenous tide clock or night×tide mechanism.

## Frozen source admission
- Native DEM `z` vertical datum must be independently documented with original URL/attribute. Horizontal EPSG:28992 is insufficient.
- RWS Vlieland Haven measured gauge water height must have independently verified vertical datum in same reference system. Unverified offset → STOP.
- Tide propagation between harbor and actual GPS cells requires an independent spatially/temporally calibrated source (or local gauges). Harbor height is **not** automatically local depth.
- Original `isource` filename-year ≠ field survey day. Independently establish survey day and historical terrain-change uncertainty; if absent, STOP.
- Do not subtract harbor tide from historical 20m DEM z, infer exposure, fit outcome, select older layers to rescue a gate, or publish new biological effect until all three gates PASS.
- Do not commit raw GPS/ACC, native raster, or gauge observations.

`python -m unittest discover -s validation_v182 -p 'test_*.py'` checks fail-closed behavior. `python -m validation_v182.physical_source_admission` reports present default status. These are **synthetic contract tests**, not original-source validation.

After original-source admission, separately pre-register 2018-fit→2019-test with fixed cohorts, bird/week uncertainty and negative-control tide shifts.
