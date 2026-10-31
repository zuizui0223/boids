# v35: Historical Wadden Sea ecotope GIS — original spatial habitat source admission

**Frozen on 2026-10-31 JST, after v33/v34 and v34-B tide-by-GPS velocity outcomes were already opened.** This is explicitly an exploratory next step, NOT original registration of the previous movement associations, not independent animal replication, and not a causal tidal foraging test. Previous v29/v30/v31/v32/v33/v34/v34-B endpoints are immutable. The source-only checks below do not access the original bird's GPS coordinates or movement outcome values.

## Scientific question

The earlier one-site Schiermonnikoog wild oystercatcher analysis (2008–2014) found robust within-bird relationship of subdaily movement with astronomical tide height and falling/rising direction, including fixed GPS interval control, but **no directly measured food/mudflat use**. A physical exposure interpretation must be tested against an **independently constructed historical intertidal habitat map** rather than equating water level with foraging opportunities.

The available **Baptist et al. trilateral Wadden Sea ecotope map v2** is representative of **2008–2012**, and uses underlying bathymetry, mean exposure time, salinity, flow, sediments and salt marshes. It is a **STATIC categorical map with community habitat/ecotope proxy**, **not a contemporaneous sea-bed DEM** or waterline surface. Do NOT claim that a mapped polygon was actually exposed under a particular gauge height; point-specific exposure requires locally referenced bed elevation and adequate measured water-level propagation.

Original corrected publication:
- Mendeley Data v2 **DOI [10.17632/27mysx289g.2](https://doi.org/10.17632/27mysx289g.2)**, exact dataset `27mysx289g`, expected file `EctpWZ3L_gpkg.zip`. The corrigendum fixed a shallow-sublittoral / low-intertidal classification boundary from **0.001% to 4% mean exposure**. Never use v1 or silently replace with different habitat classifications.
- Second original host / distribution channel: Wageningen Marine Research (WMR) official WFS at `https://opengeodata.wmr.wur.nl/geoserver/ows`. Exact publicly advertised layer names previously identified *without any GPS spatial join*: `WS3shp:ws3_ecotope_mp_basic`, `WS3shp:ws3_ecotope_mp_litoral_zones_and_dynamics`, and `WS3shp:ws3_bivbeds_focc`. A WFS layer name alone does NOT prove it matches the corrected Mendeley v2; record source attribution and layer-version evidence before linking as one source.

## Stage A admission (this PR phase): source-only, no bird coordinates

1. Query **public** Mendeley exact v2 metadata and file manifest, original DOI/version, authorized dataset download metadata, exact full ZIP size and SHA256, CC BY 4.0 license. Public API may require authorization. If so, preserve 401/403 **SOURCE_NOT_ADMITTED** without inventing credentials or using unofficial mirrors. Do not export expiring signed download URLs or authorization tokens.
2. Independently query official WMR WFS `GetCapabilities` and `DescribeFeatureType` for exactly the three candidate layer names; record original advertised CRS, native bounding boxes, schema field names and types, source original service URL, version/metadata attribution. Limit all metadata responses to 15MB, XML parsing only, no geometry, original bird data or private locations.
3. Source gate PASS requires either **the corrected v2 file with provider-verified checksum/version** or **the WMR public original ecotope layer plus independently documented same corrected-v2 content version**. An ecotope layer accessible without source-version evidence is only `SCHEMA_AVAILABLE_VERSION_UNVERIFIED`, **not** biological analysis admission.
4. Both source paths blocked/mismatched => STOP with metadata QA. **Never make up per-pixel elevations or interpret a wetland category as instantly exposed.** No fallback to later (2015–2022) intertidal layers after seeing the earlier GPS outcome.

## What may be tested after original source pass (separate frozen Stage B)

Only original **2008–2012** Schiermonnikoog GPS source with source MD5/SHA pins and original v33-D/V34 per-bird receipt replay. Geographic cropping pre-frozen to **25km** from official `schiermonnikoog.waddenzee` WATHTE station at 53.468937N 6.202908E. Must identify publication-validated ecotope legend mapping into clearly defined **intertidal**, **sublittoral**, **salt-marsh**, and **unknown** classes; unknown excludes a bird from the class-specific comparison without reassigning. Polygon boundaries must carry a documented CRS, modern PROJ reproject, no silent longitude/latitude swap. Non-overlap and source-coverage counted; original GPS source not changed.

Candidate ecological test (conditional on source content and a **new frozen pre-outcome Stage B protocol**): assess **which ecotope habitats are occupied at low vs high tide**, and separately whether the ebb−flood *velocity* difference changes in ecotope space. Compare within bird × year-month × clock hour and GPS duty, equal bird weights. Observed point occupancy in mapped habitat is only presence, not used-versus-available selection; independently defined accessible area/choice set is needed for niche selection. Do not quietly score only occupied favorable habitats. Failure of class support => STOP and report no ecology effect. Independent site/population needed for ecological universality.

## Security, version, and no-result-repair rules

Only named host endpoints may be called by read-only GitHub Actions. Source-only API GET requests must not follow unexpected off-host redirects to untrusted addresses. Never use original GPS, original 10min tide arrays, bird IDs, coordinates, or ephemeral source tokens in reports. No confirmed ecotope/habitat association until the *version, geometry and legend* gates pass, Stage B code/tests are committed, and source-data GPS join executed. No eBird, no TinyFish.

**Deliverables Stage A:** immutable protocol, machine-readable source response inventory (including STOP/unknown), unit tests and public GitHub Actions evidence, standalone draft PR, with main/earlier drafts unchanged.
