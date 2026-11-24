# v28 observed: conditional other-fish movement residual persists in same rank as retained predictive advantage

**2026-11-24 JST; ORIGINAL OBSERVED FISH TRAJECTORIES, target-free heldout residual analysis, NOT causal social transfer, acoustic response or a formal multi-study meta-analysis.**

## Why and frozen endpoint

v27 found raw mean school velocity C(0.2s) highest in the stickleback exploratory source but did **not** reproduce the full ordering of supervised incremental predictive retention between tetra and ayu. In particular raw group C0.2(Puy)=.96555 > C0.2(ayu)=.95851, whereas v24 retained predictive I0.2(Puy)=.322/.221 < I0.2(ayu)=.432/.440. This motivated a *new* target-free test, frozen before v28 outcomes at [source protocol](V28_CONDITIONAL_SCHOOL_MOTION_INNOVATION_FREEZE.md), [commit 91a02e8b](https://github.com/zuizui0223/boids/commit/91a02e8b39383f491529f66533f99bb581a038f7).

Original source **current** and age-0.2/age-1.0 relative other-fish velocity fields were kept exactly as in the already-authenticated v24/v26d group-state predictors. Each one is the mean of the other N−1 fishes' velocity at the specified original time minus the **CURRENT focal velocity**. The baseline G contains that focal's current and prior velocity, current XY/geometry and fixed original spatial features.

For **each entire heldout original recording file** and for each age separately, predict the relative other-fish vector R_age from G via a training-file-only StandardScaler + fixed Ridge(alpha=10). Subtract predictions on the withheld file to obtain residual vectors e_age. Report the **centered two-dimensional residual vector Pearson/dot correlation** q_age=cor(e_0, e_age) on identical heldout fish×frame rows. The outcome/future-velocity Y is **never used to fit these nuisance models** and is not rescored.

Thus q_age is NOT mutual information, individual neural memory, communication rate, a causal fish-to-fish flow, and is not numerically the supervised MSE-retention index I_age. It measures how similarly the current and aged group movement fields **deviate from source-fitted focal/self/geometry predictions**. A common latent environmental driver not measured by G can still generate the same q.

## Original fish source-verified outcome

| Published fish source and source holdout | Original files | q(0.2 s) | q(1 s) | Previously observed I(0.2s) short / delayed |
|---|---:|---:|---:|---:|
| Puy 2024 black neon tetra, 8 fish each | **6** | **0.843867** | **0.249782** | 0.322423 / 0.220901 |
| Niizato 2024 ayu, 10 fish each | **7** | **0.894073** | **0.374107** | 0.432089 / 0.439580 |
| MacGregor & Ioannou 2021 stickleback, 8 fish each | **3 original files; biological shoal identities UNKNOWN** | **0.971708** | **0.815439** | 0.782893 / 0.777077 |

**PREDECLARED rank prediction: SUPPORTED** within the opened source files: at age 0.2, q(stickleback) > q(ayu) > q(tetra), matching both previous future-horizon I(0.2) orderings. At age 1, the same qualitative order recurs. All per-recording q(0.2) and q(1) estimates are positive, but source files are not all independent fish populations and no nominal population p is calculated.

Source-safe original provider evidence and artifacts:
- [Tetra Actions #45335071497](https://github.com/zuizui0223/boids/actions/runs/45335071497) SUCCESS; 6 source-free known-truth fixtures, 6 original Zenodo provider MD5 checks, original v24 Puy time cohort, [file-level receipt](v28_verification/TETRA_CONDITIONAL_GROUP_STATE_RESIDUAL_RECEIPT.json). Per original file q(0.2) range **.795991–.903094**, q(1) .176054–.393693.
- [Ayu Actions #45335075573](https://github.com/zuizui0223/boids/actions/runs/45335075573) SUCCESS; 7 original source Git blob hashes pinned and native 30Hz, fixed original t>=66 cohort, [file-level receipt](v28_verification/AYU_CONDITIONAL_GROUP_STATE_RESIDUAL_RECEIPT.json). Per source q(0.2) range **.841077–.930271**, q(1) .194586–.497031.
- [Stickleback Actions #45335080478](https://github.com/zuizui0223/boids/actions/runs/45335080478) SUCCESS; original EIDC 3 exact SHA-pinned source files, v26d common XY/NA mask and 6966/8015/5567 groups of group-time rows, [file-level receipt](v28_verification/STICKLEBACK_CONDITIONAL_GROUP_STATE_RESIDUAL_RECEIPT.json). Per source q(0.2) range **.965967–.975072**, q(1) .793421–.834732.

All 3 Actions run the same 6 source-independent tests, source authentication and original case timing gates. Source safety: no raw individual fish XY or target time series exported, no new fish future velocity scored, no observed fish calls.

## Strongest scientific interpretation and contrary limitations

**Positive descriptive result:** an out-of-file, train-only adjustment for focal own state/current geometry yields a residual other-fish motion state whose temporal persistence has the *same ordering* as future-motion predictive retention across the three independently published original sources. The ordering is sharper than the source-native *unadjusted whole-school mean velocity autocorrelation* in v27. This is a promising measurement decomposition.

**However it is NOT a mechanism identification.** q and I were computed using the *same* source fish recordings and partially overlapping model features; both are statistically dependent and can be related by construction without proving that fish measure or respond to the residual. The original fish trajectories may be source-smoothed using future frames, while laboratory tanks, reward stimuli and observation windows differ. In particular, v27 and v28 used velocity difference windows 0.1s for Puy/Niizato, but 0.2s for stickleback. A source-normalized **common 0.2s raw group-speed window** is being audited separately under [v29 pre-result freeze](V29_HARMONIZED_200MS_GROUP_VELOCITY_FREEZE.md); its results are not yet assumed here. This harmonization is a necessary source control, though it does not fully harmonize the prediction models or the conditioned residual regressions.

The EIDC 84-file → 12 original shoal identity mapping remains unverified, so 3 stickleback selected source **files** are not independent shoals. [Open source-identity gate issue #249](https://github.com/zuizui0223/boids/issues/249) records what is needed for genuine whole-shoal transfer. At least three genuinely independent schools/individual sampling units are required before treating this as formal study-level generality.

**Next confirmatory mechanism:** independent contemporaneous common-driver measurements, or randomized sensory and auditory/visual perturbations with group motion and original individual call attribution. Across all original datasets scored in v28, no synchronized fish chorus or acoustic caller source was observed. Keep [Draft PR #248](https://github.com/zuizui0223/boids/pull/248) unmerged; main untouched.
