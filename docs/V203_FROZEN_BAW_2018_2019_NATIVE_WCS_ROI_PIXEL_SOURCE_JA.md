# v203｜Vlieland公開参照地点の同一10kmROI：2018/19 BAW元WCS地形20m TIFFの実有効画素だけを監査

v202原BAW WFS高潮/低潮 `MultiCurve`を本当に同一ROIでクリップし、2018 High 30.715km/Low 131.948km、2019 High 28.668km/Low 127.491kmを原本2回再現。しかし**線長は干潟面積を意味しない**。そこでWCSの元2018/19地形`topography_inter_supratidal`で各年の同一範囲に標高画素があるかをSOURCEだけで確認する。レイヤーが2018/19年に「当時実際測量された」ことは保証しない。

## 結果閲覧前の独立SOURCE固定
- 出典 v199/v200 元BAW `https://coast.baw.de/geoserver/TrilaWatt_Wattflaechen/wcs?REQUEST=GetCapabilities&SERVICE=WCS&VERSION=2.0.1`、WCS Cap原SHA `55e531bbe17f8720b5b1aecc82130c1d8a29adb10738fe727ac3d4869f2afeec` を再照合。年2018/19の2層は元 `CoverageId` `TrilaWatt_Wattflaechen__topography_inter_supratidal_2018_nl` / `...2019_nl`。
- 元DescribeCoverageの2018/19両層のnative EnvelopeはEPSG:25832、axisLabels=E N、x (182995...313005m)、y (5867695...5958005m)。v202と同一公表WEBTICS Vlieland Haven (RD 135280,590000)から±5kmの**10km×10km**ROIを一切変更しない。
- ネイティブ WCS2.0.1 の GetCoverage でこのEPSG:25832の`subset=E(min,max)`,`subset=N(min,max)` を指定して **2年×1回だけ**HTTP GET。format`image/tiff`。原HTTP/CA検証、未承認redirect禁止。サイズ最大20MB。範囲外の全日本海沿岸ラスタや全オランダ元GeoTIFFはダウンロードしない。
- 正真正銘TIFFであれば`rasterio`上で元ソースCRS EPSG:25832・pixel bounds・元nodata・元解像度（約20m、許容5〜100m）をSOURCE確認。original pixel mask、`abs(z)>100m`の極端な異常値候補、実数値候補のn、fraction、中央値、5/95%分位を**SOURCE-safe aggregate**として保存。生原ラスタ・生画素配列はGitHubやActions artifactに一切保存しない。
- 同じ原格子transform/shape/boundsが両年完全一致した場合だけ、原有効画素共通の2か年差分 `z_2019-z_2018` の中央値・5/95%分位等を探索的に算出。年同士がgrid不一致なら差分SOURCE_STOPで年別nのみ報告。地形のsource原測量日・潮汐侵食機構は証明しない。
- 年次`topography_inter_supratidal`の有効画素は**干潟だけでなく高潮帯も含む**。従って有効画素×20m²は「干潟面積」と誤読禁止。真の潮間帯は年平均高/低水位と地形の明確な同一datum基準、マスク範囲・実測潮位で条件づける必要がある。
- 元BAW原TIFFの`unit`、鉛直NHN/NAP換算は論文levelの記述だけであり、元TIFF metadataが証明できなければ標高候補と呼ぶ。元20m Deltares historical DEMのtrue survey day/vertical NAPやGPS実位置への接続も別SOURCE STOP。

引用：Lepper et al. (2025) Scientific Data DOI:10.1038/s41597-025-06211-1、BAW official TrilaWatt Wattflächen DOI:10.48437/5a882d-b3a571。実測bird ACC GPSと生態学的潮汐×太陽、Boids力はこの版で新規に解析しない。
