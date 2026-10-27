# Ecological synthesis and prediction boundaries (2026-10-26)

## Conceptual mechanism

A 3D agent-based flight model updates individual position and velocity under separation, alignment, optional cohesion, resource gradients, environmental forcing, internal state and heterogeneous response parameters. Repeated trajectories induce state-use distributions \(p_{si}(x,y,z,t)\). Niche metrics describe **emergent outputs of the simulator**; they do not identify the unique generating forces in observed animals.

Relevant estimands include conditional mutual information \(I(S;Z\mid X,Y)\) for species-specific vertical niche organization after horizontal context, \(I(S;X,Y)\) for spatial partition, \(I(S;T\mid X,Y)\) for temporal organization, and \(I(i;Z\mid X,Y,S)\) for within-species individual vertical profiles. All are sensitive to sampling and grid scale. A mutual-information contrast is not itself evidence of causal competition.

## What has actually been checked

| Dataset or programme | Established result | What it can inform in Boids | Not established |
|---|---|---|---|
| [batter](https://github.com/zuizui0223/batter) | Four of four evaluable fruit-bat panels retained individual vertical-strategy fidelity; zero of four supported positive excess vertical segregation. | Individual strategy persistence without obligatory exclusive vertical allocation; individual state mixture and environmental-response hypotheses. | Learned memory, social-force coefficients, competition as origin, common universal policy. |
| [ODSP](https://github.com/zuizui0223/odsp) | Tadarida estimated ~4.02 effective vertical states while frozen cross-individual x-y-z transfer failed; Serengeti detected site-adjusted species-time organization with three positive independent held-out folds. | Differentiate thickness, identity partition and independent transfer; distinguish spatial versus temporal axes. | That added-axis thickness guarantees transferable niche organization. |
| [mina](https://github.com/zuizui0223/mina) | Effective monitored penguin breeding-component number fell 19–83% across five population units beyond a defined count-error null. | Couple movement/habitat selection to annual demographic and patch-occupancy dynamics with the same fixed-composition null. | That penguin patch contraction was driven by social Boids or specific competition rules. |
| [louis](https://github.com/zuizui0223/louis) | 10/10 tracked King Rails had positive used-state temporal retention; matched hydrological coupling was about 83.8% below pseudo-use null. | Explicitly model local environmental-state tracking and time-matched available states. | Direct geographic movement-causation from unjoined coordinates or species-general tracking law. |

## Model results (synthetic: not independently observed ecological effects)

- The original v2/v3 simulations varied resource heterogeneity, replenishment, consumption, individual identity, state preference and social forces. A pseudo-species' horizontal and conditional-vertical information sometimes shifted in opposite directions as resource depletion increased; the crossing depended on horizontal grid grain.
- A two-state behavioural mixture with persistent individual mixture proportions generated centered-height distribution identity; reshuffling mixture weights among simulated sessions largely removed it. This shows **a sufficient possible mechanism, not an exclusive explanation**.
- Cohesion without fixed resource preference generated between-group spatial segregation that failed next-night transfer under randomized initial conditions. Adding a stable species-level preference improved next-night transfer under this simulation design.
- Forecast interpolation on the **same simulator family** beat mean and nearest-condition baselines for several synthetic niche metrics on unseen parameter combinations. A second holdout was used to test prediction interval coverage after calibration on the first. This demonstrates surrogate performance conditional on the *known simulator*, not interspecific prediction from independent field data.

## Observed transition test (v4)

The public Movebank Tadarida annotated source yielded 8 individual bats, 16 BatDay sessions and 9,587 eligible three-location transitions in the external extraction. Read [`EMPIRICAL_RESULT_V4.json`](../boids3d_empirical_v4/EMPIRICAL_RESULT_V4.json) for exact definitions and values.

- M0: marginal vertical next-climb-class probabilities.
- M1: transition with previous climb class; **M1−M0 = +0.01383 nats/transition** (equal-individual mean; bootstrap 95% CI ~[+0.00672,+0.02113]).
- M2: adds an archived vertical wind class; **M2−M1 = −0.00113** (bootstrap 95% CI crosses zero).
- M3: adds same-bat other-night histories; observed matched M3−M2 = −0.00916, estimator null mean −0.01149; calibrated excess +0.00233; **whole-night permutation p=0.32**.
- Under a strict <=5s and <=100m cross-individual pair criterion, **0 pairs** were available. Thus a separation/alignment/cohesion parameter is not identifiable from this observed source.

**Provenance boundary:** full CSV text was consumed by a remote public-content extractor and reduced to aggregates. A raw-byte checksum of that exact extraction was not independently confirmed in the local execution. Local unit tests validate the code on synthetic records; raw archive re-execution with checksum is the stronger reproduction target.

## Synthetic observation-error identifiability audit (v5)

A separately authored [known-truth negative control](GPS_ALTITUDE_ERROR_IDENTIFIABILITY_V5.md) shows that independent true successive vertical velocities can produce positive held-out M1−M0 log-score gains after position-level GPS height errors are differenced. Thirty synthetic seeds per scenario under an illustrative 30-second cadence yielded +0.00483 nats/transition at 10 m and +0.02623 at 20 m altitude-error SD (true velocity lag-one correlation zero by construction). Observed climb-speed lag-one correlations were negative, approximately −0.132 and −0.290, while lag-two correlations were near zero.

These magnitudes **do not estimate the actual height error of the archived Tadarida tags**. The original observed +0.01383 nats/transition improvement is statistically predictive but does not uniquely identify physical inertia. Error-aware observations, new instruments or independent sensor validation are needed before assigning an animal-movement mechanism. The v4 empirical result and all source-repository frozen analyses are unmodified.

## Independent observed synchronous-bat-pair 3D forecast (v6)

A distinct public source, [Roy & Abaid bat pairs, DOI 10.7294/W4639MWR](https://doi.org/10.7294/W4639MWR), supplied 30 paired 3D flight episodes. The source was checked for exact size and MD5, and an outcome-blind preflight admitted 28 episodes. Spline-resampled tracks were numerically decimated by a predeclared factor 6; this must not be interpreted as an independent sensor measurement cadence.

An entire-pair leave-one-out ridge predictor of the next 3D heading-change vector compared own-history baseline, actual partner and fixed other-pair ghost partner. The frozen primary actual-versus-ghost improvement was **+0.00055484 mean 3D-heading-change squared error**, whole-pair bootstrap 95% interval **[-0.00009187,+0.00127598]**; 16/28 held-out episodes favored the actual partner. The improvement was not robust and was therefore **not supported**. See [the immutable v6 receipt](OBSERVED_BAT_PAIR_RESULT_V6.md).

This observed-data failure neither falsifies reported curvature information exchange nor proves its mechanism. Trial episodes lack reliable repeated individual identity, independent camera-error calibration, measured environmental geometry and verified acquisition timing. A single paired relative-position vector cannot identify separate social attraction and repulsion forces. No bat species-level 3D niche or interspecies partition forecast follows from this result.

## Empirical v8 pigeon and mathematical v9 transfer audit

The independent historical pigeon source (Zenodo 5010830, original DOI 10.5061/dryad.53f4b) supported **197/199** synchronized two-tracker flights, **320,723** matched GPS pairs, and **10 disjoint bird-identity-connected validation groups**. The frozen 1-second *horizontal next-turn* endpoint showed a +0.00031012 rad² secondary MSE gain for actual partner versus own history, but its **primary current-partner versus 10-second-stale partner** gain +0.00008669 had 95% group-bootstrap CI crossing zero; 6/10 groups improved (sign p=0.377). Therefore no unique contemporaneous social forcing has been identified, and this does **not** show 3D niche or species partition. [Read the complete frozen analysis](OBSERVED_PIGEON_V8_FROZEN_RESULT.md).

A separate, explicitly **synthetic** v9 structural identified-set calculation proves by construction that equal instantaneous steering at a fixed neighbor distance can correspond to different long-horizon spatial predictions at new distances. Five candidate coefficient pairs calibrated to 10 m produce a 30-second predicted pair-spacing interval **28.28–34.75 m** starting from 25 m, although all make an identical steering prediction at their calibration distance. This is only a mathematical counterexample about extrapolation, not a field estimate or environmental niche probability distribution. [Read the mathematical conditions and forecast ladder](MOVEMENT_TO_NICHE_IDENTIFIABILITY_V9.md).

These v8/v9 results are frozen as an independently checkable receipt and a known-truth warning; the original `batter`, `ODSP`, `mina`, `louis` files and source claims are unchanged.

## Falsifiable future predictions

1. With synchronized sub-second/second-scale 3D tracks and actual neighbor co-observation, social-force models should outperform a matched inertia+habitat-only transition model on held-out groups if social interactions are genuinely predictive in the sampled contexts.
2. If stable individual action-selection policies drive repeatable vertical profiles, adding independently measured behavioural state and fine environment should reduce self-history gain while leaving residual gains only where unexplained persistent individual policy remains.
3. If resource consumption produces genuine context-dependent niche-axis shifts, the predicted direction and magnitude of \(I(S;X,Y)\) versus \(I(S;Z\mid X,Y)\) should transfer to new localities and spatial grains declared *before* outcomes are inspected.
4. Local environmental heterogeneity is predicted to buffer experienced state when accessible alternatives are present; an absence-of-alternatives control should abolish buffering beyond the availability-matched null.
5. Breeding-component concentration must be assessed with population total held fixed in the null and an observation error model; an ABM may generate it but **cannot claim the penguin field mechanism** without measured resource/breeding substrate and demographic processes.

## Stop conditions

Do not reopen frozen batter/ODSP/mina/louis research outcomes for post-hoc model rescue. No positive wild multi-taxon Boids forecast has yet been demonstrated. Prior v1–v3 scripts and original outputs remain available in the archived snapshots and canonical v4 tree.
