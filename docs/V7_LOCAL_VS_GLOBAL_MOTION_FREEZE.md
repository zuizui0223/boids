# v7 frozen local alignment versus whole-school common motion

**Freeze before new v7 numerical outcomes** 2026-11-20; original v5/v6 effects already opened and all results **exploratory**, same one species/6 recordings.

## Purpose

v6 Puy et al. original 8-fish data, 6 full heldout recordings: geometry-only+alignment had **+2.412116 (cm/s)²** mean extra gain relative to geometry-only, 6/6 signs. That does not distinguish local neighbor influence from a common school velocity signal. If all fish are moving in the same direction because of one global cue, every fish's neighbors can predict its next step without actual local steering.

## Frozen models (all source target/test rows unchanged)
Exact six original 2024 recordings, 50 fps, 100cm/2745 px, 0.2sec target, 25cm neighborhood, 8cm separation, ridge alpha10, training other five whole recordings / scoring the heldout recording. Do NOT tune model by withheld outcomes.

- G = own motion+wall + present neighbor repulsion, cohesion, neighbor count (source-v6 geometry).
- G+Global = G plus mean velocity of **other seven fish minus focal fish's velocity**, two features. This describes global (whole-school) contemporary motion regardless of local distance.
- G+Local = exact original v5 full-Boids: G plus *within 25cm* mean relative neighbor velocity (2 features).
- G+Global+Local = both global and local components appended, same target data and ridge alpha.
- G+LaggedLocal = G plus 2s-old (pre-existing) neighbor relative velocity, **but G still current**, equal dimensions. An absolute 2s lag is a fixed specificity diagnostic, not an exchangeable null.

**Primary v7:** MSE(G+Global)−MSE(G+Global+Local): does nearby fish alignment retain incremental information after the whole-group motion field is known?
**Secondaries** MSE(G)−MSE(G+Global), MSE(G)−MSE(G+Local), MSE(G+Local)−MSE(G+Global+Local), and stale-local vs current-local on identical G.

## Required gates
Published source MD5 checks all six before reading numerical outcomes. Frozen v5 M0/full precise MSE and v6 geometry MSE must replay per recording (absolute tolerance 2e-5 for precise, 6e-5 for printed geometry). If any fails, **SOURCE_REPLAY_STOP** before new inference. Source 39-fish recordings excluded under earlier cap.

Trial-equal mean MSE, six individual recording signs, nominal exact one-sided sign p only if recordings independent, and 5000 whole-recording resampling interval. No new tuned horizon, radius, eligibility or penalization after v7 outcomes. Source smoothing and repeated fish prevent causal or population-general claims.

## Ecological claim boundary
Positive local conditional increment supports **incremental predictive information from local neighbors beyond group-level velocity**, not a Reynolds force, neural behavioral rule, perturbation or biological causality. If nonpositive, the v6 alignment success may be **common school motion rather than local social selection**. The source has no fish calls and cannot establish sound chorus.

Code `validation_fish_school_v7/local_global.py`, known-truth tests and `.github/workflows/fish-school-v7-local-global.yml`. PR remains Draft.
