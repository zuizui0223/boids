# v18 — Frozen independent 14-pair future-memory route forecasting protocol

**Registered 2026-10-28 JST, BEFORE inspecting individual GPS values or the scored CM memory-test trajectories. Status: NEW exploratory observed-source forecast, not a causal memory mechanism.** Do not modify the v13 simulation, v15/v16 observed studies or the v17-B five-network confirmatory STOP.

## Original independent source and data rights

Morford et al. (2026), *Collective route memories emerge through differential forgetting of navigational information in homing pigeons*, *Scientific Reports*, DOI [10.1038/s41598-026-39898-2](https://doi.org/10.1038/s41598-026-39898-2).

Authors' GitHub `Morfordjoe/Collective-route-memories-in-homing-pigeons`, fixed commit `8e4f7e48abfa57212c5207c28580003f0ef14210`; **author-pinned Git blob files**:
- `CM info.csv` 348 bytes, Git blob `8c607d535e549fb72f0863b616e28cac24d031f7`, independently obtained SHA256 `8796f115d80f13b455704a2ad4c8710e23b18103ab0ba6d913c553fbd7342279`.
- `CM_trimmed.zip` 21,425,810 bytes, Git blob `0b1bd66f08c1cac5f8ca582f289d49c43f553bfa`, independently obtained SHA256 `8e3f588ae927ab196f8c9dc9eebc9146bf656b344e68db8ba5f3c20d49edc3dc`.
- Source counts **14 originally assigned disjoint pairs**, 28 individuals; pairs' assigned `Additional_training_site`: LH 7, SH 7. Original ZIP contains **426 proper GPS CSVs** and one consistent 18-column header; no raw GPS contents have yet been examined.
- Public author repository root has **no established original GPS data redistribution license**; download only on ephemeral CI and store aggregate group results, not raw tracks. Source is processed/trimmed, not native original GPS sensor dumps; report that provenance explicitly.

## New falsifiable question

Do **previous training (`TR`) flights** produce a transferable route-direction signature that predicts later memory-test (`CM`) flight routes, over the source-site-specific population baseline, and is there additional **individual** prediction beyond a **pair** history?

We test held-out spatial **navigation route**, NOT feeding patch usage, wildlife resource competition, social-choice imitation coefficients, neural memory, altitude ecological niche or Boids physical force. Existing 2026 paper reports behavior; this project independently scores *different* prior-history predictions.

## Independent units, labels and fixed design

- **14 original `Pair_ID` components**, each with two nonoverlapping bird IDs from source metadata. Pair_ID = independent cluster, not 28 birds, flight files, or GPS fixes. Any source pair-sharing/filename conflict is a hard STOP.
- Recorded GPS filename must explicitly match `<bird>_Site_<LH|SH>_<pair|solo>_Nocheck_<TR|CM>_<YYYY-MM-DD HH:MM:SS>.csv`; otherwise non-matching CSVs are reported and stopped, *not* silently relabeled. Two original source release sites (coordinates from the pinned authors' analysis code):
  - **LH:** longitude −1.3915, latitude 51.8303056
  - **SH:** longitude −1.42375, latitude 51.7527778
- Both release sites differ in direction to the loft; all templates and outcomes are stratified by the *true original source site*. No pooling of site labels that can fake a "memory" gain.
- **Only original `TR` flights train historical templates. All `CM` flights are strictly future heldout outcomes**; no `CM` GPS position or original destination is used to define training, transforms, hyperparameters or group identities. Use original site/condition labels from filenames and Bird/Pair_ID from `CM info.csv`.
- Pre-register all navigation shells from release at **250, 500, 750, 1000, 1250, 1500, 1750, 2000 m**. The target is original observed bearing (clockwise north) to the *first outward* crossing of that shell, using the released unaltered GPS row coordinates (not other authors' `DistRS`/homing efficiency/experimental outcome fields). No interpolation to manufacture a shell fix.
- A shell is admitted only when two successive measured positions have a **strictly increasing recorded UTC timestamp gap ≤5 s**, measured separation ≤100 m, prior radius below shell, observed next radius ≥ shell but **≤75 m overshoot**. GPS values must be finite and valid range; `DT` should match strict ISO-like original `YYYY-MM-DD HH:MM:SS[.fraction]` (with optional `T`), timezone interpreted as authors' source standard `UTC` but no cross-receiver calibration claimed. Any row/time parse failure breaks continuity. Need original GPS time that increases; reject repeated/decreasing time. `Time`, `Local.Time` and `round` are NOT assumed to be synchronized alternatives.
- Metrics are **wrapped circular squared bearing error rad²** and are only compared when ALL registered candidate templates are supported from training, based on historical training counts **before test outcomes**.

## Models, same target support and hierarchy

For each original bird×site×CM flight×shell, predict using only `TR` history:

- **M0 (source-site population)**: at each shell, compute the circular mean of the **other 13 pairs'** bird-equalized `TR` route templates at the same LH/SH site. Every independent training pair gets equal weight, regardless of number of flights, bird fixes, or experimental solo/pair mix.
- **M1 (own pair historical route)**: at each shell/site, circular mean over all `TR` flights for each of this pair's two birds, then circular mean of supported bird means. No `CM` information.
- **M2 (own bird historical route)**: at each shell/site, the bird's own circular training mean over its `TR` flights. **If own bird is unsupported for an eligible shell, use the M1 pair template** based solely on training support and count this fallback; do not drop a target because its error was large.
- The same future `CM` target GPS fixes are scored by M0/M1/M2 on the same support. If any relevant M0/M1 is not defined from `TR`, the shell is ineligible for ALL three models before test angle values are examined.
- All eligible memory-test flights (`CM`) are stratified into original `pair` and `solo` modes; **primary across both**. The pair-vs-solo *difference* in gain is a **predeclared exploratory secondary**, not a causal treatment test without separately verifying release pairing/perception and experiment schedule.
- For each CM flight, average over its eligible shells. For each bird, average over its CM flights (same site/mode), then per pair/site/mode. For each pair, average across observed **site×mode** cell means with equal weight. Thus 14 independent pair-level scores, not 426 flight-level iid observations. Show support and per-pair site/mode cell availability.
- Primary `G_pair = MSE(M0) − MSE(M1)` (positive means pair historical route predicts better than source population); secondary `G_indiv = MSE(M1) − MSE(M2)` (positive means personal history adds predictive information).
- Report full means and positive pair counts with whole-pair bootstrap 95% **10,000 resamples**, fixed RNG seed **20261028**. Exact one-sided 14-pair sign p may be reported only with caveat source pairs share loft/site/weather and are not fully independent environments.

## Outcome-blind eligibility / hard stops

- All **14 original pair IDs** must have ≥1 `TR` flight at each source site (LH and SH) and ≥1 `CM` memory-test flight at each site, with at least **two individuals** per pair represented in the original source archive. All 14 independent pair clusters must each yield ≥**8** eligible `CM` flight×shell units, across ≥**2** distinct `CM` files, before group comparisons are admitted. If not, result is `NOT_ADMITTED` and full structural counts are reported; do not change shells, minimum or group acceptance to rescue a result.
- At least 1 originally admitted `TR` shell per site across other 13 pairs for each scored shell; do not use future outcomes to pick shells.
- Store original release mode (`solo`/`pair`), source site and train/test type **from recorded filenames**. Do not relabel GPS contacts from their observed positions.
- No proof of wind/environmental information gating can be claimed without verified original wind/weather records. No calibrated GPS altitude or experimental neural memory mechanism is identified in this protocol.
- If an author-preprocessed archive prevents exact raw datetime/coordinate verification, retain the stop and describe the source limitation rather than refitting arbitrary time filters.

## Exact reproducibility

```bash
python -m pip install 'numpy>=1.26,<3'
PYTHONPATH=validation_v17:validation_v18 python -m unittest discover -s validation_v18 -p 'test_*.py' -v
PYTHONPATH=validation_v17:validation_v18 python validation_v18/slow_pair_memory.py --out validation_v18/results/slow_pair_memory_v18.json
```

Source download remains ephemeral. Output consists of **aggregate pair-/site-/condition-level** error summaries and source hashes, no animal GPS positions, exact individual timestamps, or raw route-angle targets. A negative result is a valid frozen endpoint, not an invitation to optimize the same data until positive.
