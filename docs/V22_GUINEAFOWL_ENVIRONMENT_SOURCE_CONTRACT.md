# v22-A pre-outcome source admission: wet/dry seasonal context versus historical social-group states

**Registered 2026-10-28 JST BEFORE reading any v22 source movement-response values.** The original v20 wild guineafowl results and all earlier pigeon/research endpoints remain frozen.

## Source and independence classification

Papageorgiou, Rozen-Rechels, Nyaguthii & Farine (2021), *Seasonality impacts collective movements in a wild group-living bird*, *Movement Ecology*, original authors' public [ranging_seasonality](https://github.com/DanPapageorgiou/ranging_seasonality) repository, pinned author commit `2a3aec308bb4a8449d1eeb16beed4aff8f387116`. Original author-derived Rdata files (not native GPS):
- `ddf_hr_dtd.Rdata`, Git blob SHA1 `65cbed930dd0924dec32fd7115f016f6b3fbc3d6`, **8,783 bytes**: group-season home-range area and travel distance.
- `df_dhor.Rdata`, Git blob SHA1 `a365bea412cdb6eb3f7b4c76bb0f9dda2268ea8a`, **1,911 bytes**: original source day-to-day space-use overlap.
- `df_dshor.RData`, Git blob SHA1 `6b389efeed3c23c498735362cdd2befb5ff8b00a`, **4,002 bytes**: original season-to-season home-range overlap.

Original source scripts expressly reference **Movebank Avulturinum_Farine study 475851705**, identical underlying tracked Kenyan vulturine guineafowl population as v20. This is **NOT independent biological replication** of v20's positive fidelity result, even if newer seasons and additional source labels are present. All source ecological records are authors' original *derived* summaries, not individual GPS telemetry or observed food patches.

## Source-only stage, before any prediction

1. Download the three exact author-pinned GitHub Rdata files temporarily via `raw.githubusercontent.com`; verify each original byte length and actual Git blob SHA1, compute independent SHA256. Hard cap 1 MB/file. Do not include original Rdata or response rows in boids.
2. Inspect R object names, frame shapes, column names/types, source group ID/season columns, unique group IDs, number with ≥2/≥3 seasons, season codes/counts, wet/dry/intermediate or other original season_type categories and their row counts. Inspect numeric response **only for missingness counts**, never emit values, source ecology estimates or model effects.
3. Determine actual grain: one group×season row or multiple birds per group×season (the published 2021 source code uses groupss_ for group random intercept and counts tracked individuals in each group/season). **Do not treat source data rows as independent group-season replicates**. If multiple individuals observed in the same group×season, require a predeclared way to aggregate the original response without future outcome leakage before any forecast.
4. Establish whether environmental condition `season_type` is a single time-wide condition shared by all groups and whether one original season code maps uniquely to one season_type label. This could enable only a **contextual categorical environmental baseline**, not a model of independently measured rainfall/NDVI.
5. Compare source group-season identity overlap with prior v20 author Rdata (using only IDs+season keys, without response values) if source ID conventions align, and separately note same biological population even if exact ID matches fail.
6. For a new future-season prediction, require **≥8 actual independent original group IDs with ≥3 chronologically ordered original seasons**, ≥3 distinct season-type categories if provided, and ≥12 group-season future targets under available previous seasons and ≥3 comparison groups. Otherwise report `NOT_ADMITTED`, not a favorable subset.
7. Source identity/time schema alone cannot identify the chronology of numeric season labels if absent from source documentation. Do not sort wet/dry conditions as if time order, and do not select a time ordering based on observed response signs.

## Distinct later v22-B (not yet authorized)

Freeze actual original season chronology, response (first day-to-day fidelity), wet/dry/intermediate environment-only baseline trained on **other group IDs' strictly earlier seasons**, own group previous states, fixed partial pooling, common future target support, whole-group uncertainty, and *leave-one-entire-season-out* diagnostics. Only after Stage A and independently checked chronology is it valid to open ecological response values for an exploratory model.

The future model should compare contextual seasonal information with group history, but it cannot constitute new-species biological confirmation of v20 and cannot estimate social-network causal mechanisms or individual private memory.

**All prior v13-v21 endpoints, especially v20's +0.0026483 group-fidelity gain, remain unchanged.**
