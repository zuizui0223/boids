# v119 source-backed result: authenticated original 2019/2020 Vaklodingen NetCDF files are OUTSIDE Oosterschelde

2026-11-10 JST. Genuine original two-year source from the historical OpenEarth archive was verified by two successful [Actions #42836008750](https://github.com/zuizui0223/boids/actions/runs/42836008750) and corrected metadata-variable audit [#42836755891](https://github.com/zuizui0223/boids/actions/runs/42836755891), five source/schema/georeferencing known-truth tests PASS.

## Genuine source identity and where it really is

Two original public files:
- 2019 \`20190712_vaklodingen.nc\` authentic native NetCDF 3,594,788 bytes, SHA256 \`9e6f902a3511495259f8f5cef06888d1724f78e3da58cd70c834432d5333c024\`. Native RD New EPSG:28992 x coordinate extent **155,390–175,350 metres**, y **602,190–620,070 metres**, native \`altitude\` array dimension y×x = 895×999 with \`units=m\` and CF \`grid_mapping=oblique_stereographic\`. Source NetCDF metadata has **no explicit NAP vertical datum string**. True source input filename refers to \`_20190712_Brndp19KG2tt.asc\`, northern Borndiep/Kustgenese2 sector.
- 2020 \`20200717_vaklodingen.nc\` authentic native NetCDF 3,991,532 bytes, native RD New EPSG:28992 x **155,370–176,170 m**, y **600,990–620,050 m**, native \`altitude\` array y×x = 954×1041 with metres units and no verified NAP vertical metadata, source input \`_20200717_Borndiep20KG2.asc\`.
- The four **PREDECLARED** WGS84 source-probe points (Roggenplaat, Roompotsluis Buiten, Neeltje Jans, Roompot Marina) convert to Dutch RD coordinates near x≈37–45 thousand m and y≈402–410 thousand m. **ALL FOUR are OUTSIDE both NetCDF files' native x/y bounding boxes**. The netCDF data are genuinely published archived seabed elevations but are not soundings at ANY Oosterschelde research location. Simply possessing a historical Vaklodingen archive does not fill any missing 2019 RWS ground DTM pixel for the 2020 Zeeland bird GPS.

## Source audit correction and confidence

First run properly detected native CRS and all 4×2 geographic out-of-bounds outcomes but the metadata scanner omitted CF variable named **\`altitude\`** from the candidate bed-elevation variable list, printing empty; the corrective run added \`altitude\` (exact source unchanged), now correctly reports original native altitude arrays and units. Neither run ever exported per-pixel seabed values, enrolled birds, GPS coords/times, or inferred local tidal exposure. This is a source candidate classification repair only, no cherry picking.

**Science source status = AUTHENTIC_NONLOCAL_HISTORICAL_BATHYMETRY_NOT_USABLE_FOR_OOSTERSCHELDE.** The v118 strict ≥90% each species' 2019 terrain all-8point source gate remained failed (L. argentatus 41.71%, L. fuscus 57.80%). No dynamic 2020 bird used-vs-available preference, 2020 dry tidal flat, tide-specific time-niche or new animal effect estimated. The dataset-year 2019/2020 is not proof of Zeeland geographical relevance.

## Conditional next source, not yet a scientific success

A DIFFERENT comprehensive original Deltares THREDDS Vaklodingen bathymetry tile catalog is available at https://opendap.deltares.nl/thredds/catalog/opendap/rijkswaterstaat/vaklodingen/catalog.html and Deltares documentation says the historical tiles have multi-year time data and may require caution about interpolated/last-observation-held time series. Published wiki points to a \`vaklodingen_new\` 2020-era release, which is a **distinct** source collection. Future source auditing must prove tile original CRS/x/y encompasses Oosterschelde and actual bathymetric survey YEAR is no later than the 2020 bird period, with original NAP vertical datum. Old source **pre-2014** interpolated bathymetry (if such) must not be passed off as a measured 2020 seabed. Do not replace missing real 2019 lidar heights with an invented bathymetric interpolant.

No biological inference is added by this source audit. No file URL from a wiki or dataset index by itself certifies source local seabed measurements.
