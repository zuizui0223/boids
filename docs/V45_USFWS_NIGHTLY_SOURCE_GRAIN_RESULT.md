# v45 USFWS original Nightly Pass Counts source grain — 33,168 unique site-nights, no effort column

**Executed:** 2026-11-19 JST. [Source-only Actions run 44525738294](https://github.com/zuizui0223/boids/actions/runs/44525738294), five known-truth site/date/CRC/zero-detection tests PASS. Original USFWS full-archive v42 cap, v43 precise second-range transport STOP and v43a/v44 original source successes retained without revision.

## Authentic source verification

ZIP final 65KB fixed SHA256 \`69f4410f8b868849e6e17160b377e6f34fc65068e62f2590e31b598bc5f0fa59\`. Original Nightly Pass Counts XLSX reconstructed from compressed range and CRC32 \`3666e794\`; original Metadata XLSX CRC32 \`19f9b7c8\`. No full 495MB original ZIP checksum or animal/source site names reported.

Nightly source first worksheet: **33,168 original data rows**, exactly **33,168 distinct \`AcousticSite×NightOf\` values**, no duplicates. Precisely 17 original columns:
\`AcousticSite, NightOf, ALL, EPTFUS, LASBOR, LASCIN, LASNOC, MYOLUC, MYOSEP, PERSUB, MYOLEI, MYOSOD, NYCHUM, CORRAF, ANTPAL, LASINT, TADBRA\`.

Fourteen original species classifier labels plus total \`ALL\` are acoustic-derived **recorded response variables**, not independent bat animal counts. This v45 audit **did not open any of their numeric values**.

A second Nightly workbook worksheet contains documentation about WAC and recorder operation. Metadata XLSX contains a source table with **277 rows**, but that is **NOT** proof of 277 independent biological sites; original agency catalog describes 276 sites across the area.

## Exact effort conclusion

- There is **NO per-night WAC-file-count or detector-recorded-hours field** in the 17-column nightly table. The original author description says nights with >=8 WAC files (>=2 nominal recording hours) are eligible; it does not provide exact per-night recording exposure.
- v45 source verdict \`SOURCE_NIGHT_OR_EFFORT_GRAIN_UNRESOLVED_STOP\`: original observation *site/night grain* PASSED, explicit per-night source effort information **FAILED structural verification**. Do not interpret this as an observed bat behavior null.
- Thus the number of passes per night cannot be converted into comparable calls/recording-hour, and missing site-night dates cannot be imputed as true biological zeros. A recorded zero in an included row may be a classifier zero under author qualification, not an unsurveyed night's verified absence.

## Separately predeclared new v46 endpoint (NOT a v45 rescue)

The independently frozen [v46 contract](V46_USFWS_BAT_SEASONAL_COMPOSITION_TRANSFER_FREEZE.md) only permits **relative composition among automatically labeled 14 bat species, on originally included site-nights where at least one named label is positive**, without using absolute nightly recording intensity. It tests whether a seasonal time-of-year predictor transfers to entire unseen recording sites/years. It never uses unobserved recording effort, cannot infer true zeros, and is not a universal causal flight law. Source numerical count opening is permitted **only** after the v46 contract was committed; prior v45 source stops are immutable.

No other published \`batter\` or prior \`boids\` result was changed.
