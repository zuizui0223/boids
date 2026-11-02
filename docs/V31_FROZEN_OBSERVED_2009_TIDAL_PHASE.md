# v31 PRE-OUTCOME: observed 2009 oystercatcher movement × measured RWS tide

**Frozen before field outcome is opened. Date: 2026-11-02 JST.**
New analysis of original GPS × independently measured water-level series; not part of v29 known-truth. Do not change the primary split/features after opening the observed score.

## Source and scope

- 2009 only, original `O_SCHIERMONNIKOOG-gps-2009.csv.gz` in [Zenodo 22296922 v5](https://zenodo.org/records/22296922), must match MD5 `1967bdcd6a4720c63bb986abdaf48ab0`.
- RWS DDAPI2 original observed `WATHTE` at **`schiermonnikoog.waddenzee`**, `Hoedanigheid: NAP`, `Eenheid: cm`, `ProcesType: meting`. Request all measurements 2009-05-18T00:00 fixed +01:00 through 2010-01-02T00:00 fixed +01:00 in 14-day chunks (exact overlapping boundaries deduplicated). Reject inconsistent units/datum, unknown offsets, missing values or discontinuities >30 min at the focal matching time. Station is a Waddenzee **candidate**, not independently proven identical to the gauge in the Dryad paper. Neither GIS elevation nor local front distance is available. Physical tide propagation across the island is not controlled.
- The Movebank source header defines the original naive GPS timestamp as **UTC or GPS time**; as a conditional exploratory conversion, first treat it as UTC, then report prespecified sensitivity at offset `-18 s`, `-1 h`, `+1 h`. This cannot independently resolve the clock standard. The result shall be tagged **EXPLORATORY_CLOCK_UNVERIFIED** until original logger clock documentation is verified.

## Endpoint and inclusion

- Original 2009 **visible, finite** GPS fixes inside latitude [53.2, 53.7], longitude [5.7, 6.6]. Original individual ID is used in memory only and never written to GitHub. Missing IDs, timestamps or coordinates are excluded.
- Successive positions of same animal: elapsed time 120–3600 seconds; observed horizontal great-circle (haversine) displacement / elapsed time in **km/h**, with implausible speed >120 km/h rejected. Outcome is `log1p(km/h)`, NOT instantaneous flight speed, foraging performance or prey catch.
- Tide at **start** of GPS interval; water height (NAP m), phase via **lagged 20-minute slope** of water-level interpolation (≥+0.012 m/h flood, ≤−0.012 m/h ebb, else slack). Retrospective interpolation sometimes uses a nearby future gauge sample; report historical association/prediction only, not operational future environmental forecasts.

## Primary models and untouched holdout

- M0 design: intercept, observed water level and square, spatial latitude+longitude, diel sine/cosine, annual sine/cosine, log interval length, bird training identity intercepts.
- M1: M0 + lagged **ebb/flood phase** coded -1/0/+1, + phase × water height. Both models use train-only standardization and ridge penalty λ=1.0 with equal total weight per original bird. No post-result tuning.
- Sort **calendar ISO weeks** chronologically; use first floor(0.70×Nweeks) as training, **one entire next week embargo**, all remaining weeks test. Model estimation uses no test outcome. Primary test restricted to same individuals with training GPS records; test birds absent in training are reported separately and **never silently relabelled train birds**.
- Report M0 and M1 mean square errors on exactly the same held-out test rows, averaged **equally across birds**, ΔMSE=M0−M1 (positive predictive increment), individual positive counts, bird-bootstrap and week-bootstrap paired 95% percentile intervals (fixed seed 20261102, 4000 replicates). Week bootstrap resamples complete test week strata.
- Minimum viable observational report: >=3 same-animal held-out birds, >=4 independent held-out weeks, >=10000 valid observed gauge values, >=1000 observed GPS steps. If any fail, stop primary effect interpretation and output `NOT_ADMITTED`.

## Mechanism and negative controls

- M1 improvement alone = tide-phase *association* with displacement after M0 covariates; cannot prove exposure-front pursuit, cause of synchronized flocking, niche partition, ecological resource use, or social steering.
- No M2 patch exposure without measured DEM and no M3 social inference until synchronous pair velocity geometry and independent animal-group holdout are separately screened. Original v29 simulation cannot be claimed as field replication.
- For diagnostics, retain 2009-year-only, clock-offset sensitivity without picking a winning offset; and report water-height quartiles and phase counts. Identical source GPS and RWS data across all models.
- No raw GPS coordinates, identifying bird tokens, raw gauge timeseries, or derived location coordinates committed to GitHub; only aggregate score receipts including provider SHA256 and code revision.
