# Marais Breton 18-site waterbird community-state comparison — source-only v3

**Registered 2026-11-15, before original source outcome values are opened.**

Independent data: Secondi et al. 2026, https://doi.org/10.5281/zenodo.18161913 (CC BY 4.0), DOI paper https://doi.org/10.1007/s10344-025-02051-x. Original researchers already found guild-dependent response to water/vegetation and divergence of taxonomic and functional diversity. Do not claim those effects are new.

Reported public source: 18 wetland sites, repeat surveys 2015–2020, species abundances and water area/level/vegetation characteristics. This is a **community assembly** validation, not individual movement or King Rail buffering replication.

## Source admission

Freeze original metadata, SHA-256/provider MD5, sheet names, column names, date/site/effort grammar, and presence of species-by-visit abundance and same-visit habitat metrics. Fail closed if no exact source access, or if the workbook contains only site/annual summaries rather than species-by-visit counts. No biological outcomes opened in this stage.

## Prediction target to preregister after source-only schema admission, before biological numeric values

Test whether hydrological environmental state helps predict **changes in waterbird species composition at the same site** beyond seasonal timing and site context. A replicate is a visit; independent geographical transfer units are whole monitored **sites**, with at most 18 independent site blocks. Source outcome is species count composition, not a tagged individual choice. Observation effort and visit dates must be accounted for, and do not pool species counts as independent animals.

Frozen modeling direction: compare temporal/calendar baseline with water-level state and separately vegetation state. Hold out sites completely from model training, report equal-site score improvements and uncertainty; if site identifiers in unseen sites have no fitted effects, don't use them as predictors. Do not change species/season filters based on response magnitude. Include guild subgroup only with a source-defined guild label and a declared biological question. A predictive difference cannot identify competition, causal environmental filtering or a switch of the same animal.

**Current step source-only.** No numerical ecological claim until complete source file is inspected and a species-by-visit pre-outcome model schema is committed.
