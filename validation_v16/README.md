# v16 — Independent eight-flock observed GPS prediction at two time horizons

**Source:** Watts, Nagy, Burt de Perera & Biro (2016), [Zenodo 4943714](https://zenodo.org/records/4943714), data DOI `10.5061/dryad.508j2`, CC0. Original ZIP 272,270,105 bytes; SHA256 `7380feccd8c2e4e1675679411d1ee8075cd29ccbd2dada98e317ca88053ffbfa`. No GPS animal tracks are redistributed.

## Purpose and evidence

The repository separates source integrity, the near-instantaneous **GPS heading** forecast, and the repeated **navigation-route bearing** forecast.

- `source_gate.py`, `format_gate.py`: independently verified 8 flocks, 559 true GPS CSVs, 178 `._` sidecars excluded, 11,575,534 physical data rows, identical Qstarz 18-column GPS schemas. Source checks only — **not ecological effects**.
- `route_memory_forecast.py`: frozen first-observed outward 500–4500m bearing test on future releases 9–15, trained only from releases 5–8. Across eight flock clusters, past flock-history advantage was **4/8** positive with 95% cluster CI crossing zero. [Result](../docs/OBSERVED_EIGHT_FLOCK_ROUTE_RESULT_V16.md).
- `fast_turn_forecast.py`: frozen future-release 1-second GPS heading change test on 9,279 matched anchors; current nearest partner vs same partner 10 seconds earlier vs own+route. Eight whole-flock holdouts, training on only other flocks' releases 5–8. **7/8 flocks positive**, mean error reduction 4.64% relative to stale. [Result](../docs/OBSERVED_EIGHT_FLOCK_FAST_RESULT_V16.md).
- `results/slow_route_aggregate_v16.json`, `results/fast_turn_aggregate_v16.json`: aggregate-only machine-readable extractions from full passing CI receipts. They do **not** include exact animal locations, times or unaggregated predictions.

The pre-outcome [prediction protocol](../docs/DUAL_TIMESCALE_ROUTE_PREDICTION_CONTRACT_V16.md) and [source admission](../docs/EIGHT_FLOCK_INDEPENDENT_SOURCE_CONTRACT_V16.md) are preserved. No post-hoc threshold/lag/ridge/model change was used to rescue any failure. Both raw-source studies can be re-run with original Zenodo archive; they are independent of v6, v8 and v15 previously frozen observed sources.

## Reproduce

```bash
python -m pip install "numpy>=1.26,<3"
PYTHONPATH=validation_v16 python -m unittest discover -s validation_v16 -p 'test_source_gate.py' -v
PYTHONPATH=validation_v16 python -m unittest discover -s validation_v16 -p 'test_format_gate.py' -v
PYTHONPATH=validation_v16 python -m unittest discover -s validation_v16 -p 'test_route_memory_forecast.py' -v
PYTHONPATH=validation_v16 python -m unittest discover -s validation_v16 -p 'test_fast_turn_forecast.py' -v
PYTHONPATH=validation_v16 python validation_v16/source_gate.py
PYTHONPATH=validation_v16 python validation_v16/route_memory_forecast.py
PYTHONPATH=validation_v16 python validation_v16/fast_turn_forecast.py
```

This uses several hundred MB of temporary source archive and streams GPS rows; it may require multiple GB of transient disk during execution. GitHub Actions [source audit](https://github.com/zuizui0223/boids/actions/runs/40614271265), [slow forecast](https://github.com/zuizui0223/boids/actions/runs/40614826472), [fast forecast](https://github.com/zuizui0223/boids/actions/runs/40615273961) are the original outcome receipts. Each script downloads/checks the same original archive independently before its analysis.

## What v16 does NOT demonstrate

- Direct animal-to-animal causal influence, true separation/alignment/cohesion forces or their unique coefficients.
- A real food niche, resource access, breeding success, stable species partition, field-confirmed social-choice imitation or v13's simulated network rewiring.
- A measured vertical niche: Qstarz `ALTITUDE` is present but uncalibrated and can contain geoid and instrument errors.
- A controlled comparison between v15's negative and v16's positive fast forecasts; different data/feature regimes remain.
- Long-run equivalence of flock history to a null: its 8-flock bootstrap CI includes zero, which is **not** an equivalence test.

All biological claims are restricted to **held-out predictive information** in a particular independent original-GPS experiment.
