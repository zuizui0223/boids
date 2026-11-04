# v42 — ORIGINAL 2014 Dryad Wadden Sea coastline/elevation source admission, before GPS join

**2026-11-05 JST. SOURCE ONLY; not an ecological field result.** Prior v35A-v36 independent Dutch morphological polygon and bathymetry preflights stopped or lacked pointwise elevation. This is a distinct published source with relevant original GIS data.

## Original provider

[van de Pol et al. 2024, Dryad DOI 10.5061/dryad.wm37pvmth](https://doi.org/10.5061/dryad.wm37pvmth) and its public [original-source description](https://datadryad.org/dataset/doi%3A10.5061/dryad.wm37pvmth) state that `all_code_and_data_files.zip` (~1.43 GB) contains:
- Original 2014 AHN LiDAR terrain elevation tiles (GeoTIFF, 0.5m source cells, EPSG:28992 RD New horizontal metres, elevation **NAP metres**);
- Explicit, archive-internal files `maps/CoastSouth_Ameland.txt` and `maps/CoastSouth_Schiermonnikoog.txt`, each with 2014 Wadden Sea coastline RD coordinates;
- Other original tidal station data, coastal creeks, and model grid cells of **1986 initialized** vegetation elevation; 1986 model-initialized grid elevations must NOT be conflated with observed 2014 LiDAR elevations.

### Zero-new-ecological-outcome admission protocol

Retrieve official Dryad API dataset and file metadata via GET `/api/v2/datasets/doi%3A10.5061%2Fdryad.wm37pvmth/versions` and `/api/v2/versions/{id}/files`, then the file's authoritative `/api/v2/files/{id}/download` endpoint. Use bounded HTTPS **Range** reads to discover the ZIP central directory and extract only the two original southern Wadden coastline text members if the host explicitly supports byte ranges. Reject an HTTP 200 response to a Range request to avoid downloading an unexpected full 1.43 GB archive. MAX 16 MB network reads, MAX 6 MB original uncompressed per selected member.

- Validate original Dryad dataset DOI, ZIP file identity/size and archive member paths. Check each selected member's ZIP CRC32 through Python's standard `zipfile`; independently calculate SHA256 of the small extracted member. Do not claim the full ZIP MD5 or source hash verified by selective Range extraction.
- Preserve the original coordinate reference (RD New EPSG:28992) and 2014 vintage. Count numeric two-coordinate rows and source availability only. Do not print raw original geometry or animal locations; no visual/geospatial ecology is tested in this source probe.
- If public API or file endpoint rejects Range/HEAD or requires a 1.43GB full download, output `SOURCE_STOP_RANGE_NOT_SUPPORTED`/specific SOURCE_STOP; do not substitute a modern coastline or fabricate geographic exposure. Original v32–v40 findings remain untouched.
- Original 2014 coastline only describes static shore location. It **does not** establish 2009–2012 exact waterline, exposed flat area, food availability, hydrodynamic lag, or prey resources. Even a successful distance-to-coast join will require year-mismatch sensitivity and separate pre-outcome spatial prediction controls.

**No M2 dynamic-front or social M3 mechanism inferred by source success alone.**
