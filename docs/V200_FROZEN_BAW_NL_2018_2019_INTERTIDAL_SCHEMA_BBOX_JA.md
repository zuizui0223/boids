# v200 | BAW 2018・2019年オランダ高潮/低潮境界および干潟地形の原空間範囲・属性・Nil判定（SOURCE ONLY）

v199（Actions #44429739018, #44429768184）は、BAW公式の308 original redirect先`coast.baw.de`でWFS2.0.0（28 features、原XML SHA `ea41b511a593b37e87bae1cc53dfc18c071f4e8769cbff93fa01f5a6618788b5`）、WCS2.0.1（42 coverages、SHA `55e531bbe17f8720b5b1aecc82130c1d8a29adb10738fe727ac3d4869f2afeec`）およびWMS1.3（70 layers）を原本TLS検証済み。**v200は数値やポリゴンの中身でなく、座標範囲とスキーマ**を確かめる。

## あらかじめ固定する真の原レイヤー
WFS (2018/19×high/lowの4 native FeatureType):
- `TrilaWatt_Wattflaechen:high_water_boundary_2018_nl`
- `TrilaWatt_Wattflaechen:low_water_boundary_2018_nl`
- `TrilaWatt_Wattflaechen:high_water_boundary_2019_nl`
- `TrilaWatt_Wattflaechen:low_water_boundary_2019_nl`

WCS (2018/19×topography/high_boundary_confidence/low_boundary_confidence の6 native CoverageId):
- `TrilaWatt_Wattflaechen__topography_inter_supratidal_2018_nl` / `2019_nl`
- `TrilaWatt_Wattflaechen__high_water_boundary_confidence_2018_nl` / `2019_nl`
- `TrilaWatt_Wattflaechen__low_water_boundary_confidence_2018_nl` / `2019_nl`

これらのexact namesはv199真正XMLから直接固定した。地理は2011 WEBTICSの公表Vlieland Haven RD=135280,590000をEPSG:28992→4326で変換した**公開参照点**を使う。鳥GPSそのものや2018年の原観測機器位置ではない。

## ネイティブSOURCEゲート
1. 公式2サービスの`GetCapabilities`を再取得し**SHA完全一致**、native version WFS 2.0.0/WCS 2.0.1、全4 WFS feature types/全6 WCS CoverageIdと元列挙の一致、元HTTP/TLSを厳格検証する。
2. ネイティブWFS `FeatureTypeList`の各4つについて、元`WGS84BoundingBox`と`DefaultCRS`を取得。公開Vlieland地点がこのsource bboxに入るか二分する。これはレイヤーの「カタログ地理範囲」であってGPS実点の重なりでも干潟ポリゴンの存在でもない。
3. ネイティブOGC operationsで`DescribeFeatureType`が公表されていれば、それぞれexact typeNameに対し**元XSD schema metadataのみ**をHTTPS CA ONで取得（各最大0.6MB）。元XSDのSHA、native element/geometry-like field名前/型を出す。namespaceが不正・sourceがHTML/OGC exceptionならSTOP。**WFS GetFeatureは禁止**。
4. WCSが`DescribeCoverage`をadvertiseする場合、6 exact coverageの原GML metadataを各最大1MBで取得。原horizontal bbox/CRS、rangeType field labels/uom、NilValue文字列だけをsource-safeに保存。**GetCoverageは禁止、ラスタなし**。
5. 全引用はBAW独立metadataに限定し、原データ自身を読んで初めて2018/19年の地形実数・高潮線の実ポリゴンが使えると主張する。年別高/低潮線は瞬間干出でも、ローカル水位の独立現地観測でもない。

不合格項目が1つでもあればその系統はSOURCE STOP; ほかの系統のsource positiveは維持し、正しく分離する。時刻別TrilaWatt水位はv197 17/24 plausible numeric, 7/24 extreme NoData candidateであり、native netCDF `_FillValue`、鉛直datum、原実測潮位との誤差はまだ検証していない。

**生物学的な結論は増やさない**。v182原20m DEMの測量日・原NAP、鳥の実GPS水深・採餌ACC・潮汐×日照・社会BoidsはSOURCE STOP。
