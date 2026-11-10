# v116 | Frozen terrain source / NAP gate for the real Oosterschelde 2020 gull study

Registered 2026-11-10 JST AFTER v115 observed original gull spatial result and BEFORE reading any new DTM pixel outcomes. This is NEW environmental SOURCE admission, not a species time-niche finding. The 2020 two-Larus spatial GIC RF endpoint contrast persisted after real GPS distance matching (B_step +0.0428166, true-bird CI [0.0255629,0.0613190]), while species tide×sun I, tidal phase T and solar S were not established. All past negative ghosts and post-hoc status stay visible.

## Authenticated candidate

Rijkswaterstaat original historical Oosterschelde *digital terrain model*, not DSM. Exact first-party historical source catalogue:
- 5m 2019 DTM PRIMARY: https://data.overheid.nl/dataset/46816-hoogtegegevens-oosterschelde-5m-grid-2019-dtm ; native TIFF https://downloads.rijkswaterstaatdata.nl/hoogte_2019/oosterschelde_2019_dtm_5.tif
- 2m 2019 DTM SECONDARY: https://data.overheid.nl/dataset/12788-hoogtegegevens-oosterschelde-2m-grid-2019-dtm ; native TIFF https://downloads.rijkswaterstaatdata.nl/hoogte_2019/oosterschelde_2019_dtm_2.tif
- Original WCS data transport https://geo.rijkswaterstaat.nl/services/ogc/gdr/hoogte_2019/ows with WCS 2.0.1, official source-native coverage identifier hoogte_2019:oosterschelde_2019_dtm_5, respectively hoogte_2019:oosterschelde_2019_dtm_2.
- The national AHN heights are given relative to NAP according to Rijkswaterstaat (https://www.rijkswaterstaat.nl/zakelijk/open-data/actueel-hoogtebestand-nederland), but historical original DEM native metadata, CRS, units and nodata MUST be source-verified before any comparison to official 2020 Roompotsluis WATER LEVEL cm relative to NAP. Catalogue says 2019 DTM with AHN3 2018 survey source; do not claim instant 2020 bed altitude. Lidar source may miss underwater elevations.

## Frozen data source gates

Query publisher WCS GetCapabilities and DescribeCoverage for exact DTM5m/DTM2m native identifiers (do not accept WMS rendered JPEG, colorized map or source exception HTML as actual elevation). Projection EPSG:28992 RD New / horizontal metric. Independently verify the actual returned original source TIFF native CRS, geotransform, nodata and raw value units; do not make a confident NAP claim without official vertical reference.

Before inspecting source elevations, four fixed landmark probe points (NOT selected by tide/GIC/animal Y):
1. Original Roompotsluis Buiten official gauge geographic reference 51.619722 N, 3.681944 E.
2. Roggenplaat shoal (mapped landmark) 51.66398 N, 3.79130 E.
3. Neeltje Jans island map center 51.631944 N, 3.698889 E.
4. Roompot Marina 51.59357 N, 3.71752 E.
Each source probe is a fixed 100m x 100m rectangle in EPSG:28992 around these WGS84 coordinates, 5m (primary) and 2m (secondary) source, preserve source nodata and errors, no relocation to a favorable beach or GPS-use location. 2019 DTM coverage missing is NOT wetland absence, underwater bed or zero dry habitat. Original point coordinates are public landmarks only.

First v116 result is a SOURCE-verified spatial coverage/CRS/units/vertical datum QA table. If native z (ground elevation) and 2020 official RWS h (cm NAP) can be compared in the SAME vertical datum, a *hypothetical gauge-stage inundation screening* under h±20cm may be reported for these fixed probes using original 2020 June1–3 tide. **Do not call this actually available flat or food**: the storm-surge barrier separates Buiten/Binnen, and the gauge does not measure local tide at each GPS site. Before assessing biological use-availability, require terrain z at *real original GPS destination AND every one of seven same-step rotated alternatives*, verified estuarine waterbody and measured/time-propagated appropriate local tide, valid original wetland substrate type, prey or foraging observation, and actual accessibility. No bird-level effects or hypothesis tests at v116.

Predeclared stage: source first -> pilot raster values -> provenance & missingness -> possible later physics with proper datum. The scientific interpretation cannot be upgraded because a WCS source returned without error.
