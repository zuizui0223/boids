# v217 実SOURCE結果｜2018/19時刻別TrilaWattのNetCDF4 WCS出力形式・UTC時間軸を検証

2026-11-19。v216で真正BAW年別2018/2019 WCS2 field`Wasserstand`（uom `m`、Nil `9.999999848243207E30`）が源SOURCE positiveだったことを受け、当該元WCSのGetCapabilities/DescribeCoverageを二度SHA固定して再取得。

## 真正SOURCE 2回
- [GitHub Actions #44474745384](https://github.com/zuizui0223/boids/actions/runs/44474745384) と [#44474801873](https://github.com/zuizui0223/boids/actions/runs/44474801873)：両方全テスト・原BAW source SHA/元nil/unitsゲートSUCCESS、元出力結果一致。
- 2018 WCS original Cap SHA `7b439a8ad1af2fb1e341af5e7b4306535d134ed06d0315df99e2e5488f322388`、2019 `a124a47f4ba037f1403f60b52c8b02750308ee201a88f026c42721f664def37d`。
- 2018 original WCS DescribeCoverage SHA `bf5976a6edd2365ff33b90bf0214042884e0d6d3fc9b3eb3dbb7c28a96245664`、2019 `9a0bd587debfaba85fd877c788273a18c5ae6ea57a8a9efdb88c344da6ec1e91`（いずれもv216と完全一致）。

## 2018・2019共通の元WCS2出典構造
- `GetCoverage`公式WCS2が対応、original`formatSupported`は **`application/gml+xml`**, **`application/x-netcdf`**, **`application/x-netcdf4`**, `image/jpeg`,`image/png`,`image/tiff`,`image/tiff;application=geotiff`, `text/plain`。**NetCDFとNetCDF4は元WCSが実際に列挙した正規MIME名**。
- 元CoverageId year2018 `TrilaWatt_ncHydro_2018__sea_surface_height_2d_2018_NL`、year2019 `TrilaWatt_ncHydro_2019__sea_surface_height_2d_2019_NL`。
- native `gml:EnvelopeWithTimePeriod` axisLabels **`Lat Long time`**、horizontal CRS `http://www.opengis.net/def/crs/EPSG/0/4326`、native uomLabels `Deg Deg s`。
- 両年同じsource水平extent：**Lat 52.8632601075–53.9411522296, Long 4.1769204900–7.3396245355**。元source sampling grid原点 `53.938934344529976 4.179138375068806`（Lat Long）、`RectifiedGrid`、`0, +0.004435770049680624`（Long方向）と`−0.004435770049680619, 0`（Lat方向）の2 offset vectors。角度0.004436°は約500m級だが、緯度によって実距離が異なることとnative EPSG4326 axis orderを確認して初めて実metricへ変換すべき。
- original UTC time extent：2018 **2018-01-01T00:00:00.000Z→2019-01-01T00:00:00.000Z**、2019 **2019-01-01T00:00:00.000Z→2020-01-01T00:00:00.000Z**。
- native WCS original field `Wasserstand`単位`m`とOGC NilValue `9.999999848243207E30`がsource再認証。元NetCDF本体の直接取得にはまだ至っていない。

## ここからの具体的なSOURCEステップ
year2018/19の**同日6月1日12:00UTC**、以前から固定された2011公表WEBTICS2参考地点`VlielandHaven`・`Wierumergronden`周囲の各±0.015° rectangle（native Lat Long）で、WCS2`GetCoverage`の元advertised `application/x-netcdf4`を**各年×2地点の4件だけ**取得する。NetCDF4が返らない/時間slice失敗の場合はそのSOURCE STOPを正直に報告し、余分なサイトや日付で有利な結果に救済しない。単一時刻・小さな範囲に限定し、巨大年次NetCDFのダウンロードは禁止。

成功してもWCSから再生成されたNetCDF4小領域ファイルであり、元BAW download配布の年NetCDF本体と完全同じ`_FillValue` attrsとは直ちに見なせない。物理乾出、RWS計測器の真正局所座標、鳥GPSでの15min冠水/採餌、Boids社会力を推定していない。これらはSOURCE STOPを保持。
