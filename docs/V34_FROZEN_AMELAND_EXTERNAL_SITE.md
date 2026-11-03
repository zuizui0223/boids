# v34 — PRE-OUTCOME INDEPENDENT ISLAND REPLICATION: Ameland, 2010 → 2011

**Frozen 2026-11-02 JST BEFORE examining Ameland GPS/tide movement outcomes.** Schiermonnikoog v29–v33 results already known and must not be presented as independent Ameland validation.

## Scientific target
Does the discrete ebb/flood phase improve out-of-calendar-year GPS-derived horizontal displacement prediction in a **different oystercatcher population/island** beyond contemporaneous measured height, geography, diel and seasonal clocks? This is a transfer of the *hypothesis/model specification* to a new island, NOT transporting the Schier fitted coefficients. Still one taxon, not multi-species generality.

## Original external data and unmoved clock
- [Zenodo O_AMELAND v6, fixed record 10053853](https://zenodo.org/records/10053853), UvA-BiTS original GPS annual gzip 2010 and 2011. Source MD5 hard-pinned **2010 `71e0b66230b508873897c99464146167`; 2011 `ab74f7443bb09bd5be90bde69fc612eb`**. No hourly GBIF/OBIS occurrences substituted.
- RWS official [water data instructions](https://rijkswaterstaatdata.nl/waterdata/) explicitly give original measured WATHTE station code `ameland.nes`. Request **meting** WATHTE, centimeters relative to **NAP**, source timestamps fixed UTC+01:00, each calendar month 2010 and 2011. Reject wrong unit, datum, timestamp or failure to obtain >=12,000 source gauge observations per year. Do NOT choose a different gauge based on prediction outcome.
- Ameland within-site original GPS positions admitted only for latitude 53.2–53.6 and longitude 5.3–6.1 (fixed geographical envelope before opening GPS fixes). Original GPS metadata say timestamp **UTC or GPS time**; primary assumes naive clock in UTC, sensitivity -15 sec for the historical GPS−UTC offset. Other clock explanations are not resolved.

## Unchanged v33 model and primary transfer
- One first visible original GPS fix **per native UTC hour** per bird; successive chosen fixes **0.5–2h apart**, source log1p(km/h) great-circle displacement, >120km/h rejected. No synthetic interpolation, classification as foraging, or patch DEM.
- Reuse `validation_v31/observed_phase.py` original feature specification: M0 = intercept, height, height², latitude, longitude, 24h sine/cosine and 365.25-day sine/cosine; Mphase = M0 + phase (-1/+1) and phase×height **without rate**. Slack phases dropped. Same 20-minute trailing phase threshold ±0.012m/h; same standardized ridge penalty **λ=10** and training bird weighting. **No site-derived tuning or new features.**
- **Primary** fit M0 and Mphase on 2010 Ameland and score all eligible 2011 Ameland animals with original steps. Test unit: equal bird MSE, and 4000 whole-bird and 4000 whole-ISO-week bootstrap replicates fixed seed 20261102. Positive gain = MSE(M0)−MSE(Mphase). Keep 2011 completely untouched during fitting, no per-ID test predictors. If test <3 birds, test <4 ISO weeks, test <1000 steps, or train <1000: NOT_ADMITTED.
- **Secondary fixed sensitivity** same data with source clock -15 seconds and unmodified v33 Mboth/Mrate comparisons (no reweighting). Secondary descriptive same-height ebb-flood difference matched within bird, month, 0.15m NAP height and six-hour local-independent UTC clock bin, >=3 each phase. Do not turn this into a causal label.
- All outcomes — positive, negative, inaccessible, underpowered — must be reported. If technical source cannot be opened, SOURCE_STOP, not biological absence of effect.

## Mandatory evidence limits
Ameland is a different **site/population** from Schiermonnikoog, but a repeated species and same Dutch Wadden Sea region; complete macroecological universality remains untested. We have no calibrated local mudflat DEM/elevation and true exposure front and do not estimate prey-access mechanism or actual social Boids forces. Bird GPS clock remains UTC/GPS ambiguous; two timestamps less than 20s apart are sensitivity, not identifying the correct clock. Local station-to-bird hydrodynamic lag remains uncalibrated; positive phase prediction is a conditional **association**.

No original bird IDs or raw coordinates are printed, uploaded or committed. Only aggregate original-source receipts and scores.

## Execution
```bash
PYTHONPATH=validation_v29:validation_v30:validation_v31:validation_v32:validation_v33:validation_v34 python -m unittest discover -s validation_v34 -p 'test_*.py' -v
PYTHONPATH=validation_v29:validation_v30:validation_v31:validation_v32:validation_v33:validation_v34 python validation_v34/ameland_external_site.py --output /tmp/boids_v34_ameland_results.json
```
