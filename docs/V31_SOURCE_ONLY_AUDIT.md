# v31-A frozen source-only original-data admission

**Status: SOURCE_ONLY_TWO_ORIGINAL_ZENODO_RECORDS_VERIFIED.** The actual published source-only run was [GitHub Actions 41184502922](https://github.com/zuizui0223/boids/actions/runs/41184502922) on the initial pre-outcome code/protocol commit `3e9c2d994f0ad9f8f4a8a2a2dd82a50eeb854399`.

The exactly specified 2023 Zenodo record versions 10053970 and 10053702 gave **10 original GPS-year gzip files, 32,223,027 compressed bytes, 675,443 actual original GPS rows**, all provider MD5 and independent SHA256 successfully verified. Only CSV headers, original bird identifiers, UTC timestamps and repeated-date support were examined. The code **did not read latitude/longitude, altitudes, device speed or movement responses**. Complete file-by-file provider/derived hashes and source-only counts are saved in [the frozen machine-readable receipt](../validation_v31/results/oystercatcher_source_only_v31.json).

Original exposed headers include `individual-local-identifier`, `timestamp`, `location-lat`, `location-long`, `visible`, `gps:dop` (general dilution of precision, **not the same as v23's HDOP**), `location-error-numerical` and `manually-marked-outlier`. Header names alone were inspected; observed values have not been opened. Stage B must not silently interpret `gps:dop` as `gps:hdop`.

- **Schiermonnikoog:** GPS years 2008–2014, original source-only row total 602,396, yearwise identity support 2008:3, 2009:10, 2010:21, 2011:14, 2012:5, 2013:1, 2014:8. Species/source publication reports 43 tagged over the entire study, but **the count eligible for next-day forecasting remains unknown**.
- **Westerschelde:** GPS years 2018–2020, 73,047 rows. Year-by-year IDs 2018:6, 2019:2, 2020:1; those counts may overlap across years. It is entirely possible that this study does **not** meet v31's registered ≥8 *eligible* birds. If so, stop pooled effects, retain explicit source-availability result; do not relax to six, choose a year, or add a new study after reviewing outcomes.

The next stage is exactly the [previously registered source-independent forecast](V31_OYSTERCATCHER_CROSS_SOURCE_PROTOCOL.md): target next-day GPS spread using M0, MP, MI, MH; same eligible bird-days; primary `MSE(MP)-MSE(MH)`; ≥8 birds and ≥80 days per study, overall ≥20 birds and ≥300 days, no post-result parameter tuning. Compute no new ecological effects unless the full source and cohort gates pass.

Source licenses are CC0 as reported in the selected Zenodo records; raw GPS are not added to this repository.
