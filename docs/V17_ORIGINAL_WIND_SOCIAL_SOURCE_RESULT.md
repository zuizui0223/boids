# v17 independent original-source evidence: 20 pigeons, wind clock uncertainty and explicit observation limits

**Date:** 2026-10-28 JST. **Result:** independent original data-source admission, not an ecological prediction test or observed causal Boids mechanism. v17 has **NO measured turn-prediction gains**. The source gate is complete but the wind-gated social hypothesis remains **NOT ADMITTED**.

## 1. Independent publicly archived dataset, fully verified

Taylor, L. A., Taylor, G. K., Lambert, B., Walker, J. A., Biro, D. & Portugal, S. J. (2019). *Birds invest wingbeats to keep a steady head and reap the ultimate benefits of flying together*, **PLOS Biology** 17:e3000299, [paper DOI 10.1371/journal.pbio.3000299](https://doi.org/10.1371/journal.pbio.3000299). Original source [Zenodo record 5026107](https://zenodo.org/records/5026107), dataset DOI `10.5061/dryad.m7253n8`, provider license **CC0**.

| Original public file | Exact verified byte length | Published MD5 match | Independently computed SHA256 |
|---|---:|---|---|
| `Experiment 1 - GPS data.zip` | **240,056,153** | `499943131e1f6596187cf2a756e3c8dd` | `030e70082b107a353dd4f0afb0cd54868438273a416efac135120a6bdf9c2b29` |
| `Experiment 1 - Weather Data.csv` | **11,529,364** | `1a8c56601ed982a7f2968f1348831317` | `45885ce19954fd99397b92847421d3e11a6ea2c8d22d1a1d6220ea4940fa2917` |

[GitHub Actions source run 40617588626](https://github.com/zuizui0223/boids/actions/runs/40617588626) passed 11/11 source-only tests, verified both files and inventoried the original archive without reading a target GPS turn. This archive is not v8, v15 or v16's data and **none of those frozen empirical results was reopened**.

## 2. Biological sampling grain and actual repeated structure

The original GPS ZIP contains **458 biological CSV files** (all one 18-column Qstarz schema); each filename explicitly encodes a bird ID, four experimental phases and a within-phase release number. A second independently reproducible [source-only schema audit run 40618193722](https://github.com/zuizui0223/boids/actions/runs/40618193722) passed 5/5 tests.

| Source phase (paper's published design) | Original GPS files |
|---|---:|
| Phase 1: solo before paired flights | **120** |
| Phase 2: similar-size paired flights | **120** |
| Phase 3: different-size paired flights | **113** |
| Phase 4: solo after paired flights | **105** |
| **Total** | **458** |

There are **20 distinct bird identifiers**. Nineteen have at least one track in every phase; the source contains 12 IDs with 24 total files, plus missing files in some other IDs. The pre-outcome source-only audit sampled the first 100 rows of 32 deterministic GPS files: all **3,200 samples** had `VALID=FIXED`, all 18 expected headers matched and recorded `UTC DATE`, `UTC TIME`, `MS` were structurally parseable. This is **not** a complete file-by-file quality profile or proof of raw co-time partner synchronization.

These are not 458 independent animals/flocks. The published paper studied **20 pigeons** repeatedly, and the paired treatment creates connected partners and repeated bird identities. We **do not** assume independent pairs from filename or shared GPS time alone. The **original PLOS S3 Table bird-pair ledger has now been independently downloaded, SHA256-pinned and machine-verified**. Its assigned phase-2 and phase-3 dyads form exactly **five four-bird connected social components**, each a C₄ cycle, as documented in [v17-B original graph result](V17_PUBLISHED_PAIR_GRAPH_RESULT.md). The required minimum **eight** independent social components therefore **fails** for this experiment; do not perform the preregistered confirmatory partner forecast on the source.

## 3. Meteorological source time: a concrete identifiability issue

`Experiment 1 - Weather Data.csv` has **152,227 original rows**, no named header, **three numeric columns**. The publication describes timestamp, wind speed and wind bearing, but the last two columns' units/convention must still be checked against original station documentation. Its first numeric column is consistent with **MATLAB serial-day time** rather than an ordinary date string.

The predeclared third [timing-only audit run 40618700050](https://github.com/zuizui0223/boids/actions/runs/40618700050) (5/5 pure no-outcome tests) found:

- All **152,227/152,227** weather serial-day values decode to calendar **2015** under the standard MATLAB serial-day candidate conversion, over **124** unique dates; median positive sample interval **59.999996 seconds**.
- Original GPS UTC date/time/MS was decoded for a fixed first+last-three-record sample of every file, **2,748 timestamps**, **0** parse failures. All movement, positions, headings and speeds were excluded.
- Structural weather-match fractions at ±90 seconds under **predeclared** candidate weather→GPS UTC shifts:

| Candidate weather clock shift | GPS timestamp samples with a nearby original weather measurement | Fraction |
|---|---:|---:|
| Weather shifted **−1 hour** | 2,691 / 2,748 | **97.93%** |
| Weather shifted **0 hours** | 2,748 / 2,748 | **100.00%** |
| Weather shifted **+1 hour** | 2,739 / 2,748 | **99.67%** |

**Critical interpretation:** The near-continuous one-minute weather record makes all three offsets structurally plausible, so source overlap does **not** identify the correct time zone or one-hour weather context. The 100% UTC-source correspondence **must not be selected as the 'true' clock simply because it is numerically highest**. The weather station used Cumulus software in UK summer; original station timezone and any processing to MATLAB serial days need separate documentary corroboration.

This is an **observational-identifiability result** about *what the source allows*, not a measured effect of wind on animals.

## 4. Mathematical ecological context implemented

The repository now includes [pure functions](../validation_v17/context_features.py) to calculate:

- solar azimuth/elevation from **verified timezone-aware UTC** and geographic coordinates with the documented NOAA fractional-year approximation;
- wind tailwind support and signed crosswind relative to the animal's observed heading, **only after wind-from bearing and units are verified**;
- signed bird-heading-versus-sun-azimuth angle.

[8 deterministic tests in CI run 40618948563](https://github.com/zuizui0223/boids/actions/runs/40618948563) passed, including wind-from/wind-to direction, summer solar noon and ambiguous/naive-time rejection. These are **known-truth mathematical unit tests**, not evidence that animals use the solar compass or wind in a particular way. Sun position alone is **not** direct observation of sun visibility, cloud opacity, or an individual's internal clock.

The future falsifiable question is:

> After independently conditioning on own route, sun geometry and *verified* wind, does a measured contemporaneous partner carry a **larger increment in held-out next-turn prediction under one wind context than another**, with entire bird-connected social groups held out?

That requires verified partner assignments and weather time, not merely co-located files.

## 5. Strict current endpoint decisions

| Scientific target | v17 result |
|---|---|
| New original GPS and weather integrity | **PASS**: exact source hashes verified |
| Repeated individual/phase design | **PASS, structural only**: 20 birds, 458 GPS files, four phases |
| Source meteorological calendar format | **PASS, candidate interpretation**: MATLAB serial-day yields 2015; 60-second cadence |
| Weather station absolute timezone / GPS clock join | **NOT IDENTIFIED**; 0, ±1 hours all high source coverage |
| Independently published assigned partner graph | **VERIFIED** from original S3 Table: **five C₄ components, not eight**; preregistered confirmatory gate **FAILED** |
| Measured wind × contemporaneous partner added prediction | **NOT RUN**; eligibility gate not passed |
| Experimental sun-visibility/clock-shift inference from 2019 source | **NOT ADMITTED**: recordings selected for visible-sun releases |
| Animal-specific 3D feeding niches, Reynolds forces, learning mechanism | **NOT TESTED** |

**Most valuable next step:** the PLOS S3 pairing ledger is now verified and establishes **only five independent four-bird networks**, below the predeclared eight-component threshold. Do **not** fit the registered confirmatory v17 wind × neighbor model on this experiment. Obtain an independently replicated social GPS/wind dataset with ≥8 external network units and verify the weather station timezone and wind-direction convention before opening new behavioral outcomes. The original S3 result and its source hash are frozen in [v17-B](V17_PUBLISHED_PAIR_GRAPH_RESULT.md).

## Reproduce source-only receipts

```bash
PYTHONPATH=validation_v17 python -m unittest discover -s validation_v17 -p 'test_source_gate.py' -v
PYTHONPATH=validation_v17 python -m unittest discover -s validation_v17 -p 'test_schema_gate.py' -v
PYTHONPATH=validation_v17 python -m unittest discover -s validation_v17 -p 'test_weather_clock_gate.py' -v
PYTHONPATH=validation_v17 python -m unittest discover -s validation_v17 -p 'test_context_features.py' -v
PYTHONPATH=validation_v17 python validation_v17/source_gate.py
PYTHONPATH=validation_v17 python validation_v17/schema_gate.py
PYTHONPATH=validation_v17 python validation_v17/weather_clock_gate.py
```

These downloads are bounded and temporary. Do not redistribute source animal tracking records. [Machine-readable original-source receipt](../validation_v17/results/source_observability_v17.json) contains only provenance, aggregate counts and explicit blocked endpoints.
