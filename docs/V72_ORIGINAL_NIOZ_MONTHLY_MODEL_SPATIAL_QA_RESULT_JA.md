# v72/v72D: Native NIOZ model 2010/2011 monthly spatial-exposure source audit — documented source failure and usable 2010-only branch

**2026-11-08 JST**: original NIOZ DOI [10.25850/nioz/7b.b.n](https://doi.org/10.25850/nioz/7b.b.n) publisher **36 monthly files and 2010/01, 2011/01 NetCDF original MD5 and SHA256** all authenticated. Initial [v71 GitHub Actions #42439052267](https://github.com/zuizui0223/boids/actions/runs/42439052267) completed original-source discovery, four known-truth tests PASS, with **NOT_ADMITTED** within-tide timing because monthly files have **no time axis**, even though native 820×486 grid includes a `time_expo` variable.

The strict v72 [original workflow #42439373352](https://github.com/zuizui0223/boids/actions/runs/42439373352) **failed by design at original native year-to-year grid-source equality gate**: `SOURCE_STOP_V72_DIFFERENT_SOURCE_NATIVE_GRIDS`. New source-only **v72D diagnosis [#42439693259](https://github.com/zuizui0223/boids/actions/runs/42439693259) SUCCESS** (4 v72D + 4 prior v71 known-truth checks). It does not waive the strict v72 test. Interpret a successful *diagnostic program* separately from a failed *source-eligibility rule*.

## Original source facts the diagnostic actually established

| Original native source | 2010 January | 2011 January |
|---|---:|---:|
| Same native NetCDF data grid dimensions | 820×486 | 820×486 |
| Original usable finite latitude+longitude cell pairs in plausible Wadden *degrees* | **398,520** | **0** |
| Original `lat` array numerical finite cells | **398,520** | **0** |
| Original `lon` array numerical finite cells | 398,520 | **398,520** |
| Original NIOZ `time_expo` numerical finite cells | 398,520 | 398,520 |
| `time_expo` negative source values | 0 | 0 |
| Original modeled `time_expo` numerical minimum/maximum | 0 / 1 | 0 / 1 |
| `time_expo` 50th percentile | 0 | 0 |
| `time_expo` 99th percentile | **0.9100** | **0.8696** |

2010 original native lat numeric range [52.49747, 53.76075] degrees; lon [4.025996, 6.789564] degrees. 2011 source longitude range is identically [4.025996,6.789564], but **all original latitude values are missing when decoded according to the original NetCDF missing-data rules**. Thus **there are zero cells with independently verified native latitude/longitude in both months** and 2011 original cell-by-cell geolocation cannot be claimed. The original MD5 proof certifies unmodified bytes, not absence of missing values.

The original publisher's README explicitly mentions `time_expo` as exposure time of tidal flats (verified original README line 21) and provides additional discussion (line 23). The source NetCDF file has **no variable `units` or `long_name` attributes**. Our conservative automatic original README-unit check returned `NOT_ADMITTED_ORIGINAL_README_UNIT_UNKNOWN_OR_CONFLICTING`; original `time_expo` numeric range [0,1] **does not by itself justify assigning hours, fraction of day, or annual/tidal duration**. These original 2010/2011 native source pixel values represent a model, not observed water heights/real feeding.

**Strict v72 source admission remains `STILL_NOT_ADMITTED_V72_NO_JOINT_GEOGRAPHIC_COORDINATES`**. Do not just copy 2010 lat into 2011 without a newly frozen, explicitly marked imputation method and independent original source grid alignment validation. Do not call the source monthly model a 10-minute or 1-hour tidal cycle. **No original GPS use-location selection, 2011 B→C heading, daytime foraging or biological adaptation was scored** in v71/72D.

## What positive source capabilities are available (not biological results)

- The **original 2010 January native model grid** appears geographically plausible for the Wadden Sea and contains finite original model exposure numbers across all **398,520** cells. It is a candidate for **2010-only source GPS↔environment geolocation**, once the original README units/provenance and the model wet/dry mask/land cells are checked.
- The **2011 January original model's `time_expo` values exist** but original `lat` array is entirely missing. Source spatial joins therefore **cannot** be authenticated without an additional independent grid-reference proof; even an apparent 2010↔2011 spatial difference is not an observed hydrogeomorphology change until the grid is properly verified.
- The measured Rijkswaterstaat 2010–2011 10-minute station gauge overlap with astronomical daylight in [v70](V70_ORIGINAL_MEASURED_LOW_TIDE_SUNLIGHT_OPPORTUNITY_RESULT_JA.md) remains **positive physical opportunity heterogeneity** (2 gauges, 2 years, 660 near-identical-daylength pairs, 398 with ≥1h differing low-water daylight overlap), but new 2011 wild heading gain was **not supported**. All old positive v43–v63 wild tidal movement direction matched effects are retained.

## Scientific next source decision

**Do not attempt original wild 2011 GPS×NIOZ month model join yet**. First confirm whether the 2011 native latitude missingness results from explicit original `_FillValue` masking or truly unpopulated bytes, and whether the original NIOZ product's static 2D latitude template is independent of month. A carefully marked **post-v72 exploratory sensitivity** might use identical original longitude/index/source grid provenance from 2010 as a 2011 spatial template; that is **an imputation**, not a newly observed original 2011 coordinate. Prefer direct verified dated NAP bathymetry (WadGrid survey year) or full 2009–2011 model files with complete spatial coordinates when available.

This is a concrete data-quality result, NOT absence of shorebird tide–daylength ecology. Do not erase source failures or simulate missing geospatial points to manufacture a biological conclusion.

## Reproduction

- v71 source identity/fixed model months: [run #42439052267](https://github.com/zuizui0223/boids/actions/runs/42439052267).
- v72 strict original data source gate: [run #42439373352](https://github.com/zuizui0223/boids/actions/runs/42439373352), FAILED due original coordinate mismatch; all scoped synthetic regression tests PASS.
- v72D independent source diagnostic: [run #42439693259](https://github.com/zuizui0223/boids/actions/runs/42439693259), SUCCESS, source artifact `v72d-original-nioz-model-coordinate-drift-source-only` ZIP SHA256 `743cfee99276a43266ecd83fc1cf8ce46aff3fb878f4abadbb91332d66772f6b`.
- v71 original 2010 January NetCDF SHA256 `f8df67d7351754173978364cd89afbf3a2bba4f3a4f85ef270b1090c14e72bad`; original 2011 January `fb709111351182af3355730b100e41010a565dd92d12b26f6212356ccaa3e5da`. NIOZ original README SHA `4a273823ed9ea7925caccecf87b1d0220d8c4eeed25869cbb379c45de66e19ff`.
- No original bird identity, timestamp, position, velocity, gauge raw time series or original NIOZ model grid released.


## Original 2010 geo-source coverage added after separate frozen diagnostic

[Latest original NIOZ v72D source audit #42439877809](https://github.com/zuizui0223/boids/actions/runs/42439877809) **SUCCESS**. The original published NIOZ 2010 January `lat/lon` array allows only a **2010 model-source-only** 5 km neighborhood check around independent public RWS station points. This is NOT an animal GPS join, nor a validation of source `time_expo` units.

| 2010 January native NIOZ modeled source near authentic RWS gauge | Schiermonnikoog | Ameland Nes |
|---|---:|---:|
| Original model grid cell centers within 5 km | **1,974** | **1,970** |
| Model original `time_expo` finite/nonnegative cells within 5 km | **1,974** | **1,970** |
| Nearest original native grid cell center to public tide station | **38.28 m** | **99.60 m** |
| `time_expo` numerical median, source unit **unverified** | **0.20618** | **0** |
| `time_expo` numerical 90th percentile, unit unverified | **0.97293** | **0.62532** |
| `time_expo` numerical original maximum | **1.0** | **1.0** |

This is positive evidence that the **2010 original model grid has source cells near both reference locations** and a heterogeneous monthly numeric `time_expo` field. Values cannot be interpreted as original measured 2010 exposed-cell **hours**, actual prey, or instantaneous daylight coincidence. The original 2011 latitude remains missing in all 398,520 cells and the original strict two-year source gate remains **NOT_ADMITTED**. The two month grids have not been co-georeferenced by an independently verified original 2011 latitude file.

The next honest biologically focused cohort would be a **separately frozen 2010-only real GPS use-location × modelled January spatial index** source gate, with unambiguous model units or predeclared ordinal-scale-only analysis, and explicit local background habitat availability. This is not completed by v72D and there is no v72D wildlife habitat-selection result.
