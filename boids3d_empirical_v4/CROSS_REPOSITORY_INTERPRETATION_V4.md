# Ecological interpretation after first observed short-horizon test (v4)

Date: 2026-10-26. The results herein are independent **analysis outputs**, not modifications to frozen manuscripts. This is an **exploratory** sidecar program.

## 1. Exactly where Boids fits

A true Boids-style simulator has an individual state `q_i(t)=(r_i,v_i,h_i,m_i)` and a set of interactions and environmental controls `F_i`. A continuous stochastic acceleration sketch is

    dr_i(t) = v_i(t) dt
    dv_i(t) = [a_sep S_i + a_align A_i + a_coh C_i + F_resource + F_environment + F_memory - gamma v_i]dt + Sigma dW_i.

An observation model turns latent `q_i(t)` into sampled GPS/IMU events at irregular times, with vertical offsets and noise. This mapping must be explicit before fitting parameters.

If `K_theta(q'|q,E,R,neighbor)` is the measurable transition kernel implied by those rules, then the observable occupancy can be propagated via

    p_{t+1}(q') = Integral K_theta(q'|q, E_t, R_t, neighbors_t) p_t(q) dq.

For interacting organisms, the joint multiagent distribution or an explicitly justified approximation is required; a single-individual closed kernel is generally insufficient. The v3 synthetic ABM defines the forward arrow. The v4 real-data analysis measures only a **coarse vertical-climb-class transition** (down/level/up) as one small, estimable part of that kernel. It does *not* derive an empirical whole-3D occupancy forecast.

## 2. Ecological patterns as testable functionals

Define `S=species`, `I=individual`, `B=(X,Y)=horizontal cell`, `Z=height state`, `T=time bin`, `H=environment experienced`, and `J=breeding component`:

- Within-species identity: `I(I;Z|B,S)`, paired with held-out self-history log gain and null-corrected inference.
- Between-species horizontal differentiation: `I(S;B)`.
- Between-species vertical differentiation: `I(S;Z|B)`.
- Temporal niche differentiation: `I(S;T|B)`, with independent-site transfer and detectability adjustment.
- Environmental state tracking: stability of the used-state time series relative to time-matched local availability (louis); without matched availability, low variance alone is not evidence of active buffering.
- Spatial breeding concentration: `N_eff(t)=1/sum_j share_j(t)^2` and its deviation from a fixed-component-share count-error null (mina).

These are distinct; spatial differentiation is not competition, and an effective component number is neither occupied area nor population size. Species and individual metrics require sampling that covers comparable biological units. Information measures depend strongly on binning, sampling and detectability. Compare data at fixed, reported grains and avoid re-picking grains to obtain positive effects.

## 3. Observed-data v4 result and what it rules out

Complete public annotated Tadarida data were fetched through an external content reader. `EMPIRICAL_RESULT_V4.json` preserves aggregate evidence; the original raw csv was not locally materialized and thus its MD5 could not be freshly checked. An independent network-enabled reproduction command performs source checksum pinning. Source was already used in `batter` and `odsp`; this is an exploratory new outcome, not independent corroboration.

M1 (previous climb class) outperformed M0 (marginal) by +0.01383 nats/transition, 95% individual bootstrap percentile CI +0.00672 to +0.02113; 7/8 bats positive. M2 (+ archival estimated wind) **failed** to improve: -0.00113 (CI -0.00252 to +0.00012) for held-out sessions and -0.00118 for held-out unseen individuals. M3 (+ self's other-night history) produced a **raw** -0.00916, but the null mean itself is -0.01149, calibrated contrast +0.00233, one-sided 199-permutation p=0.32; no individual-policy improvement is established. These are model- and cadence-specific results and should not be interpreted as wind physically irrelevant or personal differences absent. M1 forecasting utility is not proof of physical inertia: GPS noise, hidden behavioral mode and terrain/route effects may produce predictability.

An illustrative simultaneous-neighbor gate failed: no cross-individual GPS fixes <=5s and <=100m even though there were 15,676 time-near fix pairings. 39 pairs met <=15s and <=500m, not enough for fast spatial interaction force identification. Accordingly, **do not report fitted separation, alignment, or cohesion parameters from these data**. For Eidolon helvum, fixed 15–75s 3-fix cadence gate failed altogether; 0 eligible triples despite 18,154 records/63 bats.

## 4. Compare existing projects without conflating endpoints

| Program | Actually supported evidence from its frozen research | What v4 adds or does not add |
|---|---|---|
| batter | Repeatable centered vertical distribution in 5 non-Tadarida panels; terrain-relative strategies sustained 4/4 evaluable fruit-bat panels while strong additional segregation was unsupported 0/4 | Short-step individual transition policy was *not* recovered in historical Tadarida; not logically inconsistent, and Tadarida is already the negative centered-shape case |
| odsp | Effective ~4.02 height states in Tadarida yet cross-individual transfer of detailed x-y-height organization failed; species-time partition of Serengeti camera detections generalized across three site folds | v4 demonstrates simple short-step inertia transfer, but higher-resolution environment-conditioned movement does not automatically improve prediction. Not direct replication of same outcome |
| louis | Used King Rail water-depth trajectories vary less than time-matched local availability (10/10 birds; hydrological coupling buffered) | A new Boids/state-tracking kernel should predict experienced environmental **stability vs matched local opportunities**, not equate environmental steering to spatial partition. No ecological state-buffering result is estimated from Tadarida here |
| mina | Effective monitored penguin breeding-component number contracted 19–83% in five population units beyond fixed composition finite-count null | Breeding-site selection and demography are a **separate annual-scale settlement layer**, not consequences of flight trajectory Boids without further coupling |

Source repositories: https://github.com/zuizui0223/batter, https://github.com/zuizui0223/odsp, https://github.com/zuizui0223/louis, https://github.com/zuizui0223/mina

## 5. What would make the unified model truly predictive?

Predeclare an independent, high-frequency (task-specific, not assumed universal) **co-tracked** dataset with synchrony and near-neighbor observations. Record morphology, 3D position, observation error and independent environmental/resource states. Reject models in order:

1. Inertia-only transition kernel plus field measurement model;
2. + terrain/environment/food gradient, with held-out site or nights;
3. + persistent individual response or latent behavior mixture, calibrated against whole-bout permutations;
4. + neighbor interactions *only if social observability gate passes*;
5. jointly generate held-out 3D occupancy and patterns `I(S;B)`, `I(S;Z|B)`, spatial overlap and environmental state buffering; evaluate against empirical observations independently of fitting.

Biological predictive claim requires **both** (a) improved held-out forecast and (b) correct prediction of the spatial/time/niche summary in truly independent animal/night/site conditions. Recovering coefficients in a synthetic simulator is not enough. The Tadarida/Eidolon source gates preclude the full social component at present; no additional same-source parameter fishing is authorized by this report.
