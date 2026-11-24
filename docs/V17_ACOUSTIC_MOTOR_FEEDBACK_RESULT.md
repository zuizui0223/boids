# Acoustic Boids v17 — independent 384-seed source-frozen motor-feedback ablation
2026-11-22 · **SYNTHETIC_ONLY_NOT_FIELD_RESULT (NOT REAL FISH DATA)**.

## Main result
The v16 positive feedback sensitivity strongly correlates with pre-cue low calling, but the high group is near 100% (measurement ceiling). We preregistered a new fixed seed census 4000–4383 and, before opening outcomes, selected every checkpoint with pre-cue calling q<.90. The [frozen protocol](https://github.com/zuizui0223/boids/blob/41accf4675946a92a70e96c4f044680bcdd6d27b/docs/V17_ACOUSTIC_MOTOR_FEEDBACK_FREEZE.md) and [implementation](https://github.com/zuizui0223/boids/blob/d4902f77fbcf1023328391867c55fc7b2476b2a2/validation_fish_boids_v17/motor_feedback.py) preceded all v17 outcomes.

The full original census had **9/384 (2.3438%)** low q<.90, with remaining 375 already high (358 exactly 32/32 calling). From every low checkpoint, six trajectories shared exact position, velocity, prior binary calls, and PCG64 RNG. Arms: motor weight 5 or 0 with hearing-calling weight 3, and motor weight5/hearing0 structural negative control, each paired with pulse/no-pulse cue 0.8 on updates1000–1039; outcome after cue updates1040–4039.

| Original fixed 9 low seed arm | Mean pulse minus no-pulse calling over 3000 post-stimulus updates |
|---|---:|
| Acoustic motor 5, hearing3 | **+19.6601 percentage points** |
| Acoustic motor 0, hearing3 | +0.0572 percentage points |
| Acoustic motor 5, hearing0 | 0.0000 points, model-structural null |

**Primary pulse×motor interaction** = +19.6029 points, conditional 10,000 seed-resampled descriptive95% [4.3178, 39.2110] points. But **median only +0.0354 points, signs 5 positive vs4 negative**. Authors should NOT claim a broadly positive individual group effect on this small conditional sample. Source-verified original all6 arms ×9 low q.

### Large heterogeneity and exploratory geometry
Three positive simulator seeds **4099, 4277, 4138** produce **99.4744% of the positive effect mass** in these 9 low-prestate seeds; their motor interactions are +71.6219, +63.1104, +41.7240 points, respectively. Remaining six are near zero or adverse. Within these already-opened nine seeds, exploratory pre-cue convex-hull area vs signed motor×cue effect has Spearman ρ=**−0.8667** (n=9). This was found **AFTER** seeing outcome values and is an unvalidated candidate for a separate frozen independent geometry test, NOT a preregistered confirmatory result. The smallest hull areas overlap the large responses, but compactness alone cannot be causally identified.

### Time, geometry and caveats
- Pulse minus no-pulse convex hull area under motor5: −13.864 model area units in nine-seed mean, smaller in 6/9; under motor0, pulse/no-pulse area identical by update equations.
- Motor5 mean restricted latency difference to 200-update rolling call fraction >=.90: **−600.11 model updates** (4 earlier, 5 tied; 6 control, 5 pulse trials right-censored at t4040). Motor0 restricted latency contrast zero. Censored ties do **not** prove eventual same state.
- Hearing0 post-pulse call traces identical across cue/no-cue by model construction. This is an implementation check, not independent biological evidence.
- The motor0-versus5 intervention changes the no-pulse geometry and its baseline call frequency as well, so the main difference-in-differences is a **model parameter interaction**, not natural mediation or the necessity of motor steering in real fish.
- 9 eligible seeds are from a particular artificial simulator, not 9 independent real fish schools; descriptive Monte Carlo uncertainty and exploratory rank correlations are not ecological population tests.
- No long-run stationary attractor, natural hysteresis, field acoustic interaction, learning or fish vocal physiology is inferred from finite post-pulse traces.

## Verifiability and downloads
[Original CI run #45013210312](https://github.com/zuizui0223/boids/actions/runs/45013210312): 6 source-independent fixtures PASS, 384 frozen pre-state census and six simulations in each of 9 eligible seeds PASS, artifact uploaded. [Original numerical and six-arm trace artifact #14750636600](https://github.com/zuizui0223/boids/actions/runs/45013210312/artifacts/14750636600). ZIP SHA256: 2a1a716ffb61fdd720278bd544968a6688b92dfe2dc44b21f784cef8f099b800. Raw NPZ SHA256: 78d23c1764a24b1babdea1a463d47e6016d556bedbc7ba603a0d7f6fbcda18ff. An independent verifier reconstructed integer call contrasts, 10,000 bootstrap draws, all source eligibility, structural motor/hearing controls, per-seed area metrics, latency and censoring from the saved original NPZ without importing the production analysis. All hashes and scores agree.

**Scientific decision:** The model has a feasible acoustic motor amplification mechanism in rare low/compact configurations, but not a widely replicated positive stimulus effect. The next genuine test must manipulate pre-cue geometry separately from q and use new seed populations; actual fish would require simultaneous tracked positions and assigned calling after playback. Keep [PR #248](https://github.com/zuizui0223/boids/pull/248) Draft and main unchanged.
