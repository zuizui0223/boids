# v14 Acoustic Boids: delayed arrival versus maintenance

Frozen computational follow-up, 2026-11-22 JST. **SYNTHETIC_ONLY_NOT_FIELD_RESULT.**

## Purpose and alternatives

v13's delayed-pulse effect at steps 3000–3999 was concentrated in two of 24 seeds. This follow-up asks whether that difference remains over a longer finite horizon, and whether the two acoustic links are needed *after* playback ends. This is an exploratory follow-up on the same simulator seeds, not an independent replication, animal experiment, or proof of stationarity.

Three approaches were considered: longer trajectories alone (tests delay but does not intervene on maintenance), reciprocal motion/calling-state transplants (locates stored history but adds a distinct intervention), and longer trajectories plus post-pulse link removal. The third is the implementation choice for this continuation. Transplants remain outside v14; state-memory localization will not be claimed. A frozen-geometry deterministic closure is a separate mathematical diagnostic.

## Fixed experiment

- Authoritative predecessor: commit `f558b7f5de63e3b3e712b92a0b2239a08663264f`, `validation_fish_boids_v13/simulation.py`. Preserve its equations, initial distribution, random draws, step order and parameters.
- Individuals: 32; timestep 0.06, arbitrary model time, not calibrated fish seconds.
- Seeds: **1000–1023, all 24**, including the two large v13 responses; no outcome-based exclusions or extra seeds.
- Horizon: **16000 steps**, fixed before new outcomes. No adaptive horizon extension.
- Playback: absent versus amplitude 0.8 at integer steps **1000–1039** inclusive.
- Before step 1040, all mechanisms use caller-attraction weight 5 and hearing-to-calling weight 3.
- Starting at step **1040**, continue with one of four weight pairs: intact (5,3), motor cut (0,3), hearing cut (5,0), both cut (0,0).
- Apply each continuation to **both** pulse and no-pulse histories: 24 × 2 × 4 = **192 trajectories**, each simulated from the original initialization. Caller-attraction removal does not stop motion or remove visual social forces.
- The same seed consumes the same random draws in all arms; numerical identity before intervention is an invariant.
- Record every step's call fraction, convex-hull area and playback cue. Record positions, velocities and binary calls after 1000, 1040, 4000 and 16000 completed updates. Snapshot at completed count s is the state before update t=s.

## Estimands, fixed before outcomes

The primary endpoint is the intact-arm paired mean call-fraction difference, pulse minus no pulse, averaged over **[12000,16000)**.

Prespecified secondary endpoints:

1. The same paired call-fraction and area contrasts for every mechanism in [1040,1240), [3000,4000), [7000,8000), and [12000,16000).
2. For each cut, the paired difference-in-differences `(pulse−none)_cut − (pulse−none)_intact`, in those same windows. This changes neither the comparator nor the denominator to the intact no-pulse arm alone.
3. The factorial contrast of pulse effects: intact − motor_cut − hearing_cut + both_cut, in the terminal window. It is secondary, unadjusted and cannot replace the primary endpoint.
4. Full per-seed outcomes, median, sign counts, and concentration of the positive effect. Retain every seed.

Resample whole paired seeds using 10000 bootstrap draws, RNG seed **20261122**, reporting percentile 95% intervals. All arm outcomes for a seed stay paired in every contrast. These intervals describe simulator-seed variation; they are not animal-population intervals, an equivalence test, or a multiplicity-adjusted confirmatory analysis.

## Arrival-time diagnostic

For intact arms only, record the earliest *confirmation* time after step 1040 of a 200-step window whose mean call fraction is at least 0.90. Search window starts s=1040 through s=15800 inclusive; confirmation is s+200. No qualifying window is right-censored at 16000, with an explicit event flag. Restricted latency is min(confirmation,16000)−1040; censoring is never labeled an observed arrival.

Repeat this definition at fixed thresholds 0.80 and 0.95 as descriptive sensitivity checks. Baseline high activity is determined by the common **[800,1000)** mean at the same threshold, before any playback. Report it explicitly, and separately describe seeds below that baseline threshold. A first qualifying window is neither an absorbing transition nor evidence of equilibrium. No threshold will be selected after observing the outcomes.

## Frozen-geometry diagnostic

Use only intact pulse/no-pulse snapshots at completed counts 1000, 1040, 4000 and 16000: 192 geometry records, including identical pre-pulse pairs. For N=32 and H_ij=exp(−distance_ij/5), H_ii=0, iterate the deterministic closure

`T(q) = sigmoid(−2.8 + [3/(N/4)] H q)`.

Start separately from all-zero and all-one probability vectors. Monotonicity brackets every closure fixed point. Iterate to both fixed-point residuals ≤1e−12, or at most 10000 iterations. Record full endpoint vectors, residuals, maximum bracket gap, iterations, and spectral radii of the two Jacobians. Gap ≤1e−8 with convergence is `collapsed_bounds`; larger converged gaps are `separated_fixed_points`; failure to converge is `unresolved`. These are numerical classifications, not formal interval-arithmetic certificates.

Also report the global sufficient contraction bound `(3/N) spectral_radius(H)`, and the weighted row sums. A bound below 1 is sufficient, not necessary, for uniqueness of this closure. A bound above 1 is not evidence of bistability.

The closure is **not** the exact expected stochastic call dynamics: E[sigmoid(Hc)] generally differs from sigmoid(H E[c]). At fixed geometry, the exact finite binary calling chain has positive transition probabilities and one stationary distribution; this does not preclude long metastability. Neither statement establishes uniqueness or ergodicity of the full moving-position model.

## Interpretation boundaries

- Hearing removal makes post-pulse calling iid Bernoulli(sigmoid(−2.8)) by construction. Equality under common random draws is an implementation/control check, not independent evidence for spatial reinforcement.
- Motor removal tests dependence on continued acoustic steering. Its effect also changes the geometry and baseline trajectory; report both arms and the paired interaction.
- A small terminal average does not prove equal stationary distributions or eventual disappearance of every individual difference. A persistent finite-window difference does not prove two attractors.
- Do not tune weights, pulse, thresholds, seeds or horizon to obtain a positive result. Do not treat two responsive seeds as representative of all initialization states.
- No new fish observations or fitted ecological parameter values enter this analysis.

## Validation and delivery

Preserve v12/v13 source bytes. Require exact intact 4000-step prefix replay against v13 for every pulse/no-pulse seed pair; independently compare with the archived v13 raw traces locally. Test intervention boundaries, state snapshots, paired contrasts and censoring with known fixtures. Validate exact array keys/shapes and finite physical ranges before atomic output writes. Save raw arrays, per-seed windows and arrival records, closure diagnostics, source hashes, plots and a Japanese report. Use an independent final review. Update Draft PR #248 with guarded branch updates; do not merge or change main.
