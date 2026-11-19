# v35 — Broad-scale bat movement transfer: source-admission freeze

**Date:** 2026-11-19 JST. **Source-only stage, before reading numerical home-range or commuting-distance outcomes.**  
**Repository:** \`zuizui0223/boids\` research branch. All original \`batter\`, \`boids\` v30 negative and v32–v34 source-access and structure STOPs remain intact.

## New macro question

Do the relationships among bat movement distances, landscape organization, flight morphology and habitat specialization **predict independent studies, countries and species that were not used for training**? Which ecological/contextual boundaries cause transfer to fail?

This is a **test of ecological transportability**, not a new claim that forest affects home range size or that wing morphology predicts space use. Those associations were explicitly demonstrated in the underlying original study and cannot be re-presented as novel.

## Independent original source identity

Laforge, Barbaro, Archaux et al. (2021/2022), *Landscape composition and life-history traits influence bat movement and space use: analysis of 30 years of published telemetry data*. Source paper and dataset [Dryad 10.5061/dryad.qnk98sfhh](https://doi.org/10.5061/dryad.qnk98sfhh); original open mirror [Zenodo 5794471](https://zenodo.org/records/5794471), published 2022-09-10. Authors report literature compilation of **166 studies**, **49 bat species**, **3,129 tracked individuals**, **22 countries** from Europe and North America, 1988–2016 telemetry. **These are published parent-study counts**, not 3,129 guaranteed independent CSV rows or uniform source support for each endpoint.

Original files from the pinned record:
- \`Meta_data_bat_home_ranges.csv\`: published MD5 **bf24d4f5bde98ee696a6f8f7745577a2**, about 524 KB.
- \`Lanscape_data_bat_home_ranges.csv\` (original spelling): published MD5 **a8a501e5e426cbf79447fda6b23f1e5e**, about 48 KB.
- \`Readme_home_ranges.xlsx\`: published MD5 **86da8c29e3088ee35fc1bc65149e583b**, about 12.7 KB, used only if source field definitions cannot otherwise be inferred without looking at outcomes.

Avoid substituting another Dryad version with nonidentical bytes after seeing outcomes. Verify these exact two published CSV MD5 values and derived SHA256 from complete original bytes before evaluating anything. The earlier 2026 *Chrotopterus* dataset is **not** an independent replication of any effect in this 2021 compilation and is not used here.

## Fixed source-only structural questions

1. Can official published Zenodo file endpoints return actual CSV rather than a browser-challenge HTML or login page? Record HTTP response, byte length, actual MD5, derived SHA256 and file header.
2. Report only column names, row counts, presence/absence and nonempty structural ID, species, country, study and colony keys. Original \`Meta_data\` may mix individual/colony-level observations, repeated effect sizes or multiple response types. Do **not** treat every CSV record as an independent bat; confirm inferential grain from source headers/codebook.
3. Check whether \`Lanscape_data\` can join unambiguously to movement metadata on geographic/study/colony IDs. Count duplicate keys at that join grain and one-to-many relationships before target values are opened. Do not create multi-row amplification through joins.
4. Candidate outcomes and their units need verification: individual or colony home-range area (ha/km²) and mean roost-to-foraging distance (km). If a source contains already-aggregated study means rather than raw movement traces, we can evaluate transfer of published summary effects only, **not future behavioral decisions or active-search/perch switching**.
5. **Predeclared primary feasibility:** at least 8 independent study source IDs, 4 country values, 10 unique species labels, a valid contextual join or sufficient covariates in one row, and at least 100 nonmissing units of the *chosen target* before numerical values. If no ID/country, **SOURCE_SUPPORT_STOP**; do not declare country generality.
6. Prevent pseudo-replication: leave-whole-study-out is the primary independence boundary. Country and species withholding are separate, exploratory generality axes and not phylogenetically independent if multiple taxa share studies/regions.
7. No numerical ecological outcomes, effect estimation, regressions, future movement, plot or habitat values may be evaluated until a separate fixed predictive model contract is committed after the structural schema audit.

## Candidate model after admission (separate contract required)

- **M0:** training-only intercept + bat body mass and foraging guild where available, species code never a primary explanatory variable in a left-out-species test.
- **M1:** M0 plus habitat fraction, landscape diversity/configuration, wing loading or aspect ratio, using pre-registered source fields; compare heldout **study-weighted** log-distance MSE or log-area MSE.
- **Country/species tests:** nested source support and train-only imputation; never select favorable country/species groups post-outcome; study-level uncertainty, and cross-group heterogeneity.
- **Success ceiling:** significant global regression effects in the original article are prior art. Robust *prediction of heldout study/country/species* would be a distinct result. A single temperate-region compilation cannot establish a global bat species law or memory/learning.

**Stage-1 output:** source byte integrity and schema-only receipt, no ecological result.
