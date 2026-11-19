# v34 — *Chrotopterus auritus* landscape-transfer: original-source admission contract

**Frozen 2026-11-19 JST before any numeric GPS or movement outcomes are read by this programme.**  
Stage 1: public original-file acquisition, integrity, and data-structure eligibility **only**. Stage 2 movement prediction is forbidden until a separate written outcome contract is committed.

## Source and prior art

Trujillo et al. (2026), *Journal of Animal Ecology*, DOI [10.1111/1365-2656.70391](https://doi.org/10.1111/1365-2656.70391), published 2026-11-09. Original Dryad DOI [10.5061/dryad.7d7wm38c0](https://doi.org/10.5061/dryad.7d7wm38c0), published 2026-10-30. Authors report **17 individuals, 57 nightly trajectories and three Mexican landscapes** (El Hormiguero, Okolhuitz and El Corriental). Published finding: evergreen/subdeciduous forest use was consistently high under both inferred active-search and sit-and-wait states, while landscape context more strongly affected *where* states were expressed than *when* transitions occurred. That is **prior art**, not a discovery to be re-labelled.

Official original files listed at Dryad, verified by source landing page:
- `Raw_movement_data.zip`, published file ID **5036052**, ~408 KB, GPS observations; source has raw records (often names ending `df.csv`).
- `Movement_data.zip`, file ID **5036051**, ~696 KB, including **interpolated 30-second coordinates** (filenames containing `homogein`).
- `Chrotopterus_auritus_Movement_Ecology_Analysis.zip`, file ID **5036053**, ~10 KB; source R code including state HMM.
- `README.md`, file ID **5036059**, ~8 KB.
- `Landscape_data.zip`, file ID **5036050**, ~145 MB, seven ~10 m landcover layers; **not downloaded** in v34 since only original movement-source structural admission is needed.

**DO NOT** claim original coordinates or trace numbers were verified merely because the Dryad page lists files. The direct links can be blocked by anti-bot checks: classify HTML `Validating...` and HTTP 401/403 as source transport failures, not absence of animals.

## Why v34 is not a repeat of the article

Novel prospective question: does a model of **short-horizon movement persistence** fitted in two landscapes improve next-step prediction in the third, beyond a pooled movement baseline? This is a predictive out-of-landscape transfer problem, not a new claim that there are two HMM states or that forest is preferred.

The primary outcome will eventually be chosen from genuine **original GPS fixes**, never from model-decoded full-track HMM labels or 30-s interpolation treated as independent measurements. State switching is a secondary biological interpretation only if validated from original fixes. We will not infer prey acquisition, memory, learning or actual acoustic pulses from GPS alone.

Only three geographically nearby landscapes exist, so **at most a within-region feasibility test** is possible. The minimum exact one-sided sign probability for unanimous three-landscape agreement is 1/8=0.125; no 5%-level site-universality claim is possible from a three-site sign test.

## Fixed source-only gate

1. Retrieve the exact published Dryad files 5036052 (raw GPS) and 5036051 (processed) from **only** their official file stream or REST download URLs. Also optionally R-script zip 5036053 (source-code only). Do not try unrelated mirrors or bypass authentication challenges. Preserve transport HTTP status, actual MIME, body leading type, file length and SHA256 if bytes obtained.
2. Original zip header must be valid; reject HTML/JSON error pages despite HTTP 200, malformed ZIP, files >8 MB for either movement zip, and zip members exceeding an uncompressed 30 MB per archive cap. No original animal arrays are exported or re-published in the repository.
3. On ZIP entries, inspect only filenames, file extensions and CSV header, row counts, distinct **bat-label counts**, dated-track counts, site token counts, and timestamp-string support. Do not open/read numeric lat/long, height, step lengths, turning angles, speed, or HMM state labels.
4. Require verifiable (not guessed) linkage of original labels to landscape IDs, individual IDs and original time fields, and evidence that processed interpolated fixes can be distinguished from genuine original GPS observations. Record original vs interpolated support separately.
5. A later raw-GPS forecasting programme can open only if at least **two unambiguously identified landscapes, eight animal labels, 20 source nocturnal tracks** and **2,000 raw GPS rows** are structurally confirmed. These gates are fixed independently of behavioural outcomes. Three-landscape generality still needs all three source sites and at least 3 individuals per site. If any fail, record **SOURCE_ACCESS_STOP**, **SOURCE_SCHEMA_STOP** or **SOURCE_SUPPORT_STOP**, not a negative ecological result.
6. No data-leakage by training on full-track HMM-decoded states or interpolated self-generated fixes. No same-individual label across landscape groups can be treated as an independent individual.
7. Any future model must use whole-landscape holdout, train-only preprocessing, reporting of positive and negative landscapes, and no outcome-driven tuning. The future frozen outcome contract must define target and baseline *before* reading numeric positions.

## Open questions v34 is allowed to answer

- Can the original published movement ZIP actually be retrieved in CI from a pinned Dryad file ID?
- Are the original `ID`, `timestamp`, site and nightly-trajectory labels sufficient for whole-landscape leave-one-site-out without lookahead?
- Do original and homogein 30-s interpolated files have distinguishable source fields and traceable provenance?

**Scientific claim boundary:** source structure alone never establishes exploration, perch-search transitions, site-independent policies, behaviour prediction, resource selection, or ecological universality. Prior `batter`, `boids` v30 negative and v32–v33 structural STOPs remain untouched.