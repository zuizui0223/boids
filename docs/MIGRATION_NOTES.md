# Migration notes

Source: local ChatGPT-generated 3D Boids outputs from 2026-10-25 and observed-data validation v4 from 2026-10-26.

- `boids3d_empirical_v4/` is a **byte-preserving copy** of the available 70-file v4 snapshot; neither the data nor the original `FILE_MANIFEST_V4.json` has been silently changed.
- `archives/` preserves three published ZIP snapshots (v2, v3, v4). v1 material is present in the later snapshots and canonical v4 research folder.
- New top-level README, dependencies, evidence document, CI configuration, and migration manifest are additional organizational files, not new empirical findings.
- The sibling repository results are referenced by GitHub URL only; their repositories and frozen papers are untouched.
- Raw bat movement records and credentials are not transferred.

Tested before export: 24 research unit tests + 4 observed-data method unit tests, Python 3.11+-compatible scientific packages available in local runner.
