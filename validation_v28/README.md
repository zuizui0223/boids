# v28 — independently published common noctule bat original GPS/RSF, habitat context and wind turbines

Original Reusch et al. (2023) Current Biology DOI 10.1016/j.cub.2022.12.050, open [Zenodo 7535030](https://zenodo.org/records/7535030), original CC BY 4.0. All three original published CSVs fully downloaded, exact Zenodo MD5+bytes and independent SHA256 checked. Original source model has **8,129 original used GPS fixes + 40,645 author-generated random points**, from **60 independent bats across 107 flight paths**. All bat-ID tokens occur in original capture ledger and GPS records. **Only one bat has 3+ flights**: the preregistered independent repeated-bat private-history gate **FAILS**. No new memory/social-Boids effect is fitted.

## Distinct ecological predictor (registered BEFORE bat-case numeric values)

Within each source flight, compare true used versus author-sampled random locations. Train L2 logistics C=1.0 on other bats, 5 bat-ID SHA256 holdouts; each bat equal training and test weight, each flight within bat equal weight, and used/random within flight balanced. Source-only global km distance and landcover category validation (48,774 source rows, zero missing; 7 landcover classes) passed before model outcomes.

- MN source-random baseline balanced log loss **0.693147** (AUC .5000)
- M0 original landcover + forest + assumed roost distance **0.683859** (AUC **.608655**)
- M1 M0 + nearest turbine distance **0.683792** (AUC **.609172**)
- M2 M1 + forest/roost × turbine distance interactions **0.679617** (AUC **.616311**)

**Frozen primary simple turbine increment** M0−M1 **+0.00006695** mean balanced log-loss gain, **34/60** bats positive, whole-bat 10,000 resamples 95% **[−0.000544,+0.000682]**: **NOT supported as a general improvement**. **Fixed secondary interaction** M1−M2 **+0.004175**, **38/60**, 95% **[+0.000992,+0.007418]**: exploratory positive conditional prediction, not multiplicity-corrected or a causal turbine response. Original M0 forest/roost vs random gain +0.009288 (46/60, 95% [+0.006163,+0.012260]).

Scientific limits: original 40,645 random points are not independent original bats or discrete offered choices, 107 tracks nested in 60 bats, no actual synchronized co-movement or resource reward measurements, no calibrated GPS height/3D ecological niche. Original authors already reported turbine-distance patterns near and away from roosts; Boids adds bat-heldout predictive tests within the same source landscape, **not independent field replication of causal wind effects**.

## Reproduce with original source hashes

Install Python 3.11, `numpy>=1.26,<3`, `pandas>=2,<3`, `scikit-learn>=1.4,<2`.

Run from repository root:

```bash
PYTHONPATH=validation_v28 python -m unittest discover -s validation_v28 -p 'test_original_source_manifest.py' -v
PYTHONPATH=validation_v28 python -m unittest discover -s validation_v28 -p 'test_three_file_source_gate.py' -v
PYTHONPATH=validation_v28 python -m unittest discover -s validation_v28 -p 'test_source_landscape_domain.py' -v
PYTHONPATH=validation_v28 python -m unittest discover -s validation_v28 -p 'test_bat_wind_heldout.py' -v

PYTHONPATH=validation_v28 python validation_v28/original_source_manifest.py
PYTHONPATH=validation_v28 python validation_v28/three_file_source_gate.py
PYTHONPATH=validation_v28 python validation_v28/source_landscape_domain.py
PYTHONPATH=validation_v28 OPENBLAS_NUM_THREADS=1 python validation_v28/bat_wind_heldout.py
```

Original CI source A1 40860616465, B1 40861335939, C0 40861753381, observed model C1 40862630762; all succeeded with independent original files. Original full scientific paper-style report: `docs/V28_OBSERVED_NOCTULE_WIND_CONTEXT_RESULT.md`, exact anonymized independent source and model JSON receipts in `validation_v28/results/`. No original animal IDs, roost coordinates or source raw GPS are redistributed.
