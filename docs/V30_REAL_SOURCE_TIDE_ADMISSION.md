# v30 — original high-frequency oystercatcher GPS and RWS 2008 historical tide: SOURCE GATES ONLY

**2026-11-02 JST. This is a source audit, NOT an observed tide-movement result.** v29 synthetic results and previously frozen evidence remain unchanged.

## Hypothesis
Can a moving tidal-accessibility boundary explain within-individual ebb/flood movement hysteresis, collective heading patterns and spatiotemporal niche allocation **without assuming bird–bird steering**? First identify original GPS sampling and independent historical measured water levels. Biological tide, front or social effects are not estimated in this stage.

## Original animal GPS
- Hourly public occurrence archive: [INBO v1.3](https://ipt.inbo.be/resource?r=o_schiermonnikoog&v=1.3), 171,132 rows, 43 individuals, first location hourly; NOT the native high-cadence input for social inference.
- Original source: [Zenodo O_SCHIERMONNIKOOG v5, 22296922](https://zenodo.org/records/22296922), 2008–2014 year-separated GPS gz, source `datapackage.json` with `event-id, timestamp, location-lat, location-long, individual-local-identifier, visible` field dictionary.
- Source original timestamp unit is documented as **UTC or GPS time**, not guaranteed independently verified UTC. Preserve native clock and STOP before a source-verified exact historical phase join.
- `validation_v30/source_preflight.py` opens ONLY original GPS 2008 and 2009 first; checks provider MD5 on original gzip bytes, calculates SHA256, parses source schema, and reports eligible original GPS fixes, individual sampling intervals, near-neighbor candidates within 5 seconds and 100m, and source dropped counts. No raw animal coordinates or animal IDs are committed or printed.
- Near-neighbor candidates are an observation-feasibility bound, not proof of social steering, data accuracy or independent group replication. Source data cannot establish Boids motor forces from their spatial coincidence alone.

## Historical instrument source
- [RWS Waterinfo DDAPI2](https://github.com/Rijkswaterstaat/wm-ws-dl) provides a historical measured water level API at `https://ddapi20-waterwebservices.rijkswaterstaat.nl`.
- [DDAPI 2.0 implementation and pitfalls](https://www.opendataindex.nl/en/bron/rws-waterinfo): query a uniquely identified station, WATHTE surface water, **meting** only, 2008-08-14..16. Dutch gauge timestamps are **fixed +01:00**, including in the summer; do not apply Europe/Amsterdam DST shifts. No cm→m conversion before unit verification; do not confuse **LAT and NAP**.
- Independent source documentation: [Dryad 2024](https://doi.org/10.5061/dryad.wm37pvmth) contains 1982–2022 10-minute `water_schiermonnikoog.txt` originally measured relative to NAP and 2014 AHN LiDAR maps in RD/New NAP elevation, but its ~1.43GB archive is not yet extracted or verified.
- `validation_v30/rws_source_probe.py` probes exactly 2008-08-14..16 and reports source metadata, measured value count, time offsets, units and datum. Any unavailable source produces an explicit STOP not a negative biological effect.

## Frozen next observational comparison, only after source passage
1. Confirm GPS original clock, tide instrument identity, NAP datum, gauge phase lag and baseline geographic transforms EPSG:4326→28992; join measured DEM NAP without inventing elevation or local shore slope.
2. At equal water height **within the same bird**, compare ebb vs flood displacement and cross-shore direction using tidal-cycle blocked uncertainty and day/night, season, position covariates.
3. M0 = tide height + spatial/clock; M1 = M0 + ebb/flood × height; M2 = M1 + real dynamic front, local inundation/exposure history. Freeze equal-bird, temporal-block and no-future-leakage scoring. A positive M1/M2 effect is predictive association, not uniquely causal front tracking.
4. M3 = M2 + real synchronous neighbors vs ghost negatives, only after source identifies enough true simultaneous spatial pair replicates, and independently held-out connected groups. Otherwise NOT_ADMITTED.
5. Ultimately transfer from one species to multiple independently sampled shoreline bird species and compare temporal vs spatial information, not instantaneous force coefficients alone.

## Reproduce
```bash
PYTHONPATH=validation_v30 python -m unittest discover -s validation_v30 -p 'test_*.py' -v
python validation_v30/source_preflight.py --years 2008 2009 --output /tmp/boids_v30_gps.json
python validation_v30/rws_source_probe.py --output /tmp/boids_v30_rws.json
```
Remote source downloading is NOT triggered by unit tests. Workflow runs on an ephemeral runner and emits only metadata summaries. Actual original source run receipts must be checked before ecological interpretations are accepted.
