# King Rail v5: Does event-time availability beat recent environmental history for the same observed ecological state?

**Frozen analytical design** — 2026-11-15, after the published King Rail microhabitat result and earlier `louis` buffering analyses, but **before** scoring the new temporal-grain test below. This is an **exploratory reanalysis of known original biological responses**, not an untouched independent species replication and not a pre-registered confirmation of an existing cause. Keep all existing `louis` results and all `boids` v1–v4 statuses unchanged.

## Biological question

The cross-taxon state-grain idea says that matching environmental measurements to an animal's decision time should improve ecological-state prediction, relative to coarse/inherited environment. This is *not* implied by a single source's strong state buffering: if used water depth is stable despite local changes, a personal fixed target might beat any exposure-based forecast. A **negative prediction result is scientifically informative**.

The exact original ecological source is Brewer et al., 2023, *King rail (Rallus elegans) home range and microhabitat characteristics in western Lake Erie coastal marshes*, https://doi.org/10.1002/ece3.10043, underlying Zenodo https://doi.org/10.5281/zenodo.6604660 (`CARTdataset_12.31.21_All_D.csv`). Original paper: 10 stabilized home ranges, homing vs two nearby random 75-m plots surveyed within 72 h; published original target preference is often 6–17 cm, but **no model here is fitted from that published preferred-range number**. Original authors report that no banded birds were recaptured or observed between years; preserve distinct full source bird-year ID and report repeated bare-prefix strings as metadata uncertainty, not proof of the same individual.

## Hard source gate

Obtain the exact original CSV from official Zenodo record API, verify its published provider MD5 against downloaded bytes and retain the SHA-256 in the result. No hashes are constructed from derived, partial, or unverified alternative tables. Replicate the existing Louis ID grammar `^(\d+)\.(\d+)(H|R)(\d+)(?:_(\d+))?_(\d{2})$`, eliminate provider `Missing=Yes`, exclude malformed IDs without repair, and reconstruct each matched event from one homing-used and at least one random water-depth plot. Expect original `607` rows, `190` valid matched events, `10` distinct full bird-year IDs. If these fail: source STOP; no numerical result.

## SAME TARGET, four explicit forecasts

For every bird-year series independently, order homing events by original `Year`, `Julian` and event ID, with **all occurrences of a calendar date in the same split**. Use earliest `60%` of unique dates for personal training, final `40%` for heldout test. Need ≥4 training dates, ≥3 test dates, ≥5 training and ≥3 testing events; if fewer than 7 eligible bird-year series, stop. Same heldout response in all models: original homing-used `WaterDepth` (cm). Same original events, same time blocks, same denominator.

For bird i, calculate its training mean used `\bar U_i`, training mean matched random mean `\bar A_i`, and **leave-whole-bird-year-out** common within-series slope `\beta_{-i}` from the training dates of the other eligible series. This slope does not use any heldout used depth or other data from bird i. Define:

- **M0 — personal historical state:** `pred=mean_train(U_i)`, no current environment.
- **Mlag — coarse recent environment:** `pred=mean_train(U_i)+beta_-i*(mean(previous 3 available A *dates*)-mean_train(A_i))`. For each heldout date, only earlier dates' available water depth may enter. No future or same-day A may enter the lag predictor.
- **Mevent — original event-matched environment:** `pred=mean_train(U_i)+beta_-i*(A_i,t-mean_train(A_i))`. Current paired random plots **are retrospectively measured within 72h**, not advance forecasts. This is a same-event conditional prediction, not prediction of a location before an animal moves.
- **Mother — other-individual mean with event environment:** same event-matched A and `beta_-i` but both U and A baseline means from *only the other bird-year training series*. This is a secondary individual-baseline predictability test with spatial confounds.

At each test time, water depth observations from the current test date are added to the historical environmental state only **after** that date has been scored; the heldout used depth never updates either model. The fixed 60% history length, 3-day lag window, and absence of hyperparameter tuning are registered before opening the new result.

### Primary estimand and decision rule

For each heldout bird-year, compute test mean-square error (cm²), and `G_i=MSE(Mlag)−MSE(Mevent)`. Positive G means current paired availability improves over the lagged environmental reference on the **same used-depth target**. Equal-bird-year mean across 10 series; 10,000 full bird-year cluster-bootstrap replicates, percentile 95% CI, exact positive series count. **Supported only if the 95% CI lies strictly above zero AND ≥70% of eligible bird-years have G>0**. Otherwise `FAIL`; no later redefinition of lag windows or target. Mean absolute error (cm) is descriptive secondary.

Secondary no-refit comparisons:
- `MSE(M0)−MSE(Mevent)`: whether contemporaneous A beats personal fixed-state history.
- `MSE(Mother)−MSE(Mevent)`: conditional individual intercept predictability, **not proof of a stable preference or spatially overlapping individuals**.
- Within-test calendar order circular shift of observed A, 3,999 joint whole-series rotations, to assess event alignment given the same marginal availability values. This is descriptive because short series constrain distinct shifts and temporal autocorrelation matters.
- Conservative prefix-level bootstrap, merging duplicate bare ID codes (possibly reused differently across years). This is only a sensitivity check; original paper reports no across-year recaptures.

## Why this is not a proof of accessible-state portfolio dynamics

The two random plots lie 75 m from each **used** homing point. They are samples of local surrounding habitats conditional on where birds were found; they do not map all **reachable** alternatives from the prior position. Original coordinate records cannot be reliably matched at event level. The model can test prediction of realised habitat water depth, **not** actual movement causation, local option exhaustion, adaptive memory, cognitive choice, fitness or general species competition.

In particular, the original 2023 paper tested vegetation/water preference and our older `louis` analysis found attenuation of used-depth response to local random depth. Therefore the claimed novelty is only a **within-source, fixed-target falsification of the proposed time-resolution hypothesis**, not a new discovery that King Rail selects shallow water.

## Reproduction

- Python standard library, no hidden external modeling packages.
- Run `python -m unittest comparative_state.test_king_rail_temporal_grain_v5 -v` (6 synthetic known-truth tests) before downloading observed outcomes.
- Run `python comparative_state/king_rail_temporal_grain_v5.py --out comparative_state/results/king_rail_temporal_grain_v5.json` in the GitHub Actions job (network needed).
- Commit only the small source-checksum/audited numerical receipt, **never the original individuals' raw CSV**. GitHub Actions archives the result, with biological inference explicitly conditional on source verification.

**Future independent validation remains needed even if this exploratory same-source model succeeds.**
