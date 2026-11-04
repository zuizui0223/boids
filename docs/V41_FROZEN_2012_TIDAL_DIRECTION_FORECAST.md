# v41 FROZEN BEFORE NEW DIRECTIONAL OUTCOME — does tide phase predict wild birds' steering beyond inertia?

**2026-11-05 JST, outcome-blind for v41.** Prior v29–v40 GPS displacement-speed, tide phase and lag results are known; source 2012 was already used for a SPEED endpoint. This is a NEW, previously unscored **horizontal turning / displacement-heading** endpoint in the SAME original 2010–2012 birds. Not a second independent population study, not novel raw source.

## Ecological question

Do birds change **where they head** with the rising/falling tide, beyond where they already are, the tide's absolute height, the time of day/year and their **own immediately preceding heading and speed**? This moves from speed-only associations toward *dynamic directional spatial-niche organization*. No social Boids force is inferred.

## Unchanged source and truly withheld directional endpoint

Two original source-confirmed Eurasian oystercatcher cohorts:
- `O_SCHIERMONNIKOOG`, Zenodo original GPS 2010–2012, original provider MD5 pinned by v30/v40;
- `O_AMELAND`, Zenodo original GPS 2010–2012, provider MD5 pinned by v34/v40.
Same original RWS local `schiermonnikoog.waddenzee` and `ameland.nes` measured `WATHTE meting` water levels (cm relative NAP), fixed UTC+01 year-round, conversion to NAP metres. All source bytes retrieved anew with checksums and no raw GPS written to repository; measured gauge timestamps interpolated for *retrospective* association only.

The primary original source clock interpretation is native naive timestamp treated as UTC, secondary source clock shifted -15 seconds (still an approximation for GPS−UTC in 2012 after 2012-07-01 leap-second change to 16s). Do not choose a clock offset by observed score.

## Fixes, movement and target geometry (all fixed before v41 outcomes)

1. Source GPS: `event-id` uniqueness, visible original records, finite WGS84 latitude/longitude and original bird token, frozen site regional bbox from v34/v40. Within bird and calendar year, choose **the earliest available original fix in each UTC hour** (no interpolation).
2. Each candidate episode is **three successive selected fixes** `A→B→C` of the same bird. Both A→B and B→C gaps must be in **[30min, 2h]** and geodesic horizontal speed in **[0.4km/h, 120km/h]**, excluding near-stationary noisy headings. No synthetic heading or next-position feature is allowed.
3. At focal time B, the bird's previous **unit displacement heading** in an ENU local tangent frame is an available predictor; its own previous speed is a predictor. Bird's actual **next unit displacement heading B→C** is held-out evaluation outcome only. Use WGS84 longitude scaled by `cos(mean latitude)` and latitude for direction. The physical position B, source clock cyclic terms, and source gauge water level at B are available before future C. Drop tide gauge gaps >30 minutes and source slack phase to replicate prior sign-defined ebb/flood sampling.
4. The response is the unit heading vector (east, north); scalar loss `0.5*((east−predEast)^2 +(north−predNorth)^2)`. Fitting a 2D vector via weighted ridge *without normalizing predictions* yields a conditional expected direction vector. Do not claim this is a calibrated turning acceleration or animal's heading in flight.

## Frozen models and year-external validation

Training: all admitted original 2010 and 2011 episodes, pooled **within each island only**. Test: 2012 episodes only, no test outcome in train fitting or feature selection. Two models on *identical* source rows:

- **M0:** intercept, h(t), h²(t), lat/lon(B), 24-hour sine/cosine, 365.25-day sine/cosine, previous heading east/north, `log1p(previous horizontal speed km/h)`.
- **M1:** M0 plus actual gauge ebb/flood phase(t) coded -1/+1 and phase(t)×h(t). Tidal phase from trailing 20-min gradient threshold ±0.012 metres/hour, unchanged from v31–v40.

Train-only standardized features; training bird-equal total weights; ridge L2 **10.0**, intercept unpenalized. Report both 2D directional half-MSEs and primary pooled equal-bird gain **Δ=M0 loss−M1 loss** (positive phase helps), corresponding **10,000 whole-bird paired bootstrap** 95% interval and positive bird count. Independently, report equal-week-then-bird Δ, corresponding **4,000 whole-week bootstrap** interval and positive weeks; these are distinct point estimands and cannot be interchanged.

**Minimum source gate per island:** at least 3 qualifying source birds, 4 distinct 2012 test weeks, at least 1,000 original three-fix direction episodes, and 1,000 original 2010+2011 training episodes. If any fail: `NOT_ADMITTED` and no biological effect claim. Must report both islands, including negative or null results and source failure.

## Interpretation and controls

A positive directional increment on original 2012 data supports **transferable tide phase information about *turning / heading choice*, conditional on prior heading and observed position**. A null says phase addition lacks transferable directional value under this instrument/grain; neither null nor positive identifies *where exposed food is*, tidal-front pursuit or a Reynolds social alignment term. Both sites share one species and Wadden Sea region and may contain repeated birds; no global universality. Original gauge may not represent local time-varying mudflat hydrograph. 2014 LiDAR/shoreline source not yet joined, and 2009–2012 GPS does not establish 2014 patch height was constant during animal tracking.

No moving habitat boundary, prey capture, true social neighbor force, or species-niche divergence is directly measured in v41. Treat this as **a new endpoint on an already inspected cohort**, not an untouched population-level confirmation.
