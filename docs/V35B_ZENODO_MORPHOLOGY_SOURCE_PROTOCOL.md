# v35-B — independent Zenodo tidal-flat polygon source gate (not corrected ecotope v2)

**2026-10-31 JST.** This is a new explicitly post-v35A source study after the original Mendeley v2 API failed with HTTP 401 and official WMR WFS failed with HTTP 503. The original v35-A source STOP is immutable. All v33/v34 GPS+tide results are already known; any later spatial overlap is exploratory, not independent animal evidence or blind registration.

## Exact original source and version

Pineda Leiva, Lorenz & Lepper, Zenodo [14535985](https://zenodo.org/records/14535985), DOI 10.5281/zenodo.14535985, version v2, CC BY 4.0. Required archive filename **TidalFlats_UTM32_Baptistetal2019_extended.zip**, published MD5 **eaa559c9b8401ed4db70b0ef70fe2d7c**, approx 194.4kB. This is a **derived extended morphological/tidal-flat polygon** based on Baptist et al. 2019, and is expressly **NOT** the 2021 corrected v2 ecotope GeoPackage whose 4% exposure threshold was fixed. It is a STATIC footprint, not the actual waterline at any GPS timestamp or local bed elevation.

## Source-only SHA/CRS admission

1. Fetch only the official provider metadata at https://zenodo.org/api/records/14535985. Require ID 14535985, exact original filename, positive byte count <=10MB, published MD5 and original Zenodo HTTPS file URL. Download ephemeral, recompute MD5/SHA256, STOP on any drift or missing archive.
2. Safely inspect ZIP membership, source .shp/.shx/.dbf/.prj, shapefile geometry type, field names/types, original polygon count and global bbox. Decompressed cap 30MB, member count <=100, polygon features <=100k; no path traversal. A second optional archive QuantileRegressionbased_ElevationChangesInTheWaddenSea.zip may be listed and verified as source metadata but no fitted numeric elevations are used here.
3. Verify the original projection metadata rather than guessing from UTM32 in the filename, and verify that the polygon bounds can reach the named Schiermonnikoog coastal station. If the CRS is absent, internally contradictory, or coverage does not include the study island neighborhood, preserve STOP and do NOT transform animal coordinates.
4. No original bird GPS, private IDs, animal clock times, RWS tide numeric heights, per-feature ecological mapping at animal coordinates, or habitat-association scores shall be opened in Stage A. Export only source metadata and geometry-level bounds.
5. A passed source DOES NOT prove the polygon's year specificity, classification legend, local instantaneous mudflat exposure, actual foraging resource, or corrected v2 ecotope class. Do not infer pointwise seabed elevation from a categorical tidal-flat polygon.

## Conditional Stage B (requires new protocol and code before opening source GPS overlap)

Only consider original 2008–2012 birds from Zenodo 10053970, with source-pinned GPS and original WATHTE astronomical tide, and original 25-km source gauge radius. If polygon fields establish meaningful morphological classes, a fixed spatial point-in-polygon join could measure observed bird association. Inside and outside are mapped footprint versus not mapped, **not** an actual available-habitat choice set. Record complete source QA, CRS, geometry type and original GPS coverage for all points; no favorable spatial clipping or post-outcome class selection.

A time-varying physical availability area still requires a real dated bed DEM in NAP and a local water-level propagation model. Do not represent an arbitrary static polygon as an exposure surface or label GPS fixes as feeding.

## Deliverable

Original-source read-only CI, invented source safety tests, immutable original ZIP SHA, source-only CRS/attribute and spatial-coverage receipt, separate draft PR stacked on v35-A. Never merge earlier stopped results into positive GPS claims.
