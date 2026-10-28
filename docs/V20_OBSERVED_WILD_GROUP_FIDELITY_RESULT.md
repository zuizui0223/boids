# v20 observed wild group-level ecological prediction — past spatial persistence can help future-season forecasts

**2026-10-28 JST. New independently published wildlife source, predeclared chronological prediction models and explicit after-result audit.** This is the first Boids branch using wild, free-ranging vulturine guineafowl rather than experimental homing-pigeon navigation. It is **derived source-data analysis**, not recovered raw GPS, niche/foraging mechanisms, individual memory or Reynolds forces.

## Original ecological source and independently checked grain

Papageorgiou & Farine (2020), *Group size and composition influence collective movement in a highly social terrestrial bird*, eLife 9:e59902, [DOI 10.7554/eLife.59902](https://doi.org/10.7554/eLife.59902).

Author-public `Computed_seasonal_measurements.Rdata` in [DanPapageorgiou/Group_size](https://github.com/DanPapageorgiou/Group_size), exact author commit `15ea08ed10555beba227792f4ef106d87d52b6a4`, **2,717 original bytes**, Git blob SHA1 `3fe1e3245cb97026b03125582d5af14ab9fd5b39`, independent downloaded SHA256 `c6a534993e99f2cb324e9691ff7ec58095bf7cd7e82d7a38721f3575097cbb55`. The data table `sDCEFGnu` is explicitly identified by the author's README as the original eLife Supplementary File 1A group/season summary.

The outcome-blind [source gate](V20_WILD_GROUP_INDEPENDENT_SOURCE_PROTOCOL.md) and [actual source CI run 40627875842](https://github.com/zuizui0223/boids/actions/runs/40627875842) verified:

| Original summary grain | Actual source |
|---|---:|
| Group × season rows | **45** |
| Distinct original social group IDs | **21** |
| Groups with ≥2 observed seasons | **15** |
| Groups with ≥3 observed seasons | **8** |
| Groups with 4 seasons | 1 |
| Original seasonal categories | **C, D, E, F, G** |
| Duplicate (group, season) keys / missing values | **0 / 0** |

Original raw GPS is retained in **Movebank Avulturinum_Farine, study 475851705**, whose author R download code requires **study-specific account access**. Our program did **not** obtain or infer that raw animal GPS. Group IDs are not individual bird IDs. All 15 tested groups live in one ecological region and share seasonal weather, so they are not 15 independent climate experiments.

## Independently frozen held-out future-season forecast

The complete [v20-B contract](V20_FROZEN_GROUP_SEASON_FIDELITY_FORECAST.md) was committed **before reading any 2020 summary-response values for prediction**. Chronological source season codes are C,D,E,F,G.

- Primary response **fidelity**, original authors' within-season short-lag day-to-day group *spatial-use overlap* index, derived from GPS movement/ctmm analysis. A predictive indicator of spatial persistence, NOT directly measured food choice or neural memory.
- **M0, external prior:** mean earlier-season fidelity of **OTHER group IDs**, first averaging historic rows within each other group and giving each other group equal weight. Focal group and all current/future source-season values excluded.
- **M1, own group history:** mean strictly earlier same-ID observed seasons.
- **M2, fixed partial pooling:** (1−w) M0 + w M1, where w=n/(n+2) and n is the number of observed earlier focal-group seasons; **kappa=2 fixed before results**, never tuned on future targets. For n=1 w=1/3, n=2 w=1/2.
- Each test target requires ≥1 focal earlier season and ≥3 other groups with earlier data; identical target cells across all three models. Score per group-season squared fidelity error, average within each original group, and then mean with **equal weight across 15 original group clusters**, not treating 24 targets as iid animals.
- Whole-group bootstrap 10,000 resamples, seed 20261028. Original [source-backed CI run 40628278255](https://github.com/zuizui0223/boids/actions/runs/40628278255) passed **8/8 synthetic preregistered chronology and no-leakage tests**, exact published source hash, source support gate and full actual data scoring.

## Main new observed result — fidelity prediction

**15 original groups, 24 chronologically held-out future group-season cells** qualified from the published 45-row summary:

| Model | Equal-group held-out fidelity MSE (lower better) |
|---|---:|
| **M0: other groups' earlier states** | **0.010566863** |
| **M1: same group's earlier states** | **0.007216487** |
| **M2: fixed shrinkage, M0+M1** | **0.007918567** |

**Predeclared primary gain** = MSE(M0)−MSE(M2) = **+0.002648296** fidelity-MSE units, **11/15** positive groups; **25.06%** lower MSE than the equal-group M0 mean. Whole-group percentile-bootstrap 95% **[+0.000618080,+0.004492740]**.

**Important qualifications:**
- The unpooled M1 had the numerically smallest mean MSE, but its separate M0−M1 contrast was **+0.003350376**, 10/15 groups, bootstrap **[−0.001034266,+0.007394808]**, not consistently positive at group level. M1 vs M2 = **−0.000702080** (negative sign favors M1) and bootstrap **[−0.003184287,+0.001952395]**. **We have not demonstrated that shrinkage beats unpooled group history.**
- A *post-result* exact sign calculation for 11/15 positive group gains gives one-sided `p=0.059234619`, not below 0.05. The positive bootstrap mean interval and the nonconfirmatory sign result must **both** be stated; neither proves a universal group-memory mechanism.
- Seasonal correlation and only four eligible target seasons limit interpreting group-only bootstrap as confirmation across environmental regimes.

## Other two fixed ecological outcomes — no robust gain

The source provides two other derived ecological properties. These were **predeclared secondary** outcomes and are shown regardless of sign:

| Original outcome | Transformation | Mean MSE(M0)−MSE(M2) | Positive groups | 10k group-bootstrap 95% |
|---|---|---:|---:|---|
| **Core home-range area AREA_SQM** | natural log, positive | +0.131224 | 10/15 | [−0.029107,+0.309449] |
| **Group movement speed speed_km_day** | natural log, positive | +0.002107 | 7/15 | [−0.006656,+0.011359] |

Both intervals include zero. This does not show an absence of climatic effects, but **does not support a universal group-historical improvement across all movement/space-use metrics**.

## After-outcome credibility audit — pre-specified NOT confirmatory

Once the primary was seen, a separate [fully labeled after-outcome audit plan](V20_POSTRESULT_GROUP_SEASON_AUDIT.md) and [passing CI run 40628553210](https://github.com/zuizui0223/boids/actions/runs/40628553210) tested whether one group or one test season alone explains it. The identical original primary **+0.002648295758** was exactly reproduced; no data were removed from the primary, no kappa was changed.

| Original held-out target season | Observed target cells | MSE(M0)−MSE(M2), group-equal within season |
|---|---:|---:|
| D | 2 | +0.003281 |
| E | 6 | +0.002432 |
| F | 5 | +0.002817 |
| G | 11 | +0.001183 |

All four season-point-estimates were positive, but some have very few group observations. After leaving each whole season out in turn, the group-equal primary mean remained positive in all four reanalyses (range **+0.002219 to +0.003029**). Omitting each original group in turn gave positive primary means ranging **+0.002262 to +0.003370**. **This is descriptive robustness after outcome opening, not independent preregistered significance.**

## Biological meaning, and what is not shown

**Observed predictive statement:** In a distinct original group-level wildlife dataset, the amount that a given guineafowl group reused space on nearby days in its preceding seasons contained some information about the corresponding within-season spatial-use overlap in a later observed season that was absent from a simple *earlier OTHER-group* reference. It is about **predicting a derived spatial-persistence statistic**, not forecasting exact GPS locations.

**Not demonstrated:** the dataset contains no published raw GPS fixes accessible to this workflow, no true individual histories, no independent seasonal precipitation/vegetation/resource availability used by this forecast, no experimental social network rewiring, no measured solar/visibility or wind, no food intake or fitness prediction, and no unique Reynolds separation/alignment/cohesion forces. M0 is an **external group-history** comparator, NOT an adequately matched measured-climate/environment-only baseline. The 15 groups share the same seasonal environment and only four later season labels are forecasted.

### Link to v19 versus v20

- [v19 independent 2026 pigeon pairs](V19_OBSERVED_COMPLETECASE_13PAIR_MEMORY_RESULT.md): personal historical route bearings beat own-pair historical route averages (exploratory), while source-site other-pair population context achieved the best absolute mean accuracy. This is **pigeon homing route bearings**.
- **v20 independent wild guineafowl:** preceding **group** spatial-overlap history improves a shrunk next-season *fidelity* prediction versus older other-group reference, while the group's home-range area and movement speed indicators show no robust corresponding improvement.

The contrast is **consistent with target- and time-scale-dependent information utility**, not a controlled cross-taxon demonstration of one common mechanism. Neither empirical pattern by itself verifies v13's synthetic social-policy and niche hierarchy.

## Reproducibility and files

- [Source-only structural receipt](../validation_v20/results/wild_group_source_metadata_v20.json)
- [Original published-derived full 15-group/24-target numerical receipt](../validation_v20/results/forward_group_fidelity_v20.json)
- [Post-outcome all-season and all-group diagnostic](../validation_v20/results/postresult_group_season_audit_v20.json)
- Executable original-source download/prediction/no-leakage tests: `validation_v20/`.
- Original CI source admission [40627875842](https://github.com/zuizui0223/boids/actions/runs/40627875842), observed model [40628278255](https://github.com/zuizui0223/boids/actions/runs/40628278255), diagnostic [40628553210](https://github.com/zuizui0223/boids/actions/runs/40628553210), all successful.
- The original observed source `.Rdata` is NOT redistributed. No group-season original response rows, animal telemetry, GPS tracks, individual information or environmental measurement records are committed.

**Status:** observed out-of-sample seasonal group-history **predictive gain for fidelity** (exploratory), no causal memory or ecological-niche mechanism claim, and no observed person/animal-level Boids-force calibration.
