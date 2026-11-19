# v216 実SOURCE結果｜時刻別TrilaWatt 2018/19の水位WCSはメートル、NilValueは約1e31

2026-11-19。BAW公式カタログが公開する時刻別Hydrodynamik year-NLの**WMS**原XMLを2018/2019それぞれ既知SHAで照合し、その同一BAW GeoServer year workspaceにある仮説上のWCS2 endpointを、通常TLS CAで初めて実際に問い合わせた。**2年ともHTTP200、native WCS2本体と元水位CoverageId・DescribeCoverageを検証できた。**

## 真正出典の二重再現
- [original source GitHub Actions #44473878254](https://github.com/zuizui0223/boids/actions/runs/44473878254) と [#44473887025](https://github.com/zuizui0223/boids/actions/runs/44473887025) はともに**SUCCESS**、original 2018/19 WCS GetCapabilities+DescribeCoverageの出典SHAと元WCS NilValue/unitのsource-safe結果が完全一致。初期CI2件は`pyproj` dependency漏れでテスト時に止まった（原WCSにアクセス前）、修正済みでsource resultには関係しない。
- 2018 published WMS Cap SHA `386af7c9a75b66ef23017dfd49abe3afb71a530011e9f7bedbf3904281b7484f` /2019 `a52bf61de7bc50495ea75782a6e4bc5b4762ce3174e29a961cec1f697fe9b20a` を両run再検証。
- 2018 **WCS GetCapabilities** genuine SHA `7b439a8ad1af2fb1e341af5e7b4306535d134ed06d0315df99e2e5488f322388`、native CoverageIds **82**、`DescribeCoverage`と`GetCoverage`対応。2019 SHA `a124a47f4ba037f1403f60b52c8b02750308ee201a88f026c42721f664def37d`、CoverageIds **84**、同じOGC ops。
- NL原source exact CoverageId:
  - 2018 `TrilaWatt_ncHydro_2018__sea_surface_height_2d_2018_NL`
  - 2019 `TrilaWatt_ncHydro_2019__sea_surface_height_2d_2019_NL`
- 真正 **DescribeCoverage** source SHA 2018 `bf5976a6edd2365ff33b90bf0214042884e0d6d3fc9b3eb3dbb7c28a96245664`、2019 `9a0bd587debfaba85fd877c788273a18c5ae6ea57a8a9efdb88c344da6ec1e91`（各4,398 bytes）。
- native WCS rangeType field `Wasserstand`、真正 **uom `m`**、native NilValue literal **`9.999999848243207E30`**、そのreason `http://www.opengis.net/def/nil/OGC/0/unknown`。**全属性は2年で一致**。このNilValueはv195/v197/v206/v207/v209でモデルWMS GetFeatureInfoに出現した極端値と一致。

## 科学的な採用範囲
ここで正式確認できたのは**WCSから公開される同名時刻別モデル水位のメートル単位とOGC NilValueの定義**。v209/210の「1e31候補」を単に水位値として使わない判定に、元sourceに基づく強い根拠を追加した。v209の8/8低潮時にNilが多い、v210のBAW WMSで値のある時刻だけ残すとRWS mNAPグループ平均が+0.529m上方選択されるという**源選択効果は変わらない**。

重要な3つの区別：
1. **OGC WCS2 `NilValue` はサービスメタデータの出典**。配布される巨大NetCDF元`sea_surface_height_2d` variableの生`_FillValue`を直接取得して照合したわけではない。よって`native NetCDF _FillValue`の欄は引き続きUNKNOWNとする。
2. Field`Wasserstand`のWCSでの単位`m`は確認できたが、**元配布NetCDF本体のunits、vertical NHN/NAP variable datum attributesを個別に取得したわけではない**。原論文は製品NHN≈NAPを記載（v208で原JATS確認済み）だが、WCS serviceの元直行値が特定局の現地NAPへ正式換算済みかは未保証。
3. Nilが正式に源サービスで定義されても、その値が出る原因は**物理的な干出とは限らない**。モデルの格子外、no coverage、wetting/drying、時間外、幾何補間失敗などがありえるため、元NetCDFの処理やsource gridを確認するまで「Nil=dry flat」としない。

## 次の科学的SOURCE条件
WCS2が真正の`GetCoverage`をadvertiseしているので、v217ではまず**本当のnative `DescribeCoverage`の時間・空間座標軸とWCSが宣言する出力形式**を元原XMLで監査し、切り出し可能な元水位データの条件だけを固定する。v217で元NetCDF実数値や生巨大datasetはダウンロードしない。

物理から生態への結合：実ミヤコドリGPS地点のモデルh(s,t)と元地形zの垂直datum・実測日・source maskを独立に整合させた後、年外行動予測/太陽×潮汐/社会Boidsを再検定する。現時点の科学的STOPは継続。
