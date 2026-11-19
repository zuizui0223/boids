# v38b — Finland original Excel bat night × activity-phase feasibility (before outcomes)

**Freeze 2026-11-19 JST; no \`prop_activity\`, \`n\`, \`total_nightly_activity\` or physical weather values opened.** Original downloaded version: Lilley et al. 2026 Zenodo 18298435, \`Data.xlsx\` published MD5 444c510bcb154bf9272d620f1ce0ec5a, v38 7/7 MD5 source check PASS.

First worksheet original headings: species, region, period, location, lat, lon, device, year, startdate, quartiles, night_length, mean_temp, sum_rain, mean_wind, total_nightly_activity, n, prop_activity. Second worksheet includes hours_after_sunset_group instead of quartiles. The rows are **aggregated night × time-bin observations**, not independent bats and not GPS flight events.

Before numeric outcome, inspect only:
- original record number, years, regions, species labels, devices, dates, season/period and per-night time-bin support, with no original coordinates exported;
- unique night key \`(region,location,device,year,startdate)\` and distinct quartile membership;
- completeness of \`prop_activity\`, \`total_nightly_activity\`, \`mean_temp\`, \`night_length\` **only as nonempty/missing**, no values opened;
- exact 4-unique-quartile nights, duplicate bin keys, corresponding hour-group structure in sheet 2.

**Source gate frozen**: >=3 years, >=2 regions, >=1,000 unique nights, >=1,000 nights with exactly 4 distinct quartile bins, no duplicate \`night×quartile\` key and >=1,000 four-bin nights with all four nonempty \`prop_activity\` fields. Without these do not open the next model.

Potential v39 prediction, if admitted:
- test whether nocturnal activity **redistribution among quartiles** (conditional on the nightly total) is predictable from mean temperature, night length and their interaction, beyond the training-region/year average quartile profile;
- whole-year out-of-year and whole-region-out-of-region scoring must preserve nights as units, with training-only imputation/standardization, no target-time leakage; hold out rare years/regions rather than dropping them;
- use a separate frozen outcome/model contract after the source preflight, **before** decoding weather or \`prop_activity\` numeric values. Retain complete negative cases; no tuning.
- This measures passive acoustics in one species across Finland, **not** universal cross-species behavior or independent global replication. Published within-data thermal/night-phase result is prior art; transferable prediction is the new target.

Italy 64,275 detection records and Belgium 2,834 bat activity rows remain **independent source-screen successes**, not automatically compatible nightly outcomes: original effort and true zero-activity windows must be audited separately, with sound-treatment / repeated acoustic sampling controlled before cross-country transfer.
