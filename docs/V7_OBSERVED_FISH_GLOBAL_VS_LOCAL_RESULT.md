# v7 genuine original fish: local neighbor alignment versus whole-school movement

Completed original field source analysis 2026-11-20: [GitHub Actions #44751635828](https://github.com/zuizui0223/boids/actions/runs/44751635828), [complete source-safe numerical artifact](https://github.com/zuizui0223/boids/actions/runs/44751635828/artifacts/14636735362). Source: Puy et al. 2024 PNAS `10.1073/pnas.2309733121`, original Zenodo 10890112. Original six 8-fish CSV MD5 verified; previously frozen v5 original own/full and v6 geometry per-recording test MSE replayed. Five synthetic tests passed.

## Objective and original data

The strong previous v6 local-alignment gain may simply represent **shared whole-school velocity**. This is a separate exploratory secondary test after v5/v6 original outcomes, not a fully independent preregistration or fresh population. Retain all v5 original cohort, feature radius 25cm, future 0.20s mean Cartesian velocity, 50fps and train other 5 entire recordings / test withheld 6th. No post-outcome tuning.

Frozen comparison:
- G: own-state & wall plus near-neighbor present geometry (repulsion/cohesion/count), original v6 geometry
- G+Global: G plus the two-component **mean of velocities of all other seven fish minus the focal fish velocity**, independent of neighborhood membership
- G+Local: G plus mean relative velocity among fish *within 25cm*, the byte-exact original v5 full Boids features
- G+Global+Local: both velocity components, no more test samples
- G+StaleLocal: G with velocity alignment from 2 seconds earlier, rather than current, controlling present geometry.

## Six original recording results

MSE [(cm/s)²] of heldout 0.20s future mean velocity. Exact aggregate score JSON is in the run artifact, here rounded.

| Test recording | G: geometry | G+Global | G+Local | G+Both | G+StaleLocal |
|---:|---:|---:|---:|---:|---:|
| 0 | 15.141333 | 12.140563 | 12.115604 | 12.114212 | 15.135828 |
| 1 | 13.036827 | 10.616998 | 10.581969 | 10.583004 | 13.031270 |
| 2 | 12.267273 | 10.129958 | 10.120567 | 10.121057 | 12.262283 |
| 3 | 12.882361 | 10.587340 | 10.559745 | 10.555843 | 12.880165 |
| 4 | 13.567800 | 11.955914 | 11.879668 | 11.875855 | 13.564738 |
| 5 | 15.516678 | 12.687114 | 12.682023 | 12.675138 | 15.515451 |
| **Trial-equal mean** | **13.735379** | **11.352981** | **11.323263** | **11.320852** | **13.731623** |

### Frozen effect ledger

- Add **whole-school velocity beyond local geometry**: +2.38239753 (cm/s)² MSE reduction, **6/6** test recordings positive; descriptive whole-recording bootstrap 95% [2.014604, 2.731503].
- Add **local neighbors' velocity beyond local geometry**: +2.41211614, **6/6** positive; previously frozen v6 replay.
- **NEW PRIMARY: local-neighbor velocity added after whole-school velocity**: +0.03212948, **6/6** positive; descriptive whole-recording bootstrap [0.016504, 0.052428]. Exact one-sided sign p=.015625 **assuming independent recording-level signs**; six recordings may share fish or setting, so this is not an independent-species p-value.
- Add global mean after local: +0.00241087, 4/6 positive; exact directional sign p=.34375.
- Real current local versus **2-second stale local**: +2.40836016, 6/6 positive. But 2s-lag surrogate is not an exchangeable causal counterfactual.

## Interpretation and novelty boundary

About **98.8% of the total G→G+Local gain** (2.3824 of 2.4121) is matched by an alternative predictor comprising *whole-school velocity*, even though the local-current model performs slightly better. The truly local increment beyond whole-school velocity is only **0.0321** MSE, about **1.25% of the total v5 own→full Boids gain** +2.5798, and 0.28% of the G+Global test MSE.

**Most local-alignment predictive value is consistent with shared collective movement.** A small additional within-neighborhood signal appears in every original recording under the tested regressions. It is NOT proof of a local causal alignment force. Same school-level flow, wall constraints, and latent common cues can cause both global and local velocities; correlated neighboring features are predictive proxies rather than randomized individual effects.

Published Puy et al. already measured selective speed-neighbor interactions; v7 does not refute or rediscover that. The original source uses partly future-symmetric Gaussian-smoothed or corrected trajectories, so this is *retrospective withheld-recording prediction*, not prospective online behavior forecasting. Six recordings are from one species/study and may share fish. No synchronized calls or fish sound sources were measured in Puy recordings, so no actual school-to-chorus causal result was fitted.

**Research decision:** use local-versus-global nested predictive contrast as an ecological *identification test* and do not sell the huge v5/v6 gain as unique local Boids steering. Next mechanistic requirement: independently observed fish position/velocity and attributable calling within the same field array, ideally playback manipulation. Mouy OSF 66 source-localized sound rows do not supply continuous per-fish track IDs.

Keep [PR #248](https://github.com/zuizui0223/boids/pull/248) DRAFT; main unchanged. No original animal tracks or waveforms redistributed.

