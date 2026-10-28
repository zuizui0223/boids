# v16 source-blind admission — independent eight-flock, repeated-release pigeon experiment

**Registered 2026-10-28 (JST), BEFORE inspecting the raw GPS course, positions, future route targets or effect-size outcomes.** This is a *source-admission* phase, not model fitting, and it does **not** reopen or retune the frozen v15 negative result.

## Data-source candidate

Watts, Nagy, Burt de Perera & Biro (2016), *Misinformed leaders lose influence over pigeon flocks*, *Biology Letters* 12:20160544, DOI [10.1098/rsbl.2016.0544](https://doi.org/10.1098/rsbl.2016.0544). Independently deposited original GPS data: Zenodo [record 4943714](https://zenodo.org/records/4943714), titled `Data from: Misinformed leaders lose influence over pigeon flocks`. Source record publicly advertises `Data.zip` with MD5 **`ab0950ffebd924950632f727cd487c27`**; exact byte length, SHA256 and license must be obtained and pinned from the API and downloaded original, not guessed.

Published observational design is **8 flocks × 5 pigeons**, repeated training/releases, 5 Hz GPS, with experimentally manipulated *clock-shifts* to established leaders and sometimes the entire flock. The paper reports 8 prior training releases and subsequent experimental stages. These **are not 8 independent species**, nor a measured foraging niche, prey resource, or Boids force coefficient.

## Why it can address a new ecological question

The 2026 v15 source allowed only three independent flock-flight episodes, and present-partner 1-s GPS heading features failed to improve against own/route or 10-s-stale controls. This new source is independent, contains eight group-level units, and an external intervention on navigation information quality.

The two-layer *hypothesis for a future outcome-blind test* is:
1. **Fast:** immediate social information may or may not improve future turning after own-state/route controls;
2. **Slow:** repeated release experience, group history and information perturbation may influence **subsequent horizontal route organization** even when fast one-step partner gain is small.

This is about *navigation and social information architecture*, not a proven ecological space/resource niche. Never interpret the two timescales as a biological dissociation just because one fails conventional significance.

## Stage A — frozen integrity and structural admission only

- API URL `https://zenodo.org/api/records/4943714`. Require matching record ID, expected filename `Data.zip`, source MD5, open access, explicit size ≤400 MB and license; fail closed if any are missing or conflicting. Download once into an ephemeral GitHub Actions runner, cap at 400 MB. Compute MD5 and SHA256 from actual bytes; match published MD5 and size.
- Enumerate ZIP entries and reject path traversal, encrypted entries, duplicate names, decompressed total >3 GB, or extra files whose provenance is unclear. **Never** check raw track coordinates or calculate motion outcomes in Stage A.
- For every CSV, inspect only ZIP filename, first header row and up to one **structural** data row for column types (do not save the row), and count raw rows without parsing numerical GPS values. Record per-trial metadata such as source path format, header variants, file count by inferred flock/release, candidate individual identifier stability, observed time-column presence, possible latitude/longitude columns, malformed CSVs, row-count distributions and license. **Do not output exact GPS positions or individual route tracks.**
- Expected filenames from public description: `01_<flock ID>_<bird ID>_<release ID>.csv`. If filenames do not match or include ambiguous multiple releases, return `NOT_ADMITTED` with structure reasons; do not silently relabel. Predeclared minimum: **≥8 identifiable independent flocks; each has ≥5 separate releases and ≥3 stable individuals within repeated releases**, else no dual-timescale test admission.
- Critical: verify actual rather than nominal timestamps and the presence of a plausible cross-bird synchronization field *before* any fast social test. Filename/release matching or same row index is not synchronization. No 3D claim unless a separately calibrated altitude field exists.
- The release identifier may NOT encode treatment. A specific control/leader-only/flock-wide clock-shift categorization requires an independent pre-outcome treatment schedule from source documentation; otherwise keep intervention comparison `NOT_ADMITTED` and only consider descriptive repeated release prediction.

## Stage B — frozen *before* any fit or numerical forecast outcomes

After Stage A record/source schema and digest are committed:
- Predeclare exact observed columns, valid original time units, duplicate and missingness filters, spatial projection and synchronized ≤200 ms pair observations for the fast task. Test an own/route vs current-neighbor vs same-partner-stale control on an *identical target set*; **whole-flock** heldouts and only training-based scalers.
- For slow navigation, define spatial/route occupancy distribution conditional on **path progress** and compare history-aware group/individual predictors with an environment/route-context baseline on *future complete release episodes*. Predictive scoring (e.g. held-out log score or circular heading MSE) must use a predeclared spatial grain and shared support, with no target-leakage from centroid/leader labels. Do not call this habitat use or foraging niche.
- To compare across timescales, compute flock-level held-out `Δ_fast` and `Δ_slow` with uncertainty from the **eight flock clusters**; report the actual two-dimensional effect and no universal threshold. A null fast effect does not imply fast equivalence or absence of social interaction.
- Include experimentally clock-shifted states only when an independent treatment ledger is found and frozen **before reading course outcomes**. Prior publication's positive hierarchical result is context, not the new forecast result.
- Preserve all negative outcomes and source-admission failures without tuning cuts or reusing v15 data.

## Files & release boundary

`validation_v16/source_gate.py` is the **only** implemented v16 procedure at this stage. Its GitHub CI receipt contains source metadata, SHA256, headers, counts and admissibility flags, not animal movement rows or forecasts. The source ZIP is never committed, and reuse is attributed to the Zenodo record license. **Stage A success is not empirical support for a fast/slow theory**.
