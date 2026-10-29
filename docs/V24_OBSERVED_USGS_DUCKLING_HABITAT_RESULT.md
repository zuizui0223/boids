# v24 original USGS wetlands — static habitat predictability is positive, temporal private history is unidentifiable

**2026-10-29 JST. Source-backed USGS original, new predictive target on independent held-out broods. The originally proposed time-ordered wetland-history study remains NOT_ADMITTED.** This distinction is essential: success in a static environment-only habitat classifier does not rescue or test private memory, flock rules, social interactions or animal resource niche formation.

## Independent source and source checksums

Peterson & Ackerman (2026), *Dabbling Duckling Habitat Use and Movements*, official USGS CC0 data release [DOI 10.5066/P13NYGAI](https://doi.org/10.5066/P13NYGAI), ScienceBase item `68631b39d4be025653d31f22`; associated publication Peterson et al., *Wetland characteristics influence dabbling duckling habitat use and movements*, [DOI 10.1093/ornithapp/duag014](https://doi.org/10.1093/ornithapp/duag014). Suisun Marsh, California, 2016–2019. Original birds: radio-tagged Mallard (*Anas platyrhynchos*) and Gadwall (*Mareca strepera*) ducklings in brood units.

Three original files were downloaded directly through the official source, matched to original USGS published MD5 and independently SHA256-hashed BEFORE habitat model scoring:

| Original file | Exact bytes | Provider MD5 | Independent original SHA256 |
|---|---:|---|---|
| Duckling_Habitat_Selection_Dataset.csv | 7,699,152 | f4bf54ea42490b535f77400fe3308c06 | e4ac32416e2f013efcca8e40b9916e73c72e2e1891a09f78d865524ee16ea036 |
| Duckling_Movement_Dataset.csv | 109,492 | cbcc3c8f6602f5e5df256b6c315f6f5f | 10041a7c04512159e7d9f99a01be1572335264c997bbc1726919de219e8d1c49 |
| duckling_habitat_use_movements.xml | 47,300 | 9787a34e43410a5544cb9b12fedc3cbc | 26f677759eec4859ae7941058bc936b85e942be3e527f9433abc46f9e4dc44b4 |

Original provenance/metadata-source GitHub Actions [A1 40806691670](https://github.com/zuizui0223/boids/actions/runs/40806691670) and full-file/header/FGDC [A2 40806987026](https://github.com/zuizui0223/boids/actions/runs/40806987026) passed tests and recorded the exact source manifests, without fitting animal habitat outcome effects.

## 1. Original future individual wetland-choice history hypothesis FAILED source admission

Original source rows:

- **76,069** habitat-selection rows across **185 brood IDs**: **2,069 actual used-location records** (Used=1) and **74,000 generated available locations** (Used=0), exactly **400 generated points per brood**. Every brood has 1–40 actual used records.
- FGDC metadata state the generated available points were sampled within **2.4 km of the nest** for each radio-tracked brood. They are not verified **actual unchosen wetland sites** or actual choices presented to a duckling.
- All **74,000 generated available rows lack the original discrete Wetland ID** (literal NA; the header is present but no value), whereas observed used rows have wetland IDs. Original 89/185 broods visited at least two distinct mapped wetland IDs across the study.
- **Habitat-use rows have Year and hatch-associated Water Map Time Period, but NO visit date or duckling age per used location.** The water map period is a single temporal habitat map aligned with brood hatch period, not an observed sequential timestamp for visits.
- The companion **2,039-row movement file** has **188 brood IDs** and Duckling Age / Distance from Nest, with 185 IDs in common and 3 movement-only broods, but **NO Wetland ID or environment attributes**. Joining only on Brood ID would create spurious many-to-many "visits" and is disallowed.
- Therefore **zero genuine dated future wetland-choice events** can be admitted from the deposited two tables. The original [v24 preregistered time-history contract](V24_USGS_ORIGINAL_USED_AVAILABLE_SOURCE_CONTRACT.md) required at least eight broods with ≥3 ordered used-choice dates and ≥200 future matched choice sets; **NOT_ADMITTED_NO_DATED_WETLAND_CHOICE_OR_MATCHED_TEMPORAL_AVAILABILITY** is the scientifically necessary endpoint. [Original source-only structural evidence and corrected literal-NA parser, CI run 40807540242](https://github.com/zuizui0223/boids/actions/runs/40807540242).

This is not evidence that ducks lack cognitive wetland memory; it is a real source-identifiability constraint.

## 2. Separately preregistered static environmental-choice transfer

After establishing the *absence* of visit chronology using metadata only, a distinct [v24-S static habitat transfer prediction protocol](V24_FROZEN_BROOD_HELDOUT_STATIC_HABITAT_CHOICE.md) was committed BEFORE inspecting the actual numerical wetland environmental attributes or any habitat-model prediction scores.

This new, more limited question is **whether wetland ecological attributes rank observed brood-use locations above originally GENERATED available points for entirely new brood IDs, including broods from different years**. It does not claim to predict what a brood chooses tomorrow.

**Frozen source/independence and features:**
- Each of the 185 original brood IDs is one independent statistical unit (not 76,069 rows or 2,069 independent animals).
- Test data are separated by whole brood via source-only stable SHA256 modulo-five folds; all 185 broods get out-of-brood predictions. The source's original 400 availability points per brood are kept as a fixed matched sample.
- Environmental features: wetland flooding type, dominant vegetation category, vegetation cover percent, salinity, flooded wetland area. Categorical one-hot encoding, numeric log1p area/salinity and training-brood-only standardization/imputation. No original brood ID, wetland ID, source Used response, coordinates or arbitrary original Weight enters the predictor. Model uses fixed L2 logistic regression C=1.0, with per-brood balanced used/availability sample weights (each brood contributes equally).
- **M0 uniform no-habitat information**: within-brood discrimination AUC 0.5, pseudo-choice log loss ln(401)=5.993961 nats.
- **M1 fixed ecological attributes**: out-of-brood model trained on other assigned brood folds only.
- **M2 optional predeclared species×habitat interactions** with same training controls and fixed regularization, to test whether extra complexity transfers.
- Main metric: original heldout **brood-equal within-brood AUC** comparing original used records to each of its 400 originally generated available points, with 10,000 whole-brood bootstrap samples (seed 20261029). This is sampled used-versus-available ranking, NOT a calibrated probability of a genuinely observed set of 401 wetlands.
- Secondary sample-defined pseudo-choice log loss: at each original used point, its model score versus that point plus the original 400 sampled controls; average observed used points within brood, then equal-weight original broods. This metric is explicitly **not real-time 401-wetland navigation choice likelihood**.
- Separate four **predeclared leave-one-entire-year-out** validations; each train on the other 3 original calendar years only, without choosing a favorable year post-outcome.

Full [original GitHub Actions 40808140284](https://github.com/zuizui0223/boids/actions/runs/40808140284) successfully completed **8/8 synthetic source independence/known-truth tests** before source model evaluation, exact original MD5+SHA and all 5 heldout folds + all 4 entire-year folds. No test brood rows were used in training.

## 3. New heldout-brood static habitat prediction result

| Predictor, tested on 185 unseen source broods | Brood-equal AUC (higher better) | Mean sampled pseudo-choice log loss (lower better) |
|---|---:|---:|
| **M0 uniform generated availability** | 0.500000 | 5.993961 |
| **M1 wetland habitat attributes** | **0.612653** | **5.911347** |
| M2 wetland attributes + species interactions | 0.600246 | 5.923284 |

| Predeclared comparison | Equal-brood gain | Positive original broods | Whole-brood bootstrap 95% |
|---|---:|---:|---|
| **Primary M1 AUC − uniform 0.5** | **+0.112653** | **126/185** | **[+0.080543,+0.144126]** |
| M0−M1 pseudo-choice log-loss reduction (nats) | **+0.082614** | **121/185** | **[+0.031434,+0.132769]** |
| M2 AUC − M1 (added species interaction) | −0.012407 | 78/185 | [−0.025927,+0.001682] |
| M1−M2 pseudo-choice log-loss reduction | −0.011937 | 85/185 | [−0.034238,+0.010470] |

**Primary source-backed conclusion:** Five original wetland environmental attributes have *transferable sampled used-versus-generated-available ranking information* across withheld radio brood IDs within the same original Suisun Marsh landscape. This does **not** establish a universal resource-selection mechanism, nor imply that one brood's prior wetland use improves next-day choice. Adding species-specific habitat interactions did **not** improve the tested out-of-brood predictor on average.

### Entire original study-year holdouts

| Entire original heldout year | Source independent test broods | M1 AUC | M1 pseudo-choice log loss | Baseline pseudo-choice log loss |
|---|---:|---:|---:|---:|
| 2016 | 39 | 0.582852 | 5.922724 | 5.993961 |
| 2017 | 47 | 0.609249 | 5.914637 | 5.993961 |
| 2018 | 38 | 0.548169 | **6.010489 (worse)** | 5.993961 |
| 2019 | 61 | 0.609578 | 5.907891 | 5.993961 |

Every year had AUC numerically above 0.5, but **2018 lost predictive sampled pseudo-choice log-loss transfer**, demonstrating temporal fragility in probability ranking. Four years in one marsh are not four independent ecological regions; no claim of broad climatic generality.

**After-outcome descriptive species-only counts (not new confirmation):** 118 Mallard broods (1,342 used points), mean 5-fold M1 AUC 0.6204; 67 Gadwall broods (727 used points), mean M1 AUC 0.5990. Both are from the same landscape and original field protocol. Do not treat the AUC difference as an independently tested species effect; M2 species interaction CI includes zero.

## 4. Scientific boundaries and Boids relevance

This v24 source supplies **static original habitat condition and generated nest-accessible spatial availability** but no actual visit timestamps for the selected wetland records. It is suitable for testing transfer of environmental preference ranking in an original source landscape, while **not** suitable for testing transfer of an individual's private temporal history into later habitat choices. The 2,039 original radio-tagged movement records quantify duckling age and nest distance but cannot be linked to habitat use chronologically by wetland ID.

The original Peterson et al. 2026 published paper already reported selective use of semi-permanent wetlands and lower salinity/intermediate vegetation cover. The new v24-S contribution is a **pre-outcome registered brood-/year-heldout predictive benchmark** on original authors' data, *not* rediscovery of their fitted coefficients. Source available points were computer-generated within 2.4km of nests; no recorded prey intake, food availability, nest-level detection bias or independent resource patch choices were measured.

Relative to the frozen previous results:
- **v23** new original wild Bangladesh duck GPS plus prior-day gridded ERA5: private past daily movement spread predicted tomorrow's extent better than other ducks' historic weather bins, 49 birds / 2664 individual-days; this is movement magnitude, not habitat selection.
- **v24** independent California mallard/gadwall broods: wetland attributes predict *static sampled used-versus-generated-available* status in 185 heldout brood units, but no dated individual use history is available.
- The two tests do NOT identify a single observed mechanism connecting memory to habitat selection. Different cohorts/ages, target variables, source availability and study continents prevent equating their numerical effect sizes.

No original simultaneous flock contacts, Boids separation/alignment/cohesion steering coefficients, experimental private reward/learned policy, 3D niches or interspecific resource competition were recovered. A future independent study must include true temporal used/available wetland sets per marked animal, habitat resource measurements and actual group-contact data to connect these levels.

## Reproduction and source receipts

- [USGS original source manifest](../validation_v24/results/sciencebase_source_a1.json)
- [Original three source SHA256, 12-column choice/6-column movement FGDC scheme](../validation_v24/results/duckling_source_a2.json)
- [Exact no-future-wetland-choice-chronology identifiability result](../validation_v24/results/used_available_temporal_design_v24.json)
- [185-brood anonymized environmental AUC/log loss, five-fold source-groups, four heldout years](../validation_v24/results/static_brood_habitat_preference_v24.json)
- Source parser and schema tests: `validation_v24/`, with registered source and prediction contracts under `docs/`.
- Successful CI: [manifest A1 40806691670](https://github.com/zuizui0223/boids/actions/runs/40806691670), [original MD5+FGDC A2 40806987026](https://github.com/zuizui0223/boids/actions/runs/40806987026), [temporal stop A3 40807540242](https://github.com/zuizui0223/boids/actions/runs/40807540242), [real static habitat heldout benchmark 40808140284](https://github.com/zuizui0223/boids/actions/runs/40808140284).

**Original USGS files, radio brood IDs, nest coordinates, wetland numeric rows and observed target locations are not redistributed.** All earlier v13-v23 source/results stay frozen.
