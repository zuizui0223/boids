# v38 — Structural counterexample to necessity of latent tidal state transitions

**2026-10-31 JST, after the observed v33/v34 tide–GPS signs and v37's source-free 24/24 state+commute construction were already known.** This is a *synthetic mathematical identifiability audit*, not newly observed ecological evidence and not an original preregistration of the earlier GPS experiment.

## Question and logical distinction

v37 showed a *particular* tide-dependent four-state policy with finite commute was sufficient for the three-signed wild-GPS motif, with or without 3D Reynolds-like heading forces; A0–A3 failed their particular fixed ablations. **A3's failure does NOT establish that latent memory or an explicit commute is generally necessary.** Construct the strongest simple counterexample: a memoryless, instantaneously responding, *smoothly height×ebb/flood interactive* scalar movement-speed rule, while still moving agent positions through 3D kinematics.

The signed pattern is (same fixed v37 estimands):
- High-water (H≥0.75) minus low-water (H≤−0.75) mean log1p(horizontal GPS-like speed) < 0;
- **height-bin matched** ebb−flood difference for H<+0.5 > 0;
- height-bin matched ebb−flood difference for H≥+0.5 < 0.

The signs were deliberately selected after field observation; reproducing them is **mechanistic sufficiency in a toy**, not empirical confirmation.

## Frozen direct rule (NO private ROOST/FORAGE/COMMUTE state)

Use the same synthetic v37 tidal forcing H(t)=1.2 sin(2πt/12.4206h)+0.09 sin(2πt/354.48h), synthetic exposed fraction A(H)=clip((1.25−H)/2.4,0,1), 3D toy positions/headings, 30 artificial agents, Δt=10min, 24 days with 48h burn-in, same 24 RNG seeds 0..23. 3D velocities are speed times unit 3D heading, with reported outcomes the *horizontal* magnitude exactly as v37. No RWS water levels, actual oystercatcher GPS, bathymetry or biological observations.

**Direct tide×phase rule:**

\[
v(t)=0.30+0.48A(H(t))+0.12\;\mathrm{sgn}(-\dot H(t))\tanh\left(\frac{0.50-H(t)}{0.30}\right)\quad \mathrm{km/h}.
\]

The parameters are hand-constructed from the *already known qualitative motif* and **not fitted to source animals**. This rule has **no latent roost/forage state, no commute timers, no individual learning and no resource-choice policy**. Heading inertia needed for 3D position integration remains purely kinematic; do not call it zero memory of all conceivable forms.

## Four fixed counterexample controls

- C0 **ADDITIVE_H_PLUS_PHASE:** v=0.30+0.48A(H)+0.12 sgn(−Hdot), with 3D kinematics and no Reynolds social forces. No height×phase interaction (negative control).
- C1 **SMOOTH_DIRECT_INTERACTION_NO_SOCIAL:** exact direct rule above, 3D position and inertial heading with random noise, but no latent activity state and no Reynolds social forces.
- C2 **SMOOTH_DIRECT_INTERACTION_WITH_3D_BOIDS:** identical direct scalar speed law plus the same v37 heading-only social alignment/cohesion/separation with hardcoded fixed coefficients. Social motor may change 3D trajectories but **cannot implement a hidden tide-state policy**.
- C3 **DIRECT_RULE_WRONG_TIDE_CLOCK:** compute the same direct rule from synthetic astronomical H(t+6.2103h),Hdot(t+6.2103h), but score sign contrasts against the unshifted H(t),Hdot(t). This deliberate **phase misalignment placebo** is not a causal manipulation, future information or biological predictor; it tests temporal specificity of the constructed oscillator.

Report complete mean signed contrasts and 24 seed signed motif counts for ALL four, including nulls. No after-score model substitutions.

## Fixed parameter sensitivity / non-fine-tuning counterexample

In a separate **analytic direct scalar speed** calculation (not full position integration), hold the same source-free tide and 30 artificial animals/24 seeds, but vary:
- exposed fraction coefficient α = [0.20, 0.48, 0.80];
- interaction coefficient β = [0.06, 0.12, 0.20];
- tanh width w (m) = [0.15, 0.30].

These **18 fixed parameter combinations** include the reference width/rule and are evaluated for the same three registered signs. Use the same lognormal speed noise sd=.03, no data from v37 positive seed filtering, no biological CI/p-value. This grid is deliberately centered around already chosen handcoded values, **not globally representative parameter space**. Report full 18×24 signs including failures, no motif-only subset. Explicitly disclose that synthetic analytic fixed-speed statistics need not precisely match a v37 3D motor run's tiny horizontal-projection attenuation.

## Causal-identifiability / intervention contrast

- For the **same** frozen instantaneous H=0 and Hdot=0, C1's deterministic speed is identical regardless of history. At identical instantaneous H/Hdot, however, two deliberately initialized v37 latent states ROOST vs FORAGE yield speeds 0.09 vs 1.1 km/h if no transition is triggered. The same target three-sign motif therefore does **not identify** a private state-dependent policy.
- Predictive **discriminator for actual field research**: under matched H, Hdot, UTC clock time, GPS duty and position/ecotope/landcover, the **previous tidal phase/previous habitat state** should add conditional information for an actual hysteretic state model but not an adequately specified memoryless smooth tide-speed model. Other unmeasured effects can also produce lags, so this is a model contrast, not proof of cognition.
- A second discrimination is direction/position transitions near actual exposed-flat boundaries; scalar GPS speed signs alone cannot infer feeding, commute, or social Boids forces.

## Source and CI rules

1. Commit this source-free protocol before running the new four counterexample models.
2. Add numpy-only deterministic v38 module importing **exact v37 source-free tide, heading update, signed-bin estimands**, and pure known-truth tests. If any v37 routine/parameter changed, refuse instead of silently replacing it.
3. GitHub Actions must validate 10+ tests, run all four variants over same 24 seeds and all 18 sensitivity scenarios/24 seeds, and emit **every** full signed result and failure, without statistical p-values from artificial seeds.
4. Retain v37 original separate branch/PR #40 and all previous empirical/source gate results unchanged. Separate draft PR stacked on v37; never merge without authorization. No eBird/TinyFish or original GPS data.

**The result can disprove the universal necessity of private state memory/finite commute for these three selected signs if C1 succeeds, but cannot disprove the possibility or actual importance of memories, commute, social interactions or true 3D niche segregation in animals.**
