# v80 result: authentic NIOZ 2010 static native model mesh verified, June/July latitude remains originally missing

**2026-11-08 JST, original NIOZ publisher MD5+SHA verified source-backed GitHub Actions [#42447580398](https://github.com/zuizui0223/boids/actions/runs/42447580398) SUCCESS**, six predeclared known-truth geometry tests PASS, original 2010 **ALL 12** monthly native NIOZ `eco_av` NetCDF and four prespecified 2009/2011 external-model months reauthenticated with original file sizes/provider MD5. Only native geographic coordinate/source header were inspected; **NO GPS biological outcomes or new model index used-location results**.

## Distinguishing actual original coordinate observations from a model-imputed template

| Predeclared static grid test | Original real result |
|---|---|
| 2010 Jan–May and Aug–Dec, 10 native geolocated files | **10/10** have all 398,520 genuine latitude and longitude coordinate values, all **exactly equal at the corresponding native array indices** to original Jan2010 |
| Original NIOZ Jun2010 | `lat` all **398,520 masked**, `lon` all **398,520 genuine** and all original indexwise **exactly equal** to Jan2010 |
| Original NIOZ Jul2010 | `lat` all **398,520 masked**, `lon` all **398,520 genuine** and all original indexwise **exactly equal** to Jan2010 |
| External original 2009 Jan | 398,520 genuine `lat` and `lon`, all exactly equal to Jan2010 native grid |
| External original 2009 Aug | 398,520 genuine `lat` and `lon`, all exactly equal to Jan2010 native grid |
| Preregistered original 2011 Aug/Dec | **Both `lat` all masked**; `lon` genuine, do not claim independent 2011 geographic observation |
| Model station-source coverage | Actual original Jan2010 native nearest cell to public Schier RWS coordinate **38.28m**, Ameland Nes **99.60m** |
| Source-only frozen conclusion | **`MODEL_STATIC_GRID_PROVENANCE_SUPPORTED_FOR_NEW_EXPLICIT_IMPUTATION_STUDY`** |

Every one of the ten 2010 complete original native `lat/lon` sets and the two original 2009 complete native `lat/lon` sets is numerically equal **with no tolerance or nearest neighbor interpolation**. The original June/July 2010 native longitude arrays are also byte-numerically unchanged at corresponding indices; original missing latitude was not assumed equivalent to an original measured latitude. This is strong provenance for a **fixed model computation grid**, not for actual time-dependent intertidal exposure. Native NIOZ `time_expo` remains an **unknown-unit numerical monthly hydro-model index**, not directly measured wet/dry hours.

The June/July `lat` zeros are original *masked metadata values* in the original genuinely publisher-authenticated files, **not 0° latitude observed on Earth**. A new subsequent analysis can, under new dedicated source and outcome registration, assign the original Jan2010 static native mesh's latitude as **explicitly inferred model-grid coordinates** for June/July, with complete audit trail, while retaining both original source masks. This is **model template imputation**, not new field observation of June/July native latitude.

## Biological findings and preexisting caveat untouched

- Original Schier GPS original tide×sun same-bird, same-month, same measured water-height, four-cell true ebb/flood×DAY/NIGHT D-in-D v77 **+0.0380311 in modeled native tide-index local ordinal rank**, whole original bird bootstrap95 **[+0.0191616,+0.0598180]**, 14/16 real birds positive. This original *spatial-use association* already arose after multiple analyses of the same Schier cohort; no new replication in v80.
- Original Ameland late Aug–Dec site separate v78 267 complete four-cell source groups had only **7 birds**, below fixed original **8-bird** source threshold, so external effect correctly **NOT_SCORED** and **not rescued by v80**.
- Original Ameland 2010 full-year v79 showed **June 15 birds/6450 bird×hours, July 8 birds/5321**, but those months' NIOZ native `lat` was missing. A new explicit model-grid template source framework *may* add these months to a separately frozen new Ameland analysis, which remains **post-v79 exploratory** and must quantify its imputation reliance. Do not merge v78's failed source status.
- v70 official measured physical RWS two-island same-daylength low tide×sunlit clock overlap differences remain independently valid; v63 wild tidal heading source directional positives and v69/v70 added daylight heading prediction negatives/unestablished remain separate endpoints.

## Original reproduction
- [GitHub Actions #42447580398](https://github.com/zuizui0223/boids/actions/runs/42447580398) SUCCESS, six known-truth tests.
- [v80 fixed prereg source method](V80_FROZEN_ORIGINAL_NIOZ_2010_STATIC_GRID_TEMPLATE_AUDIT.md), `validation_v80/original_nioz_static_2010_grid.py`, `validation_v80/test_original_nioz_static_2010_grid.py`.
- Original monthly coordinate/status-only artifact `v80-original-NIOZ-2010-geographic-static-template-source-only` ZIP sha256 `7fee60421b6598c1b07ec84a375a8a805ee22328c7abdccf83e4cfffda35d1dc`. No raw native grid pixels, original GPS tags/times/locations, inferred coordinates or wildlife effect estimates released.

**Next model-imputed source-only gate if desired:** pre-freeze separate v81 explicit reconstructed native coordinate template for 2010 June/July, original Ameland 2010 GPS source and same original 2010 Ameland Nes official tide, keep unchanged original 4-way 0.20m tide × +3° daylight eligibility; score interaction only after a source gate (≥8 original birds, ≥100 genuine 4-way strata, ≥2000 GPS source positions, ≥3 calendar months) passes. Original model imputation can make additional **modelled** habitat index comparable geographically, but cannot prove actual observed foraging or universal bird tidal-light ecology.