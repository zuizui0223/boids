# v19: Pre-outcome **exploratory 13 complete-case pair** training-to-memory GPS route forecast

**Registered 2026-10-28 JST, AFTER the source-only availability result of v18 and BEFORE GPS coordinates, direction, or memory-test outcomes have been opened.**

## Source eligibility event that motivates this separate, non-confirmatory study

The fully preregistered [v18 all-14-pair benchmark](V18_FROZEN_FOURTEEN_PAIR_ROUTE_STOP_RESULT.md) **failed** its original source stage/site gate. The author's pinned GPS ZIP has original pair **O19** with 10 LH and 14 SH `TR` tracks, but zero `CM` tracks at either site; all remaining **13 original pair components** have `TR` and `CM` files at both LH and SH. This fact was learned entirely from filename metadata, **not from fitting any model or examining route-bearing target values**. The source-native `Checked` and `pair*` labels were already reconciled and included before any GPS trajectory was opened.

**This new study is exploratory, conditional on data completeness, NOT a relabeled confirmation of the original all-14 hypothesis.** The previous v18 NOT_ADMITTED result remains immutable and quoted in any future report.

## Original source and unchanged hypotheses

Morford et al. (2026) Scientific Reports DOI `10.1038/s41598-026-39898-2`. Original author repository `Morfordjoe/Collective-route-memories-in-homing-pigeons`, pinned commit `8e4f7e48abfa57212c5207c28580003f0ef14210`. Verified exact archive SHA256 `8e3f588ae927ab196f8c9dc9eebc9146bf656b344e68db8ba5f3c20d49edc3dc`; pair metadata SHA256 `8796f115d80f13b455704a2ad4c8710e23b18103ab0ba6d913c553fbd7342279`.

- **Evaluation units:** all 13 original assigned pair IDs *other than O19*, exactly one excluded **solely** because no future `CM` outcome exists. No other pair may be dropped after GPS route errors are examined. Require all 13 with ≥2 `CM` files and ≥8 eligible test file×shell units and sites LH,SH with both `TR` and `CM`.
- **Training/reference source population:** All **14 original pairs' `TR` flights**, including O19. O19 contributes only historical route data to the other-pair M0 reference population; it never contributes a heldout `CM` score, because such source files do not exist.
- **Target:** Identical to frozen v18 protocol: *first measured outward route-bearing* crossing at 250, 500, 750, 1000, 1250, 1500, 1750 and 2000m from true original release site, bearing circular square error in rad²; observed GPS `DT` gap≤5s, valid horizontal GPS step≤100m, shell crossing overshoot≤75m, no interpolated positions or timestamps.
- **M0:** each test pair's site-specific source population historical `TR` circular group mean, other 13 pairs equally weighted; **M1:** same pair's source-site historical `TR` circular mean (bird-equalized); **M2:** same bird's `TR` mean (fallback to M1 if historic bird template unsupported). Identical `CM` test observations, each model fitted from training only.
- All original *pair versus solo*, `LH` versus `SH` sites, and repeated flight histories are present from **source filename labels**, not inferred by cluster, GPS proximity or outcome. Source original `Checked`/`Nocheck` included uniformly, source `pair*` classified as paired as per original authors.
- **Aggregation:** shell means within each future `CM` file, file means within bird, bird means within site×mode, site×mode equal weight within pair, **13 original pair equal-weight** overall. Main `G_group=MSE(M0)-MSE(M1)`; secondary `G_individual=MSE(M1)-MSE(M2)`. Pair bootstrap 10,000 with seed 20261028; report all source pairs, support, missing individual templates, positive counts and intervals. No p-value across 426 original CSV rows.
- **Stop:** any of 13 pairs fails historical site `TR`, future site `CM`, ≥2 CM GPS tracks or ≥8 matched CM flight×shell targets, or the original source hash/label structure changes. Report `NOT_ADMITTED` with no outcomes and do **not** relax shells/limits after seeing scores.
- **Interpretation:** any predictive gain is a **navigation route-use history association** in a published preprocessed GPS data source; cannot identify neural memory, social causation, resource competition, 3D niche or wind/sun environmental influence. The earlier source study's published biological memory effect remains prior literature, not this new gain.

## Pipeline logic

The new `validation_v19/complete_case_memory.py` must use the v18 frozen template, shell, scoring and no-leakage routines **without changing v18 code or its frozen result**. Its only necessary difference is *explicitly registered after metadata auditing* test-cohort size 13 and inclusion of O19 historical `TR` templates for references. Record original source SHA256 and original all-14 stop alongside the new exploratory result. No raw source GPS/animal coordinates or individual event-level data are committed.
