# v21 independent redstart NDVI × individual foray source — currently NOT ADMITTED

**2026-10-28 JST. Frozen source-access result; no ecological outcome, environmental effect, GPS, or cognitive/social-behavior model was fitted.**

## New independent ecological source

Dossman, Rodewald & Marra (2024), *Hidden space use behaviors of a nonbreeding migratory bird: the role of environment and social context*, *Movement Ecology* 12:82, DOI [10.1186/s40462-024-00523-4](https://doi.org/10.1186/s40462-024-00523-4); deposited independent original [Dryad DOI 10.5061/dryad.gb5mkkwx1](https://doi.org/10.5061/dryad.gb5mkkwx1), source metadata published 2025-11-24, **CC0**.

This dataset is an independent American redstart (*Setophaga ruticilla*) study in Jamaica, combining original receiver-transition/foray measurements with source NDVI (vegetation-resource proxy), habitat type, age and sex. Source paper reports different cohorts; do **not** infer number of repeated individual-week records from publication prose.

## What was *actually* verified

The [original provider metadata](https://github.com/zuizui0223/boids/actions/runs/40635750171) was fetched from the public Dryad v2 API for published version **5**. Official file manifest returned, among six files:

| Original version-5 file | Exact provider file ID | Reported bytes | Provider SHA256 (metadata) |
|---|---:|---:|---|
| `forays.rds` | **4478645** | **971** | `a1457fe03d6a454210e019c96724e60b8aa6ba30f124128714e035d20052b3b9` |
| `ndvi.rds` | **4478644** | **2,245** | `0ee6605fe491b2be2917f5c3c1c1123c2ff180ca36921c101f069282683069c1` |

**These digests were read from the publisher's source metadata, NOT independently recomputed over downloaded RDS bytes.** The other listed source includes `individual.rds`, `mcp.rds`, `change.rds`, `README.md`; original mcp tracks were deliberately not opened for this source-only stage.

The original download attempts returned `HTTP_401` on public `/api/v2/files/{id}/download` and `HTTP_403` on `/stash/downloads/file_stream/{id}`; on a subsequent API request even the dataset metadata returned `HTTP_403` (source-limited). Therefore **NO source RDS content was fetched and no actual individual×year×week grain could be inspected**. [Passing updated fail-closed CI](https://github.com/zuizui0223/boids/actions/runs/40635763390) preserved this negative admission status rather than declaring the source eligible.

## Original pre-outcome scientific plan and hard boundary

The [registered source contract](V21_INDEPENDENT_NDVI_INDIVIDUAL_SOURCE_CONTRACT.md) required verified original bird IDs/year/week repetition, real weekly raw NDVI and at least 8 birds / 30 eligible future weekly targets. The intended prediction was next-week forays using **previous-week NDVI** and previous individual foray history, with habitat and demographic controls; source `pred` temporally smoothed NDVI may leak future weeks and was **explicitly excluded** as a prospective predictor.

But original file access did not pass, so this condition is untested. **No new individual-memory, foraging/NDVI interaction, social network, niche, or Boids-force result exists in v21 from these files.** A publisher listing a `.rds` file is not verification that its contained bird IDs and environmental values can be independently analyzed. No prior frozen v13–v20 outcome is modified.

## Source-backed next workflow

Either obtain authorized Dryad original-file access (without inventing or bypassing restrictions), or use a **different, fully retrievable public original ecological dataset**. A separately published 2021 guineafowl seasonal source, [Papageorgiou et al. *Seasonality impacts collective movements in a wild group-living bird*](https://pmc.ncbi.nlm.nih.gov/articles/PMC8268463/) and author [ranging_seasonality repository](https://github.com/DanPapageorgiou/ranging_seasonality), contains environment **wet/intermediate/dry season_type** and group-season derived space-use fields. This may support a *new environment-label forecast*, but it shares the **same Movebank population** as v20, therefore is **NOT independent biological replication of v20**. Its exact original Rdata byte/ID/season provenance and overlap with v20 must be audited before opening response values or fitting another model.

[Machine-readable exact Dryad file manifest and access result](../validation_v21/results/source_gate_v21.json); [reproducible provider protocol and negative-control tests](../validation_v21/source_gate.py).
