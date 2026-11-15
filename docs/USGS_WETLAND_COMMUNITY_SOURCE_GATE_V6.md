# Original USGS California Waterfowl Habitat Program 2025 — source-only admission (v6)

**Registered 2026-11-15. Research context: `boids` cross-taxon ecological-state PR #146.**

## Source identity and novel question

- Hartman & Ackerman (2025), USGS Data Release 10.5066/P13UJQP5, publicly marked CC0.
- Provider item ID `67c8bbcdd34ea599a3b9ae77` (catalog inventory).
- Public release describes **240 visits to 117 managed wetland units** across Sacramento Valley, San Joaquin Valley and Suisun Marsh, 2022–2023. Original paper already analyses guild-specific densities in relation to mean water depth, vegetation and landscape context (2025, *Ecology and Evolution*, DOI 10.1002/ece3.72032); duplicating that is not novel.
- Proposed genuinely independent ecological *community* endpoint: **Does same-visit depth heterogeneity provide independently transferable information about wetland guild/assemblage use beyond same-visit mean depth, area, year/season and landscape context?** Assess at unseen wetlands, not random rows. **This is not an individual movement, state-retention or resource-exhaustion test.**

## Admission sequence — first run source-file inventory only

1. Fetch exact ScienceBase item JSON using HTTPS and record original filename, size, provider checksums and download URL; do not read biological rows. Source stop if ID/title/file manifest fails.
2. Independently check that a selected source table contains original visit ID, wetland unit ID, survey date, sampling effort, individual guild counts (or species counts), contemporaneous water depth distribution/histogram, wetland area, and relevant sampling controls. Record original native units. If no within-wetland water-depth heterogeneity is present, `SOURCE_SCHEMA_STOP_NO_STATE_PORTFOLIO`; do not infer it from site-area or static land cover.
3. Require at least 30 wetlands with the above data. Sites in the same managed complex should be treated as a correlated group, if identifiable. If original geography is only three regions, no leave-region-out inference without sufficient balanced sample.
4. **Only after structural admission** freeze the exact response, train-only centering/regularization, predictor sets, missingness handling, split keys, and no-leak contrasts. Do not open species counts or environmental values before this protocol exists.

## Candidate predictive comparison (not yet authorized to fit)

- Same *visit-level* composition response, Dirichlet-multinomial or categorical count likelihood, with survey effort offset and full support reported.
- Reference: survey period (season, region), flooded area, effort, mean/median water depth, surrounding landscape and year, with training-only preprocessing.
- Added variable: source-measured **within-wetland depth diversity** at the very same survey date; avoid using spatial variability estimated from the bird choice point alone.
- Primary transfer: whole-wetland group exclusion and equal-wetland scoring; paired improvement `heldout_logloss(reference) - heldout_logloss(+depth_heterogeneity)`. Bootstrap entire independent wetlands, not visits or individual bird records; include no-data outcomes.
- Falsification: if effects fail in unseen wetlands or vanish after mean-depth/area controls, portfolio hypothesis is not supported for this site-scale community endpoint. Even a positive gain is predictive, not causal.

**Claim ceiling:** This data source is an independent co-observed environment/community candidate. It cannot identify individual movement routes, animal-chosen local alternatives, site-specific state buffering, or fixed depth preferences without new data; do not pool effects with King Rail `louis` bird-year slope.
