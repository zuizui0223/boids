# v198 | 原BAW Wattflächen WFSリダイレクトの厳格診断（公式WMS/WCSも元CAPだけ）

v196 2018/19 original vector WFSはGitHub Actions #44308055460 と #44308100414でSOURCE_STOP。元公開URLに対する **REDIRECT_TO_NONPUBLIC_OR_NONCAPABILITY_SOURCE** として安全ゲートがリダイレクトを拒否した。これは干潟原ファイル欠如の証明ではない。以下の3つの**BAW公式メタデータに明示されたoriginal service URL**を結果前に固定し、TLS認証を維持したままGETの一次HTTP応答を記録する。

1. 公式WFS: `https://mdi-dienste.baw.de/geoserver/TrilaWatt_Wattflaechen/wfs?REQUEST=GetCapabilities&SERVICE=WFS`。公式WFSカタログ：BAW original WFS `AE65CB1D-9A89-4087-9091-61EC1DE82BB8`。
2. 公式WMS: `https://mdi-dienste.baw.de/geoserver/TrilaWatt_Wattflaechen/wms?REQUEST=GetCapabilities&SERVICE=WMS`。公式WMSカタログ：BAW original WMS `9D237666-EFA1-4525-BF87-FCFACBF4ABFF`。
3. 公式WCS: `https://mdi-dienste.baw.de/geoserver/TrilaWatt_Wattflaechen/wcs?REQUEST=GetCapabilities&SERVICE=WCS&VERSION=2.0.1`。公式WCSカタログ：BAW original WCS `B56E7E66-B895-40BE-A087-B8A7F18A3F8E`。

## 凍結SOURCEルール
- `ssl.create_default_context()`の通常CA検証をON。リダイレクトは**一切追跡しない**。一次応答statusが301/302/303/307/308なら元`Location`ヘッダーとURLのhost/path(正規URL文字列は公開可)、responseヘッダーだけを記録して**診断STOP**。HTTPS以外のLocationも絶対に辿らない。
- 原HTTP200かつ原XML4MB以下のときのみ、DTDやENTITYのないOGC WFS/WMS/WCS CapabilitiesルートをXML解析し、原SHA、native version、native FeatureType/Layer/CoverageSummaryの`Name`/`Title`だけ保存。実GeoTIFF、Shapefile、GetFeature、GetCoverageは一切読み込まない。
- 公式URLが404/500、TLS失敗、redirectの場合はSOURCE_STOP。公的なhostにredirectする場合も今版では自動追跡しない。次版で公式URLと証明書チェーン/OGC service宣言を別途認証した場合のみ、リンク先をSOURCE候補として追加できる。
- 原2018年・2019年のNL `Wattflächen`領域のFeatureTypeの同定、年別マスクの地理範囲、鳥GPS被覆、当時の実測水位との整合性はまだ未確認。2015–21年の年別モデル干潟マスクは15分ごとの干出ではない。

重要：v195は公式年別WMSのGeoJSON `Wasserstand`値を6件取得したが、2019年2地点で約1e31のNoData候補があり、v197で時刻を固定した原本監査中。これはv198干潟WFSの成功/失敗とは別SOURCEである。

実証的に支持された生態効果は現段階で増えていない。v182 native historical DEM z vertical datum/field survey date と original GPS-local h(s,t) が未解決。
