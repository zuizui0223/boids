# v24: Original USGS Suisun Marsh brood wetland source and sampled habitat choice benchmark

Original 2026 USGS CC0 data release DOI 10.5066/P13NYGAI, ScienceBase 68631b39d4be025653d31f22, 2016–2019 radio-tracked Mallard and Gadwall ducklings.

All 3 original USGS files were actually downloaded through ScienceBase, exact publisher MD5 verified, and SHA256 computed. Habitat source Duckling_Habitat_Selection_Dataset.csv (7,699,152 bytes, SHA256 e4ac32416e2f013efcca8e40b9916e73c72e2e1891a09f78d865524ee16ea036) contains 76,069 rows: 2,069 observed used and 74,000 GENERATED available points within 2.4km of the brood's nest, exactly 400 available for each of 185 original broods. Movement source Duckling_Movement_Dataset.csv (109,492 bytes, SHA256 10041a7c04512159e7d9f99a01be1572335264c997bbc1726919de219e8d1c49) has 2,039 age/distance rows from 188 brood IDs (185 shared with habitat source).

## Distinct scientific endpoints

The originally intended **prospective private wetland revisit-history comparison is NOT_ADMITTED**. The source habitat table has no recorded visit date or duckling age for any used wetland location; the source movement table has ages but no Wetland ID, and all 74,000 generated available points have Wetland ID NA. A join on brood alone is many-to-many and cannot create real dated choices. The source supports neither a future individual wetland preference target nor a measured social history. This is not a biological negative effect.

A separate static habitat-generalization analysis was registered **after finding this source time absence but before opening numerical habitat covariates**. The fixed models are:
- M0: uniform sampled availability, AUC=0.5 and sampled pseudo-choice log loss ln(401) = 5.993961 nats.
- M1: L2 logistic environmental ranker trained on wetland flooding type, dominant vegetation category, percent cover, salinity and flooded wetland area; original brood-equal balanced sample weights, fixed L2 C=1.0; no original brood IDs, wetland ID or published Weight as predictors.
- M2: M1 with source species-by-habitat interactions, fixed same preprocessing/regularization.

Hold out **ENTIRE original radio broods** in five deterministic source-ID-only SHA256 folds. Score all original used points against that brood's 400 originally generated available points, average first within each brood, then equally over 185 broods. Secondary original four entire-year holdouts (2016–2019), training on remaining three years. No future trajectory prediction is claimed by these static scores.

## Verified real result — exploratory

All source and model tests passed CI run 40808140284. Equal-original-brood AUC: M0 0.500000, M1 0.612653, M2 0.600246. Primary M1−M0 **+0.112653**, **126/185 broods** positive, whole-brood 10,000-sample 95% bootstrap **[+0.080543,+0.144126]**. Source-sampled pseudo-choice log loss baseline 5.993961 vs M1 5.911347 (gain +0.082614 nats, bootstrap [0.031434,0.132769]). M2 species interactions DID NOT yield a robust incremental gain (AUC difference −0.012407, CI [−0.025927,+0.001682]).

Entire-year heldout M1 AUC: 2016 0.582852; 2017 0.609249; 2018 0.548169; 2019 0.609578. Importantly original 2018 pseudo-choice log loss 6.010489 was WORSE than 5.993961 uniform baseline, so the result is not uniformly year-transferable in calibrated choice ranking.

**Do not interpret 400 generated available points as 400 genuinely offered unique wetlands or independent animals.** Original paper already reports environment-related habitat selection; the added result is BROOD-/YEAR-heldout prediction of sampled used-vs-available features within one Suisun Marsh source landscape. No individual memory, social Boids motor force, prey fitness, real habitat resource intake or 3D niche was measured.

## Reproduction

Original source-only audits:
- sciencebase_source_gate.py (metadata/DOI/license/files only)
- source_file_schema_gate.py (exact original MD5+SHA256, CSV column names and FGDC definitions only)
- used_available_temporal_gate.py (original brood/no-date nonidentifiability)

Source-only CI: 40806691670, 40806987026, 40807540242 (all successful).

Static real-data model: static_habitat_transfer.py and test_static_habitat_transfer.py (eight synthetic known-truth tests before habitat scores). Real CI: 40808140284.

Run with Python 3.11, numpy 1.26–2.x, pandas 2.x, scipy 1.11–1.x, scikit-learn 1.4–1.x. Set PYTHONPATH=validation_v24 before invoking the scripts; the code downloads exact public USGS source files into temporary runtime directories and writes only deidentified aggregate results.

Full original source-backed scientific discussion: docs/V24_OBSERVED_USGS_DUCKLING_HABITAT_RESULT.md. Original manifest/source schema/static metrics: results/sciencebase_source_a1.json, results/duckling_source_a2.json, results/used_available_temporal_design_v24.json, results/static_brood_habitat_preference_v24.json.

Earlier v13–v23 original field/synthetic results remain frozen and separately interpreted. Future independent real history/niche research requires actual dated individual wetland use and contemporaneous used-and-available habitat opportunities, not reconstructed history from multiple original tables without join keys.
