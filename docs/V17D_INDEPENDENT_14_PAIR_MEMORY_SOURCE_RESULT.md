# v17-D observed-source result — 14 independent homing-pigeon pairs and 426 GPS tracks (no forecast fitted)

**2026-10-28 JST. Source-first provenance and repeated-pair admission is COMPLETE. No new memory mechanism or predictive effect is claimed.**

## Original independent 2026 research source and checksums

Morford et al. (2026), *Collective route memories emerge through differential forgetting of navigational information in homing pigeons*, *Scientific Reports*, DOI [10.1038/s41598-026-39898-2](https://doi.org/10.1038/s41598-026-39898-2). Original authors' [public GitHub repository](https://github.com/Morfordjoe/Collective-route-memories-in-homing-pigeons), pinned author commit `8e4f7e48abfa57212c5207c28580003f0ef14210` (2025-05-22).

The complete bounded original records were **actually downloaded by CI**, verifying both exact source file lengths and Git blob SHA1 (not confusing Git blob IDs with plain-file SHA1) and independently computing SHA256:

| Original file | Verified bytes | Original Git blob SHA1 | Independently computed SHA256 |
|---|---:|---|---|
| `CM info.csv` | **348** | `8c607d535e549fb72f0863b616e28cac24d031f7` | `8796f115d80f13b455704a2ad4c8710e23b18103ab0ba6d913c553fbd7342279` |
| `CM_trimmed.zip` | **21,425,810** | `0b1bd66f08c1cac5f8ca582f289d49c43f553bfa` | `8e3f588ae927ab196f8c9dc9eebc9146bf656b344e68db8ba5f3c20d49edc3dc` |

[GitHub Actions run 40625385833](https://github.com/zuizui0223/boids/actions/runs/40625385833) succeeded, **5/5 offline structural/anti-leakage tests** and raw source download/structural gates passed. [Source parser](../validation_v17/fourteen_pair_source_gate.py), [tests](../validation_v17/test_fourteen_pair_source_gate.py) and [machine-readable pinned receipt](../validation_v17/results/2026_fourteen_pair_source_audit.json) are in this repo. No bird GPS trajectory row, animal location, course, or future memory test result was read or redistributed.

## Original experiment topology: 14 actual independent assigned pair components

The author-pinned `CM info.csv` defines `Bird, Partner, Pair_ID, Additional_training_site`. The full roster has exactly **14 different named pairs and 28 unique bird IDs**, with **no bird assigned to more than one pair**; hence the externally recorded pair-membership graph contains **14 disconnected two-bird components**.

- Seven pairs have `Additional_training_site=LH`; seven have `SH`. These denote the original extra-training assignment sites and **do not make 28 independent site-level experiments**.
- The published protocol compares paired versus solo navigation under training and memory test phases at two release sites, and differences in experience over delayed testing. **The original authors' reported scientific effects are literature context, not newly fitted results**.
- This source exceeds the strictly preregistered minimum **≥8 independent social connected units** that the 2019 Taylor et al. experiment failed with only five C₄ components. The new source meets the **membership gate**, but has not passed GPS clock, real co-observation, environmental, functional niche or forecast-prediction gates.
- Complete pair IDs and members are in the JSON receipt; no source animal measurement values or GPS fixes are included.

## GPS file structure, supported and missing measurements

The pinned GPS ZIP expands to **435 regular files**, including **426 original CSV tracks** (six extra CSV entries excluded by the source-only sampling grammar), plus miscellaneous metadata. The 32 deterministically sampled CSV headers have **one matching 18-column format**:

`Time, Region, Local.Time, Latitude, Longitude, Altitude.m., Speed.km.h., Course, Distance.m., Visible.Satellites, Satellites.CN.22., HDOP, DT, DistHome, site, DistRS, round, check`.

Filename patterns independently indicate bird identity, `Site_LH`/`Site_SH`, `pair`/`solo`, `TR` training and `CM` memory-testing, and dated release episodes (for example `15-X40_Site_LH_pair_Nocheck_CM_2024-08-16 09:36:05.csv`). These are original source declarations, NOT proof of physically synchronized paired flight fixes or a predictive behavioral effect.

- `DT` exists and the original author's R script interprets it as UTC. **Actual raw datetime consistency, duplicate timestamps, precision, simultaneous partner coverage and potential GPS interpolation** still require a new source-only check.
- `Altitude.m.` exists but cannot be used for a credible 3D ecological niche without documented GPS/geoid vertical accuracy and the source error process.
- `Speed.km.h.`, `DistRS` and `DistHome` are derived track fields, and measured movement outcomes must not be used as instantaneous predictors unless they would actually be available at decision time.
- No source-specific weather station/recorded wind context was confirmed. Thus this study is a candidate for **slow navigation-route history**, NOT currently a test of v17 wind×current-social information.
- The original author GitHub repo does not advertise a root-level `LICENSE`; verify track-level data reuse permissions before redistribution. Original data are used here only for research provenance and structural counts.

## Suggested next *independent future-session* test — NOT YET OPENED

A potential new, preregistered slow-memory endpoint is whether pre-memory-test route experience improves held-out `CM` route-bearing prediction after site, release direction, and whole-pair separation are accounted for. The two source release sites demand distinct environmental baselines, and pair/solo comparisons must score **matched sites and forecast events**, not create a spurious benefit by mixing routes from distinct geographical origins.

- Independent statistical/holdout unit: **the entire author-defined Pair_ID connected component** (14 groups), never individual fixes or both birds independently.
- Within test-pair support, only historical `TR` trials can inform a personal or pair route template; `CM` targets must be entirely withheld.
- Generic regularization/smoothing/grain cannot be optimized on held-out `CM` trajectories; leave-one-pair-out training from the other 13 groups is a natural structure but should be fixed in a **new versioned outcome-blind protocol before predictions**.
- True “social memory” causal claims need a counterfactual matched environment/time/treatment schedule and error model. This source's published treatment is real, but independently fitting a predictive contrast does **not** alone establish a neural memory mechanism.

**Current scientific status:** independent 14-pair source membership **PASS**; GPS and future-memory forecast eligibility **NOT YET CHECKED**; newly measured memory prediction **NOT RUN**. The 2019 v17 five-component confirmatory stop remains unchanged; prior v6/v8/v15 negatives, v16 fast positive/slow inconclusive and v13 synthetic positives remain frozen.
