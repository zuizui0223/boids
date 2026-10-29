# v28: New independent wild noctule bat habitat and wind turbine source — environment predictive, turbine main effect uncertain

**2026-10-29 JST. Actual original GPS-derived wild-bat RSF data, validated source bytes and distinct pre-outcome environmental model.** This is independent of the previous homing-pigeon, wild guineafowl and waterfowl observational sources. Original model's animal-ID and generated-random-position data support a **new bat-heldout environmental predictive comparison**, but **NOT the private three-flight memory or Boids motor-force hypothesis**.

## Original published data and reproducible source-quality result

Reusch, Paul, Fritze, Kramer-Schadt & Voigt (2023), *Wind energy production in forests conflicts with tree-roosting bats*, *Current Biology* 33:737–743.e3, [paper DOI 10.1016/j.cub.2022.12.050](https://doi.org/10.1016/j.cub.2022.12.050). Original publicly published CC BY 4.0 field data [Zenodo record/DOI 10.5281/zenodo.7535030](https://zenodo.org/records/7535030). The authors monitored German forest-associated common noctule bats (*Nyctalus noctula*).

**All three original published CSVs were ACTUALLY DOWNLOADED**, provider MD5 matched exact source byte length and independent SHA256 calculated. [A1 original provider manifest CI 40860616465](https://github.com/zuizui0223/boids/actions/runs/40860616465), [B1 full-source ID-quality CI 40861335939](https://github.com/zuizui0223/boids/actions/runs/40861335939).

| Original published file | Verified bytes | Provider MD5 | Independently calculated SHA256 |
|---|---:|---|---|
| `Model_dataset_RSFFlight_Complete_EPSG25833.csv` | **17,582,302** | `fb0d7967d552b855ab530eeedcede7ff` | `76f92b1442eb4350ee6d83ede83b5e43fda4b9f3997e3fd9a3618a44f2470375` |
| `Observed_GPS_locations.csv` | **3,080,045** | `a1583b48487a78259f7e63937af232e5` | `2f373d47706c5b56313de70b623bb5446f5925c69af30f1b145993419e382aa9` |
| `Individual_Characteristics_Capture.csv` | **6,388** | `84e78242135fc50b12e5e2ffff91bcb5` | `105becdf16f38b7ce39b911c2e42b9a12502d835fcda5cdc21a78d8eee3f5418` |

Original model RSF is **48,774 rows: 8,129 TRUE GPS-used observations and 40,645 original author-generated FALSE random positions**. Original **60 individual bat IDs** (all 60 linked to the capture `ring_number` and GPS `bat_id`) and **107 `trackid` flight paths**. All tracks have both TRUE and FALSE labels: per original flight 12–219 TRUE, 60–1,095 FALSE. Source field periods `one`/ `two`, source age/sex original recorded. The unmodified GPS source has exactly 8,129 original rows; this should not be inflated into 48,774 biological positions.

**Critical original independent-history hard stop:** 46 original bats have ≥2 separate flight paths, but only **1 bat has ≥3 paths**. The frozen prospective threshold was **≥8 independent bats with ≥3 original flight episodes each**. **The within-individual flight-history prediction is NOT ADMITTED** in this source and no "private cognitive memory" mechanism has been fitted. A source flight is not a single matched decision step.

The original author's PDF dictionary has original UTM `x_,y_` positions EPSG:25833 and wind-turbine/cropland/forest covariates; those coordinates, original bat ring IDs, exact roost positions and original GPS receiver heights were **not accessed or republished** in this Boids analysis. Calibrated 3D movement and social-contact forces were not estimated.

## Source-only environmental format, then a separate frozen bat-heldout model

[Pre-outcome source-only C0 contract](V28_SOURCE_ONLY_TURBINE_LANDCOVER_SCALE_GATE.md) and [passing no-effect CI 40861753381](https://github.com/zuizui0223/boids/actions/runs/40861753381) checked original global environmental data *without case labels*: all 48,774 rows had zero missing and nonnegative finite kilometre distance values. Original wind turbine distance `mindist_WKA_inKm` was **0.002433–7.525411 km**, original assumed roost distance `DistanceAssumedRoostsInKm` **0.000000584–8.576829 km**. Landcover `clc2_20m` has seven source categories, and forest status `forestornot` has exactly `forest` or `others`. The environmental source original units were pinned before ecological effect assessment.

[Distinct fully pre-outcome registered v28-C1 contract](V28_FROZEN_BAT_TURBINE_HELDOUT_PREDICTION.md) then fixed **five entire original bat-ID heldout folds** (`SHA256(batid) mod 5`), train-only feature encoding and standardization, fixed LogisticRegression L2 C=1.0, and equal bat/flight weights. Every bat contributes equal total training weight; every flight within a bat equal; TRUE and generated FALSE within a flight each get 0.5 of that flight's weight. This prevents random points or repeat tracks from dominating as IID biological animals.

Test source compares TRUE (original used) to FALSE (original generated random) **within each flight**, averages flight-level AUC and source-case-balanced log loss within a bat, then averages equally across the 60 original independent bat tokens. No actual 101-step alternatives or prospective future animal choices are claimed.

Three frozen environmental models:
- **MN** reference: random classification, AUC 0.5 and balanced log loss `ln 2`;
- **M0**: source landcover `clc2_20m`, forest status and **log1p assumed roost distance**;
- **M1**: M0 + **log1p nearest wind-turbine distance**, same original feature units;
- **M2**: M1 + **forest status × turbine distance** and **roost distance × turbine distance** predictive interactions.

The **predeclared main test** was M0−M1 balanced log-loss reduction: does turbine distance *alone* add transferable information beyond forest and roost? Source period one/two and sex/age are descriptions, never model predictors or post-result sample selection.

## Actual observed wild bat predictive results — all source bats retained

Original [v28-C1 GitHub Actions CI 40862630762](https://github.com/zuizui0223/boids/actions/runs/40862630762) passed **6/6 pure known-truth and source anti-leakage tests**, all original published source MD5 and SHA256 checks, and all 60 actual bat/107 flight heldouts.

| Predictor | Equal-bat heldout used-vs-random AUC (higher better) | Equal-bat balanced source log loss (lower better) |
|---|---:|---:|
| MN no information | 0.500000 | 0.693147 |
| **M0** forest, landcover and assumed roost distance | **0.608655** | **0.683859** |
| **M1** M0 plus turbine distance | **0.609172** | **0.683792** |
| **M2** M1 plus forest/roost turbine interaction | **0.616311** | **0.679617** |

Individual bat-ID whole-cluster bootstrap **10,000 resamples**, seed `20261029`; all effects retain original source bat equal weights. Positive gains mean better prediction for source original used-vs-generated-random pseudo-availability, **not** observed choices between actual alternative destinations.

| Frozen signed comparison | Equal-bat gain | Positive bats | Whole-bat percentile bootstrap 95% |
|---|---:|---:|---|
| **Primary M0−M1**, added simple nearest turbine distance (balanced loss) | **+0.00006695** | **34/60** | **[−0.0005443,+0.0006821]** |
| Secondary MN−M0, forest/landcover/roost baseline (balanced loss) | **+0.00928780** | **46/60** | **[+0.0061625,+0.0122604]** |
| Secondary M1−M2, forest/roost × turbine interactions (balanced loss) | **+0.00417510** | **38/60** | **[+0.0009918,+0.0074176]** |
| Secondary M1−M0 turbine AUC | +0.0005164 | 27/60 | [−0.0036898,+0.0049531] |
| Secondary M0−MN landcover/roost AUC | **+0.108655** | 55/60 | [+0.08749,+0.12824] |

**Scientific interpretation:** These German source used-versus-random comparisons support **modest environmental predictability beyond uniform sample design**, and **an exploratory positive increment of context interactions**. However the main simple wind-turbine distance increment was **not robust** (34/60, CI crosses zero); the interaction benefit is a *predeclared secondary* and has **not** been adjusted for multiple testing across model comparisons. Hence it does NOT prove a uniform causal turbine avoidance response across species/landscapes or an optimized general mechanism.

The original paper had already observed differing turbine responses near roosts and away from roosts. Our additional evidence is *bat-heldout predictive transfer* of a fixed simple interaction representation within the same original observational field population. It does not add an independent experimental replication of the paper's turbine mechanism.

## Boids theory: use and limitations

- **Motor layer:** Source random-vs-used environmental habitat association does not identify Reynolds separation, alignment or cohesion parameters, flight turning reaction forces or individual social influence.
- **Information layer:** Original bat landscape/roost context helps distinguish source used-vs-random locations, and the predictive value of turbine distance is conditional on forest/roost context in the tested model. The interaction is a model-performance observation, not identification of a cognitive or social policy.
- **Temporal private history:** Hard STOP, only one bat with ≥3 flight paths. Neither sustained individual private memory nor group niche divergence can be tested using this original cohort.
- **Spatial niche / vertical:** Original labels and habitat support are within one German landscape and source availability sampling, not prey resource consumption or independent suitable/unsuitable counterfactual habitats. Raw GPS `Height` is not independently calibrated for vertical ecological niches.

Relative to earlier Boids findings, v23's original Bangladesh duck GPS showed positive *individual previous daily spread* prediction, v24 USGS duckling data showed static sampled wetland ranking but no dated use, and v25 corrected USGS four-waterfowl aggregate habitat profiles showed no transferable added private-history effect. The bat study independently adds environmental-conditional habitat information but cannot make these distinct endpoints a single universal Boids law. Source sampling method, group units and time scales are different.

## Machine-readable results and reproducibility

- [Zenodo original provider metadata, license and file MD5](../validation_v28/results/zenodo_original_bat_source_manifest_v28.json)
- [All three original CSVs verified SHA and 60 bat/107 track ID-only source quality](../validation_v28/results/original_three_bat_CSV_source_gate_v28.json)
- [No-case numeric/km landcover source audit](../validation_v28/results/noctule_source_landcover_turbine_domain_v28.json)
- [Actual full 60 independent bat scores and five folds, every registered model contrast](../validation_v28/results/bat_turbine_landcover_heldout_v28.json)
- Source scripts/tests/workflows `validation_v28/`, `.github/workflows/v28-*.yml`, original registered source/model contracts `docs/V28_*.md`.
- Successful independent CI: [A1 40860616465](https://github.com/zuizui0223/boids/actions/runs/40860616465), [B1 40861335939](https://github.com/zuizui0223/boids/actions/runs/40861335939), [C0 40861753381](https://github.com/zuizui0223/boids/actions/runs/40861753381), [C1 40862630762](https://github.com/zuizui0223/boids/actions/runs/40862630762). First pure-synthetic fixture test stopped only because it originally omitted five original landcover categories; fixture was corrected **before animal numeric effects were opened**, keeping all real source/control/feature/fold rules unchanged.

All original wildlife files were downloaded temporarily only during CI; no ring IDs, UTM roost/flight coordinates, animal exact timestamps, actual sensitive turbine positions or original CSV source rows were redistributed. Original CC BY 4.0 attribution retained.
