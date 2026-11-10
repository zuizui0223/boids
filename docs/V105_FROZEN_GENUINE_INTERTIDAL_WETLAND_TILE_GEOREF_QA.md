# v105 — original GIC 2019 tidal-wetland GeoTIFF source audit (new source-based information)

Frozen 2026-11-10 JST after source-only original v104 discovered genuine GCS `twprobabilityEnd` tiles. These 2017–2019 30-m probabilities include tidal flat/mangrove/saltmarsh, and are *not* tide-exposed dry ground at a particular hour; the publication is Murray et al. 2022 Science DOI 10.1126/science.abm9583.

## Pre-specified source and estimand

Choose exactly the lexicographically first original provider object in `gs://gic-archive/gic-2019-v1-0/v1-0-1/murray-gic-v1.0.1-twprobabilityEnd-*` from original v104 metadata, with file name `murray-gic-v1.0.1-twprobabilityEnd-0000000000-0000000000.tif`. Read its genuine bytes from original Cloud Storage public HTTPS GCS, verify base64-encoded original provider MD5 and source size from provider metadata BEFORE any raster extraction, never substitute random synthetic raster or a different layer.

Primary result: actual raster CRS, transform, bounds, width/height, native no-data convention, alpha/internal mask, pixel size, original source value range on fixed sampled windows, and summary source QA. No source point or radius is selected based on whether a plausible ecological effect is found.

Secondary source-identity test: obtain all *2019* original 160 quality-eligible UHSLC gauge locations from 12 source-immutable v94 artifacts, and check which gauge **point coordinates** fall inside this one tile's footprint (converted to WGS84). Do not report outside-this-tile gauges as having no tidal wetland. If an original station falls within this tile, sample its native pixel with no temporal interpolation; no causal habitat area or true dry habitat window estimated. Stations without this tile's geographic support remain `SOURCE_OUT_OF_SELECTED_TILE`, *not* absence of wetland.

Do not perform real coastal-buffer pixel area estimation until original tile CRS, scale, mask, projection, theme and valid probabilities are checked. No claimed biotic signal, physical tidal habitat exposure, food or GPS. This is a technical QA stage necessary before a real macroscopic habitat-conditional ecological model.

Source reference: https://globalintertidalchange.org/data-usage and GCS first party object metadata. Keep original checksum, generation, and bytes in report, plus selected actual pixel result if source support, but never copy 53MB raw GeoTIFF to GitHub repo.
