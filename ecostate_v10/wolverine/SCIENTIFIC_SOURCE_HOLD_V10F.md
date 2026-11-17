# v10f–v10g scientific HOLD — original wolverine source may encode used/available label in start/end environmental fields

**Audit date:** 2026-11-17. **Status:** ORIGINAL STATISTICAL PREDICTION REPRODUCIBLE, BIOLOGICAL START-STATE RETENTION CLAIM **NOT ADMITTED**.

This document supersedes the ecological interpretation of v10c and the preliminary v10d positive residual, **not their frozen numbers**. No original field manuscript submission or management inference from the inferred start/end-state retention until original attribute semantics are independently verified.

## v10g exact-equality source-label audit — 17 November 2026

This is a **post-result source integrity test**, not a new estimate of animal behavior. Reacquired the same provider-MD5-verified original 74 MB workbook and kept all 31 animal tokens and 37,855 originally matched 1-used + 20-alternative strata.

- Both `road_start==road_end` and `stream_start==stream_end` **exactly**: **85.146% of actual used** versus **2.261% of alternate case rows**. The corresponding exact equalities even when both source values are **strictly greater than zero** are **81.125% used** versus **2.169% alternative**, excluding a simple all-zero explanation.
- In **source worksheet 2**, ***all 17,338 used rows*** have `road_start==road_end`, `stream_start==stream_end`, ***and*** `traffic_start==traffic_end` exactly (**100.00%**), while only **2.629%** of the 346,760 source-generated alternatives have all three equal. In worksheet 1, all-three equality is **68.061% used** versus **1.585% alternatives**.
- **32,670/37,855** source strata have *exactly one* candidate with both road and stream start/end equality; that sole candidate is the used step in **27,134** of these strata.
- A post-result **equality-indicator-only** conditional logit—one binary predictor, no road distance value, traffic volume, stream distance, movement length, or source environment—improves the whole-animal-heldout log-score against equal 1/21 candidate chance by **+2.09551 nats/group** (31-animal bootstrap 95% **[+1.78711,+2.36935]**, **30/31** original animal IDs positive). Equal-bear average log loss: uniform **3.04452**, equality-only **0.94901**. This is **used/available source-label discriminability**, not observed wildlife state regulation.
- Original workbook source SHA256 `979a362af1acaff069a7c53dfabf5284eb68d0c448899858ae18be999513b1bd`, [original CI execution](https://github.com/zuizui0223/boids/actions/runs/44009797044), [archived original source summary](../results/wolverine_source_label_leak_v10g.json).

The source provider documents that `start` and `end` refer to step start and end and the candidate case label denotes observed versus generated alternatives, but GPS coordinates were intentionally removed from the public file (Dryad DOI `10.5061/dryad.44pp0`). Therefore **the source processing reason is unresolved**. Exact three-variable equality in every observed row of one worksheet is a severe data-structure signal; we cannot establish from this table whether an endpoint covariate was copied from a start, a common coarse spatial attribution was applied, or another workflow occurred. Do not attribute malpractice or invalidate the authors' original hypotheses.

**Updated scientific decision: strong reproducible source-label feature leakage risk; v10c and v10d remain numerical results only; the environmental-state maintenance hypothesis is not established in this source.** Do not select outcome-defined subsets to rescue it. Any future independent study must test both real and generated movement source/end attribute calculations for symmetry before any ecological outcomes are opened.

---

## Frozen original v10c remains numerically reproducible

- Scrafford et al. (2018), Dryad DOI 10.5061/dryad.44pp0 / Zenodo 5011732. Original workbook SHA256 `979a362af1acaff069a7c53dfabf5284eb68d0c448899858ae18be999513b1bd`.
- 31 source ID tokens, 37,855 matched used/20 available groups, 794,955 original case rows across 2 worksheets. Whole-individual heldout road-start/end divergence model gain +0.630451 nats/choice (animal bootstrap 95% +0.431425 to +0.813346), 27/31 positive. **This is a predictive contrast on the released table, not an identified biological state-maintenance behavior.**
- v10d *post-result* length-matched diagnostic (13,475/37,855 groups): road continuity rank excess +0.389318 [0.349520,0.425357], 31/31 positive; **stream** continuity +0.392471 [0.351567,0.429687], also 31/31 positive; traffic +0.131988. Adding road start/end divergence to M0+stream divergence gives +0.310021 [0.207023,0.406606], 26/31 positive. This suggests source-specific additional predictive information beyond one nonroad control but cannot identify specific road behavior. [v10d successful re-run](https://github.com/zuizui0223/boids/actions/runs/44007363291); initial diagnostic was stopped by a `fold`/`folds` typo, corrected without changing model or thresholds.
- v10e *post-result* source audit: **road_start == road_end** exactly on 85.2358% of used vs 3.9629% of available rows; **stream_start == stream_end** on 85.2965% used vs 3.8492% available. Raw absolute road distance change exceeded `SL_m` on 7.201% used vs 30.628% available rows. The provider explicitly labels `SL_m` as metres, but the exact distance-field units and raster/network definition require independent verification before interpreting geometric limits. [v10e](https://github.com/zuizui0223/boids/actions/runs/44007574887).
- v10f *post-result*, checksum-pinned **stationarity falsification**: used-step length median **192.938 m**, available-step median **545.078 m**; exact step length zero was only **0.1189% used** versus **0.1177% available**. For used `SL_m >100 m` (**21,781 records**), **83.3708%** nevertheless had *both* road and stream start/end values exactly identical. For available `SL_m >100 m` (**567,686 records**), only **0.9777%** had both identical. Overall dual-field equality: **85.1460% used vs 2.2611% available**. Thus **zero movement does NOT explain the equality disparity**. [v10f source audit](https://github.com/zuizui0223/boids/actions/runs/44008191847).

## Inference boundary — serious differential source-state measurement

These data make a low start/end divergence a very strong classifier of the original source `used` label. This can arise from environmental attributes being calculated/retained differently for used versus generated alternatives, or other provider-specific coding/measurement pipelines. **The data alone do not identify the exact technical cause**, and these audits do not invalidate the authors' published road-avoidance and traffic analyses. Do not call the original source corrupt or claim intentional copying without evidence.

The measured difference persists among movements longer than 100 m, so it cannot simply be ascribed to stationary animals or insufficient movement. Until the source field definitions, original GPS endpoint extractions and candidate-generation geometry are independently checked, v10c and v10d **must not be cited as evidence of active environmental-state maintenance**. Negative-control stream effects and positive road|stream prediction are both compatible with source construction differences.

This source-specific claim is **ON SCIENTIFIC HOLD**. Keep source tests and original numerical results unchanged and visible; do not rescue a biological headline by post hoc excluding 85% of used steps, retuning thresholds, or conditioning on outcome-defined features.

## Next valid evidence gate

An independent original movement dataset must provide unambiguous same-step start/end environmental fields and used/available candidate strata with a documented, common extraction pipeline; original geometry or a source-published quality-control crosswalk must validate attribute consistency for both case classes. Only then lock whole-individual/whole-area holdouts, destination and movement-kernel nulls and origin-continuity additions before testing. Independent source documentation or provider clarification might resolve current structural issue without rerunning this exploratory result.

**Publication:** Draft only, not ready to submit as original empirical demonstration of state fidelity.
