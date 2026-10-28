# v22 observed seasonal-environment group history in wild guineafowl — shrinkage helps, simple history gains do not reliably generalize

**2026-10-28 JST. Newly evaluated original author-derived wildlife data from the 2021 seasonal study. Exploratory within-population companion to v20, NOT independent biological replication or raw GPS analysis.** All predeclared models, source calendar order, historical restrictions and source sampling criteria were frozen before opening numerical ecological outcomes.

## Original source and exact reproducibility

Papageorgiou, Rozen-Rechels, Nyaguthii & Farine (2021), *Seasonality impacts collective movements in a wild group-living bird*, *Movement Ecology*, original [author repository](https://github.com/DanPapageorgiou/ranging_seasonality), original author Git commit `2a3aec308bb4a8449d1eeb16beed4aff8f387116`.

Three original Rdata files from the authors were **actually downloaded and SHA/Git-blob verified**:
- `ddf_hr_dtd.Rdata` 8,783 bytes, SHA256 `9b7b06538138bddd15874ac43403050f62d6da7baeea186bc2ff488765bb49aa`.
- `df_dhor.Rdata` **1,911 bytes**, SHA256 `d08864e91a543403cb1e8abf1bf9ea84247543181b8d4f4464ceb03929c0fa83` (**model's full source**).
- `df_dshor.RData` 4,002 bytes, SHA256 `808824277d53b616f24bd5e619b82e3b39eb156d527c9b418e01fa20a98b646f`.

The pre-outcome original-source [contract](V22_GUINEAFOWL_ENVIRONMENT_SOURCE_CONTRACT.md), [passing source audit CI](https://github.com/zuizui0223/boids/actions/runs/40636174443) and [source-only JSON](../validation_v22/results/original_seasonality_source_v22.json) verified:

| Original scientific source property | Actual source |
|---|---:|
| Group × season rows in day-to-day fidelity source | **143** |
| Independent source group identifiers | **26** |
| Groups in 2+ seasons / 3+ seasons | 23 / 16 |
| Seasonal units, chronological year_one_1..6/year_two_1..5 | **11** |
| Season-wide categorical context labels | **4** (dry, intermediate, wet, wet_breeding) |
| Missing original fidelity values | **4** |
| Duplicated group-season keys | **0** |

The author other tables contain 328 group/season/bird rows for home-range and speed (multiple birds per social group-season, so these are **not independent groups**), and 255 season-to-season overlap comparison rows. We did not repurpose these different grains into v22 predictive targets.

**Cohort dependency:** The 2021 author study and v20's 2020 author source BOTH originated from restricted Movebank study `Avulturinum_Farine` `475851705`. They share one wild Kenyan social-group population. **This is a separate outcome/source analysis, not confirmation from independent biological animals.**

## Fixed seasonal-response forecast design

[Pre-outcome model contract](V22_FROZEN_WET_DRY_CONTEXT_GROUP_PREDICTION.md) locked the following predictor information hierarchy at each future source group×season fidelity target:

- **M0:** mean of strictly prior seasons from all *other* original groups (each group equal weight), ignoring season weather regime.
- **ME:** mean of strictly prior *other-group* historical seasons assigned the **same original wet/dry/intermediate/wet_breeding class** as the target source season; fallback to M0 when fewer than 3 prior other groups share that class. This fallback is only source-support-driven, not outcome-driven.
- **MG:** the focal group's own historical fidelity from strictly prior source seasons, no future responses.
- **MEG:** ME plus own MG history with predeclared fixed shrinkage: `(1−w) ME+w MG`, where `w=n/(n+2)`, n = focal group's number of previously observed nonmissing seasons; `kappa=2` never tuned.

**Important temporal limit:** The original `season_type` is observed/assigned over the *target* season, not an independent prediction of its future weather. This is a **conditional forecast under known future-season environmental regime**, rather than a real pre-season operational forecast. The environmental categories are shared by all groups in a season, with no independent numeric rainfall or NDVI in this dataset.

The [real-data GitHub Actions run 40636440228](https://github.com/zuizui0223/boids/actions/runs/40636440228) completed **9/9 pre-outcome synthetic leakage and known-truth tests**, pinned original source checksum and real-data scoring on an **identical 113 target group×season cells from 23 distinct groups**. Out of 113 original target cells, 29 required preregistered ME→M0 fallback because no adequate earlier comparison-group history had that regime. No raw GPS and no individual ecological row was exported.

## Frozen four-model scores

| Model | Equal-original-group squared fidelity forecast error (MSE; lower is better) |
|---|---:|
| **M0** other-group historical pooled state | 0.003817929 |
| **ME** other-group matching observed seasonal regime | 0.003614641 |
| **MG** own-group historical state without shrinkage | 0.005484724 |
| **MEG** same-regime context + own-group fixed shrinkage | **0.003292301** |

The **predeclared primary**, `MSE(ME)−MSE(MEG)`, addresses whether own-group historical information adds a transferable benefit beyond recorded regime-conditioned environmental context.

| Predeclared signed comparison | Mean gain (squared fidelity) | Positive group IDs | 10,000 whole-group bootstrap 95% |
|---|---:|---:|---|
| **Primary:** ME−MEG (group history beyond observed regime) | **+0.00032234** | **11/23** | **[−0.00059173,+0.00124564]** |
| **Secondary:** M0−ME (categorical regime beyond pooled previous groups) | **+0.00020329** | **12/23** | **[−0.00005007,+0.00050924]** |
| **Secondary:** ME−MG (unpooled own group versus regime context) | **−0.00187008** | **11/23** | **[−0.00462173,+0.00059499]** |
| **Secondary:** MG−MEG (fixed shrinkage avoids overreliance on raw own history) | **+0.00219242** | **18/23** | **[+0.00054356,+0.00415334]** |

**Scientific direction:**
1. The predeclared primary **did NOT establish** a repeatable additional gain from own-group history after conditioning on season regime; only 11/23 group-level effects were positive and interval includes zero.
2. The direct added value of a *coarse* dry/wet/intermediate regime label over all-other-group historical states was also **not robust** (12/23; interval includes zero).
3. The fixed shrinkage prediction MEG had the **lowest group-mean error**, and outperformed **unpooled MG** on 18/23 groups, with a positive group-resampled interval. This is an **exploratory positive reliability result for partial pooling of historical group information**, *not* identification of the best biological learning weight.
4. MEG also had a lower numerical mean than M0 and ME, but their respective incremental gain contrasts were not all positive/confirmed. **Do not claim that seasonal regime caused improved movement or that personal memory was rejected biologically.**

## Per-season source breadth and dependencies

Ten original seasonal units have future prediction targets (the first has no earlier state). All ten **season-level** group-mean ME−MEG point estimates happened to be positive, from +0.000099 to +0.002060, but only 9–17 observed group-season records per season. The seasonal environment is **the same for all groups at each season**, and many original group IDs recur across up to 11 seasons. A whole-group bootstrap interval is **not a climate/season independent confidence interval**. These ten signs are descriptive, not ten independent randomized weather experiments. [Complete per-season, per-group original source scores](../validation_v22/results/regime_group_history_forecast_v22.json) are preserved, including the 29 matched-environment historical-support fallbacks.

The two underlying author group-level sources from 2020 and 2021 may share seasons, but are differently processed, with different spatial fidelity definitions and temporal coverage. The earlier v20 result on five seasons (external M0 vs fixed M2 group-history gain +0.002648) is **untouched**; v22's 11-season ME/MEG contextual benchmark is a new comparison but **not an independent taxon/population replication**. No comparisons of raw MSE magnitudes across these differing response measures are scientifically warranted.

## Limits and future original field test

- The response is author-estimated **daily group space-use overlap**, not raw animal movements, feeding resource selection, actual fitness or vertical niches.
- Environment is wet/intermediate/dry/wet_breeding **categorical season label**, not rainfall, NDVI, wind or resource availability measured quantitatively and independently at each bird location.
- No original individual ID sequence, partner-contact network, actual social transmission, natal memory or identified Boids steering laws are present in the tested group-season table.
- Source groups inhabit one field location and share the same seasonal shocks; full environmental replication requires *other locations/years* and preferably independent groups and measured rainfall/resources.
- v13 toy simulations, frozen v15/v16 short-turn results, v17-B five-component stop, v18 missing-CM stop, v19 individual-versus-pair result, v20 original group fidelity result, and v21 blocked original Dryad source remain unchanged.

**Current conclusion:** In this **same-source-population exploratory setting**, neither coarse environmental regime nor raw historical group state by itself consistently improves future-season fidelity prediction beyond its comparator. **A fixed, conservatively pooled environment-plus-history model was less error-prone than unpooled group history**, supporting further validation of information-reliability weighting in *independent biological groups with truly measured environmental variables*.
