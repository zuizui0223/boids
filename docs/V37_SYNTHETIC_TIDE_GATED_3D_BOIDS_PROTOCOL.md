# v37 — Synthetic 3D Boids + tidal-resource state transitions: mechanism sufficiency, not empirical validation

**Frozen 2026-10-31 JST.** This study was explicitly designed AFTER viewing real Schiermonnikoog v33/v34/v34B oystercatcher results (v33-D high-level slow vs low-level fast, v34 low-water ebb faster, high-water flood faster). Its primary outputs are synthetic numerical demonstrations of **sufficient and unnecessary mechanisms**, NOT independent bird data, prediction on heldout wild populations, or any causal estimation of actual foraging, mudflat exposure, memory or Boids forces. No original GPS, RWS water heights, seabed DEM, ecotope polygons or external biologic files used.

## Target qualitative signs and hypothesis

The pattern to generate is the three-signed motif:

1. High astronomical tidal water **−** low tidal water mean log1p(horizontal displacement speed) negative (overall low-water activity).
2. At LOW tide water H < +0.5m in original reference, mean **ebb−flood** log speed positive.
3. At HIGH water H >= +0.5m, mean **ebb−flood** log speed negative.

These three signs were already known from the observed source and are a **target of construction**. Model's success is *theoretical consistency*, not a new ecological discovery from independent field observations.

### Synthetic physical setup

- One dimensionless synthetic slope/intertidal shelf elevation distribution, not sampled from a real shore: `z_min=-1.15m`, `z_max=+1.25m`, uniformly distributed sediment heights, fixed in model land units. Fraction of *toy exposed resource* `A(H)=clip((z_max-H)/(z_max-z_min),0,1)`. This is a **mathematical proxy**, not remotely sensed mudflat exposure.
- Synthetic astronomical sea water height `H(t)=1.2 sin(2π t/12.4206h)+0.09 sin(2π t/(14.77×24h))` meters in an arbitrary local vertical datum. The approximately semidiurnal and spring-neap astronomical frequencies are plausible but **not calibrated to RWS**. Synthetic ebb/flood is sign of successive analytic H derivative; report sign on all snapshots. Day/night, meteorology, sediment, prey, population biology and phenology not modeled.
- Sampling/integration `Δt=1/6 hour` (10 min), simulation 24 days, first 48h removed as burn-in, **30 artificial agents** per experiment, **24 fixed RNG seeds 0..23**. No field sample size or confidence intervals inferred from artificial 30 agents/24 seeds.
- State labels: `ROOST`, `OUTBOUND`, `FORAGE`, `INBOUND`; policy leaves roost on **ebb** once toy exposed fraction rises past (A_{enter}=(1.25-.35)/2.4=.375) (equivalently H<+.35m), travels for **0.65h**, then forages. It returns on **flood** once resource A falls below (A_{exit}=(1.25-.85)/2.4=.1666667) (H>+.85m), travels **0.65h**, then roosts. State-specific speeds (km/h): rest **0.09**, outbound/inbound **4.0**, forage **1.1**. This is constructed after observing the empirical sign pattern; **the threshold .5m in the motif is not inferred as a universal ecological threshold**. Fixed lognormal step speed noise sd=.03, heading noise scale=.04; random original headings seed based only on model RNG.
- 3D kinematic agents update positions (r_i=(x_i,y_i,z_i)), headings, and speed over time. Velocity is normalized 3D heading times state speed, observations measured from the **horizontal (x,y) component** of consecutive 3D positions. No local resource DEM sampling, no actual headwind and no predator.
- Steering with social motor: radius 0.6km, separation 0.12km, neighbor alignment, cohesion and separation using fixed weights **align=.14, cohesion=.08, separation=.20**, inertial self weight 1; distance-weighted separation. Social rules act on **heading only**, not latent tide states or speed. Motor OFF suppresses all neighbor terms, same noise model. A 3D Boids motor is a *toy positional rule*, not identified animal flock force.

### Six registered ablations, no result-directed substitution

A0 **NO_TIDE_NO_SOCIAL:** fixed .60km/h; headings inertial + noise, no tidal mechanism.
A1 **HEIGHT_ONLY_NO_SOCIAL:** memoryless speed `0.09 + 1.10*A(H)` (monotonic low-water activity), independent of ebb/flood and state.
A2 **PHASE_ONLY_NO_SOCIAL:** speed `0.40+0.70*I(ebb)` (phase only), independent of absolute height, state or memory.
A3 **HYSTERESIS_NO_COMMUTE_NO_SOCIAL:** environmental threshold-dependent ROOST/FORAGE state memory but instantaneous change and respective speed .09/1.1; no outbound/inbound transient 4.0km/h.
A4 **TIDE_STATE_GATE_NO_SOCIAL:** four-state crossing/hysteresis + finite commute, no Boids social steering.
A5 **TIDE_STATE_GATE_WITH_3D_BOIDS:** same state machine/commute plus 3D Reynolds-like heading alignment/cohesion/separation with fixed source-independent coefficients.

These are not fits to original animal GPS. The model has no taxon labels; each "agent" is synthetic.

## Primary synthetic estimands and interpretation

For each seed×ablation after burnin:
- `high_minus_low` = mean log1p(horizontal synthetic step km/h) at H≥+.75m minus H≤−.75m.
- `low_ebb_minus_flood` = mean of ebb−flood horizontal log speed at synthetic water height H<+.5m, **matched on original source-independent 0.5m height bins**, i.e., first each bin with both ebb/flood then equal-bin mean.
- `high_ebb_minus_flood` = same at H≥+.5m, height-bin matched.
- `low_minus_high_phase_difference` = previous two contrasts subtracted.
- Additional descriptive per-height-band `[0,.5)`, `[.5,1.0)` ebb−flood contrasts, and mean finite 3D speed, state fractions, social motor neighbor counts.

**Registered motif:** high_minus_low negative; low phase difference positive; high phase difference negative. Count how many of **24 artificial seeds** satisfy all three signs per ablation. Report every seed's complete signed outputs, all ablations and their all-seed mean and min/max. No statistical p-value for synthetic 24 seeds as if they were real biological sites. If state-gating fails, report failure and DO NOT tune thresholds/commute duration to force positivity within this v37; any subsequent construction must be a named follow-up separate experiment.
- Motor A5 vs A4 tests whether the 3D social steering is **needed for sufficiency in this constructed world**. If A4 succeeds, social alignment/cohesion are **not necessary** for this particular three-sign pattern; the result does not say these social forces are absent in wild birds.
- A3 vs A4 tests whether explicit transition/commute speeds matter in this constructed world; A0–A2 show which simple processes can or cannot suffice.

## Validation and audit

1. Commit this protocol to a separate branch from main before the code output run.
2. Implement numpy-only deterministic source-free simulation with known-truth tests for source-free tide periodicity, resource monotonicity, no future information, state transitions including hysteresis, 3D position updates, Boids heading-only steering, ablation controls and equal-bin aggregation.
3. Frozen run via GitHub Actions CI with all ablations 24 seeds, machine-readable full synthetic receipt, numerical replay and source-free assertion. Do not fail CI merely because biological sign motif is unsupported; failing models are informative and are reported.
4. No animal names, empirical GPS, original RWS tide data or mutable prior result numerics included. The observed v33/v34 and v35/v36 source STO P remain unchanged. No merge without review.

The next actual empirical step still requires dated spatially referenced local bed elevation, validated NAP↔DHHN2016 vertical conversion, source-known actual exposed flat area or directly labeled foraging/roost positions, and independent biological populations.
