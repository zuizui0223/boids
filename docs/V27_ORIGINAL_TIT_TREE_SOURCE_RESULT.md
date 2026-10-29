# v27 original 18 breeding-pair long-tailed tit movement × available tree source — provider SHA manifest PASS, source bytes NOT ADMITTED

**2026-10-29 JST. Source-only provider provenance result, not a new habitat-use or social-movement effect.** Original publication: Ellison-Neary et al. (2026), *An intuitive method to calculate the utilization distribution of an animal from step-selection analysis*, *Methods in Ecology and Evolution* [DOI 10.1111/2041-210x.70316](https://doi.org/10.1111/2041-210x.70316). Independent original [Dryad DOI 10.5061/dryad.kprr4xhm0](https://doi.org/10.5061/dryad.kprr4xhm0), published April 29, 2026.

The original authors' paper described **18 long-tailed tit breeding pairs** tracked by following jointly moving pairs on foot and independently sampled tree cover/availability. That is authors' reported study design; the current v27 workflow has NOT directly inspected original animal rows, pair IDs, observed movement sequences or tree cover values.

## Original provider metadata actually verified

Official Dryad v2 API DOI/version query succeeded, confirming source dataset **version 4**, **CC0-1.0**, exact original file sizes/IDs and provider **SHA-256** declarations:

| Original file | Exact source bytes | Dryad official SHA256 (provider only) |
|---|---:|---|
| `GPS_LOCATIONS.csv` | **136,016** | `4a19c45a370971a95e70eea84c8415f1ebc42e616e5122924b938469fedf5530` |
| `NestLocations.csv` | **7,742** | `f3f350d2f720b4e504b01d3fbfb2fa6d8a95dc6ad02228dd7464cd4562ba2123` |
| `README.md` | **2,123** | `19b56ab3e4d5d684d63a3baa83e166919b8e7ff72ba24b655829718449212b51` |
| `Tree_Availability_Data.csv` | **128,484** | `91ec96d3dc3c59ba8b2a692749ef5e119ef56e51513e4ffd4493da93fa8b9e66` |
| `TREE_SAMPLING_LOCATIONS.csv` | **8,431** | `11c580ed70caed1958a537a432e46e1ff54cbcd27abf69e26a33609427afa96d` |

These digests were **READ from official publisher metadata**, NOT independently verified by hashing source file bytes.

## Actual original source access result

Every one of the five publisher-authorized public file URLs returned HTTP **401** (API `/api/v2/files/{id}/download`) and the alternate provider file-stream URL returned HTTP **403**. No actual `.csv` or README bytes were downloaded.

The independently reproducible [source CI 40850950358](https://github.com/zuizui0223/boids/actions/runs/40850950358) completed **5/5 known-truth source identity/access tests**, preserved all original IDs, file sizes and failure codes, and returned `NOT_ADMITTED_SOME_OR_ALL_ORIGINAL_DRYAD_FILES_NOT_RETRIEVABLE`. That is **source access rejection**, not evidence that the original experiment lacks chronological GPS, tree cover or repeated pair histories.

[Original provider-only machine-readable source receipt](../validation_v27/results/longtailed_tit_original_Dryad_source_v27.json). [Source contract](V27_LONGTAILED_TIT_ORIGINAL_SOURCE_CONTRACT.md) prespecified only genuine original bytes, pair×time structure, independent mapped tree grids and future-choice model admission if the files were accessible. It was not relaxed and no habitat-choice model was fitted.

## Implication for Boids / ecological prediction

The experimental design of 18 jointly traveling long-tailed tit pairs and sampled tree abundance could test whether earlier group spatial-use state adds information to a movement-kernel/environment-only prediction. But this requires access to the original GPS and availability grids and an honest pair-level holdout. A published source description or provider SHA is insufficient to claim such a field effect.

The original v25 case-dependent habitat source format artifact and corrected non-support for individual private history remain unchanged, as does v26 USGS turtle PIT/step labels STOP. A separate Zenodo-hosted original multi-taxon source with downloadable original bytes and source-identified used/available alternatives should be prioritized for the next ecological effect, rather than repeatedly retrying inaccessible Dryad anonymous file downloads.
