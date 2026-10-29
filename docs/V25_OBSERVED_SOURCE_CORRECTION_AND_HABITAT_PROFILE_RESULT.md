# v25 full result: source-unit error detected, perfect classification invalidated; corrected environmental ranking positive, private-history increment not supported

**2026-10-29 JST. Original source verified. All biological conclusions explicitly conditional/exploratory.** These are separate v25-A (Dryad inaccessible), v25-B (USGS source), v25-C (unit STOP), v25-D (INVALID artificial 100% ranking), v25-E (post-outcome artifact audit) and v25-F (case-specific source-corrected exploratory) results. **Do not cite v25-D as ecology.** No actual future GPS destination-choice or Boids/foraging-resource niche mechanism is established.

## 1. Data sources and genuine original measurement

Overton & Casazza (2023), *Movement behavior, habitat selection, and functional responses to habitat availability among four species of wintering waterfowl in California*, [Frontiers DOI 10.3389/fevo.2023.1232704](https://doi.org/10.3389/fevo.2023.1232704), official USGS [data release DOI 10.5066/P9ELSUHN](https://doi.org/10.5066/P9ELSUHN). Original author ScienceBase `652edfe8d34edd15305a9ab0`, `Data Release P9ELSUHN.csv` **27,997,528 original bytes**. Published MD5 **`78eb6064eca992225d6907d6e46f5bef` independently matched**; independently computed SHA256 **`1a5c2342f9df4c70f170741c14b92b5146f0558f29fd593307768a228b82ca15`**. Source headers and rows from actual downloads were independently verified, including the [B3 categorical source CI 40827753426](https://github.com/zuizui0223/boids/actions/runs/40827753426).

The actual original source contains exactly **380,578 rows**, **190,289 unique `birdyear × timestamp` source pairs**, each with **ONE `case=TRUE` and ONE `case=FALSE`**. Four taxon labels `GWFG,LSGO,MALL,NOPI`, source night/day labels, seasons `Breeding,Early Winter,Late Winter`, and **493 original `birdyear` tokens**. The source data span calendar timestamps 2015–2023 (winter-year boundaries), despite the release label emphasizing 2016–2022. Source `birdyear` need not represent a lifelong individual ID (268 of 493 tokens occur across more than one calendar year). This is **one regional USGS tracking system**, not four independent species-level replicated field experiments.

### The SOURCE is two aggregated habitat profiles, NOT 101 discrete destination options

The paper generated **100 random movements from the start of an observed step**. The deposited CSV does **not** retain the 100 generated destinations, the original start positions or movement-kernel train/test origin. Instead it pairs `TRUE` (one observed used habitat category) with `FALSE` (the *aggregated habitat counts among 100 generated steps*). Seven original fields: `Corn,Field,Other,Protected,Rice,Urban,Wetland`. The original classification from the source at **one site/time** is static/retrospective and not proof of what was accessible or perceived before future movement. The source movement-length distribution was originally fitted using full study movements, which can include heldout birdyears.

The 26,316-byte associated `Data Release P9ELSUHN.xml` FGDC attachment had a **provider MD5 mismatch** on a separately repeated original-source GET (observed MD5 b159ed... vs published MD5 170cf7...); it remains `NOT_ADMITTED_ORIGINAL_FGDC_BYTES_INTEGRITY`. Scientific calculations use the independently full-file-hash-verified **CSV only**.

## 2. Important scientific data-quality discovery: incompatible raw TRUE/FALSE scales

v25-C's preregistered source-domain assumption that all seven raw columns were proportions [0,1] **failed before any model fit** on original Corn (frozen [v25-C source stop](../validation_v25/results/frozen_original_unit_stop_v25C.json); [CI 40828633631](https://github.com/zuizui0223/boids/actions/runs/40828633631)).

A separate SOURCE-ONLY domain audit (D0) established all seven fields are nonmissing nonnegative integers 0–100 in 380,578 rows, but inspected **without original TRUE/FALSE labels**, so its universal divide-by-100 hypothesis could not detect **case-dependent source encoding**. v25-D's separately preregistered all-seven /100 correction yielded **exactly 100% retrospective source TRUE/FALSE ranking for M1/M2/M3**, equal-birdyear surrogate pseudo log losses 0.04626/0.03861/0.04040, and apparent primary M1−M3 gain +0.005855. These results are **methodologically invalid for ecology** and must never be used as a positive animal-memory or habitat-choice finding. [Frozen flawed D numeric receipt](../validation_v25/results/source_unit_corrected_paired_profile_v25D.json).

The explicitly **POST-OUTCOME** source-geometry audit v25-E read all 190,289 matched original source cases and showed the exact cause:

| Raw original source property | TRUE (observed used case) | FALSE (aggregated 100 generated availability cases) |
|---|---:|---:|
| Nonzero habitat columns per row | **Exactly 1** | Mean **5.29** |
| Raw nonzero entry value | **1 in 189,961 rows; 2 in 328** | Values 0–100 (counts) |
| Seven-field raw sum | Mean **1.00172** | Mean **100.10043** |
| Source sum distribution | 1 or 2 | 100 in **189,989/190,289**, >100 in 300 rows |
| Original row sum, norm and largest category | **Always smaller than paired FALSE** | **Always larger than paired TRUE** |

Thus simply comparing magnitudes separated the source cases in **all 190,289 pairs** WITHOUT any ecological learning. This invalidates the earlier apparently perfect ranking. [Full post-outcome data audit](../validation_v25/results/postresult_source_artifact_v25E.json); [CI 40841863363](https://github.com/zuizui0223/boids/actions/runs/40841863363).

## 3. Separate v25-F unit-corrected exploratory analysis (registered AFTER artifact was found)

A new [explicit **post-source-effect** frozen unit rule](V25F_FROZEN_CASE_SPECIFIC_SOURCE_UNIT_CORRECTION.md) then required **case-specific common scientific meaning**:
- `TRUE`: exactly one positive source habitat class in each row, raw code 1 or 2; map ANY positive value to category **1** (others 0). All 328 `2` occurrences retained as the same observed class rather than treated as two independent birds or two choices.
- `FALSE`: original count of each habitat class among 100 generated steps, **divide by exactly 100**, keeping all rows; 300 original rows sum to >100 due potentially overlapping protected/class map assignments, without forcing a spurious disjoint composition.
- Same original 493 birdyear sources/190,289 paired profiles, same chronological within-birdyear first-three-pairs history rule, SAME original v25-C **untouched** model code and frozen (w=n/(n+2)), same SHA256-defined five heldout-birdyear folds and all original calendar-year holdouts. There were **492 scored birdyear tokens and 188,812 later paired source profiles**; one original token lacked sufficient earlier history.

The [source-corrected original GitHub Actions CI run 40842443398](https://github.com/zuizui0223/boids/actions/runs/40842443398) passed **4/4 new source-unit tests and 6/6 original v25-C model/chronology known-truth tests**. Exact original CSV SHA/MD5, TRUE/FALSE encoding and all 380,578 original source rows were preserved.

### Corrected, honest model results

Models rank the already-published observed used habitat category versus aggregated generated availability habitat profile. They **do not** forecast a real new GPS destination or a choice among 101 observed wetland sites. The likelihood is a **retrospective paired-profile surrogate** (`logaddexp(0,−βᵀd)`), not a calibrated biological choice probability.

| Source-registered model | Equal-birdyear **paired-profile surrogate** log loss (lower better) | Equal-birdyear correct TRUE-vs-FALSE profile ranking |
|---|---:|---:|
| M0 uniform paired-profile null | 0.693147 | 0.5000 |
| **M1 common environmental profile** (seven fields) | **0.602916** | 0.8145 |
| **M2 environmental profile + species-specific slopes** | **0.595042** (lowest) | **0.8161** |
| M3 M1 + fixed past birdyear profile-history weighting | **0.611741** | 0.7476 |

Original whole-`birdyear` bootstrap 10,000 draws, seed 20261029, equal 492 source tokens:

| Registered corrected contrast | Equal-birdyear mean paired-profile surrogate log-loss gain | Positive birdyear tokens | Whole-birdyear 95% |
|---|---:|---:|---|
| **Primary M1−M3**, individual-year history adds beyond common habitat | **−0.008825** | **196/492** | **[−0.018191,+0.000810]** |
| **M0−M1**, general environmental profile beyond null | **+0.090231** | **420/492** | **[+0.079754,+0.100476]** |
| **M1−M2**, source taxon-specific environmental slopes | **+0.007875** | **310/492** | **[+0.004963,+0.010909]** |
| M0−M3, source private-history blend over uniform null | **+0.081406** | **373/492** | **[+0.069051,+0.093824]** |

**Substantive limited interpretation:** In the case-specific properly normalized original source summaries, environmental class-profile differences have predictive information for *sampled used-versus-generated-available aggregate profile labels* across heldout birdyear tokens, and the registered taxon interactions give a small incremental source-surrogate gain. **Adding birdyear-private previous habitat profile information did NOT show a robust improvement over the common environmental model**; indeed M3 had a larger mean surrogate loss and lower profile rank performance than M1. This cannot prove that actual birds lack individual habitat memory.

### Fixed entire-calendar-year source cohort holdouts

The source's nine chronological calendar year labels (including boundary years 2015 and 2023) were evaluated by fitting M1 to all other source years (excluding overlapping birdyear tokens). M1 mean source-profile surrogate log loss:

| Heldout calendar year | Test birdyear tokens | M1 surrogate log loss |
|---|---:|---:|
| 2015 | 24 | 0.49382 |
| 2016 | 38 | 0.60168 |
| 2017 | 19 | 0.58231 |
| 2018 | 81 | 0.58868 |
| 2019 | 157 | 0.60636 |
| 2020 | 124 | 0.61710 |
| 2021 | 51 | 0.65529 |
| 2022 | 153 | 0.55840 |
| 2023 | 114 | 0.62325 |

All nine source year pseudo losses were below ln(2), but year label is not replicated environment, and original generated availability kernels may already depend on full-study data. No genuinely future out-of-study validation established.

## 4. Main Boids theory implications and STOPs

Compared with independently frozen previous studies:
- v23 raw Bangladesh dabbling duck GPS + independently retrieved ERA5: own **daily movement spread** history gave strong incremental prediction on 49 birds / 2,664 original future days, while the tested coarse gridded climate bin alone did not. Movement spread is NOT a habitat choice or cognitive memory.
- v24 original California radio brood source: static wetland properties ranked USED vs 400 generated available locations for 185 **heldout brood IDs** (mean AUC 0.61265 vs 0.5), but the habitat table lacked visit dates and the independent movement table lacked wetland IDs; time-ordered private wetland-choice history was **NOT_ADMITTED**.
- v25 original California 4-species waterfowl source has original paired habitat categories and replicated animal-year timestamps, but only **one retrospectively aggregated available profile**, not actual candidate steps or raw starting coordinates. Corrected private-history increment **was not supported** in this proxy task; v25-D's claimed perfect separation was definitively a source-unit artifact.

These studies use different animal ages/regions, spatial scales, sampling choices and endpoints. They do **not** establish a universal common learned history-weight, species niche competition or a recovered Reynolds motor-law coefficient. A mechanistic predictive ecology needs **original synchronized individual tracks, true time-specific available habitat alternatives and independently recorded food/water/hunting conditions**, preferably with data collected entirely after model calibration.

The scientific contribution of v25 is **as much methodological as ecological**: (i) original source file/grammatical audit, (ii) identifying a hidden TRUE/FALSE case-dependent scale mismatch that generated a *seemingly impeccable* but spurious 100% source predictor, (iii) correcting the source semantic units with a separate exploratory protocol that does not confirm the expected private-history benefit. This demonstrates why biological predictions must audit the observation/design process before using them as evidence of ecological niche memory.

## 5. Reproducible evidence and original-source privacy

- [Official Dryad Tennessee metadata and 401/403 access STOP](../validation_v25/results/tennessee_dryad_source_a1.json)
- [2023 USGS original manifest](../validation_v25/results/usgs_four_species_manifest_v25.json)
- [Original source exact CSV SHA and file-header/FGDC-source STOP](../validation_v25/results/usgs_four_species_schema_v25.json)
- [Original 493 birdyear/190,289 source-pair categorical proof](../validation_v25/results/usgs_step_strata_v25.json)
- [Original v25-C source-domain STOP (NOT a behavioral null)](../validation_v25/results/frozen_original_unit_stop_v25C.json)
- [Source-only D0 7-field numeric range audit](../validation_v25/results/original_habitat_unit_domain_v25.json)
- [Invalid source-biased v25-D results retained for audit](../validation_v25/results/source_unit_corrected_paired_profile_v25D.json)
- [Post-result E source TRUE/FALSE mathematical-artifact explanation](../validation_v25/results/postresult_source_artifact_v25E.json)
- [Case-corrected F all 492 birdyear source scores, every calendar year and effect](../validation_v25/results/case_corrected_paired_habitat_v25F.json)
- Original USGS exact file and model code under `validation_v25/`, original A1/B1/B2/B3/D0/C/D1/E/F CI run links in corresponding protocols and result JSON. All source reads download to ephemeral GitHub runner paths, original coordinates, bird IDs and exact times not redistributed.

**STATUS:** v25-A Tennessee original source access blocked; v25-B original USGS source admitted; v25-C source domain stop; v25-D **invalid ecological result from incompatible case units**; v25-E after-outcome source confound confirmed; v25-F case-corrected **exploratory** common habitat positive surrogate, birdyear private history **not supported**. Do not cite misleading v25-D as biological confirmation.
