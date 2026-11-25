# v46: Independent zebrafish eight-shoal hierarchy — completed, frozen replication gate NOT met

2026-11-25 JST. Original Collignon et al. 2019, PLOS ONE DOI 10.1371/journal.pone.0216798; dataset DOI 10.5281/zenodo.1470446.

## Source and execution

- Frozen v44 protocol: [V44_INDEPENDENT_ZEBRAFISH_SOURCE_AND_HIERARCHY_FREEZE.md](V44_INDEPENDENT_ZEBRAFISH_SOURCE_AND_HIERARCHY_FREEZE.md)
- Archive-defined cohort clarification and exact schema: [V45](V45_ZEBRAFISH_ARCHIVE_ROSTER_CLARIFICATION.md), [V46 admission](V46_ZEBRAFISH_SCHEMA_ADMISSION.md).
- Completed original source/model run [45568318196](https://github.com/zuizui0223/boids/actions/runs/45568318196), job 139048486893 SUCCESS. Artifact [15000508348](https://github.com/zuizui0223/boids/actions/runs/45568318196/artifacts/15000508348), downloaded ZIP SHA256 d0dd6d6472b90ec0afa3a63bd4e2f71ba32d55417da0b6406910ab9e2548336b verified locally.
- Original archive SHA256 03a754d8e6d9084bd8944540189c65a20d63644063e127bf586feb5c4eacdfe0 and 8 source member pins verified. All 8 original 10-fish files, each 54001 time rows, all finite positions, original elapsed clock verified against 15fps within .0051s. Native 15Hz grid 0.2s = 3 frames; full shared cohort 17,986 eligible group times and 179,860 fish times per trial; total 1,438,880 fish-time rows. The 17985 arithmetic in the initial implementation was corrected before outcomes (19ef306db1c31cb38e93c9403f86c29f6fad8ce1); actual time grid and scientific endpoint unchanged.
- Author reports no reuse within shoal size. Published Fig.3 roster differs from archive; these are all eight archived 10AB trials, not exact reproduction of original Fig.3. Published data columns contain XY and direction, not identification probabilities; the .75 confidence sensitivity is NOT ADMITTED. No coordinate physical-unit calibration inferred. No raw XY or fitted coefficients exported.
- Six frozen panels, whole original trial holdout (7 train, 1 test), same v30/v42 G14 and horizons 0–.2/.6–.8s, train-only StandardScaler plus fixed Ridge10 via v32 moments. Workflow passed synthetic physical-time parity, future-target isolation, shared missingness, independent sklearn/moment numeric parity. No new data-dependent tuning.

## Original four-source comparison (equal original evaluation units)

Dg = MSE_G_geometry - MSE_GLOBAL; Dl = MSE_GLOBAL - MSE_NEAR_TRUE. R=100*mean(Dl)/mean(Dg). This ratio uses nested improvements, not causal information share. All Dg positive in both horizons for every unit across the four studies. Negative Dl retained.

| Source | Unit count/type | Global improvement (% of geometry), short/delayed | Near incremental improvement (% of GLOBAL), short/delayed | R short/delayed (%) | R change pp | Units with lower R |
|---|---|---|---|---|---:|---:|
| Tetra v42 | 6 files | 17.714741 / 12.599232 | 1.762360 / .002776 | 8.186193 / .019259 | -8.166933 | 6/6 |
| Ayu v42 | 7 files | 11.405929 / 13.359527 | .822353 / -.006778 | 6.387523 / -.043959 | -6.431482 | 6/7 |
| Stickleback v33b | 12 original shoals | 1.824171 / 4.986350 | .876270 / 1.652469 | 47.160329 / 31.487374 | -15.672956 | 12/12 |
| Zebrafish v46 | 8 original within-size trials | 3.368131 / 4.255753 | .079375 / .086753 | 2.277265 / 1.951741 | -.325524 | 6/8 |

The four means are negative, 30/33 evaluation units negative. Tetra/ayu files are not verified independent biological shoals. The first three sources generated the hypothesis; zebrafish is an independent study testing the fixed endpoint. Do not treat 33 units as independent study replications or perform a pooled p-value.

## Frozen independent decision (zebrafish)

- All 8/8 global gains positive in both horizons: denominator gate PASS.
- Mean R change -0.3255241817948822 pp: direction PASS.
- 6/8 within-trial decreases: >=75% condition PASS.
- Delete-one-existing-test-score reaggregation range [-1.1496905016064694, +0.16309671781278534] pp: stability gate FAIL.
- Descriptive paired bootstrap (10000 draws, seed 20261125) 95% [-2.3311734838006934, +1.3658650801577341] pp, includes zero.
- **FROZEN_PRIMARY_DIRECTION_NOT_REPLICATED**. No threshold rescue, no redefinition. The mean has the predicted sign but independent robust replication was not established.

Per-trial R changes in sorted source filename order (pp): +3.327122, -8.901102, -3.024619, +4.386114, -4.172362, -2.766723, -2.725941, -2.745844.

## Secondary controls in zebrafish (exploratory)

| Signed loss contrast | Relative to GLOBAL MSE, short / delayed (%) | Relative to Dg, short / delayed (%) |
|---|---|---|
| Near over GLOBAL | .079375 / .086753 | 2.277265 / 1.951741 |
| Far over GLOBAL | .118643 / .154303 | 3.403886 / 3.471452 |
| Correct mapping over rotated | .083072 / .090076 | 2.383335 / 2.026490 |
| Near over far | -.039269 / -.067550 | -1.126621 / -1.519711 |
| Current near over stale near | -.012751 / .030432 | -.365831 / .684654 |

Correct position assignment adds positive predictive information in 6/8 short and 7/8 delayed trials. However, FAR_TRUE has lower mean MSE than NEAR_TRUE in both horizons; far gain relative to Dg increases slightly, contrary to a universal relative decay across all local contrasts. Proximity advantage has 6/8 positive short, 3/8 delayed; means are negative in both. Effects are small and heterogeneous. These are observational, conditional prediction differences, not causal neighbor choice, physical range or signal propagation. Near increment itself increases slightly with horizon. The global gain grows relatively more.

## Independent numerical reaggregation

Downloaded the original v46 result artifact and three prior pinned source-safe artifacts (v42 tetra 14925460476, ayu 14923998689, v33b 14906668781). Independently recomputed equal-unit MSE differences, R and sign counts directly from the archived per-unit score matrices with NumPy, without importing the training pipeline. Verified v46 ratio, sign counts, 10,000-draw bootstrap quantiles and delete-one ranges to absolute 1e-12. Earlier three study summary ratios and counts reproduce. Separate bootstrap stream restarted per study in this independent audit; minor previous-source quantile differences are Monte Carlo variation, not original model differences.

## Biological interpretation and next analysis

The original hierarchy is a useful conditional pattern, not universal. Prioritize why the small additional near prediction gain varies between shoals. A constrained two-room/corridor environment is a plausible candidate, but causal environment effects cannot be inferred by comparing zebrafish with the other species: arena, species, group size, tracking and experimental setting differ.

Next candidate: source-authenticate room and corridor coordinate boundaries and per-recording orientation, then freeze contemporaneous room residence / mixed-zone / corridor states from present positions alone. Evaluate the same 6 fixed panels and two horizons within those states, retaining whole-trial holdouts, all signed scores, minimum pre-specified support, positive-Dg gate and explicit missing-state STOPs. Do not infer physical arena boundaries from future prediction outcomes; if coordinate calibration is unavailable, stop or separately label non-spatial polarization/dispersion as a different endpoint. This is a mechanistic hypothesis, not a completed test.

Main unchanged. Original frozen v44 endpoint and failed gate preserved. Draft PR #252 remains unmerged.
