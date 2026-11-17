# v11 water-buffalo same-raster state continuity: original-data result

**Date:** 17 November 2026  
**Status:** original public source acquired and checksum verified; two independent GitHub Actions replays; **frozen primary numeric gate FAIL**; ecological mechanism **NOT ESTABLISHED**. No journal submission or merge.

## Scientific aim

Determine whether familiarity with the *origin's local environmental state* improves endpoint-choice prediction beyond endpoint conditions, turning geometry, and time of day. This is explicitly distinct from the original study's known diel movement and habitat-choice dynamics. The intended hypothesis is not that every buffalo always uses the same habitat, but that there could be a preference for retaining canopy/herbaceous state after conditioning on where it can reach.

## Original source and admission

Forrest et al. (2025), *Ecography*, e07421, DOI [10.1111/ecog.07421](https://doi.org/10.1111/ecog.07421). Original data [Zenodo 13749246](https://zenodo.org/records/13749246). Verified `buffalo.csv` provider MD5 `37d50a37a0271f4b9ee8ba1707d1d8a8`, **16,838,962 original bytes**, source SHA-256 `95224a0f22dbb12384b9cf2cad4f37c999786183152b2e861f12f352f41eae58`, **133,161 native GPS rows** with timestamp/lat/lon/node. Three additional original raster sources `canopy_cover.tif`, `veg_herby.tif`, `slope_raster.tif` had their provider MD5s and downloaded SHA-256s independently verified. All three rasters use `EPSG:3112`, 2,280 × 2,400 cells; 25,000 subsampled original GPS positions had valid values in **all three**, 133,161/133,161 GPS positions and timestamps passed basic coordinate/parse checks.

**Critical unit caveat:** native `node` has **20 distinct source tokens**, versus **13 high-quality female buffalo** represented in the published ecological paper (17 originally tagged). The exact node-to-biological-individual crosswalk is **not verified**; results below are **source-node-blocked**, not necessarily biologically independent buffalo. Therefore 17 node tokens are not represented as 17 independently established animals.

## Real original-data evaluation, prespecified source contrast

Pairs of sequential ~hourly fixes were screened for 45–75-minute timestamps and source GPS step lengths 20–5,000 m, and selected at most 900 groups per eligible node by deterministic evenly spaced ordering before habitat values were inspected. For each admitted original movement, exactly **20 same-length bearing-only alternatives** were built from the identical start point; canopy/herbaceous/slope were sampled for actual and alternatives with the **identical raster transform and NoData gate**. This prevents original-used-case-only start/end covariate copying as an input to the model. The generated directions are geometric alternatives and do not establish a completely passable landscape or a true available resource portfolio.

Models (conditional softmax among 21 candidates, 5 entire-node-disjoint folds; fixed L2 penalty 0.02; training-only scaling):

- **M0:** endpoint canopy cover, herbaceous state, slope, movement turning cosine/sine, and hourly cyclic interactions with canopy and herbaceous state.
- **M1:** M0 plus absolute `canopy_end − canopy_start` and source/end herbaceous state-change indicator.

**Original field gate** required source-node-equal mean heldout improvement lower 95% bootstrap >0, at least 65% positive source-node tokens, and both source-change coefficients negative in at least four of five folds. Source nodes were the independent resampling strata for the reported numeric uncertainty (not yet verified biological individuals).

## Results — field numeric gate FAIL

- **17 original source-node tokens**, **14,554 matched observed steps**, **305,634 total used+alternate candidate rows**.
- Mean equal-node heldout NLL **M0 2.9383957**, **M1 2.9367502** nats/choice.
- M0−M1 average **+0.00164551 nats/choice**; node-bootstrap 95% **[−0.00017635,+0.00341526]**, with **11/17** source-node differences positive and 6 negative.
- Both source-change coefficients were negative in all five folds, but the lower interval did not exclude zero and 11/17 does not meet the 65% requirement (ceil 11.05 = 12); **prespecified gate FAIL**. The average relative log loss improvement is only approximately **0.056%**.
- Source QC: 30 duplicate node×timestamp rows were excluded without choosing duplicates; 51,234 candidate hourly triples preceded deterministic subsetting; 17 source nodes had >=100 eligible hourly triples; per-node kept between 200 and 900 for heldout scoring.
- A separate zero-signal synthetic negative-control test on 1,000 matched groups produced a near-zero improvement (~0.000001 nats) and FAIL. The original GitHub CI also passed seven source and model consistency tests.

**Original evidence:** [source-only run #44012708698](https://github.com/zuizui0223/boids/actions/runs/44012708698); [native GIS QC #44013006807](https://github.com/zuizui0223/boids/actions/runs/44013006807); [field calculation #44013554427](https://github.com/zuizui0223/boids/actions/runs/44013554427), with a separate [pull-request original replay #44013627440](https://github.com/zuizui0223/boids/actions/runs/44013627440) yielding **identical effect estimates and categorical FAIL**. The archived original machine receipts are in `results/` (no original coordinates or source node strings exported).

## What this does and does NOT mean ecologically

1. **Supported:** source environmental-state continuity *features* can be calculated symmetrically, and their heldout incremental predictive effect was tiny and **not robustly established** under the fixed test. Thus the observation that animals use changing habitat conditions cannot be substituted for evidence that they actively retain a prior state.
2. **Not supported:** intentional state fidelity, adaptive buffering, individual niche conservatism, environmental portfolio exhaustion, or any species-wide universal difference based on this result. The observation is in a single Australian study and subset of three static habitat axes; no monthly NDVI or water-level changes were included in the v11 outcome models. The original authors' already established diurnal habitat selection and movement results are unchanged.
3. **Audit advantage:** unlike Wolverine v10, actual and generated candidate environment fields use the same native raster source, same start point, and identical raster extraction. The former Wolverine v10 source had massive used-label-dependent field equality (100% observed triple equality in one worksheet), so its original +0.630-nat `state fidelity` signal is scientifically ON HOLD. The two source studies differ in species and environmental endpoints and **cannot themselves establish a cross-taxon effect contrast**.
4. **Next independent science:** prior to any new biological outcome, verify one-to-one source node→animal identity; register a truly dynamic, same-time reachable-choice habitat variable (e.g. monthly source NDVI with explicit time index or direct hydrology), and retain within-animal, between-animal and between-study holdouts. DO NOT re-tune v11 thresholds or select individual IDs after inspecting the negative field result to rescue the claim.

## Publication allocation

v11 is a **source-backed exploratory negative empirical test**, worth retaining as a transparent independent boundary case, but not yet evidence for a positive general mechanism or stand-alone publication novelty. The prior supported King Rail environmental buffering, bat individual vertical profiles and Serengeti species-specific activity need to remain separately defined. The appropriate synthesis statement is that habitat state **choice**, **retention**, and **predictability/transfer** are distinct ecological observables; their common mechanisms remain untested.
