# v17 — Environmental source provenance, original pair assignments and forecast admission

**Independent source only; no new v17 wild behavioral forecast has been fitted.** The 2019 Taylor et al. pigeon experiment offers simultaneous partner GPS and wind observations but has only five independent experimental social-network components across its two paired phases, not the predeclared eight.

## Frozen source data

- Taylor et al. 2019, PLOS Biology 17:e3000299, DOI `10.1371/journal.pbio.3000299`, GPS/weather dataset Zenodo `5026107`, CC0.
- GPS ZIP 240,056,153 bytes, SHA256 `030e70082b107a353dd4f0afb0cd54868438273a416efac135120a6bdf9c2b29`; weather CSV 11,529,364 bytes, SHA256 `45885ce19954fd99397b92847421d3e11a6ea2c8d22d1a1d6220ea4940fa2917`.
- GPS inventory: 458 tracks, 20 bird IDs in four phases (120/120/113/105 records). Weather: 152,227 numeric three-field rows with candidate MATLAB serial-day timestamps.
- **Independent original published pairing XLSX:** [S3 Table](https://doi.org/10.1371/journal.pbio.3000299.s008), 12,200 bytes, SHA256 `f06a89cdb0bb4df338337c1d2f459d7eee545289ede06904bc76114653981e84`. Two phase-specific reciprocal perfect matchings of 20 pigeons form exactly **five disconnected C₄ components**. This is a **source design fact**, not a movement behavioral effect.
- An automatic 4-of-20 bird holdout is network-independent for only **5/4,845** possible four-bird subsets, a **99.897%** graph-cut probability; a 10-of-20 split cannot be network-independent. This is exploratory source-graph mathematics, not an animal result.
- Weather source clock: Cumulus v1.9.4 default logs use local/system time, but the archived three-column MATLAB day export might have been transformed. GPS/weather sample time support under −1/0/+1 hour is 97.93%/100%/99.67%, not sufficient to choose a final UTC offset. Wind-from/from-to convention also needs independent source verification.

## Reproduction and status

```bash
PYTHONPATH=validation_v17 python -m unittest discover -s validation_v17 -p 'test_source_gate.py' -v
PYTHONPATH=validation_v17 python -m unittest discover -s validation_v17 -p 'test_schema_gate.py' -v
PYTHONPATH=validation_v17 python -m unittest discover -s validation_v17 -p 'test_weather_clock_gate.py' -v
PYTHONPATH=validation_v17 python -m unittest discover -s validation_v17 -p 'test_context_features.py' -v
PYTHONPATH=validation_v17 python -m unittest discover -s validation_v17 -p 'test_published_S3_pair_source.py' -v
PYTHONPATH=validation_v17 python -m unittest discover -s validation_v17 -p 'test_published_S3_graph.py' -v
PYTHONPATH=validation_v17 python validation_v17/published_S3_graph.py
```

All source scripts download independent original data into temporary directories; raw coordinates, detailed GPS course, all original weather values and numeric tarsus/body mass are excluded from repository receipts.

- [Original GPS/weather result](../docs/V17_ORIGINAL_WIND_SOCIAL_SOURCE_RESULT.md)
- [Original S3 graph result](../docs/V17_PUBLISHED_PAIR_GRAPH_RESULT.md)
- [Source/graph preregistration](../docs/V17_PUBLISHED_PAIR_GRAPH_CONTRACT.md)
- [Durable graph JSON and exact random-split risk](results/original_s3_pair_graph_v17.json)
- [GitHub Actions source test](https://github.com/zuizui0223/boids/actions/runs/40623881771), [experiment graph test](https://github.com/zuizui0223/boids/actions/runs/40624331811)

**Stop:** `5 < 8` independent original social groups. The confirmatory wind × current-neighbor forecast is **NOT ADMITTED** on this source. Do not silently count 10 phase-specific pairs as independent units across the original two partner-switching phases, or refit already opened v15/v16 GPS outcomes.

Next admissible source selection should prioritize independent repeated social groups with original GPS UTC, verified meteorological timestamps and partner ledger. One candidate for **social-route history** (not yet verified wind) is the ten independent homing-pigeon transmission chains in Valentini et al. (2021), eLife 68653, public Figshare `10.6084/m9.figshare.14043362`. **Do not claim empirical eligibility until this new source's files and chain ID mapping have been checked.**
