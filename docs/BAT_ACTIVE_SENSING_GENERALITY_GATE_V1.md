# Bat active-sensing margin: prospective cross-context mechanism programme (v1)

**Created:** 2026-11-18 JST  
**Status:** SOURCE/IDENTIFIABILITY PREFLIGHT ONLY. No new wildlife outcome, fitted coefficient, effect or universality claim.  
**Scope:** new `boids` exploratory programme; do not change frozen `batter` / `boids` v6, v8, v15, v16 or v28 primary tests.

## Why this replaces descriptive 'individuality exists' repetition

The original `batter` result demonstrates repeatable individual vertical profiles without obligatory contemporaneous vertical partitioning. This is not itself a generative movement law, and externally frozen bat panels show heterogeneous replication. A useful next programme must predict **action selection** in an environmental context rather than repeat another identity test.

The research target is an **information-limited steering budget**: under specific geometrical and acoustic sensing constraints, when does an echolocating bat (i) slow down, (ii) shorten pulse intervals / direct acoustic gaze forward, or (iii) turn away or leave an acoustically impaired area?

### A falsifiable dimensionless exposure

For a time point strictly **before** a change in movement, define

`q(t) = v_pre(t) * IPI_pre(t) / [d_free(t) * p_usable(t)]`

where:
- `v_pre`: observed flight speed from pre-outcome trajectory samples (m/s);
- `IPI_pre`: preceding sonar inter-pulse interval (s);
- `d_free`: **independently** measured free distance ahead (m) to the relevant obstacle or neighbour, along the pre-event path/beam; not estimated from eventual turning or observed future locations;
- `p_usable`: probability of obtaining a usable echo from one pulse, from independent calibrated acoustic availability / masking observations, **not** fitted to the future action.

`q` is dimensionless. If successive usable echoes are independent Bernoulli events, `IPI/p_usable` is the expected waiting time for a usable echo, and `v*IPI/p_usable` approximates travel distance in that interval. Independence is an explicit modelling assumption, not a bat physiological fact.

**Physics-only lower bound:** `q_lb = v_pre*IPI_pre/d_free` under `p_usable = 1`. This is **not** an estimate of true echo reliability. If `p_usable` or `d_free` cannot be independently determined, stop before claiming the primary sensing law.

Optional separately measured response latency `tau_motor` would give `q_motor = v_pre*(tau_motor + IPI_pre/p_usable)/d_free`; do not invent latency, fit it from the target outcomes or select it after outcomes.

## Competing ecological predictions

**H1: sensing-margin compensation.** Higher *pre-event* `q`, holding pre-event kinematics and geometry constant, predicts a larger *subsequent* reduction in speed, shortening of IPI, increased future-directed acoustic gaze, or a reorientation toward open space. These endpoints are analyzed separately; an endpoint-specific sign is prespecified only when source conditions permit it. Compensatory modes may switch when echo availability collapses.

**H2: geometry/motor-only alternative.** Turn direction, angular speed, speed reduction and exit probability can be forecast from position, pre-event velocity, obstacle geometry and prior turns; adding pulse/gaze/masking information does not improve held-out prediction. If H2 fits equally well, do not label mere temporal correlation as active-sensing control.

**H3: species-specific policy alternative.** Species, sensing guild and fixed laboratory apparatus predict different response surfaces even at matched sensing margins. A non-invariant policy falsifies the strong scaling-law claim. Guild-specific differences are a valid positive *ecological boundary*, not an analysis failure to hide.

**H4: patch escape under interference.** Unlike geometric clutter, unresolvable acoustic interference can favor spatial escape and straighter/faster passage, so the signs of raw speed change need not be shared across disturbances. Directly compare mode-selection outcomes and avoid pooling incomparable speed changes.

These are hypotheses, **not observed results**. Already-established prior findings include anticipation of turns by sonar gaze, clutter-dependent speed/sonar changes, masking-associated collective dispersion and altered flight under acoustic deterrents. Novelty requires out-of-source *incremental prediction* and/or a bounded context-dependent response transition; re-describing these published effects is insufficient.

## Verified public source inventory (metadata/reading only)

| Source | Published data and usable structure | Main limitations / gate |
| --- | --- | --- |
| Eveland et al. 2026, J Comp Physiol A, DOI [10.1007/s00359-026-01818-0](https://doi.org/10.1007/s00359-026-01818-0) | Two differently echolocating frugivorous bats, `Rousettus aegyptiacus` (12 individuals in paper) and `Carollia perspicillata` (8); acoustic gaze, 3-D tracks, 90/180-degree corridor turns. Public GitHub [00keveland/Tunnel_2026](https://github.com/00keveland/Tunnel_2026) has **30** per-trial `Trial_Data_Carolia/*RESULTS.mat` files with labels C1–C8 and `CAROLLIA_POP_FINAL.mat`. | A full, non-truncated 80-path recursive tree audit did **not** expose the `ROUS_PlotBundle.mat` referenced by its analysis script, and scripts contain local `R:\\Keegan\\...` paths. Do not claim reproducible two-species raw joins or species-general effect until both are verified. Output documents and author results are already visible (gaze lead reported 77%, 70%). |
| Goldshtein et al. 2025, PNAS, DOI [10.1073/pnas.2407810122](https://doi.org/10.1073/pnas.2407810122) | `Rhinopoma microphyllum`; 37 and 59 simultaneous tracked bats in two years, 4 tagged audio subjects. Deposited movement/audio + code: Mendeley [10.17632/k7pt2j84f7.1](https://doi.org/10.17632/k7pt2j84f7.1). | Need original raw file/clock linkage and independent microphone sensitivity to estimate `p_usable`. Published group spreading and masking result must not be presented as new independent discovery. |
| Gilmour et al. 2021, Journal of Experimental Biology, original dataset [10.17632/gb45nfkkk5.1](https://doi.org/10.17632/gb45nfkkk5.1) | Outdoor acoustic deterrent/control data, trajectories, bat calls and echolocation parameters, CC BY 4.0. | Need verify whether trajectory/call data are linkable to the *same* bout and known stimulus geometry. Otherwise secondary contextual comparison only. |
| Delmotte et al. 2025, Behavioral Ecology, [10.1093/beheco/araf090](https://doi.org/10.1093/beheco/araf090); Dryad [10.5061/dryad.6q573n6b0](https://doi.org/10.5061/dryad.6q573n6b0) | Public CC0 `data.csv` + `R_file.R`; reconstructed 710 bat 3-D foraging trajectories, 16 sites and five focal species in one French landscape, species co-occurrence, speed, feeding buzz. | Useful independent *social-context action-selection* panel and site-heldout prediction; source contains **trajectory summaries, not synchronized per-pulse data or validated individual identity**. Cannot fit `q` from this source; do not call 710 trajectories 710 independent bats. Already-published heterospecific effect is not novel replication. |
| Teshima et al. 2026, Proc R Soc B, [10.1098/rspb.2026.1463](https://doi.org/10.1098/rspb.2026.1463) | `Rhinolophus nippon` and `Miniopterus fuliginosus` in seven obstacle arenas; latent flight-policy prediction reported. | Published summary verified, original joint per-pulse track files not yet acquired or admitted. No assumed open trajectories or independent full raw replication. |
| EuroBaTrait 1.0, Froidevaux et al. 2023, Scientific Data, [10.1038/s41597-023-02157-4](https://doi.org/10.1038/s41597-023-02157-4) | 47 European species, 118 traits including acoustics, morphology, diet, foraging and spatial behavior. | Comparative morphology/guild covariates only; not direct action observations, not global sampling, not an independent validation of a motor law. |

### First admission gate, *before* any new behavioural fit

1. Inventory original files, version, license, checksums and coordinate/timestamp units. Preserve verified original sources; do not redistribute raw animal telemetry automatically.
2. Confirm original trial/animal/source identities, repeated bouts, pre-event 3-D trajectory and synchronized acoustic pulse times. Distinguish number of frames, pulses, turns, trials, animals, sites, species and independent field populations.
3. Establish obstacle geometry / independently measured local acoustic masking and `p_usable` support. For a full `q` test, each event must have `v_pre, IPI_pre, d_free, p_usable`. Report support and missingness **before** reading future behavioral endpoints.
4. Maintain a separate source eligibility result with `ADMITTED_PRIMARY`, `ADMITTED_SECONDARY` or `STRUCTURAL_STOP`; never treat a source blocked for missing inputs as a failed biological hypothesis.
5. Source-matched sensor-lag, acoustic source clipping, preprocessing, downsampling and tracking error must be audited. Spline/resampled trajectories do not create independently observed high-frequency positions.

## Prediction test design to freeze before outcomes

- **Unit:** original animal/field site/trial at the highest independence level available. Never treat pulses or consecutive interpolated fixes as independent tests.
- **Time:** strict pre-event predictors at `t`; response at separately frozen `t+h` (h chosen from original sensor cadence and pilot *source-only* support, not from a favorable test outcome). No target/future turn geometry or observed future nearest neighbour enters `q`.
- **M0:** pre-event velocity, acceleration, bearing/turn history, and source-specific geometry (no acoustic features).
- **M1:** M0 + raw independent IPI and gaze observations, each pre-event (no `q`).
- **M2:** M1 + pre-event acoustic masking/usable-echo rate and precomputed `q`; compare against M1 to test incremental value of a cross-context scaling variable.
- **Primary outcome:** held-out, pre-specified future heading-change direction and/or absolute turning (choose ONE within each admitted source **before** target output). Secondary: ensuing deceleration, pulse-rate change, patch exit. Report physical units, calibration and model-specific baselines.
- **Holdout:** whole bats, then whole original apparatus/site/condition. Cross-species/family holdout is the generality tier. No random pulse-level train/test split. Avoid tuning on target species or source after scores are read.
- **Decision:** report signed out-of-sample improvement in log score (or predeclared bounded alternative), independent-cluster interval, per-source directional consistency, and full negative cases. A generality claim needs at least two independent source-level positive confirmations under harmonized endpoints; a robust *cross-species* law additionally needs held-out species prediction in genuinely distinct sensing guilds.
- **Controls:** randomly relabel pulse streams **within an appropriate animal/condition block** preserving gaps; shift pulse times in pre-event windows; compare raw motor-only and geometry-only models; confirm `q` is not a disguised velocity or object-distance predictor; use no future lookahead in preprocessing.
- **Failure:** if only M0/M1 succeeds and M2 does not transfer, reject the single-margin universality claim. If `q` cannot be computed from at least two independent sources, report a source identifiability stop, not a mechanism finding. If sensor error exceeds physical action signal, stop as an observation-resolution problem.

## Connection to existing 3-D niche individuality

Only **after** action-policy predictability is independently demonstrated should one simulate or predict long-run `p_i(x,y,z)` from a fitted policy; otherwise the original `batter` profile result is a *separate observation*. The relevant bridge is a new predeclared test:

`new-source 3-D use map forecast from policy + habitat geometry > habitat-only forecast`

with whole-animal/site holdout. A policy that reproduces `batter`-like shapes on synthetic trajectories is not by itself field validation, and bat sensory rules cannot be inferred from a bird/duck or simulated Boids source.

## Status at close of this v1 audit

- **Completed:** mechanism question, explicit predictor/response separation, physical lower-bound formula, competing hypotheses, public source/availability inventory and go/no-go criteria.
- **Not completed:** raw cross-source harmonization, original-file checksums for the new acoustic sources, numerical species/site-heldout prediction, a common acoustic usable-echo estimator, or any new causal inference.
- **Next executable task:** source-only file/schema audit for `00keveland/Tunnel_2026`, then separately the PNAS/Mendeley movement/audio archive. Stop and record missing ROUS source components if no joint per-turn/call data are available. Do not rescue by relaxing units or inventing coordinates.
