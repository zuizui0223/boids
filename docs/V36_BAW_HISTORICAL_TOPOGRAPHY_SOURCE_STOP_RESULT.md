# v36 — BAW historical 10m bathymetry metadata SOURCE STOP

**Date 2026-10-31 JST. STATUS: `BAW_HISTORICAL_DEM_RASTER_SOURCE_NOT_ADMITTED`.** This is a source-availability and vertical-reference gate, **not a null effect of local tidal exposure or oystercatcher habitat use**.

## Original publisher, source, temporal fit
Dataset: Bundesanstalt für Wasserbau (BAW), *TrilaWatt Topographie (1996–2014, 2022)*, original DOI [10.48437/4baaf0-aeaf58](https://doi.org/10.48437/4baaf0-aeaf58), advertised Dutch Wadden Sea annual **10m** GeoTIFF topography interpolated at July 1, 1996–2014. Intended years 2008–2012 overlap original Schiermonnikoog oystercatcher GPS period. Horizontal projected reference is **EPSG:25832 ETRS89 / UTM32**; original published vertical reference **DE_DHHN2016_NH**, while Rijkswaterstaat original official water heights at `schiermonnikoog.waddenzee` are **cm relative to NAP**. They cannot be numerically subtracted without a provider/officially validated vertical datum conversion. No guessed constant offset or movement-effect-tuned registration is admitted.

Original publisher source endpoints probed **without reading raster pixel values or any animal GPS**:

- Directory `https://dl.datenrepository.baw.de/7000/B3955.02.04.70237/Topographie_PP_1996-2014_NL/` returned **HTTP-success HTML, 2,752 bytes**, but only navigation/sort links. **No actual individual annual raster filenames for 2008–2012 appeared.** The year range in a folder title is not proof that original dated GeoTIFF files are accessible.
- WCS 2.0.1 `https://mdi-dienste.baw.de/geoserver/TrilaWatt_Topographie/wcs?SERVICE=WCS&REQUEST=GetCapabilities&VERSION=2.0.1` was **read TimeoutError** during original source-only GitHub Actions, so no original service coverage IDs were verified. Do not invent WCS `CoverageId` names.
- The original [source-only execution 41190951507](https://github.com/zuizui0223/boids/actions/runs/41190951507) passed all **five pure source grammar/CRS/vertical tests** and archived these source availability outcomes. Green CI validates our code but **not access to a GeoTIFF**.

## Scientific interpretation and next required source

Because exact original historical raster data bytes, original georeferencing, nodata/vertical units, and official NAP↔DHHN2016 transformation have not been verified, we **did not**:
- query original raster pixels, compare high/low elevation with astronomical tide height,
- calculate dynamic exposed mudflat area `A_t = area\{s : z_bed(s) > H(s,t)\}`,
- link bird GPS points with actual exposed/dry habitat,
- or infer that the v33/v34 speed effect is explained by new food supply.

These are **missing ecological measurements**, not negative evidence about tidal activity gating. A future revised source protocol can target official publisher-controlled original annual files or local verifiable native vertical conversion, with source-only admission before GPS/location joins. Do not use v35A inaccessible ecotope, v35B basin polygon or regional quantile summary as fabricated bed heights.

Earlier independent source STOPS remain separate; v29–v34-B original data and results unchanged. No eBird, no TinyFish.

[Original frozen v36 protocol](V36_BAW_HISTORICAL_BATHYMETRY_SOURCE_PROTOCOL.md) · [source-only code](../validation_v36/source_only.py) · [full machine-readable provider receipt](../validation_v36/results/BAW_original_topography_source_only.json).
