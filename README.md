# boids — 3D movement rules → ecological patterns → prediction

**Status (2026-10-26): exploratory research repository.** This repository centralizes the 3D Boids simulations, ecological niche partition analyses, cross-repository synthesis, synthetic forecasting benchmarks, and observed bat movement-transition feasibility test from the research sessions of 2026-10-25–26.

**日本語要約：** 3D Boidsの分離・整列・凝集と、資源消費・環境追跡・個体履歴を結合し、種内／種間ニッチ分化の数理指標と予測を検証する研究リポジトリ。*合成モデルによる予測成功と、実測データで検証された運動法則を混同しない。*

## Current evidence, in order of strength

1. **Synthetic mechanism / known-truth (v1–v3).** Agent-based trajectories produce persistent individual vertical-profile differences, spatial versus vertical partition contrasts, local environmental-state buffering, and breeding-component concentration under specified parameters. A surrogate predictor performs better than simple baselines at unseen combinations drawn from the same synthetic model. These are **not wild-species forecasts**.
2. **Observed Tadarida benchmark (v4).** Archived bat GPS summaries support a small positive held-out next-climb-class gain from prior climb class (M1−M0 ≈ **+0.01383 nats/transition**, equal-individual mean, 7/8 positive). Adding annotated wind gives **−0.00113**; adding other-night individual history does **not** pass label-permutation calibration (**p=0.32**). These outcomes do not establish or refute the biological causes of individuality.
3. **Full Boids social-force estimation remains unidentifiable from this source.** Approximate archived GPS observations provided no cross-individual fix pairs both within five seconds and within 100 metres; the sampling cadence and localization error are not suitable for estimating short-range separation/alignment/cohesion coefficients. The original raw-data checksum was **not independently reverified in the local run**; no raw GPS tracks are redistributed here.

## Repository contents

- [`boids3d_empirical_v4/`](boids3d_empirical_v4/) — **canonical executable snapshot** (70 source, result and figure files, preserving their original relative paths and v4 manifest).
- [`boids3d_empirical_v4/boids3d_research/`](boids3d_empirical_v4/boids3d_research/) — 3D Boids rules, ecological ABM, niche/partition metrics, resource depletion, prediction scripts, synthetic JSON outputs, figures, and 24 regression tests.
- [`boids3d_empirical_v4/EMPIRICAL_RESULT_V4.json`](boids3d_empirical_v4/EMPIRICAL_RESULT_V4.json) — observed bat next-state prediction and neighbor-observability results.
- [`boids3d_empirical_v4/PROTOCOL.md`](boids3d_empirical_v4/PROTOCOL.md) — definition of observed transition tasks, cohorts, controls, and limitations.
- [`archives/`](archives/) — unmodified original v2, v3 and v4 release ZIPs so prior snapshots are not silently rewritten.
- [`docs/EVIDENCE_AND_PREDICTION.md`](docs/EVIDENCE_AND_PREDICTION.md) — mapping to batter, ODSP, mina, and louis and the precise scientific claim boundaries.
- [`docs/MIGRATION_MANIFEST.json`](docs/MIGRATION_MANIFEST.json) — per-file SHA-256 and Git blob SHA-1 audit of the staged transfer.

## Reproduce without raw animal records

```bash
python -m pip install -r requirements.txt
cd boids3d_empirical_v4
python -m unittest discover -s boids3d_research -p 'test_*.py' -v  # 24 tests
python -m unittest discover -p 'test_*.py' -v                 # 4 tests
cd boids3d_research
python predict_niche.py --help
```

The observed-data numerical benchmark requires the original Movebank source. Follow [`boids3d_empirical_v4/README.md`](boids3d_empirical_v4/README.md) and its explicit MD5 gate. Avoid claiming raw-data re-execution from the bundled aggregates alone.

## Cross-project positioning

- [batter](https://github.com/zuizui0223/batter): persistent bat-specific vertical strategies without obligatory additional spatial segregation.
- [ODSP](https://github.com/zuizui0223/odsp): niche thickness versus transferable vertical/temporal state organization.
- [mina](https://github.com/zuizui0223/mina): concentration of penguin breeding components as abundance declines.
- [louis](https://github.com/zuizui0223/louis): within-home-range hydrological state buffering in King Rails.

The four repositories provide separate empirical results. **boids is a mechanistic bridge and an independent prediction-validation programme, not a replacement for their frozen analyses.**

## Licence and release boundary

No licence is assigned by this migration. Research source attribution and original upstream dataset licences must be verified before republishing or redistributing any raw biological records. No raw animal GPS records are included in this repository snapshot.
