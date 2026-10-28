# v17-A3 — MATLAB-serial weather clock identification and cross-source UTC coverage (source-only)

**Registered 2026-10-28 JST after completing v17-A/A2 type and filename checks, before opening any v17 GPS turning/route response.** This is a provenance/timing check, not a new model or outcome selection.

The originally verified Taylor et al. 2019 `Experiment 1 - Weather Data.csv` contains **152,227 headerless rows of three numeric columns**. The first column has six digits before the decimal and many fractional digits, **consistent with but not proof of** MATLAB serial-day numbers. The other two columns are finite numeric with the third candidate range 0–360 degrees, consistent with the published description of wind speed and wind bearing. No weather-GPS join or animal movement outcome has been computed.

## Predeclared source-only validation

1. Interpret weather column 1 *only as a candidate* MATLAB `datenum`: day ordinal convention (d_mathrm{python}=d_mathrm{MATLAB}-366), and fractional day into seconds. Check fraction mapping to calendar year **2015** (the publication reports experiments June–September 2015). If not, report invalid and stop; do not infer a better conversion by motion-model performance.
2. Count weather rows, dates covered, duplicate candidate second/minute timestamps, positive intervals and physical row format. Do not report wind magnitudes or observed model outcomes.
3. Sample first three and last three *recorded original* UTC timestamps from each of 458 GPS files (date/time/MS columns only, no position/course) to characterize flight recording windows. Count unique days and total flights covered by recorded weather at offsets **-1h, 0h, +1h relative to GPS UTC**. These are **only structural overlap diagnostics**, not time offset estimates from animal turns, not proof of source time-zone. The UK used British Summer Time (UTC+1) during June–September 2015. Any final convention requires corroboration from original weather-station software or release documentation.
4. Do not choose an offset by maximizing held-out GPS turning prediction. Where offsets cannot be independently disambiguated, report *timezone UNKNOWN* and stop v17 wind-gated causal forecast.
5. Reuse exact pinned GPS and weather source SHA256 from v17-A. No raw animal coordinates, weather values or event-level predictions may be exported. A3 success is only source alignment plausibility.

## Post-A3 decision

A paired social-forecast validation remains conditioned on an **external source pairing ledger** (PLOS Biology S3 Table / original release metadata), actual synchronized GPS co-fixes and enough independent bird-connected partner components. A candidate date overlap is not a joint behavioral dataset until these requirements pass.
