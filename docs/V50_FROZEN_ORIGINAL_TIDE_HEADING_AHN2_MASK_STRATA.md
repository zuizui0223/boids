# v50 PRE-OUTCOME: does tide-conditioned heading skill depend on the AHN2 terrain-observation domain, with NO model refitting?

**2026-11-05 JST; precommitted BEFORE v50 original group scores.** Prior v43/v44 found source-authentic 2011 direction phase gains in full moving original GPS; v49 found weak/inconsistent gain in a C-height-valid subset **after re-training on that subset**. This is **explicitly post-result exploratory** on the same original birds and is NOT independently preregistered ecological confirmation.

## Question

If exactly the original v43 tidal-phase direction model is fitted on **ALL original 2010 moving GPS triples**, does its **2011 whole-year prediction** vary by *independent AHN2 DTM availability at the true next destination C*, without re-fitting by habitat source domain? This separates test-cohort restriction from re-training effects.

IMPORTANT: historical AHN2 DTM source mask is **not a measured dynamic wet/dry boundary**. It can reflect missing LiDAR points over water, dunes, provider coverage and resampling, and data quality, not biological habitat class. Any contrast is observation-domain heterogeneity, not identified waterline chasing.

## Original source and exact replay gates

- Independent original 2010/2011 O_SCHIERMONNIKOOG / O_AMELAND Zenodo GPS original-gzip provider MD5+SHA, original 2010/11 RWS local WATHTE meting 10-min cm/NAP fixed UTC+01 at the same frozen stations; use v41 `original_three_fix_heading_episodes` untouched with source clock **native assumed UTC (0s primary only)**, true tide phase ±0.012m/h at middle B, original visible per-hour first GPS, each A→B and B→C 30–120min, each 0.4–120km/h. No source GPS original ID, raw location or exact timestamps committed.
- Fit v41 `forecast` **unchanged** on **ALL original 2010 direction-eligible moving triples**, not on AHN2-selected sample. Score **ALL original 2011 direction-eligible moving triples** with same M0 (true water height, position, diel/year, private prior heading/speed) and M1 (M0+ebb/flood+height interaction), ridge λ10, equal 2010 original bird weights.
- Before any group partition effects, hard replay **full** original v43 2010→2011 result on both original sites, including original test episode and bird counts and per-bird pooled MSE within abs 1e−9:
  * Schiermonnikoog 4,948 moving test triples, 13 birds, M0 `0.4491437063035975`, M1 `0.41370693859833235`.
  * Ameland 4,678 test triples, 5 birds, M0 `0.5107931836556263`, M1 `0.43464618382116776`.
  Results of this replay are **already known**, not a new v50 finding.
- Reuse source v46 exactly: 2010 source-hourly original GPS positions only select K=8 ranked 2km RD source cells; official AHN2 2007–2012 DTM WCS 256px×256px/2km, EPSG28992/NAP first Float32 height candidate, second source normalized 0–1 auxiliary≥0.999. Original source first-band height quality/data availability is **not used to fit the 2010 model or choose 2011 test source**. No original sea pixels imputed.
- Independently reconstruct original B→C destination fix from same source GPS using `triplets_with_past_motion`; match each exact v41 test direction episode by native source `(bird,B timestamp)`, B lat/lon, previous heading/speed and observed next B→C east/north unit vector. If any original source row missing, duplicate or inconsistent → hard SOURCE_STOP.
- Classify each **already predicted** 2011 C fix into exactly three mutually exclusive data-observability groups:
  1. `C_AHN2_VALID`: 2010-selected cell, first DTM height candidate valid and normalized auxiliary≥0.999.
  2. `C_SELECTED_CELL_AHN2_MISSING`: inside 2010-selected cell but source original DTM invalid/masked/coverage none.
  3. `C_OUTSIDE_2010_SELECTED_CELLS`: true original GPS C outside K=8 fixed source cells, never fetch additional new cells.
- The full 2011 test partition must contain **exactly all** previously replayed v43 source episodes, no outcome-dependent deletion, and the count for AHN2-valid group must equal v49 C-height-qualified count (Schier 1,009, Ameland 1,238) when both source heights/true source tide phase meet same frozen rules. If source WCS has drifted, report drift and SOURCE_STOP instead of silently changing the sample.

## Fixed effect estimates and uncertainty

Within each label, source direction error: half squared next east/north unit heading vector loss, M0 and M1 as independently predicted **before label inspection**. Summarize source test episodes, birds, ISO weeks, per-bird pooled mean M0/M1 loss and relative error reduction `R=1−M1/M0`. Whole-bird paired 10k bootstrap for R and separate equal-week-then-present-bird R with whole-week 4k bootstrap. Always report all 3 groups (including negative/null signs). **Group reporting gate**: ≥200 episodes, ≥3 source birds, ≥4 ISO weeks; else `NOT_ADMITTED` for that group, retain counts only.

**Single primary comparative estimand**: `R_selected_masked−R_selected_valid` with **same original focal bird** contributing sufficient valid/masked original C in the 2011 year, computing each group's per-bird mean of the *fixed* M0/M1 errors, then paired whole-bird resampling **10k** (seed 20261105) and matching CI. Required ≥3 common source birds and at least 200 original total episodes in EACH of these two categories. Positive means tide phase has greater relative **prediction skill** for AHN2 source-masked destinations. It is NOT a causal statement about water/intertidal flats, nor a direct social Boids mechanism or food choice. Per-bird eligibility threshold: ≥5 original episodes per group per bird to reduce one-off burst influence (fixed before new scores). If source gate fails, primary comparison NOT_ADMITTED.

**Secondary**: outside-selected-cell versus AHN2-valid relative-skill difference, reported as descriptive across different data domains, with its own source bird count, no hypothesis significance unless predefined same-bird groups pass. The location-based group proportions are a source-selection QA result, not a biological hypothesis test.

GPS clock UTC/GPS ambiguity remains, and no cross-site/multi-species generality or physical z−η exposure follows from static mask. Source v47 B+C true height pair insufficient. Do not claim genuine 2011 hydrostatic front tracking.
