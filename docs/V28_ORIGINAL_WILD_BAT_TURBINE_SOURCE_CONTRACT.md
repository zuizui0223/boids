# v28-A — independent original noctule-bat GPS, habitat and wind-turbine availability source admission

**Registered 2026-10-29 JST before inspecting the original v28 source's GPS values, actual use/availability response labels or any bat ecological effect.** Previous v13–v27 empirical and theoretical endpoints remain frozen. This is a NEW biological population and model target, not a retuning of v25.

## Scientific source and expectation (paper, NOT yet original dataset verified)

Voigt et al. (2023), *Wind energy production in forests conflicts with tree-roosting bats*, *Current Biology* 33, 737–743, [original published paper](https://doi.org/10.1016/j.cub.2022.12.050) [check original DOI independently if needed]. Original published data [Zenodo record 7535030](https://zenodo.org/records/7535030), source record ID **7535030**. German GPS tracking of common noctule bat *Nyctalus noctula*, with two field periods (early summer/late summer), distance to wind turbines, landcover and habitat features.

The published [source file dictionary](https://zenodo.org/records/7535030/files/Data_Structure_UploadedFiles.pdf) describes a table containing `case_` (TRUE observed, FALSE random), `response_rvso` (1/0), `batid` (independent original animal ring ID), `trackid` (original flight path ID with source date and bird ring number), original `x_,y_` UTM33 ETRS89 coordinates (EPSG:25833), `field_period`, `move_state` (area-restricted vs commuting vs undefined), `mindist_WKA` (distance to turbine), landcover `clc20m`, `sex` and `age_class`. The original field paper's deposited source may be **RSF/random points**, not matched **iSSF alternatives** from each recorded step; source columns must be checked and no step-level selection labels invented.

## Stage A1 original source integrity only

1. Request official `https://zenodo.org/api/records/7535030`. Verify exact ID/DOI, publisher description, version/license, original complete file listing, exact original file sizes, provider MD5 and HTTPS original download URLs. Do not invent filenames from the PDF or author narrative.
2. Hard bound **100 MB per original data file and 200 MB combined** at source stage, with zero raw original GPS redistribution. If source >cap, STOP, or (only after separately registered specific-source B) admit a bounded independently original named tabular sub-file without choosing a favorable biological subset.
3. Stage A1 does **not download or parse animal locations, use/available labels, original numeric distance, environmental values or habitat response**. Record source and file metadata only and independently published name/size.
4. Original license must be read from the Zenodo record. Original GPS access even if open does not permit public redistributing exact bat/roost locations from protected field sites.
5. Choose an original *full* public, auditable source data table by metadata only, and freeze its exact provider file name, MD5, byte length and SHA256 **before opening case or habitat numerical effects**.

## Stage A2 source-only if bytes accessible

- Verify complete original source file MD5+size (computing independent SHA256), and only inspect header, original bat-ID × distinct flight-path/date grain, used/available label coding, flight periods and *metadata-only* presence of landcover, wind turbines, start/step/stratum time and altimeter accuracy.
- **≥8 actual independent original bat IDs with ≥3 original flight nights**, and **≥200 original used/available source pairs** explicitly matched at correct source unit, for prospective repeated-flight testing. If unavailable, report `NOT_ADMITTED` and **do not** treat 200 points or 30 trips as independent bats.
- `trackid` means original *flight path*, NOT the identity of a single matched used/available step. If no source `step_id` or start point, a different original RSF-specific protocol is required before model scoring; do not group all positions in the same track as single decision step.
- Original source `x_,y_` are horizontal UTM coordinates, **not calibrated 3D height**. Nearby wind turbine fields and landcover are observed/calc external contexts but cannot infer causal turbine avoidance without site opportunity controls.
- A future true ecological niche test needs source originally generated available point method, habitat and turbine variables measured at both used and available positions, date-time and animal ID. Fixed independent bat-ID and field-period holdouts; explicit source negative cases. No direct bat-bat proximity or neural memory can be inferred from one animal at a time.

**Do not claim v28 biological results until the original file and repeated-bat independent-unit gates pass.** The source paper's turbine results are literature context, not own new effect.
