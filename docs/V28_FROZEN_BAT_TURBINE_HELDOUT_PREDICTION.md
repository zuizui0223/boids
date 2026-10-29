# v28-C1 — Frozen independent-bat-heldout turbine-context habitat prediction

**Registered 2026-10-29 JST AFTER the original v28-A1/B1 source and v28-C0 global covariate *source-only* audits, BEFORE reading any original TRUE/FALSE-associated habitat numerical data or fitting a new bat ecological predictor.** This is a separate, limited original-bat environmental predictability test, NOT a private-memory or Boids-neighbor experiment. All prior v13–v27 findings remain frozen.

## Exact original source and auditable independent units

Reusch et al. (2023), *Wind energy production in forests conflicts with tree-roosting bats*, [paper DOI 10.1016/j.cub.2022.12.050](https://doi.org/10.1016/j.cub.2022.12.050), original public CC BY 4.0 [Zenodo DOI 10.5281/zenodo.7535030](https://doi.org/10.5281/zenodo.7535030).

Source file `Model_dataset_RSFFlight_Complete_EPSG25833.csv` **17,582,302 bytes**, published MD5 `fb0d7967d552b855ab530eeedcede7ff`, independent SHA256 `76f92b1442eb4350ee6d83ede83b5e43fda4b9f3997e3fd9a3618a44f2470375`. Observed raw GPS/source ledger matched full MD5 and all 60 source bat ring-number IDs. Source contains **48,774 RSF pseudo-locations: 8,129 TRUE used positions, 40,645 FALSE author-generated random positions** from **60 original bat IDs and 107 source `trackid` flight groups**. All 107 tracks contain used and random classes; none contains only one TRUE (12–219 used and 60–1095 generated random points per track). **The source provides flight-level random-location reference, NOT individually matched chosen/not-chosen step alternatives.**

Original source-only v28-C0 [data-domain CI](https://github.com/zuizui0223/boids/actions/runs/40861753381) verified, **without inspecting case labels**, that two exact source km fields have finite nonnegative entries and zero missing:
- `DistanceAssumedRoostsInKm` range **0.000000584–8.576829 km**, source grid to *assumed* roost.
- `mindist_WKA_inKm` range **0.002433–7.525411 km**, source nearest wind turbine.
- `clc2_20m`: seven exact categories `forest, agricultural areas, meadows, water, wetland, shrubs and bushes, city area`, zero missing.
- `forestornot`: `forest` / `others`, zero missing.
These exact features are the ONLY response predictors below. Source `case_`, `response_rvso`, `trackid`, `batid`, `move_state`, original UTM GPS coordinates, source age and sex are **not predictors**; source `field_period` only for descriptive audits.

## Honest scientific target and source design

**Task:** For an original *unseen bat*, can **wind-turbine distance** improve retrospective discrimination of real observed GPS positions from source-author-generated random habitat positions **beyond land cover and assumed-roost distance**?

The random positions come from the source's availability sampling protocol and are not directly seen as options by a bat. A positive result is predictive information about *source RSF used/random labels* within this original landscape, not cognitive memory, a transferable physical Boids motor force, cause of turbine avoidance or individual fitness. No 3D altitude inference. Only **1 bat has ≥3 flights**: the previously preregistered ≥8 independent repeated-history gate definitively FAILS. No individual-history predictive model will be fitted to rescue that result.

## Frozen training and independent evaluation

- Original independent evaluation unit: the entire original `batid` token, not flight points, GPS fixes, random points, dates, or wind turbines. Fixed **5 bat-ID-only folds**: `SHA256(UTF8(batid)) mod 5`; no row from a heldout bat in train or train preprocessing.
- Original `trackid` is a **flight**; used/random source points within a flight may share sampling regions. Model training gives **every bat equal total weight**, within bat every original flight equal weight, within flight TRUE and FALSE each half its weight: point weight = `0.5/(n_flights_bat * n_points_in_this_flight_and_case)`. Thus never treat 40,645 generated alternatives as 40,645 independent animals. Each of the 60 bats must have ≥1 source track with both classes and total ≥10 TRUE/40 FALSE; original B1 already verified ≥12 TRUE and 60 FALSE for each track. If any fails or original source has missing numeric/categorical fields, STOP.
- Fixed habitat-only **M0**: OneHotEncoder `clc2_20m` (seven original classes, handle_unknown ignore) plus `forestornot` (two classes) plus **`log1p(DistanceAssumedRoostsInKm)`**, training-bat-only standardization (mean, SD) for the numeric roost-distance field.
- Fixed **M1**: add **`log1p(mindist_WKA_inKm)`**, standardized using training bats only, preserving same landcover/roost terms as M0. NO arbitrary distance threshold optimized from original results.
- Fixed **M2 exploratory context**: add interaction **forest indicator × standardized turbine distance** and **standardized roost distance × standardized turbine distance** to M1. Forest indicator exactly `forestornot == "forest"`. This is a predictive context interaction, not proof of environmental causation.
- All three use `LogisticRegression` L2 penalty, fixed `C=1.0`, solver liblinear, max_iter 400, random_state 20261029; *no source-selected hyperparameters or fit on test cases*.
- Baseline **MN** uniform chance: within flight true/random AUC 0.5, class-balanced log loss ln2.
- For each original heldout **flight**, compute TRUE versus FALSE within-flight ROC AUC and **balanced log loss** = 0.5 mean used `−log(p)` + 0.5 mean generated available `−log(1−p)`; then equal average across flights within each independent bat, and finally equal-average across the **60 independent bat tokens**. Do not compute a pseudo-choice log loss over 101 choices or claim a step direction was predicted.
- Main registered benefit `G_turbine = L(M0)−L(M1)`, positive means wind turbine distance adds out-of-bat conditional information beyond original landcover/roost context. Registered secondaries: `L(MN)−L(M0)` habitat context versus chance; `L(M1)−L(M2)` interaction versus simple wind distance, and AUC differences for each on **same bat/flight support**. Report all negative outcomes.
- Whole bat **10,000 resample** bootstrap percentile 95% interval, fixed seed 20261029, source positive bat counts. All original 60 bat IDs and 107 flights retained. Original field period one/two and original sex/age for descriptive bat-level distributions only; do not treat two periods as independent populations or post-hoc tuning strata.

## Scientific guardrails

Original random positions are defined by authors' source sampling scheme and can be correlated with used/available spatial context. A classification benefit **does not demonstrate that bat neural/social memory chooses wind farms**, or a causal wind turbine risk preference. Original paper already reported near-roost turbine activity and distant turbine avoidance; a new incremental heldout-bat predictive contrast is a distinct evaluation endpoint, not a novel empirical experiment. No same-moment bat-to-bat interaction or vertical GPS accuracy is measured by this RSF model.

If the primary confidence interval includes zero or goes negative, retain that as a frozen negative/null source result. Do not retune the turbine distance transform, change number of heldout bats, reweight source cases, select only advantageous ages/field periods, or broaden to >3-flight memory after opening effects.
