# v45 — AHN2 historical 2007–2012 original NAP DTM source gate for tidal exposure mechanisms

**2026-11-05 JST: source-only protocol fixed before any AHN2 elevation, original GPS-by-elevation or tidal exposure outcome.** Prior v29–v44 source-authentic GPS×RWS results were already known; no GPS positions are opened at this stage. This gate cannot count as a new ecological result.

## Why this source

The official Dutch elevation agency [AHN Dataroom](https://www.ahn.nl/dataroom) lists **AHN2**, original acquisition period 2007–2012, source ground **DTM** tiles at 0.5m and 5m, and exposes an official AHN2 DTM **WCS 1.0.0** endpoint through Ellipsis Drive:
`https://api.ellipsis-drive.com/v3/ogc/wcs/e96b10b9-e964-414c-958c-57a9dbe24e62`

Official datum statement: horizontal Amersfoort / RD New (EPSG:28992), vertical **NAP height metres** (compound EPSG:7415/5709). WCS link is linked directly from `ahn.nl/dataroom`, whose published date/name/collection governs this audit. AHN2 overlaps original 2009–2012 bird GPS years more closely than the v42 Dryad 2014 LiDAR archive (download HTTP 401). AHN2 is NOT an independently validated 2009 mudflat DEM everywhere: exact per-tile survey year is not yet verified, tidal geomorphology moves, and NIR LiDAR **does not penetrate water**. DTM nodata or water-surface artifacts must NEVER be interpreted as dry intertidal substrate.

## Frozen source-only checks (no bird outcome)
1. Request only official AHN2 **GetCapabilities** with WCS version 1.0.0 and requestedEpsg=28992, bounded to 2MB. Require XML declaration of WCS, coverage identifier and at least one actual advertised DTM layer; STOP if request gets 401/403/5xx/timeouts or non-XML, never silently switch to current AHN6/modern DTM.
2. Read **DescribeCoverage** on the advertised AHN2 DTM coverage, and inspect supported GeoTIFF formats and EPSG:28992 horizontal CRS; return SOURCE_STOP on ambiguous coverage ID/format. Never substitute DSM surface elevations or newer AHN versions.
3. Fixed provider metadata sample centres selected **before any DTM pixels**: Schiermonnikoog `(lat 53.470, lon 6.200)`, Ameland `(lat 53.430, lon 5.760)`. These are *broad geographical probe coordinates only*, not from source bird GPS and not asserted to fall exactly on an intertidal flat. Transform WGS84→EPSG:28992 using pyproj always_xy, request small 128×128-pixel source WCS patches covering 256×256m around each projected centre. Cap each response to 4MB; TIFF GeoTIFF only, source EPSG:28992 affine geotransform and NAP vertical metadata from AHN agency. Inspect finite/nodata coverage fraction, number of plausible NAP heights, and a broad descriptive [-3,+3] NAP candidate tide-relevant range, without selecting an optimal height threshold from model results.
4. **Feasibility pass only** if official AHN2 DTM source authentic and ≥1 patch per island returns valid georeferenced finite values; report counts for both, never fit biological tide effects in source audit. If missing offshore values, say SOURCE_STOP for intertidal substrate regardless of valid adjacent island terrain. A map probe passed ≠ actual interpolated 2009–2012 wet–dry boundary.
5. No original GPS individual keys, actual bird trajectories, accurate original coordinates or original RWS tide series are included or committed. Original WCS image bytes kept only on ephemeral runner; machine-readable source receipt keeps data coverage statistics, exact source endpoint and optional provider metadata only.
6. If official provider WCS denies access, retain truthful **SOURCE_STOP** and no ecological mechanistic conclusion, but allow future provider-approved download methods. DO NOT bypass authentication or substitute scraped/current imagery.

## Future biological preregistration gate (not run here)

Given historically sourced, georeferenced **pointwise AHN2 NAP substrate DTM**, original 2010–2012 bird GPS A→B→C and original RWS meting NAP tide on the same temporal/coordinate reference, predefine: (a) enough B and C fixes with valid substrate elevation, (b) local waterline propagation and source-clock sensitivity; then test whether the real next movement B→C ends nearer a newly exposed NAP interval than does a matched history/time/site null. The scientifically relevant hypothesis is **real exposure-front destination selection**, not elevation merely correlating with tide gauge. No claimed front mechanism until such a joined field test passes.

Independent caveats: AHN2 is often a land-surface DTM (water-masked), survey dates differ within 2007–2012, old GPS device native time could be UTC or GPS, and inshore/offshore RWS gauge timing differs locally.
