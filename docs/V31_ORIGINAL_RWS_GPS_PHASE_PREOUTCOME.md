# v31 exploratory original-GPS × observed-RWS tidal phase association (pre-outcome contract)

**2026-11-02 JST.** v29 known-truth results and v30 original-GPS source gates remain frozen. This test does **not** yet estimate real moving habitat fronts, prey, DEM-inundation, behavior causation or Boids social forces. The comparison is explicitly **exploratory** because original Movebank source timestamps are described as UTC **or** GPS time; the present pilot provisionally treats them as UTC pending independent verification.

## Frozen before the new outcome
- Original source: [Zenodo O_SCHIERMONNIKOOG GPS v5](https://zenodo.org/records/22296922), one original 2009 gzip, provider-pinned MD5 `1967bdcd6a4720c63bb986abdaf48ab0`. Download/check bytes anew; no external raw GPS positions are committed or printed.
- Historical measured water level: [RWS DDAPI 2.0](https://www.opendataindex.nl/en/bron/rws-waterinfo), specific station code `schiermonnikoog.waddenzee` discovered empirically in v30, `WATHTE`, `ProcesType=meting`, `Eenheid=cm`, reference `NAP`, fixed `+01:00` timestamp offset even in summer. Query each month of 2009, reject unverified units/datum/offset, keep only physical levels <5 m in magnitude, and convert cm→m. This station is verified as a local RWS Wadden Sea instrument, **not** verified as the identical station used in Dryad 2024. A gauge is a proxy for water level at GPS fixes.
- GPS within the Schiermonnikoog region (lat 53.2–53.7; lon 5.7–6.6), original `visible` source flag. One **first native record per hourly UTC bin** per bird (no synthetic interpolation). Consecutive same-bird timestamps 0.5–2h apart, displacement using WGS84 great circle, cap 120 km/h. Output `log1p(km/h)`. First position timestamp receives the water-level feature.
- Tide feature: RWS 20-min backward difference. Ebb < -0.012 m/hour, flood > +0.012 m/hour; drop slack. Do not use future tide samples to calculate **phase**. Interpolation of contemporaneous measured water levels is **retrospective**, never claimed available in a live forecast.
- **M0** measured water level plus square, local latitude/longitude and diel/year cyclic controls. **M1** adds ebb/flood phase, phase×water-level and 20-min trailing water-level rate. Fixed ridge penalty 10 with training-only feature standardization, balanced training total weights by bird.
- **Independent evaluation in time only:** sort distinct UTC week blocks; train first 70%; exclude a full week as embargo; test later blocks. Primary: M0 minus M1 per-bird test squared error (positive = phase adds out-of-time forecast information). Equal bird weight; 5,000 whole-bird bootstrap resamples, keep CI but with only ~10 potentially eligible birds it is not an ecosystem-wide effect.
- Descriptive secondary: same individual, calendar month, 0.15m tide-height bin and fixed 6-hour clock bin; require ≥3 ebb and ≥3 flood records per stratum; weight capped at 10 per stratum, average birds equally. Positive ebb-flood difference does not prove exposed prey tracking.
- The native clock is provisionally read as UTC; ±18s and ±1h offsets are *planned sensitivity checks* after original UTC/GPS adjudication. Even robust phase prediction does not establish a direct physical tide effect without local DEM and true spatial front and local hydrodynamic lag.
- No social M3 and no interspecific niche metrics are admitted in this stage, although v30 confirms 22,071 5s/100m original GPS candidate near-pairs across 2008–14 (not independent force samples).

## Reproduce (requires internet)
```bash
python -m pip install 'numpy>=1.24,<3'
PYTHONPATH=validation_v31:validation_v30:validation_v29 python -m unittest discover -s validation_v31 -p 'test_*.py' -v
PYTHONPATH=validation_v31:validation_v30:validation_v29 python validation_v31/observed_phase.py --year 2009 --clock-shift-s 0 --output /tmp/boids_v31_phase_exploratory.json
```
The GitHub workflow runs the source-specific pilot in ephemeral runner space and prints only aggregated results with original SHA256 and RWS monthly counts. If source acquisition fails, **STOP/NOT_EVALUABLE** and preserve the v30 positive source-coverage results without inventing ecological effects.
