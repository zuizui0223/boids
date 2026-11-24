# v29 — Harmonized 200ms group-velocity measurements: source ranking survives

**2026-11-24 JST — ORIGINAL observed fish trajectories, strictly source-descriptive. Not direct fish-fish causality, neural response times, fish-origin calling, or a formal three-taxon meta-analysis.**

## Why this correction was needed

The previous v27 original source-specific group-velocity autocorrelation used 0.1s velocity differences for Puy black neon tetra (5 frames / 50 fps) and Niizato ayu (3 / 30), but 0.2s for MacGregor stickleback (5 / 25). The longer stickleback averaging can smooth motion and artificially increase apparent persistence. Therefore the previously supported v27 ranking was methodologically confounded.

The pre-outcome frozen protocol [v29](V29_HARMONIZED_200MS_GROUP_VELOCITY_FREEZE.md), [commit 97beebb7](https://github.com/zuizui0223/boids/commit/97beebb7dbdb31b280e0c35feb3580e7caea4f71), required measuring the original group mean velocity from the SAME physical 0.2-second interval in all sources: Puy 10 source frames, Niizato 6, stickleback 5, with exact original frozen group-time cohorts, no extra smoothing/interpolation. Centered two-dimensional vector correlations against age 0.2,1,2s were recomputed independently with all original source checksums.

## Source-authenticated results

| Original published fish study | Original files | Original v27 speed window | Harmonized C(0.2s) | Harmonized C(1s) | Harmonized C(2s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Puy et al. 2024, black neon tetra | 6 | 0.1s | **0.967910** | 0.584019 | 0.155223 |
| Niizato et al. 2024, ayu | 7 | 0.1s | **0.963166** | 0.599734 | 0.248861 |
| MacGregor & Ioannou 2021, stickleback | 3 file IDs, NOT verified three distinct shoals | 0.2s | **0.985309** | **0.869427** | **0.646431** |

At age0.2, harmonization changed the source equal-file means only slightly: tetra 0.965553 → **0.967910**, ayu 0.958512 → **0.963166**, stickleback remains **0.985309** because its source-native window already was 0.2s. The prior frozen v29 decision rule—stickleback C0.2 greater than *both* other source studies—is still **SUPPORTED**. At ages 1 and 2 seconds the stickleback original source persists substantially more than the two other source cohorts.

This means the highest stickleback conditional source-autocorrelation cannot be explained **solely** by the old 0.1s versus 0.2s velocity-averaging discrepancy. It does NOT prove a biological species difference because group identities, environments, fish movement context, source tracking, native coordinate sources and fish count still differ.

### Authentic-source reproducibility

- [Puy original action #45335570192](https://github.com/zuizui0223/boids/actions/runs/45335570192), original 6 source MD5 verified, original source-time rosters exact, six known-truth tests PASS. [Source-safe receipt](v29_verification/TETRA_COMMON_200MS_GROUP_VELOCITY_RECEIPT.json), recording-level harmonized C0.2 0.961752–0.972191.
- [Niizato original action #45335575213](https://github.com/zuizui0223/boids/actions/runs/45335575213), all 7 pinned original Git SHA verified, native frame/census matched, six tests PASS. [Source-safe receipt](v29_verification/AYU_COMMON_200MS_GROUP_VELOCITY_RECEIPT.json), recording-level C0.2 0.942004–0.978893.
- [MacGregor original EIDC action #45335579194](https://github.com/zuizui0223/boids/actions/runs/45335579194), all 3 original source SHA and 6966/8015/5567 native source time cohorts verified; numerical C exactly replays original v27 25Hz speed. [Source-safe receipt](v29_verification/STICKLEBACK_COMMON_200MS_GROUP_VELOCITY_RECEIPT.json), recording-level C0.2 0.982631–0.990372.
- All three per-file study means independently reaggregated at [cross-source v29 verification JSON](v29_verification/CROSS_TAXON_HARMONIZED_200MS_RECOMPUTATION.json), no original individual fish positions committed.

## What this controls, and what it does not

**Raw group-state autocorrelation alone is still NOT a complete explanation of the supervised predictive-age retention.** Among Puy and Niizato, original group C0.2 is higher for tetra (0.9679) than ayu (0.9632), while the earlier original age-0.2 retained incremental future velocity prediction fraction I0.2 is LOWER for tetra (0.322/0.221 for short/delayed) than for ayu (0.432/0.440). The rank inversion remains after physical speed-window harmonization.

The new [v28 heldout residual group-state audit](V28_THREE_TAXA_CONDITIONAL_GROUP_STATE_INNOVATION_RESULT.md) produced q0.2 tetra **0.8439**, ayu **0.8941**, stickleback **0.9717**, which matches the order of the prior predictive I. This is a promising, target-free statistical decomposition, **not independent causal evidence**. q is conditioned on study-specific geometry and own-state inputs, and the original native velocity differencing was not harmonized in the v28 residual model. Thus v29 controls one source observable only, not every cross-study predictor/target difference.

An autocorrelated common environmental driver or future-symmetric track smoothing may generate both group persistence and predictive age patterns even with no fish-to-fish influence. The numbered EIDC records are not mapped to the original 12 biological shoals; [identity gate #249](https://github.com/zuizui0223/boids/issues/249) remains unresolved. No independent-school population p or meta-analytic common effect is available.

No synchronized fish-origin vocalization or playback attribution was observed in any of these fish-movement sources. Boids schooling to fish chorus causal feedback is **NOT TESTED**.

**Next methodological control (not yet executed):** use a common 0.2s source velocity differencing *throughout the full prediction and conditional residual pipelines*, rather than only in raw autocorrelation, with a genuinely heldout original biological shoal and independent common environmental/perturbation measurement. Keep PR #248 Draft and main unchanged.
