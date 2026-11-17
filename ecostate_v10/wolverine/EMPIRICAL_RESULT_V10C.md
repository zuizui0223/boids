> **v10g SOURCE-LABEL AUDIT (2026-11-17):** Independent re-fetch of original source shows **100% (17,338/17,338) of observed rows in source worksheet 2 have exactly identical start/end values for road, stream and traffic**, against **2.63%** of alternatives. A one-feature predictor using only exact road+stream equality achieves **+2.096 nats/stratum** over uniform candidate choice (31-animal bootstrap [+1.787,+2.369], 30/31 positive). This is a **post-result data-structure diagnostic**, not ecology. The scientific HOLD on active road-state fidelity is reinforced. See [v10g source audit](../results/wolverine_source_label_leak_v10g.json) and [superseding claim ceiling](SCIENTIFIC_SOURCE_HOLD_V10F.md).

> **v10f SCIENTIFIC HOLD (2026-11-17):** The original v10c predictive scores below are numerically reproducible, but their interpretation as wolverine road-state fidelity is **not scientifically admitted**. A checksum-pinned source audit found exact simultaneous road/stream start-end equality in **85.15% of used** vs **2.26% of available** rows, still **83.37% of used steps longer than 100 m** vs **0.98% of comparable available**. This source-structure disparity can itself predict the used label; the mechanism and attribute extraction semantics are unknown. See [v10f superseding scientific HOLD](SCIENTIFIC_SOURCE_HOLD_V10F.md). The frozen v10c numbers are preserved only as a source-table prediction result. **Do not cite them as an ecological state-maintenance effect.**

# Wolverine start-state conditioned movement choice — original field v10c

**16 November 2026. Original-data exploratory reanalysis; no submission.**

## Question and source

Can the ecological state at the beginning of a movement — here, distance to roads and traffic exposure — add predictive information about which endpoint a wolverine chooses, beyond destination road/traffic/stream context, movement length and daily timing? This is narrower than claims of learned state fidelity, active buffering, or movement-mediated compensation.

Original public workbook: Scrafford et al. (2018), *Behavioral Ecology*, DOI 10.1093/beheco/arx182, Zenodo record 5011732 (original source MD5 `6d694faeadde68fbce1c0b45632aa21c`, SHA-256 `979a362af1acaff069a7c53dfabf5284eb68d0c448899858ae18be999513b1bd`). Original material was read ephemerally on CI and is not redistributed. Both source sheets preserve exactly 17 columns (original `id,cluster,used,SL_m,road_start/end,traffic_start/end,stream_start/end`, etc.).

## Outcome-blind source-group admission and preregistered analysis

Original: 794,955 candidate rows, 37,855 matched movement choice sets and 31 source animal IDs. All passed the source-defined structure (one recorded used and 20 generated alternatives per set), numeric finite-domain and start-context equality checks. No groups were dropped. Five SHA-ordered whole-animal folds; 7/6/6/6/6 individual IDs. Train-only covariate normalization, bear/wolverine-ID-equal training weighting and whole-animal mean held-out log-loss. Penalized conditional logistic choice, fixed L2 0.02. Primary test specified before biological outcomes were opened. Bootstrap over whole animals (10,000 resamples); two independent original-source CI reruns returned numerically identical outcomes (same SHA-256 for result JSON).

| Frozen model | Equal-animal held-out negative log-choice probability (nats per movement) |
|---|---:|
| M0, destination context and movement geometry | 3.020108 |
| M1, M0 plus `abs(log1p(road_end)−log1p(road_start))` | 2.389656 |
| M2, M1 plus `abs(log1p(traffic_end)−log1p(traffic_start))` | 2.236575 |

**Frozen primary M0→M1 PASS**: improvement 0.630451 nats/movement, 95% whole-animal interval [0.431425, 0.813347], 27/31 animals positive, five/five trained road-divergence coefficients negative (roughly −2.58 to −3.16 on standardized scale). Median animal effect +0.885708. Independent sign-only one-sided 27/31 tail p ≈1.70e−5 (post-result supplementary inference).

**Secondary M1→M2**: improvement +0.153081 [0.118518,0.188214], 30/31 animals positive, negative added-traffic coefficients in all five fits.

Post-result one-animal deletion of the fixed individual gain estimates, *without any model refitting*, gives mean primary gain +0.61229 to +0.68502, retaining the positive direction. This is an **influence diagnostic added after results**, not a new preregistered analysis.

## Ecological interpretation with hard limits

There is substantial information about real candidate endpoint selection in differences between the beginning and end of a step in road- and traffic-associated exposures, beyond the original M0 covariates. Thus destination conditions alone are an insufficient representation of the observed choice process in this source. This does **not** identify intentional maintenance of a preferred road exposure, adaptation, learned habit, energetic gain, or complete reachability of simulated endpoints. Absolute divergence can encode movement geometry and local spatial autocorrelation even when animals have no explicit state-maintenance goal. Source `used` versus generated alternatives can be correlated with the generator's choice of movement-distance/direction and endpoint landscape geometry. The source includes no independently observed prey intake, movement cost intervention, survival or fitness consequences. The 2018 original study already reported road avoidance and traffic-related behavior; the added contrast is cross-individual transfer of origin-dependent endpoint information.

**Mandatory next scientific audit (post-result, not rescue):** hold movement-length alternatives roughly matched and compare absolute road/traffic divergence ranks with a non-road stream-origin–endpoint divergence. Separately evaluate whether a baseline that already includes stream-divergence retains additional value from road-divergence. Regardless of audit outcome, this is one-study observational evidence and not a cross-taxon mechanism.

Source pipeline/CI: [GitHub run 43892071770](https://github.com/zuizui0223/boids/actions/runs/43892071770), artifact `14237187624`. Snapshot is archived in `ecostate_v10/results/wolverine_field_v10c.json`.
