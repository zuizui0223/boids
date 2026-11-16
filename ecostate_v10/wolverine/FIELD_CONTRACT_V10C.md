# Original Wolverine v10c: condition on start-road state versus destination-only selection

**Frozen 2026-11-16 after official source checksum and the identical 17-column headers of BOTH original XLSX sheets, BEFORE opening any animal-level use, road, traffic, time or movement numeric values.**

Source: Scrafford, Avgar, Heeres & Boyce (2018), *Behavioral Ecology*, 29:534–542, DOI 10.1093/beheco/arx182. Original archived dataset Zenodo record 5011732 (from Dryad 10.5061/dryad.44pp0). Published original XLSX 74,178,559 bytes, MD5 6d694faeadde68fbce1c0b45632aa21c, SHA256 979a362af1acaff069a7c53dfabf5284eb68d0c448899858ae18be999513b1bd. The author study ALREADY identified road avoidance and speed response to traffic; do not rediscover them.

## Original data and predeclared hard admissions

Read both sheets in full, whose 17 headers are identical: `cluster`, `used`, `SL_m`, `id`, `sex`, `time_start`, `hour_start`, `month_start`, `day_start`, `year_start`, `twilight`, `road_end`, `road_start`, `stream_end`, `stream_start`, `traffic_end`, `traffic_start`. Group only by `(original worksheet, source id, source cluster)`; NEVER assume cluster numeric label unique across individuals/sheets. Require: >=1 real and >=4 alternatives (>=5 rows), exactly one binary used case, finite nonnegative road, stream, traffic and displacement, `0 <= hour < 24`, and within-stratum identical starting road/stream/traffic and hour to absolute tolerance 1e-6. Drop complete invalid groups without repair. Retain whole original IDs with >=50 eligible groups each; require >=10 such independent IDs and >=600 eligible groups or stop.

## Frozen model family, identical used/alternative targets

Predict **exact conditional original choice among source-defined alternatives**. M0 is fixed destination/geometry/risk baseline: `log1p(SL_m)`, `SL_m / 1000`, `log1p(road_end)`, `log1p(traffic_end)`, `log1p(stream_end)`, destination-road × destination-traffic interaction, log-road × sine/cosine source hour, log-traffic × sine/cosine hour, and log-road/traffic × original sheet2 interactions. No group-constant terms that would mathematically cancel (e.g. main effects of road_start/time/id). No tunable predictor selection.

**M1 = M0 + `abs(log1p(road_end) - log1p(road_start))`.** Primary endpoint: mean conditional log-score improvement M1 vs M0 **on whole unknown animals**. Biological *state-retention* pattern additionally requires negative M1 divergence coefficient in >=4 of 5 folds. This goes beyond generic selection for a road distance: two movements to the same end-road distance could differ in relative similarity to their own source-road exposure.

**M2 = M1 + `abs(log1p(traffic_end) - log1p(traffic_start))`.** Secondary only, non-rescuing, reports whether observed source-traffic similarity has independent predictive information beyond M1; the number and identity of features are fixed now, before numeric response analysis.

Within group conditional softmax (exact 1 used candidate). Penalty L2=0.02; train-only mean/std standardization and clip [-10,+10] for numerical stability; pooled train animals weight 1/number animals and per-animal group weight 1/n_groups. Sort unique animal IDs by SHA256 and distribute round-robin into five **animal-disjoint folds**, yielding >=1 heldout animal/fold; no same-animal rows in training. Original 10,000 bootstrap resamples of entire animal means (seed 20261116), report animal equal mean logscore improvement, 95% bootstrap, per-animal sign and median. PRIMARY PASS iff lower CI >0, positive in >=65% of admitted IDs, and road divergence coefficient negative in >=4/5 folds. Do NOT change rule after observing effects. Report all failures and post-result individual/season heterogeneity descriptively only.

## Biological claim ceiling

A positive source-state divergence contrast may reflect spatial autocorrelation of endpoints, correlated path/candidate geometry, unmeasured terrain, heterogeneous movement speed or destination resource functions. The data have no actual GPS coordinates (sensitive removed), no measured physiological state, no direct risk perception, no complete physically reachable local state surface and only one source landscape. **Even a PASS is not causal adaptive buffering, competition, cross-taxon niche partition or a conservation intervention effect.** A FAIL does not prove wolverines lack road-state fidelity. Only the fixed conditional source-defined step-selection prediction claim is permitted.

## Execution and provenance

`ecostate_v10/wolverine/field_v10c.py`, `test_field_v10c.py`, and separate workflow `ecostate-v10c-wolverine-original-field.yml`. A source checksum mismatch, invalid original grammar, impossible animal fold or nonconvergence yields `SOURCE_OR_MODEL_STOP`, never a positive/negative biological effect. Original workbook is downloaded only into CI ephemeral storage, never added to Git or archived.
