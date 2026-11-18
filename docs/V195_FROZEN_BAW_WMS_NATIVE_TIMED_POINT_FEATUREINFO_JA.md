# v195｜BAW WMS 2018/2019 オランダ水位レイヤーの同一点・同時刻での数値問い合わせSOURCEゲート

**v194原XML取得PASS後・v195水位の初回閲覧前に固定**。2018/19の公式BAW WMS `sea_surface_height_2d_2018_NL` / `sea_surface_height_2d_2019_NL` を対象。原`GetCapabilities`の真正TLS検証、XML byte SHAをv194から固定（2018 `386af7c9a75b66ef23017dfd49abe3afb71a530011e9f7bedbf3904281b7484f`、2019 `a52bf61de7bc50495ea75782a6e4bc5b4762ce3174e29a961cec1f697fe9b20a`）。違う元XMLならSOURCE STOPであり、更新されたものへ自動移行しない。

## 固定したsource-onlyサンプリング
- 年2018/2019それぞれ元の6月1日12:00:00Z、20分元グリッド時刻と完全一致。**年外テストではない**。v169ミヤコドリACCの採餌データや元RWSの個体別GPSを読み込まない。
- 公開2011年WEBTICS公表の観測局位置から、固定3地点を事前指定：Vlieland Haven RD(135280,590000)、West Terschelling RD(143870,597420)、Wierumergronden RD(192882,614562)、EPSG:28992→EPSG:4326 (always_xy) の再投影を使用。**2011参照位置≠2018/19原機器・鳥のGPS地点の同一位置**。
- 公式WMS 1.3.0、認証済み`coast.baw.de`、元レイヤーの`queryable`属性と native `GetFeatureInfo` MIME formatとEPSG:4326を元WMS XMLから確認して初めて問い合わせ。WMS1.3の`EPSG:4326`は軸順が緯度・経度なので、`BBOX=latmin,lonmin,latmax,lonmax`。51×51 pixelsの中心I=J=25で、目標点±0.01度の範囲を固定。全年×3地点とも同じ処理、結果を選択しない。
- 取得フォーマットは元Capabilitiesで宣言された`application/json`, `text/plain`, `text/xml`の中からその固定順に最初に一致したものを採用。原応答最大100KB、HTTP 200/HTTPS CA検証、元レスポンスSHAと内容種類とネイティブ`Exception`の有無のみ確認。生HTMLや座標大量出力なし。
- WMS GetFeatureInfoが返す数値は**色付けされたラスターの描画値や`GRAY_INDEX`等かもしれない**。原NetCDFの`units`, `grid_mapping`, `vertical_datum`が未検証なので、自動的に元水位[mNAP]と認定しない。たとえ3地点×2年の原サービスに問い合わせ成功しても、statusは`WMS_FEATUREINFO_SOURCE_QUERY_RETURNED_NO_HEIGHT_UNIT_ADMISSION`止まり。0をno-waterや0m潮位とはみなさない。
- 原WMSの layer は年のレイヤー名・TIME:2018-06-01T12:00Zの範囲・元SOURCEがすべて条件を満たすこと。元WMS endpoint/日時/座標・元レスポンスが無ければSOURCE STOPで、別の点へ入れ替えない。原バイナリ巨大NetCDFのダウンロード、GPS個体行動との紐付けは禁止。

次のv196で必要なもの：native WMS `GetFeatureInfo` の数値が実際の物理水位であることの原メタデータ `units` `vertical datum` とモデルの実測RWS局に対する独立検証。現時点ではlocal GPS h(s,t), 古い20m DEMのNAP・survey day, 現地冠水/採餌機構は**すべてSTOP**。

WMSは2025公表のretrospective hindcast。2018に2019のモデルが利用可能だったという実時間予報の主張も不可。
