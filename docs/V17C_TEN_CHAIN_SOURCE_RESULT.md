# v17-C source-only result: ten-chain eLife experiment has a public 1.231-GB source, not yet admissible

**2026-10-28 JST.** This is a **metadata-only independent-source audit**, not a bird GPS analysis, movement prediction, or observed wind/solar/social mechanism.

## Independently published source

Valentini et al. (2021), *Naïve individuals promote collective exploration in homing pigeons*, eLife 10:e68653, [DOI 10.7554/eLife.68653](https://doi.org/10.7554/eLife.68653). Its article describes **ten independent successive transmission chains**, each using five generations of paired homing and around twelve repeated flights per generation; 343 eligible paired flights were used in the published analysis. These are prior authors' reported experimental design and findings, **not newly verified animal records**.

The article links the original data/code to [Figshare 14043362](https://doi.org/10.6084/m9.figshare.14043362), officially reported as DOI `10.6084/m9.figshare.14043362.v1`, **CC BY 4.0**.

## Source metadata actually obtained

[GitHub Actions original Figshare API audit run 40624919419](https://github.com/zuizui0223/boids/actions/runs/40624919419) completed source-only 5/5 tests and returned this original file listing:

| Original file | Published bytes | Published MD5 | Status |
|---|---:|---|---|
| `paper_supp_info.pdf` | **660,191** | `cc6453ca9c9a0cfb0c5d2134f6b9df4d` | Source *metadata* verified only |
| `figshare.zip` | **1,231,215,640** | `4f4a3cbe268562b14b19b04eaa325470` | **Not downloaded**; exceeds frozen 160-MB per-file source safety cap |

The original ZIP's Figshare MD5 is a **provider declaration**, not independently computed. Its contents, original GPS timestamps, individual/chain IDs, overlap and raw observations remain **uninspected**. No source SHA256 or GPS outcome is claimed. [Machine-readable Figshare source-only receipt](../validation_v17/results/ten_chain_original_metadata_v17.json).

## Decision

The eLife paper reports **ten chains**, exceeding the 2019 Taylor pairing study's five 4-bird social components, and might be well suited to separate short-turn social information from later route memory. **But the new data have NOT passed source admission** because its 1.23-GB original archive was not downloaded, and cannot yet independently establish the ten raw chains, raw UTC clock, synchronized neighbor coverage or environmental wind metadata.

No version of v15/v16 results was touched, and no forecast threshold was relaxed. If a smaller official raw GPS/source subset or checksum-pinned downloadable archive with chain identifiers becomes available, re-register a bounded source-only Stage C2 before opening any movement outcomes.

## Alternative more manageable source candidate

Morford et al. (2026), *Collective route memories emerge through differential forgetting of navigational information in homing pigeons*, [Scientific Reports DOI 10.1038/s41598-026-39898-2](https://doi.org/10.1038/s41598-026-39898-2) reports **14 original pigeon pairs** with training flights and subsequent paired-vs-solo memory tests. The authors' [public GitHub repository](https://github.com/Morfordjoe/Collective-route-memories-in-homing-pigeons) contains `CM_trimmed.zip` (**21,425,810 bytes** as listed by GitHub), code and aggregate CSV tables. This is a **candidate**, not yet ingested or checked for true independent pairs/UTC. Its value is potentially in **slow route memory**, *not* an established wind × neighbor effect. This source's actual raw tracking content and author license must be verified before any model fitting.
