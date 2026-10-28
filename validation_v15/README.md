# v15 — Frozen independent observed GPS horizontal-turn forecast

**Data:** Huang et al. 2026 Zenodo DOI [10.5281/zenodo.21092705](https://doi.org/10.5281/zenodo.21092705), CC BY 4.0. Only three independently recorded pigeon flock-flight episodes. The source ZIP is 126,588,691 bytes and its exact SHA256 is pinned in `forecast.py`.

**Scope:** In-flight **2D GPS course-over-ground turning** one second ahead. This is **not** estimated Boids force, social causation, 3D niche use, learning, or the v13 network-rewiring mechanism. The original v6 bat and v8 pigeon negative primary results are not revisited.

[PREDECLARED contract](../docs/OBSERVED_HORIZONTAL_TURN_FORECAST_CONTRACT_V15.md) was saved before empirical movement outcomes. It fixes source checksum, raw UTC and speed criteria, three whole-trial holdouts, matched partner contemporaneous-versus-10s-stale/own-only models, 30s lagged same-partner surrogate on a restricted matched subset, ridge penalty and trial-balanced training weights.

### Reproduce

```bash
python -m pip install "numpy>=1.26,<3"
PYTHONPATH=validation_v15 python -m unittest discover -s validation_v15 -p 'test_*.py' -v
PYTHONPATH=validation_v15 python validation_v15/forecast.py --out validation_v15/results/frozen_turn_forecast_v15.json
```

The script downloads the original bounded ZIP temporarily, checks both declared archive hashes and all 56 original sensor-file SHA256s, uses **no repaired/interpolated GPS times**, processes airbornes with explicit speed/continuity gates and outputs **only trial-level numeric scores and aggregated source QC**. No tracks, individual coordinates or event-level predictions leave the runner.

A source-eligibility failure produces `NOT_ADMITTED` rather than a tuned threshold or an invented positive result. With only three independently held-out flight groups, the smallest one-sided exact sign-test p-value is 0.125 even if all improve. 
