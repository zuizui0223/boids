# v28-C0 — original bat landcover, roost and turbine numeric scale audit, SOURCE ONLY

Registered 2026-10-29 JST **before opening any original use/available label versus environmental measurements or fitting habitat/turbine effects**. The full 2023 source is exact Zenodo [record 7535030](https://zenodo.org/records/7535030), three original CSV MD5 and SHA256 source-verified [A1](../validation_v28/results/zenodo_original_bat_source_manifest_v28.json) and [B1](../validation_v28/results/original_three_bat_CSV_source_gate_v28.json).

B1 verified **60 bat IDs**, 107 original `trackid` paths and **8,129 TRUE observed points + 40,645 FALSE random points**, all 60 RSF bat IDs separately present in original GPS and ring-number capture ledger. The original RSF table has **only one** bat with ≥3 original track IDs, so the original prespecified **≥8 individuals with ≥3 repeat flight histories FAILS**; there is no legitimate v28 individual-history prediction or Boids social-contact mechanism. Keep that independent-group source STOP. The animal population is in one German landscape, and the source random positions are defined by authors' RSF design, not field-observed unchosen locations.

## Separate viable question (needs new, distinct preregistration)

Can measured landscape/roost context predict **sampled USED versus original RANDOM** points in wholly heldout bat IDs, and does adding distance to wind turbines improve transfer beyond landcover/roost controls? This is resource-selection association and out-of-bat sampled-availability prediction, NOT a prospective route choice or causal turbine avoidance.

**Before opening any effect, A3 source-only numeric range audit:**
- Read **ONLY** three original source covariates `mindist_WKA_inKm`, `DistanceAssumedRoostsInKm`, `clc2_20m` (original coarsened CORINE landcover category), and `forestornot` (original forest categorical indicator). Do not read `case_`, bat IDs, observed GPS x/y, timestamps, model scores or other habitat columns.
- Count original 48,774 source records, numeric finite/missing/negative counts and global range/quantiles for the **two** kilometer distance columns, and categorical token frequencies/missingness for `clc2_20m` and `forestornot`. Do not group by USED/AVAILABLE label or bat. The exact feature units are independently documented as km; no arbitrary conversion to 0–1.
- If negative distance or widespread missingness arises, document an original source-domain STOP or separately preregister training-only imputation before any ecological fit, **never** optimize transformations after examining bat effects.
- No lower threshold for 3-flight individual history; no assumption of exact 3D vertical accuracy. The original `Height` in GPS source is not used.
- All older v13–v27 endpoints and v28-B1 independent bat/grain counts remain frozen.
