# v19 independent future memory-route GPS result — individual-history gain over pair, no advantage beyond source population

**2026-10-28 JST.** This is a **new exploratory observed-data prediction result conditioned on source-availability**, NOT a confirmation of the source-failed v18 fourteen-pair pre-registration. Reanalysis method and all outcome exclusions were frozen **before opening GPS bearing or future CM targets**, based solely on the missing CM filename stage of original O19.

## Original source and traceable changes

Morford et al. (2026), *Collective route memories emerge through differential forgetting of navigational information in homing pigeons*, *Scientific Reports*, DOI [10.1038/s41598-026-39898-2](https://doi.org/10.1038/s41598-026-39898-2). Original author data [GitHub](https://github.com/Morfordjoe/Collective-route-memories-in-homing-pigeons), pinned commit `8e4f7e48abfa57212c5207c28580003f0ef14210`; recorded original ZIP **21,425,810 bytes**, exact SHA256 `8e3f588ae927ab196f8c9dc9eebc9146bf656b344e68db8ba5f3c20d49edc3dc`; pair roster SHA256 `8796f115d80f13b455704a2ad4c8710e23b18103ab0ba6d913c553fbd7342279`. Original processed/trimmed archive; no unprocessed GPS NMEA error calibration claimed.

[Pre-outcome separate complete-case source contract](V19_EXPLORATORY_COMPLETECASE_13PAIR_MEMORY_CONTRACT.md) explicitly retained original v18 design, the failed **all-14-pair `NOT_ADMITTED` result**, the previously fixed eight 250–2,000m radial shells, both source sites (LH and SH), original `TR` training only and future `CM` test only, source site/mode feature groups, original pair-independence and no outcome tuned thresholds.

Source [original v18 file-only stop](V18_FROZEN_FOURTEEN_PAIR_ROUTE_STOP_RESULT.md): original pair **O19** has 24 `TR` files but **zero** `CM` files at either site. The present new test uses exactly 13 paired components with observed `CM`, but retains O19's `TR` records for building the *other-pair population baseline*, thereby avoiding a test-dependent rewrite of the reference population. This is a separately registered exploratory conditional study, **not** a rescued primary or evidence that O19 lacks biological memory.

The [observed CI run 40626721143](https://github.com/zuizui0223/boids/actions/runs/40626721143) passed all **5 synthetic/source-only tests**, downloaded identical source bytes, passed exact 13-pair stage gate and scored original GPS route targets. The numerical source-only stage yielded 14 original pairs, 426 source files, 13 target-eligible pairs and **zero source label errors**. 72 heldout CM GPS files yielded **576** original measured crossing targets (8 shells per eligible CM track). Source processed original GPS timestamps and coordinates were not interpolated or redistributed.

## Fixed forecasting hypotheses and outcomes

At each source site and radial crossing, compare three original training-only circular bearing models:

- **M0:** other 13 source pairs' `TR` route templates, equally weighted per pair (original reference population).
- **M1:** the focal pair's `TR` route history with individual-equal weighting (group history).
- **M2:** the focal individual's `TR` route template, with prespecified M1 fallback only for historical-unsupported cells.

All score the **exact same future `CM` observation** at 250–2,000m shells, and are aggregated into independent original pair-level errors (first shells within CM track, then tracks per bird, birds per release site and flight mode, source site/mode cells per pair, then **13 pairs equal weight**). Units are wrapped circular mean squared bearing error **rad²**; lower better. The source-mode `pair` vs `solo`, and source `LH` vs `SH` are not mixed into a single route origin.

| Prespecified heldout contrast | Equal-pair mean MSE improvement (rad²) | Whole-pair bootstrap 95% (10,000, seed 20261028) | Positive pairs | Finding |
|---|---:|---|---:|---|
| **M0 − M1**: original source population → own pair history | **−0.055778** | **[−0.325982,+0.179685]** | 6/13 | **Not supported** |
| **M1 − M2**: own pair history → personal history | **+0.045130** | **[+0.007902,+0.099253]** | 9/13 | **Exploratory conditional improvement** |

**Important model-ranking check:** equal-pair absolute MSE was **M0 0.860210**, **M1 0.915988**, **M2 0.870859 rad²**. Thus **population M0 was still the best of the three models on average**, and the personally informed M2 did **not** outperform the population baseline M0 in equal-pair average. The positive secondary `M1−M2` means that within-pair averaging can discard useful bird-level information, **not** that an individual's historical route universally beats an external site-level reference.

### Full independent pair-level results

| Original Pair_ID | CM files | CM shell targets | M0−M1 (group benefit) | M1−M2 (individual benefit) |
|---|---:|---:|---:|---:|
| O1 | 3 | 24 | −1.318967 | +0.316029 |
| O2 | 8 | 64 | −0.006989 | −0.010353 |
| O4 | 3 | 24 | +0.696660 | +0.102753 |
| O5 | 3 | 24 | +0.044247 | +0.040639 |
| O6 | 8 | 64 | −0.466077 | −0.025245 |
| O7 | 8 | 64 | −0.179544 | +0.018201 |
| O8 | 6 | 48 | +0.378130 | +0.080078 |
| O9 | 6 | 48 | −0.280303 | +0.015271 |
| O10 | 7 | 56 | +0.138896 | +0.039763 |
| O12 | 3 | 24 | −0.040119 | +0.000690 |
| O14 | 7 | 56 | +0.046592 | −0.012404 |
| O15 | 4 | 32 | +0.327978 | +0.024963 |
| O16 | 6 | 48 | −0.065622 | −0.003700 |
| **Equal pair mean** | **72** | **576** | **−0.055778** | **+0.045130** |

**Post-outcome descriptive robustness only (not a new primary):** the median of 13 personal-over-pair improvements is **+0.018201 rad²**. Leaving any one pair out gives a positive remaining mean in the range **+0.022555 to +0.050994 rad²**; the largest individual improvement is O1 (+0.3160), so magnitude is heterogenous. **Only 9 of 13** pairs improved; an exact one-sided sign test for 9/13 would be **p≈0.1334**, so a positive pair-bootstrap mean is NOT uniform sign replication or a confirmatory general memory effect. The exploratory comparison of M0 vs M2 directly yields **M0−M2=−0.010649 rad²** (M0 best on average), without a preregistered formal test.

## Ecological interpretation with earlier Boids branches

The evidence indicates that in this source and this specific frozen site-controlled route-bearing forecast, individual history sometimes predicts future course direction more precisely than a pooled two-bird historical route. However **pairwise pooled route history was not reliably better than the other-pair baseline**, so the simplistic proposition that making collective memory *automatically enhances future route prediction* is not supported by this scoring task.

This is not a contradiction of the original paper's experimental memory result: experimental pair/solo forgetting behavior and *out-of-sample circular route-bearing prediction across source sites and shells* are different endpoints. The original `CM_trimmed` GPS is derived/processed, and original sensor altitude or observation error was not fitted. No demonstration of neural memory trace, learned Boids interaction parameter, genetically maintained niche, prey-resource competition, animal energetic fitness or cross-species generalization follows from this result.

Earlier independently frozen results remain:
- **v15**: another original 2026 pigeon source, 3 heldout flock flights, current-partner short-turn information failed versus stale and own-only (0/3 favorable).
- **v16**: independent 2016 8-flock source, current-partner short-turn predictive benefit in 7/8; repeated static route-history improvement not robust.
- **v17-B**: original 2019 mate graph 5 C₄ social units, not ≥8, confirming independent social-group admission fails; no wind×partner effect fitted.
- **v13**: private-reward/social-choice emergent group niches are synthetic known-truth mechanisms, not validated wild ecological resource niches.

## Reproduce and preservation

Source code: `validation_v19/complete_case_memory.py`; **reuses unchanged v18 frozen template and source parsers**. All original raw tracks remain transient; [aggregate verified numerical receipt](../validation_v19/results/frozen_thirteen_pair_aggregate_v19.json) contains original pair/site/mode summaries but no GPS coordinates or animal fix rows. The first passing CI result and artifact are available at [run 40626721143](https://github.com/zuizui0223/boids/actions/runs/40626721143). The build artifact ZIP SHA256 is `f5590f54103617883bac5b5ed535db6d7ec485eef8f1b8441beab82c5eb3af4d` (this is artifact ZIP checksum, not raw source checksum).

```bash
python -m pip install 'numpy>=1.26,<3'
PYTHONPATH=validation_v17:validation_v18:validation_v19 python -m unittest discover -s validation_v19 -p 'test_*.py' -v
PYTHONPATH=validation_v17:validation_v18:validation_v19 python validation_v19/complete_case_memory.py --out validation_v19/results/thirteen_pair_route_memory_v19.json
```

**Outcome status:** v18 full-14 result **NOT_ADMITTED**, unchanged. v19 **exploratory post-source-availability observed forecast** complete, personal vs pair positive in 9/13 with a positive bootstrap mean CI; group vs source population not supported, and M0 globally lowest average MSE. Next independent confirmatory testing must use a new population/source or a source-frozen protocol and should measure independently assigned group/individual identities and ecological context without selecting outcomes after observing gains.
