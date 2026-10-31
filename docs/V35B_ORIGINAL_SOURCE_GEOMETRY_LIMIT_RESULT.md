# v35-B — original Zenodo morphological-unit source success, habitat GIS admission STOP

**2026-10-31 JST. Two independent original-only source runs succeeded, but a pointwise tidal-flat exposure/habitat overlay is NOT ADMITTED.** The original v35-A Mendeley corrected ecotope v2 STOP (HTTP 401 / WMR WFS 503) remains unchanged.

## Source bytes and version

Source: Pineda Leiva, Lorenz & Lepper original [Zenodo 14535985](https://zenodo.org/records/14535985), published morphological units derived from Baptist et al. (2019), **not** the Mendeley corrected 2021 v2 map. DOI 10.5281/zenodo.14535985; CC BY 4.0.

- Source archive `TidalFlats_UTM32_Baptistetal2019_extended.zip`: **194,382 bytes**, original published MD5 `eaa559c9b8401ed4db70b0ef70fe2d7c`, independently verified original SHA256 `2cc448f22730ebcc751d51eba68c61d13be435479abbfd7ab483bc3f77d95856`.
- Original ESRI polygon shapefile has **38 features**, public fields `Name`, `Source`, `Item`; native projected CRS named **ETRS89 / UTM zone 32N**; original PRJ/WKT archived by digest, original layer bounds preserved. This source QA opened **no original animal GPS**.
- Separate original `QuantileRegressionbased_ElevationChangesInTheWaddenSea.zip` source: **1,458,242 bytes**, published MD5 `3842bc5d2e9c68c8c9c13f2d60e781ee`, independently verified SHA256 `e7e9206f8990290a394dc920788a2903dcfe16fd7eea7f7e869499221d0460e7`. It contains two XLSX sheets/books with regional and morphological-unit **quantile-regression summary distributions**, not a pointwise georeferenced seabed elevation GeoTIFF. No elevation numeric values were inspected or joined.

## Geometry study-area source gate

The official Schiermonnikoog Waddenzee tide station (53.468937N, 6.202908E) is geographically within the **whole 38-feature bounding box**, but **not within any of the individual valid original polygons**. Exactly 6 original named geographical units touch the fixed 25km gauge buffer: Borndiep, Pinkegat, Eilanderbalg, Lauwers, Schild, Eems-Dollard. **One of the 38 original polygons is geometrically invalid** under the original Shapely validity check (not silently repaired or ignored).

The polygons are essentially *named morphological/tidal-basin units*, not polygon classes annotated with seabed heights, exposure %, dry-at-tide or prey type. Consequently:
- They cannot establish whether any original oystercatcher GPS fix was on a dry, exposed food flat at its observation time.
- Even a point-in-polygon overlay would label basin membership, not real-time exposure or foraging.
- The yearwise quantile summaries neglect within-basin geographic structure; substituting a basin's quantile as local GPS-point elevation is an ecological measurement error.
- Repairing the invalid polygon or choosing a different spatial subset after observing prior v33/v34 animal effects is not part of the source-only protocol.

**Decision:** `V35B_ORIGINAL_MAP_GEOMETRY_STATION_OVERLAP_NOT_ADMITTED` for claims about pointwise exposed intertidal habitat or real-time bird access. This is a **source/definition limitation, not a null biological response**. Do not invent a new mudflat-area result.

## Next dataset dependency with actual seabed elevation

BAW/TrilaWatt publishes original NL coastal **1996–2014 annual 10m GeoTIFF bathymetry**, interpolated to July 1 (DOI [10.48437/4baaf0-aeaf58](https://doi.org/10.48437/4baaf0-aeaf58)), supporting the historical 2008–2012 bird period, but it is **not yet downloaded or joined**. BAW advertises ETRS89 / UTM32 and DHHN2016 elevations; original RWS Schiermonnikoog tide heights are cm relative to **NAP**. Before computing physical exposure from `z(s) > H(t)`, **verify a local vertical reference transformation**, raster nodata/units/year and source resolution; do not silently equate DHHN2016 with NAP.

## Provenance

- [Original fixed source protocol](V35B_ZENODO_MORPHOLOGY_SOURCE_PROTOCOL.md)
- [First source original ZIP/CRS verification run 41190557754](https://github.com/zuizui0223/boids/actions/runs/41190557754) (6 tests PASS)
- [Second source-only unit labels/station geometry and quantile archive check 41190694875](https://github.com/zuizui0223/boids/actions/runs/41190694875) (4 tests PASS)
- [Original polygon/CRS-only receipt](../validation_v35b/results/zenodo_static_tidal_flats_source.json)
- [Full source-only geographic and quantile inventory](../validation_v35b/results/zenodo_morphology_units_and_quantile_source.json)

All earlier v33/v34/v34-B original outcomes remain unchanged; no original animal GPS, RWS tide or individual positions were opened during these source checks.
