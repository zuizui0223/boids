# v196｜BAW年別干潟マスク（Wattflächen）2018/2019: WFS真正原メタデータだけを監査

v194の2018/2019年水位WMS原本確認後、別系統の**公的干潟データ**を見つけた。v195のWMS定点問い合わせは実行待ちであり、結果を見て別のsourceに切り替えたわけではない。v196は別の独立したSOURCE候補である。

## 公式SOURCE
- Lepper et al. (2025) `TrilaWatt: Wattflächen (2015–2021)`, Bundesanstalt für Wasserbau official DOI <https://doi.org/10.48437/5a882d-b3a571>.
- Original BAW dataset record <https://datenrepository.baw.de/trefferanzeige?docuuid=71E27987-B679-4F75-9874-5A882DB3A571>.
- Original BAW catalogued WFS GetCapabilities URL `https://mdi-dienste.baw.de/geoserver/TrilaWatt_Wattflaechen/wfs?REQUEST=GetCapabilities&SERVICE=WFS`.
- BAW describes annual 2015–2021 **intertidal and supratidal areas, annual high/low tide lines and uncertainty** as geographic model output, originally available in GeoTIFF and Shapefile. The derived high/low tide lines have reported ±25 cm uncertainty. Annual mask is an intersection of annual interpolated topography with annual mean high and low water. The mask is **NOT** a time-resolved 15-min event-specific dry-flat estimate.

## Frozen source check
1. Retrieve exact official WFS `GetCapabilities` over HTTPS with **normal CA certificate verification** and no HTTP/insecure fallback; reject cross-host redirects except same `mdi-dienste.baw.de`, non-WFS/XML, DTD/ENTITY, oversized responses ≥4MB. HTTP status, original SHA, bytes, native WFS version, operations and native FeatureType Name/Title, CRS/bbox only.
2. Search FeatureType names/titles for native `2018` and `2019`, `nl`/Nederland hints **only in original source names/titles**; do not invent featuretype URLs or claim exact layer files. The exact 2018/2019 Netherlands features can be admitted only if they are **uniquely** supported by native WFS capabilities. If multiple, no selection.
3. Do **not** call WFS GetFeature or download any shapefile/GeoTIFF raster in v196. Outputs metadata only, not bio.
4. Even if true 2018 and 2019 intertidal boundaries exist, model topography year, 2011-gauge location reference, actual local bird GPS and surface-water time series require independent spatiotemporal and datum checks. Not equivalent to `h(s,t)-z(s)` from 2018 measured local high-frequency water; 500m tide temporal/model field plus historic local z is still not evaluated.
5. Publication states mean annual tide lines' **±25cm** uncertainty; do not fabricate individual polygon confidence when source metadata does not provide it.

Next steps if metadata passes: selected vector features coverage check, original polygon geography in Vlieland and independent source year, and only later 2018/2019 tagged bird GPS source overlap to annual intertidal mask (NOT true instantaneous exposure). No Boids social forces or tide×solar effects inferred from annual geographic mask alone.

This is an observational/data-source opportunity, not a newly supported ecological effect. v182 SOURCE STOP retains DEM native datum and survey-day and original bird-local tide.
