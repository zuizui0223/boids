# v20 — Frozen independent sound-motor × vocal-hearing pathway experiment

**Synthetic simulator only, NOT wild fish data. 2026-11-22 JST.**

## Scientific premise

The v19 result from 24 pre-cue low source simulator seeds showed a large crossed physical geometry × acoustic attenuation interaction, but v19 applied a single hearing-distance kernel to BOTH sound-directed motor steering and vocal-calling probability. Thus these two computational paths remain unresolved.

## Frozen unobserved holdout and model

- New uninspected seed census **7000..7767 inclusive, 768**, disjoint from v15–v19. Same source v15 original initialization, native source simulator SHA256 **a7720cd1a482bbaff49edc9d1b15e4493bc7614cd9715e8e116cd94f583a4bdb**.
- Original 32-agent trajectory, no playback, to completed update t1000. Enroll *every* seed with last source binary call fraction q<0.90, regardless of geometry. Freeze the list before any outcome, no replenishment or seed/threshold tuning. Low n<8 means an inferential SUPPORT_STOP but retain all observed values.
- From the same t1000 source position, velocity, binary calls, IDs, centroid and PCG64 state, separately set physical positions X_phys=mu+p*(X_original-mu), p∈{.65 compact,1.35 spread}; keep all other state parts fixed.
- Two **separate** effective sound attenuation factors, m∈{.65 long motor hearing,1.35 short motor hearing}, c∈{.65 long calling hearing,1.35 short calling hearing}. At future step t, motor sound kernel equals exp[-(m/p)*physical_pair_distance(t)/5], used **ONLY** in sound-directed steering. Vocal sound kernel equals exp[-(c/p)*physical_pair_distance(t)/5], used **ONLY** to calculate heard calls in sigmoid call probability. Both exclude self-hearing, and original walls/Reynolds steering and velocity remain governed by physical coordinates and original parameters. At t1000 initial attenuation has been independently matched across physical compact/spread for either motor or calling path; after movements, observed distances and hearing can diverge. Playback external cue 0.8 acts directly in vocal logit [1000,1040), absent in quiet control.
- **Exactly 16 paired model arms:** physical 2 × motor kernel range 2 × vocal kernel range 2 × cue on/off 2. Starting RNG identical; finish t4040. Primary window postcue [1040,4040) average binary calling. Maintain exactly integer n32 individual call counts before contrasts.

## One frozen primary comparison

At **physical compact** and **long vocal-hearing**, does changing MOTOR hearing from short to long increase external playback response?

D_motor = [Gain(physical compact,motor long,vocal long) − Gain(physical compact,motor short,vocal long)], where Gain = (cue on minus cue off) mean calling in [1040,4040).

Primary report mean across ALL pre-cue low enrolled seed states, median, positive/negative/exact-zero signs, 10,000 whole-seed paired bootstrap percentile95% with RNG seed **2026112260**, descriptive and unadjusted. Model-based directional prediction positive, but all null and reversal outcomes retained. This is a **model-parameter interaction**, not natural biological motor-mediated effect.

## Frozen secondary factorial decomposition

Per physical compact and spread separately, record four cue gains G_LL, G_LS, G_SL, G_SS (first motor, second vocal). Report:
- Motor effect conditional on short vocal (G_LS−G_SS).
- Calling-hearing effect conditional on long motor (G_LL−G_LS) and short motor (G_SL−G_SS).
- Pathway interaction I=G_LL−G_LS−G_SL+G_SS.
- Two-factor Shapley distribution of joint long-vs-short gain Δ=G_LL−G_SS:
  phi_motor=[(G_LS−G_SS)+(G_LL−G_SL)]/2,
  phi_vocal=[(G_SL−G_SS)+(G_LL−G_LS)]/2.
  Exact closure phi_motor+phi_vocal=Δ, with integer numerators, denominator 2*32*3000.
- Original v19 diagonal combined-pathway contrasts under each physical geometry, plus physical compact-vs-spread for both long pathways. Cue-on and quiet absolute calling levels, hull area, 200-update rolling call threshold >=0.9 with explicit censoring at t4040. Seed effects including concentrated positive mass. No cherry-picking of favorable contrasts.

## Reproducibility gates

- v20 model is a source-controlled copy of v19, **only splitting** the previous acoustic_ratio into separate motor_acoustic_ratio and calling_acoustic_ratio. No other motion, calling, wall, time or RNG change.
- **All 8 arms with equal motor and vocal attenuation** must replay exactly (every step call fraction/hull area/cue; final positions/velocities/calls/PCG64) original immutable v19 crossed_simulation.advance(..., acoustic_ratio=s_h/p) for each eligible seed.
- On 4 arms where physical scale equals equal motor and vocal scale, also replay original immutable v15 advance, exactly. All original source hashes must remain frozen. Unit fixtures use nonreserved seeds only.
- Save all 768 original source q, all eligible 16×3040 arm call/hull traces, per-seed CSV, JSON receipt with SHA256, code hashes pre/post. Python3.12, numpy2.3.5/scipy1.17.0, GitHub Actions two workers, no post-outcome seed/radius changes.
- This is not animal evidence, not a pure hearing-only causal experiment because the motor and calling paths later reshape the same geometry, and cannot prove bistability/hysteresis in wild fish. PR #248 stays Draft, main unchanged.
