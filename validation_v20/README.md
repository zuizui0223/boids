# v20: new wild ecological group-season prediction, not a homing-route or Boids-force fit

Original wild vulturine guineafowl, Papageorgiou & Farine (2020), eLife DOI 10.7554/eLife.59902. The authors' public summary is at DanPapageorgiou/Group_size, Git commit 15ea08ed10555beba227792f4ef106d87d52b6a4, 2,717-byte original Rdata, SHA256 c6a534993e99f2cb324e9691ff7ec58095bf7cd7e82d7a38721f3575097cbb55.

The source contains **45 group-season observations of 21 original groups over five season codes**, including 15 groups repeated in at least two seasons and 8 in at least three. The published raw GPS is in author-access-restricted Movebank Avulturinum_Farine study 475851705, **not downloaded or opened**. This work forecasts a derived **within-season spatial overlap fidelity statistic**, not a trajectory/niche preference/animal memory neural process.

[Outcome-blind fixed v20 model protocol](../docs/V20_FROZEN_GROUP_SEASON_FIDELITY_FORECAST.md): For each target group-season with earlier same-group and other-group states, M0 predicts using equally weighted earlier OTHER group values; M1 from earlier OWN group values; M2 combines them with predeclared shrinkage w=n/(n+2). All predictors are older than the target season, and all models score the same eligible cells.

**New actual observed 2020-source results:** 15 group clusters / 24 future group-season targets. Fidelity: M0 MSE 0.0105669, M1 0.0072165, M2 0.0079186, M0−M2 gain **+0.0026483**, 11/15 groups positive, whole-group bootstrap 95% **[+0.000618,+0.004493]**, ~25% lower primary MSE. The 11/15 exact sign probability is 0.0592; M2 has not been shown to beat M1. Other predeclared log core-range area and log speed outcome intervals overlap zero.

An explicitly **post-outcome** audit reproduced the exact primary and found all original future-season effects and every leave-one-group-out primary mean positive; this is not an independent confirmatory test. All groups share the original savannah and four later seasonal contexts.

[Full publication-quality result and scientific limits](../docs/V20_OBSERVED_WILD_GROUP_FIDELITY_RESULT.md), [group/season signed scores and source hash](results/forward_group_fidelity_v20.json), [source-only metadata](results/wild_group_source_metadata_v20.json), [after-result audit](results/postresult_group_season_audit_v20.json).

## Reproduce

Run from the root of the boids repository:

```bash
python -m pip install "pyreadr>=0.5,<1" "pandas>=2,<3" "numpy>=1.26,<3"
PYTHONPATH=validation_v20 python -m unittest discover -s validation_v20 -p 'test_source_gate.py' -v
PYTHONPATH=validation_v20 python -m unittest discover -s validation_v20 -p 'test_group_season_forecast.py' -v
PYTHONPATH=validation_v20 python -m unittest discover -s validation_v20 -p 'test_postresult_audit.py' -v
PYTHONPATH=validation_v20 python validation_v20/source_gate.py
PYTHONPATH=validation_v20 python validation_v20/group_season_forecast.py
PYTHONPATH=validation_v20 python validation_v20/postresult_audit.py
```

All three original GitHub Actions receipts were successful: [source 40627875842](https://github.com/zuizui0223/boids/actions/runs/40627875842), [forecast 40628278255](https://github.com/zuizui0223/boids/actions/runs/40628278255), [credibility audit 40628553210](https://github.com/zuizui0223/boids/actions/runs/40628553210).

Strictly do not treat predictive source season grouping as calibrated climate/environmental availability. Full 3D niches, sensory/Boids motor laws, actual resource rewards, individual social histories, controlled temporal manipulation and interspecific evolutionary mechanisms remain untested here. All v13–v19 previous results remain unchanged.
