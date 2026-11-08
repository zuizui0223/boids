# What the original 2026 3D bat echolocation archive actually establishes

**8 November 2026 — full-source, no-new-measurement reanalysis and science decision.** Original Steckel 2026 preprint DOI [10.64898/2026.10.22.760884](https://doi.org/10.64898/2026.10.22.760884); original archive [Zenodo 23537553](https://doi.org/10.5281/zenodo.23537553). **This is a numerical reproduction of the authors' already-published saved simulation RESULTS, not a rerun of the author's Python training program, not a field experiment and not a newly demonstrated bat learning mechanism.**

## Concrete pipeline verified

1. Original 988,293,611-byte ZIP was accessed by bounded HTTP206 Range. Only source code.zip (11,212,647 bytes), index, README/manifest and source_data/run_table.json (18,123 bytes) were admitted. Full ZIP, real-species HRTF MAT, pretrained weights, simulated bat sound samples and 3D trajectories were NOT downloaded or redistributed.
2. Verified source checksum code.zip SHA256 a5b951abf5cda1ebe2e783c06d193fd9a09cb3fc36c02a265dcc7ac72bab7ae8, author experiments.json SHA256 6a8a86bdca8669468ab4ec0636369d4f1bfb9bda93c105b0e01d1cf6182833e7, original author source_data/run_table.json SHA256 42148acb514b7bb89ab77bc7815951582b32551e54da61885c81803982d30681.
3. Original experiment index 28 runs and original stored performance rows 28 entries were EXACTLY joined by normalizing source Windows path separators to archive POSIX paths. An initial 0/28 match was a path-parsing error, NOT missing data or a negative effect.
4. Source author-reported metrics az, el, gc, left/right and up/down correctness, corr (missing for exactly 3 original ear-relearning entries), original n and training step were stored for every one of 28 runs. The original source figures are prior art; we do not choose an apparently favorable condition after inspecting the metrics.
5. [Full 28-run published author source replay](https://github.com/zuizui0223/boids/actions/runs/42446564659) and [entire 28-run metric/step/test-n and checksum numerical ledger replay](https://github.com/zuizui0223/boids/actions/runs/42446672218) both passed. The data are stored in [all 28 original source-run numerical ledger](STECKEL_2026_ORIGINAL_28_RUN_SOURCE_NUMERIC_LEDGER_V1.json).

## Original author's axis-specific observability results (not novel to us)

Verbatim source `az` and `el` angular-error metrics; lower is better. The values below are the SAVED AUTHORS' simulation evaluations.

| Original source treatment | Source n | Train step | az | el |
|---|---:|---:|---:|---:|
| E1 main self-motion, seed 0 | 3990 | 59984 | 2.510 | 2.788 |
| C1 shuffled self-motion | 3990 | 59984 | 12.445 | 23.245 |
| C2 no next-call prediction | 3990 | 59984 | 26.073 | 27.404 |
| C3 self-motion shifted by two calls | 3990 | 59984 | 9.497 | 15.264 |
| C4 head fixed | 3988 | 59984 | 5.611 | 20.770 |
| E7 pan only | 3990 | 59984 | 2.367 | 14.718 |
| E7 pan + tilt | 3989 | 59984 | 2.494 | 2.479 |
| E7 pan + roll | 3994 | 59984 | 2.390 | 4.281 |
| E9 sparse reflectors | 3972 | 59984 | 4.044 | 4.448 |
| E9 same sparse reflectors in specular room | 3978 | 59984 | 4.537 | 5.535 |

**Constrained author-source descriptive interpretation:**
- Correctly aligned own-motion inputs matter for both spatial axes. A shuffle produces source `az` worsening +9.935 and `el` +20.458 against main E1. Shifting motion by two calls worsens `az` +6.987 and `el` +12.476. Removing next-call prediction worsens both (source C2 original condition).
- Head motion is axis-specific in this source: source pan-only `el` is 14.718, versus source pan+tilt 2.479, ratio **5.94x**. Source pan-only `az` 2.367 versus pan+tilt 2.494, i.e. roughly similar. Source n differs by one, so this is a saved model contrast, NOT a paired causal treatment of identical held-out examples.
- Sparse-to-specular-room source `el` increases +1.088 and `az` +0.493. Source evaluation counts 3972 vs3978, so any shared-neighbor or same-evaluation-draw inference is unsupported.

These are the original study's already-tested controls; no 3D field niche of real bats was recovered or validated.

## Original author's call-memory sweep: source-numeric prior art, not our earlier toy filter

| Original replay memory N calls | az | el | Source train step |
|---:|---:|---:|---:|
| 1 | 3.391 | 4.069 | 59399 |
| 4 | 3.401 | 3.890 | 59516 |
| 16 | 2.838 | 3.295 | 59984 |
| 64 (main) | 2.510 | 2.788 | 59984 |
| 256 | 2.759 | 2.943 | 59984 |
| 512 | 2.248 | 2.564 | 59984 |

The source's memory performance is **not strictly monotone** (N=256 is worse than N=64 on both az and el), even though 512 improves on 64 in these saved outcomes. Different training checkpoints (N=1 and 4), possible different evaluation examples and training randomness obstruct isolating memory as a direct biological causal factor. We CANNOT retrospectively select N=512 as an experimentally determined optimum for real bats. The prior 310-cell Gaussian memory/dropout equations are a different uncalibrated mathematical estimator and do not replay these source-model results.

## Population/sample-size and science scope

The original `n` range ~3972–3999 represents simulated virtual evaluation observations, NOT 4000 independent living bats. Original E3 ear-rotation runs were evaluated at training step29984 and main step59984; no equal-trained-stage causal coefficient is justified. Three original E3 `corr` entries are absent and remain explicitly missing. There is no distinct species sample, colony replicate, real foraging success or source detector masking effect in this 28-run evaluation table.

Other important 2026 prior art: Teshima et al. *Proc. R. Soc. B*, DOI `10.1098/rspb.2026.1463` already demonstrated flight-policy transfer across two bat species and seven obstacle arenas, on real trajectories and echolocation. Claiming merely that 3D flight rules are predicted has no first-discovery novelty.

## Next genuine question beyond this paper's E1–E9/C1–C5

Can the **observability of vertical versus horizontal space** in a bat-like agent be predicted from how self-motion rotates the sonar view relative to *independently held-out* obstacle geometries, rather than memorized sensor settings or fitted training distributions?

A scientifically meaningful follow-on would predeclare a geometry-by-motion **unseen interaction** outside the author's axis, symmetry, memory and specular-original controls, using the actual source simulator (not the 2024 unrelated Molossus data), common held-out scenes/steps/initial seeds, a negative control with movement cues time-shuffled, and an axis-specific error *transfer* score. Different taxa/empirical bats would remain unestablished until independent actual track/echo data are admitted. Current source is simulated and lacks real-bat ecological performance. No new untested experimental results claimed.

The original code is Python with PyTorch>=2.1, numpy/scipy/matplotlib and original 10 test modules; 29 original source Python files passed source-only AST compilation. This code preflight is [source-only CI](https://github.com/zuizui0223/boids/actions/runs/42446857141). Passing AST compilation is NOT passing original author model unit tests. A separately frozen **sixteen original source geometry/warp/axis tests** are being exercised with source-authenticated code and CPU-only PyTorch, with no trained model/animal data read; no performance claim until they actually pass.

**Decision:** results are source-verified, original authors' prior art. Maintain PR #36 Draft. Do not submit the copied result as new bat ecology, alter frozen batter paper, or rehost original code/data.
