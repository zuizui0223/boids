# v17-D / v18 slow-memory source admission: independent 2026 fourteen-pair experiment

**Registered 2026-10-28 JST before inspecting raw GPS route/turn observations and before any new predictive model.** Distinct use case from the wind-gated v17-B failure and the oversized 2021 ten-transmission-chain archive.

## Independent source facts and fixed version

Morford, Lewin, Mann, Krupenye & Biro (2026), *Collective route memories emerge through differential forgetting of navigational information in homing pigeons*, *Scientific Reports* 16:8894, [DOI 10.1038/s41598-026-39898-2](https://doi.org/10.1038/s41598-026-39898-2).

Original authors' public source repository: [Morfordjoe/Collective-route-memories-in-homing-pigeons](https://github.com/Morfordjoe/Collective-route-memories-in-homing-pigeons), pin `main` source commit **`8e4f7e48abfa57212c5207c28580003f0ef14210`** (2025-05-22). Pinned files:

- `CM info.csv`, Git blob SHA1 `8c607d535e549fb72f0863b616e28cac24d031f7`, GitHub 348 bytes: original **Bird,Partner,Pair_ID,Additional_training_site** table. Published metadata show 14 pair rows; verify that subjects do not appear in more than one original pair.
- `CM_trimmed.zip`, Git blob SHA1 `0b1bd66f08c1cac5f8ca582f289d49c43f553bfa`, official GitHub byte size **21,425,810**. Download exactly this version via `raw.githubusercontent.com/Morfordjoe/Collective-route-memories-in-homing-pigeons/8e4f7e48abfa57212c5207c28580003f0ef14210/CM_trimmed.zip`. Cap 40 MB; verify exact bytes, Git **blob** SHA1 via `sha1("blob <size>\\0" + raw_bytes)` and compute independent SHA256. Do not invent source checksums before source acquisition.
- Associated `CM tracks to stats.R`, source `CM_analysis_df.csv` and metadata may contain derived outcomes; do **not** read or use these for model outcomes during Stage D1. The repo has no explicit `LICENSE` file listed; unless independently verified, treat raw-source reuse as **citation/research inspection**, not unconditional permission to redistribute.

The authors report **14 original distinct pairs** tested at two different sites under an 8-week forgetting condition and a shorter-forgetting/extra-training condition. Original 2026 paper reports improved memory retention in pairs. These are original published scientific results, **not this project's new out-of-sample predictive gain**.

## Source-only Stage D1 (precommitted)

1. Fetch `CM info.csv` at the exact pinned source commit (small text), verify original file byte count and Git blob SHA1. Parse only bird IDs, pair ID, assigned site and check 14 unique reciprocal undirected pairs with no shared bird IDs, no duplicates or blank IDs.
2. Fetch the exact original 21,425,810-byte ZIP, SHA256 and Git blob SHA1 verified; reject decompression bombs, unsafe names, encrypted entries and duplicate entries.
3. Enumerate only GPS ZIP file names, directory structure and first header row (max 32 lexically sampled original CSVs), not track records, GPS positions, Course, speed, flight outcomes or memory effects.
4. Verify that **≥8 independent metadata-declared, non-overlapping original pair components** exist. Do not infer group identity from GPS positions/flight similarity. Distinguish individual IDs (28) from independent pairs (14); sites and pair treatment are repeated within the same social groups, not independent 28 sources.
5. Verify source CSV time column presence (preliminary accompanying R source references `DT` as UTC and `Speed.km.h.`, `DistRS`, `DistHome`, `Course`). The R script is code context only; before any forecast, check actual GPS file and timestamp quality independently. No 3D claim without real vertical accuracy.
6. No raw tracks, exact coordinates, detailed dates, response data or analyzed flight event rows to GitHub. Archive aggregate source manifest plus source SHA only.
7. **No v17 wind-context evidence** can be obtained unless actual independently measured wind time/units/source exists; the raw code listing does not establish such data. A separate **slow future-session route-memory prediction protocol** is required after Stage D1, with independent pair holdouts, matched environmental context baseline, training history and future test sessions fixed before opening outcomes.

If the ZIP cannot be downloaded or source IDs do not match, report `NOT_ADMITTED` without selecting alternative samples after seeing results. **Leave v15/v16 empirical and v13 synthetic frozen endpoints untouched.**
