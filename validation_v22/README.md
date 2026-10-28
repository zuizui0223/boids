# v22 – Wild guineafowl source context and historical-group reliability

**Biological scope:** a new 2021 author-derived 11-season ecological summary of Kenyan vulturine guineafowl groups; the **same underlying Movebank Avulturinum_Farine population as v20**, NOT independently sampled animals. The source tables are already-aggregated group/season ecological indicators, NOT native GPS locations, prey-resource measurements or individual memory.

[Original source contract](../docs/V22_GUINEAFOWL_ENVIRONMENT_SOURCE_CONTRACT.md) and [frozen forecast contract](../docs/V22_FROZEN_WET_DRY_CONTEXT_GROUP_PREDICTION.md) were registered before v22 movement-response values were opened. Source: DanPapageorgiou/ranging_seasonality original pinned commit `2a3aec308bb4a8449d1eeb16beed4aff8f387116`, 2021 Movement Ecology paper; the original model table `df_dhor.Rdata` is 1,911 bytes, Git blob `a365bea412cdb6eb3f7b4c76bb0f9dda2268ea8a`, independent SHA256 `d08864e91a543403cb1e8abf1bf9ea84247543181b8d4f4464ceb03929c0fa83`.

The source has 143 group×season fidelity rows, 26 original group IDs, 11 chronological source seasons, 4 missing original responses, and 4 shared categorical regimes (dry/intermediate/wet/wet_breeding). Original structural CI [40636174443](https://github.com/zuizui0223/boids/actions/runs/40636174443) succeeded.

**Real source exploratory forecast:** 23 original group IDs, **113** later group-season targets, same targets for M0 previous OTHER groups, ME earlier OTHER groups in matching regime (fallback only for 29 historical-unsupported contexts), MG OWN group's earlier seasons, and MEG fixed shrink w=n/(n+2) of MG into ME. Original model CI [40636440228](https://github.com/zuizui0223/boids/actions/runs/40636440228) passed all nine preregistered known-truth/no-time-leakage tests and the original source hash.

| Fixed model | Group-equal future-season fidelity MSE |
|---|---:|
| M0 pooled past external groups | 0.003818 |
| ME past external matching regime | 0.003615 |
| MG raw own group history | 0.005485 |
| **MEG context + fixed shrinkage** | **0.003292 (best)** |

**Main environmental-context-conditional history question:** ME−MEG **+0.000322**, **11/23** positive, group-bootstrap 95% [−0.000592,+0.001246]: **not robustly supported**. Pure environment class M0−ME +0.000203, **12/23** and CI crosses zero. **Registered shrinkage reliability secondary:** MG−MEG **+0.002192**, **18/23** positive, group-bootstrap 95% **[+0.000544,+0.004153]**. This is predictive regularization, not causal learning or a demonstrated optimal shrinkage coefficient.

The regime is a target-season **retrospective scenario label**, not a prospective climate forecast; a wet_breeding class additionally reflects reproductive season, not only humidity. Shared year/season effects remain a major uncertainty. No earlier v13–v21 endpoint was tuned. [Full scientific result](../docs/V22_OBSERVED_GUINEAFOWL_ENVIRONMENT_HISTORY_RESULT.md) · [actual original-source and full numerical receipts](results/).

Reproduce original source-only checks and actual exploratory forecast:

```bash
python -m pip install 'pyreadr>=0.5,<1' 'pandas>=2,<3' 'numpy>=1.26,<3'
PYTHONPATH=validation_v22 python -m unittest discover -s validation_v22 -p 'test_source_gate.py' -v
PYTHONPATH=validation_v22 python -m unittest discover -s validation_v22 -p 'test_regime_group_forecast.py' -v
PYTHONPATH=validation_v22 python validation_v22/source_gate.py
PYTHONPATH=validation_v22 python validation_v22/regime_group_forecast.py
```

Only group/season aggregate results are stored; raw original author Rdata is not redistributed. The raw Movebank wildlife GPS still needs author access, and this study does not estimate individual trajectories, real social contacts, food use or 3D niche.
