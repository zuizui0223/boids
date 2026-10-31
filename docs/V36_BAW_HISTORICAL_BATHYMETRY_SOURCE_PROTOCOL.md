# v36 — historical BAW TrilaWatt 10m bathymetric topography source-only gate

**2026-10-31 JST**, separate from the original v35-A corrected ecotope API STOP (Mendeley 401 / WMR 503) and v35-B morphological-basin source STOP (not pointwise exposure). All older v33/v34 field GPS+tide observations are already known, hence later GIS association is *post-outcome exploratory*. This protocol is frozen **before opening any actual dated BAW GeoTIFF pixel values or linking GPS to bathymetry**.

## Exact independently produced bed-elevation product

Original authoritative dataset: Bundesanstalt für Wasserbau (BAW), **Milbradt & Pineda Leiva (2025), TrilaWatt: Topographie (1996–2014, 2022)**, DOI [10.48437/4baaf0-aeaf58](https://doi.org/10.48437/4baaf0-aeaf58), CC BY 4.0. Original year-specific products cover the Dutch part of the Wadden Sea; raster GeoTIFF resolution **10m**, nominal annual snapshot date **July 1**. The source models combine surveys and use spatial-temporal interpolation; they are **not raw contemporaneous bathymetric sounding at every animal GPS fix**. The original source advertises projected CRS EPSG:25832 ETRS89/UTM32 and vertical datum **DE_DHHN2016_NH** (EPSG:7837 cited in source metadata).

Two original BAW source portals are authorized for *metadata only*:
1. HTML folder `https://dl.datenrepository.baw.de/7000/B3955.02.04.70237/Topographie_PP_1996-2014_NL/` (official reference under BAW source catalogue).
2. OGC WCS 2.0.1 capabilities `https://mdi-dienste.baw.de/geoserver/TrilaWatt_Topographie/wcs?SERVICE=WCS&REQUEST=GetCapabilities&VERSION=2.0.1` (original official linked WCS).
Exact historical observation years to locate are **2008, 2009, 2010, 2011, 2012**, matching original oystercatcher years and published ecotope period. Never replace a failed year with 2015–2022 after inspecting GPS/tide behavior.

## Stage A read-only source discovery

- Fetch each exact official URL (≤15MB response), verify returned HTML or WCS XML origin, source year labels/coverage IDs and available GeoTIFF names, original CRS/vertical metadata, nominal July reference, resolution and service format. **No raster pixel values, no animal GPS, no RWS numeric height**.
- A source year must be documented by exact provider link or WCS CoverageId, not guessed from an ISO year path or a file. Preserve original source URL/coverageID and server metadata digest; cap to 100 files per source page and 1000 coverage IDs. Redact signed/download credentials from logs.
- Source-only success means only that annual raster layers exist. It does not certify native vertical datum alignment, SHA/byte completeness, nor near-island coverage. Archive not accessible, no years or service 403/500 => `V36_HISTORICAL_BATHYMETRY_SOURCE_NOT_ADMITTED`. No opportunistic alternate cloud DEM.
- Access to WCS makes it theoretically possible later to request a **small predeclared 25-km coastal crop** around the existing public gauge (53.468937N 6.202908E), in EPSG:25832; this stage will **not** call GetCoverage, select height thresholds, read raster values or score original bird GPS.

## Mandatory vertical datum gate BEFORE any exposed-area calculation

Prior original Rijkswaterstaat astronomical gauge `schiermonnikoog.waddenzee` provides water levels in **centimeters relative to NAP**. TrilaWatt original metadata states DEM in **DHHN2016 height datum**, **NOT NAP**. A physical exposure proxy at bird location needs *both quantities in the same local height reference*. Do NOT approximate NAP equal to DHHN2016, set a guessed constant offset, standardize away unknown vertical bias or tune offset against known v34 movement effects. Require an official validated local vertical transformation (or original BAW provider clarification of datum/vertical conversion) before computing z_bed(s)-H(t). Until then, report **vertical_ref_NOT_ADMITTED** and no bird-exposed/dry habitat effect.

## Conditional Stage B held-out source checks

If exact BAW 2008–2012 GeoTIFFs with native vertical transform become available, first commit complete code/tests/geometry of the spatial query and source licenses. Validate original 10m raster nodata mask, source vertical units, DHHN2016 datum, native horizontal EPSG:25832, near-island coverage, annual GPS-date rule (before/after July snapshot), and original fixed 25km source gauge cropping. Then compute exposure mapping and test bird occurrence/step states with tide by matched original bird/year-month/clock and GPS effort, preserving all supporting and negative results. A raster crossing one RWS gauge is an approximate exposure proxy, not verified water height propagation or foraging.

No eBird/TinyFish, no GPS animal ID/coordinate/time leaks, no merge, no changing v33/v34 results. Source-only CI and concrete STOP/success receipt are deliverable.
