# v25 — Original waterfowl habitat profile source, source-scale artifact and corrected exploratory prediction

2026-10-29, original Masto 2024 Tennessee Dryad source and independent Overton/Casazza 2023 USGS data.

## Correct original source/data integrity

1. Independent Masto et al. Tennessee Mallard Dryad DOI `10.5061/dryad.cjsxksnd5`: original RDS `EAP23-0437_data.rds` 16,087,819 bytes, provider-published SHA256 `4e15093e166bdc14fa6d649ad91977839308c749a1e3fe14698fa80745511d75`, README 3,294 bytes provider SHA256 `77b4b9baeea3e57833bc279da6ddeb942156524dd9ecbb84ec921e605e65c726`; original provider license CC0 and version 4 verified, but original RDS bytes returned HTTP401/403, **NOT_ADMITTED and no habitat prediction on this source**. [Original source metadata receipt](results/tennessee_dryad_source_a1.json).
2. New actual USGS Overton & Casazza waterfowl 2023 DOI `10.5066/P9ELSUHN`, four source taxa, original `Data Release P9ELSUHN.csv`, **27,997,528 bytes**, published MD5 `78eb6064eca992225d6907d6e46f5bef` independently matched; SHA256 `1a5c2342f9df4c70f170741c14b92b5146f0558f29fd593307768a228b82ca15`. Source has **190,289 original paired TRUE/FALSE habitat summary keys, 493 original `birdyear` tokens**, 380,578 rows; **NOT 100 original alternative destination rows per recorded step**, despite original movement model using 100 simulated steps. [Original source quality](results/usgs_step_strata_v25.json).
3. USGS separately offered 26,316-byte FGDC XML but actual byte MD5 `b159ed...` differed from published `170cf7...`. This original metadata file is NOT VERIFIED; no claim of original FGDC integrity success. [Original FGDC audit](results/usgs_fgdc_original_v25.json).

## Most important finding: bogus 100% rank was source unit mismatch

- Original v25-C assumed all habitat predictors already [0,1] and STOPPED before fitting, because original `Corn` had values >1. [Frozen honest source stop](results/frozen_original_unit_stop_v25C.json).
- Source-only v25-D0 (without case labels) found all 7 numeric fields [0,100], registered global /100; **new exploratory v25-D1** scored original data and all M1/M2/M3 source TRUE-vs-FALSE ranks were artificially **100%**, suggesting source construction bias.
- Explicitly **post-outcome v25-E** discovered original TRUE row is **ONE used category encoded 1 or 2**; original FALSE row has **100 simulated alternatives' counted habitats** with total 100 in 189,989/190,289 rows and >100 in 300. TRUE total=1.00172 mean, FALSE total=100.10043 mean. Every FALSE vector had larger sum, Euclidean norm and max than its TRUE pair. **The global /100 of both cases was WRONG and v25-D results are INVALID FOR ECOLOGY**. [Source-construction audit](results/postresult_source_artifact_v25E.json).
- New, explicitly AFTER-outcome source-case correction **v25-F** represented TRUE as one-hot observed habitat category and FALSE as 100 simulated-step class counts /100, retaining all 190,289 source pairs and the 328 used rows with original raw code2; reuses untouched v25-C modeling and support.

## The corrected v25-F limited source-derived result

Whole `birdyear` heldout 5-fold source model, 492 eligible original tokens (one fewer than 493 because first 3 pairs needed) and **188,812 later source profiles**. All model loss values are **paired-profile retrospective surrogate log loss**, not real future destination choice probability or a 101-alternative step-selection likelihood. Units are properly matched original source category indicators versus generated candidate frequencies.

| Model | Equal-birdyear surrogate log loss | Paired-source rank fraction |
|---|---:|---:|
| M0 null source pair | 0.693147 | 0.5000 |
| M1 pooled habitat slope | 0.602916 | 0.8145 |
| M2 habitat + species slope | **0.595042** | **0.8161** |
| M3 M1 + past same-birdyear habitat history, w=n/(n+2) | 0.611741 | 0.7476 |

- **Primary past individual-history increment M1−M3 = −0.008825**, **196/492** positive, whole-birdyear bootstrap **[−0.018191,+0.000810]**: **NOT SUPPORTED** on this source surrogate, not evidence that animals lack biological memory.
- General environmental source-profile increment M0−M1 **+0.090231**, **420/492**, bootstrap **[+0.079754,+0.100476]**; a positive source-surrogate ranking effect, **not prospective habitat-choice prediction**.
- Source taxon interaction increment M1−M2 **+0.007875**, **310/492**, 95% **[+0.004963,+0.010909]**; four taxa share same original region/method/availability generator.
- All original 2015–2023 calendar year holdouts yielded environment-only source surrogate loss below null `ln2`, but the original published simulated movement kernel used full-study tracking and source temporal labels are not independent future habitats.

**No causal cognitive memory, actual prey consumption, true resource niche partition, social partner network or Boids force is measured by v25.** The v23 original wild duck result was about tomorrow's daily GPS movement spread, NOT habitat choice. The original v24 brood static environmental predictor supports sampled habitat rank but not time-ordered individual history. v25 shows source data representation can produce artificial apparently perfect prediction if the TRUE/FALSE scales are not matched.

## Reproduce

```bash
python -m pip install 'numpy>=1.26,<3' 'pandas>=2,<3' 'scikit-learn>=1.4,<2'
PYTHONPATH=validation_v25 python -m unittest discover -s validation_v25 -p 'test_source_manifest_gate.py' -v
PYTHONPATH=validation_v25 python -m unittest discover -s validation_v25 -p 'test_usgs_step_manifest_gate.py' -v
PYTHONPATH=validation_v25 python -m unittest discover -s validation_v25 -p 'test_usgs_step_strata_gate.py' -v
PYTHONPATH=validation_v25 python -m unittest discover -s validation_v25 -p 'test_source_numeric_unit_gate.py' -v
PYTHONPATH=validation_v25 python -m unittest discover -s validation_v25 -p 'test_unit_corrected_profiles.py' -v
PYTHONPATH=validation_v25 python -m unittest discover -s validation_v25 -p 'test_postresult_source_artifact.py' -v
PYTHONPATH=validation_v25 python -m unittest discover -s validation_v25 -p 'test_case_specific_source_profiles.py' -v
PYTHONPATH=validation_v25 OPENBLAS_NUM_THREADS=1 python validation_v25/case_specific_source_profiles.py
```

The original results/receipts and all source integrity checks are in `validation_v25/results/`; full narrative and scientific limits in [v25 result](../docs/V25_OBSERVED_SOURCE_CORRECTION_AND_HABITAT_PROFILE_RESULT.md). Downloaded original tracking data are temporary and not redistributed in the repository. Original source-only/real-data GitHub Actions runs: 40825659679, 40826027315, 40826264476, 40827753426, 40828633631, 40840767213, 40841206422, 40841863363, 40842443398.
