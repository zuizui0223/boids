# v25-F: Correctly harmonized TRUE used habitat category and FALSE 100 simulated-step availability fractions

**Registered 2026-10-29 JST, after the v25-D1 modeled results and after the explicitly POST-OUTCOME source-construction audit v25-E. This is a NEW, severely qualified exploratory source-unit reconciliation, not an independent confirmation or legitimate rescue of v25-C/D.** All prior v13–v24 frozen observations remain untouched.

## Why earlier v25-D ecological conclusions are invalidated

Original USGS Overton & Casazza (2023) [DOI 10.5066/P9ELSUHN](https://doi.org/10.5066/P9ELSUHN), file `Data Release P9ELSUHN.csv`, 27,997,528 bytes, independently verified original SHA256 `1a5c2342f9df4c70f170741c14b92b5146f0558f29fd593307768a228b82ca15`. V25-E [original CI 40841863363](https://github.com/zuizui0223/boids/actions/runs/40841863363) checked full 190,289 paired TRUE/FALSE profiles and found:
- `case=TRUE` (used) row has **exactly ONE** nonzero habitat column, integer value either **1 or 2**. 189,961 rows summed to 1, **328** summed to 2. TRUE's mean seven-column sum **1.001724**.
- `case=FALSE` (available) row represents the source's **100 simulated steps** aggregated into seven habitat count columns, each integer [0,100], row sum typically **100** (189,989 of 190,289), with 300 source rows exceeding 100 and maximum 201 because source map categories may overlap/record error. FALSE's mean seven-column sum **100.100431**.
- The original v25-D fixed **/100 for BOTH cases** mistakenly encoded used rows as near-zero vectors and available rows as proportions. Every one of 190,289 available rows had a larger seven-field sum, Euclidean norm and single-category maximum than its paired used row. Consequently v25-D M1/M2/M3 **all 100% ranking** is a source scale artifact. Its original **M1−M3 +0.005855** log-loss gain and nearly zero fitted errors **MUST NOT** be cited as positive ecological predictive results.
- v25-C remains independently frozen `NOT_ADMITTED_FROZEN_ORIGINAL_HABITAT_DOMAIN_OR_SOURCE`. V25-D remains a public inspectable methodologically **INVALID_FOR_ECOLOGY** archived result, not a result to quietly amend. V25-E diagnostics are explicitly *post-outcome*.

The original authors' [2023 publication](https://doi.org/10.3389/fevo.2023.1232704) reports observed habitat classes ("Used") and the average of 100 simulated movements' available habitat classes. The public CSV is a **two-profile aggregate**, not 101 independently available destination coordinates.

## New exact source-unit transformation — fixed before v25-F is fitted

Normalize source **asymmetrically, according to data-generating role**:
- For original `case=TRUE`, require each row has **exactly one nonzero of 7 source fields** and that the nonzero is **either 1 or 2**. Code the single observed used habitat category as `1.0` (any positive original count maps to 1), all other fields `0.0`. The 328 original `2` values are treated as occurrence coding of the SAME single observed class, not as two independent locations. Do **not** exclude these rows or choose a target-favorable subset. Report that unusual source encoding explicitly.
- For original `case=FALSE`, require all seven original field values are finite integers [0,100] and the row sum lies in **[100,201]** as found source-only/after-D1 audit. Divide all seven available-class counts by **exactly 100**, representing each original candidate habitat frequency per 100 analyst-generated movements. Because Protected may overlap a landcover category, do NOT renormalize false row to sum1, or force the 300 source rows with totals >100 to fit a disjoint composition.
- Every original profile row from every birdyear/time is kept, exact original MD5+SHA checked again. No data-dependent clipping, cohort exclusion, optimized unit factor, environmental feature selection, posthoc logistic penalty, or rewritten source TRUE/FALSE stratum.
- This is a **post-source-effect revealed** model based on correct physical data semantics, thus **exploratory method repair only**. A new independent source is required for confirmation even if effects are positive.

## ALL numerical prediction design from original frozen v25-C reused unchanged

The transformed temporary source CSV is fed to the **unchanged frozen v25-C model code** in `validation_v25/retrospective_habitat_profiles.py`:
- 493 original `birdyear` tokens, 190,289 observed TRUE-vs-FALSE aggregate habitat profile pairs, four source taxa `GWFG,LSGO,MALL,NOPI`, all seasons and photoperiods, no source stage filtering except original first three pairs history only. `birdyear` is NOT guaranteed to denote a perennial individual.
- Exact five SHA256-mod-5 whole-birdyear holdout folds. M0 `ln2` uniform pseudo-label; M1 seven source habitat profile differences `d=TRUE-FALSE` with C=1 L2 no-intercept mirrored-sign logistic trained on other birdyears, M2 fixed four species interactions, M3 M1 blended with strictly earlier same birdyear mean profile direction using **fixed `w=n/(n+2)`** imported without tuning.
- Identical **188,812 later original profile pairs** anticipated from v25-D source-only history support (the exact count is verified on the new run). Whole-birdyear equal weights, 10,000 original birdyear cluster bootstrap seed 20261029. All nine calendar years' environment-only leave-entire-year-out scores.
- **Primary exploratory signed log-loss gain M1−M3**, secondary M0−M1, M1−M2 and M0−M3. FULL 492-birdyear results, every species and source year, and **any negative** effect to be saved. Source geometry can still produce easy structural comparisons even after this correction.
- Source `FALSE` is the aggregate proportion of simulated endpoints derived from an original full-data movement kernel, NOT a location the duck actually declined, or 100 independent source choice rows. Pairwise logistic log loss is a **surrogate** useful for method comparison only, not biological probability of choosing a reachable wetland in the future.

**Strong negative control / caution:** if the corrected source is still perfectly separable by a simple structural statistic or the resulting environmental M1 is trivially 100% accurate, retain as a source artifact, not a scientific niche-memory claim. The absence of original step starting coordinates and trained movement-kernel provenance **always bars prospective location-choice and causal Boids claims**.

## Implementation limits

v25-F code may only provide the above asymmetric normalization; it MUST import the original v25-C prediction/bootstrapping functions without changing them, and must record all original v25-C/D failure audit chains in its result JSON. Do not count 492 birdyears as independent species/landscapes or 188,812 pairs as independent animals.

The objective is **source-corrected retrospective habitat-profile information analysis**, with lower evidentiary status than independent habitat-choice prediction. Future genuinely prospective verification needs original GPS starts and alternatives generated using training-only movement kernels in a new population.
