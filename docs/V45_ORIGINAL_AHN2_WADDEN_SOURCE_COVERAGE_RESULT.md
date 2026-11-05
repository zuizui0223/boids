# v45 AHN2 (2007–2012) original NAP DTM source probe: both Wadden islands have valid georeferenced height candidates

**2026-11-05 JST. SOURCE-ONLY result, NOT a bird×tide or resource-front ecological result.**

## Reproducible original provider

[Official AHN Dataroom](https://www.ahn.nl/dataroom) lists original **AHN2 DTM** survey period 2007–2012, horizontal RD New (EPSG:28992) plus NAP vertical height in metres, source Ellipsis WCS 1.0.0 `https://api.ellipsis-drive.com/v3/ogc/wcs/e96b10b9-e964-414c-958c-57a9dbe24e62`. Unlike v42's later 2014 Dryad archive which returned HTTP401, this historical official WCS responds to GetCapabilities, DescribeCoverage and small GetCoverage GeoTIFF reads.

Original 1 WCS coverage identified: `f380e0a0-4446-4d79-b2d1-3d4df40cbc93`, advertises GeoTIFF and EPSG:28992. Each requested small **256m ×256m** source patch returned 128×128 georeferenced cells (2m resampled resolution, not native 0.5m), with a first Float32 candidate height band and second Float32 normalized 0–1 auxiliary band. The latter behaves like a coverage/validity weight, but **its alpha/quality semantics are not independently documented**. Source-only conservative gate: first-band finite and between -20..+50m NAP, second-band auxiliary >=0.999; no water/void filling, no landward extrapolation.

## Fixed source-only probe results

| Island | Original predeclared WGS84 sample lat/lon | Candidate finite pixels/16,384 | Pixels between −3 and +3m NAP | Status |
|---|---|---:|---:|---|
| Schiermonnikoog | (53.470,6.200) | **8,587** (52.41%) | **8,572** | SOURCE HEIGHT CANDIDATE |
| Ameland | (53.430,5.760) | **0 usable** | **not evaluated** | SOURCE_STOP_AUXILIARY_MASK_ALL_MISSING |
| Ameland source-only QA extension | (53.450,5.760) | **1,975** (12.05%) | **1,378** | SOURCE HEIGHT CANDIDATE |
| Ameland source-only QA extension | (53.460,5.760) | **11,851** (72.33%) | **10,709** | SOURCE HEIGHT CANDIDATE |

Ameland extension positions were frozen in [source-only amendment](V45A_SOURCE_BAND_AND_AMELAND_COVERAGE_DIAGNOSTIC.md) **after discovering the original sample location's missing auxiliary source**, but **before either new sample elevation or any bird GPS/tide spatial outcome**. They are convenience source QA points, not random habitats or independent ecological replicates. The −3/+3m band is deliberately broad physical plausibility only, not claimed accessible substrate or prey.

Original patch SHA256, source CRS, TIFF properties, normalized source auxiliary coverage and data counts are recorded in original GitHub Actions JSON. Source DTM pixel values and original GPS positions are not committed; fixed public sample coordinates are harmless source probe centers, not animal localizations. Original AHN2 DTM valid above/tide-adjacent land does **not** guarantee underwater tidal flat elevation: LiDAR may have water mask or reflected-water artifacts. Other source tile survey dates in 2007–2012 may differ from the bird GPS year. Need flightline/acquisition-year source metadata before treating height as a synchronous exact surface.

## Next field admission, NOT yet performed

Use authentic original 2010 GPS first-hour fixes to freeze source-available spatial sampling locations (not movement outcomes), request small georeferenced AHN2 coverage patches without downloading the whole AHN, then count how many **unseen 2011/2012 original GPS movement triples** have both origin/destination pointwise valid elevation and RWS matched source tide; do not modify previous fixed source movement gates. Only if enough independent birds/days/historical patches exist may a tide-stage relative destination selection hypothesis be defined. A binary hydrostatic test `elevation > remote tide-gauge height` does not yet prove locally exposed mudflat, because local hydrodynamic lag, puddles, channels, survey year and prey remain unknown.

## Exact source receipt

- [Original successful two-island WCS source CI 41946816409](https://github.com/zuizui0223/boids/actions/runs/41946816409), pure regression tests and original WCS requests PASS.
- `validation_v45/ahn2_original_dtm_source_gate.py`, `validation_v45/test_ahn2_original_dtm_source_gate.py`.
- Source pre-registration `docs/V45_FROZEN_AHN2_HISTORICAL_NAP_DTM_SOURCE.md`; transparent source extension `docs/V45A_SOURCE_BAND_AND_AMELAND_COVERAGE_DIAGNOSTIC.md`.
- Field v44 positive/negative speed-direction outcomes remain frozen separately; *no new ecology was measured at v45*.
