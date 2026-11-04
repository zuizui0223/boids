# v42 SOURCE STOP — original Dryad 2014 Wadden coastline ZIP download requires authorization

**2026-11-05 JST. Original source-only audit; no animal GPS/tide spatial outcomes were opened.**

## Original published GIS resource

[van de Pol et al. 2024 Dryad DOI 10.5061/dryad.wm37pvmth](https://doi.org/10.5061/dryad.wm37pvmth) publicly describes an archive `all_code_and_data_files.zip` (~1.43 GB) with original 2014 AHN LiDAR 0.5m DTM tiles in RD New horizontal (EPSG:28992) / **NAP metres**, including Wadden southern coastline source files `CoastSouth_Ameland.txt` and `CoastSouth_Schiermonnikoog.txt`.

The original data description also names model-initialized `gridcells_loc_start6*` files whose source heights are simulation-era initial conditions (typically 1986), **not necessarily directly observed 2014 DEM heights**.

## Actual source gate

- Read-only program `validation_v42/dryad_2014_coastline_source.py` uses official Dryad API version/file metadata to select exactly `all_code_and_data_files.zip` and an official original per-file download URL.
- Bounded HTTP byte range probe `Range: bytes=0-0` then returned **HTTP 401 Unauthorized** from the official `/api/v2/files/{id}/download` file endpoint. Earlier version-metadata HAL-link parsing issue was repaired in pure source-interface code before this final stage-specific receipt; the final source stop is **download authorization**, not absence of original GIS data.
- The source code refuses HTTP 200 returned to a Range request, refuses >16MB remote reads and refuses silent 1.43GB full-archive downloads. Four synthetic unit tests pass on known ZIP CRC/range behavior.
- The original ZIP was **not obtained**, and original member CRC / SHA / source heights were **not** verified. Do NOT report a successful map extraction, or claim the 2014 coastline or elevation actually joined to original 2009–2012 GPS. No original bird or tide outcomes were touched here.
- This is **`SOURCE_STOP_DRYAD_RANGE_PROBE_STAGE_HTTPError_HTTP Error 401: Unauthorized`**, not a biological negative result, nor a claim that the archive is permanently unavailable to all users. Future legitimate data access could use the publisher's approved public download/UI or authenticated institutional access. Do not bypass authorization.

## What remains scientifically unsupported

No measured GPS-by-local-cell NAP height, historical wet/dry crossing, exposure age, exposed prey resource, or front-distance field effect from these original sources. The 2014 measurement year is later than the 2009–2012 tracking years and would require explicit temporal mismatch/sediment migration sensitivity before historical ecological claims. Previous v32/v33/v39/v40 field SPEED evidence and v41 conditional DIRECTION evidence remain unchanged.

Reproducibility: [v42 final stage-specific source probe CI 41924394619](https://github.com/zuizui0223/boids/actions/runs/41924394619), original code and unit tests under `validation_v42/`. No user secrets or raw GPS were requested.
