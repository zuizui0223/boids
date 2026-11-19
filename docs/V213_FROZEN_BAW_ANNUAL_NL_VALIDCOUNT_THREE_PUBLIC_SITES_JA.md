# v213｜BAW 2018/2019年 年間有効データ点数の20m格子を、公開3地点の固定1km ROIで取得（SOURCE ONLY）

v211年別水理統計2018/19原WCS2各201件 `CoverageId`から、唯一の年・オランダ領域native source：
- `TrilaWatt_Hydrodynamik_2018__nof_valid_data_points_2018_nl`
- `TrilaWatt_Hydrodynamik_2019__nof_valid_data_points_2019_nl`

v212でnative `DescribeCoverage`原SHA2018 `5a878c6b2920e2e7a24d608553bd4264a426227ac86867a47e86b834f492e5fb`、2019 `db2e57532ec6c7378dc1b7ff31fc18ea88f5820eb3290a6474d171fda9949dcf`。両年共にEPSG25832、軸E N、20mのorigin+offsetで同grid（0..10264×0..5515）と実証。native uom/ nilValues は元responseに存在せず、1年の`valid data points`の分母・元`_FillValue`も未確認。**この年度別製品は時刻別WMS`sea_surface_height_2d`とは別であり、年別カウントを時刻別値の補間・マスク埋めに使うのは禁止。**

## 元sourceデータを見る前に固定
- 対象3地点：2011 WEBTICS公表のRD reference、Vlieland Haven(135280,590000)、West Terschelling(143870,597420)、Wierumergronden(192882,614562)。全て**公表された地名の参考座標**であり、2018/19原RWS測定機器の真の位置や元鳥GPSではない。
- 両年2018,2019、計6組、**各site中心から±500mの固定1km×1km EPSG25832**。元値がないsource地点を別地点へ置き換えない・ROIを結果に合わせて拡大しない。対象年も3地点も全件sourceアーカイブに残す。
- 公式WCS2 original GetCapabilitiesをv211 SHA2018 `b22c4571435b5da1d4cc11dfcca985d536f447337a0bf869780b77d4360a6f28`、2019 `af18e4a3280e5bfaef58e525b7079f5e4c4d9b57beea6c7743ae9f2ac16143e4` で再照合、native `DescribeCoverage`もv212既知SHAと同じなら`GetCoverage`を実行可。元official mdi→coastの1回だけsource-authenticated redirect、TLS標準CA ON、他redirect拒否。
- WCS2 GetCoverage `coverageId=元2018/2019 __nof_valid_data_points_YEAR_nl`、`subset=E(e−500,e+500)`、`subset=N(n−500,n+500)`、`format=image/tiff`。レスポンス各最大5MB、2年×3ROI、原SHA・bytes保存、生TIFFピクセルはrunner RAMのみ/公開しない。native TIFF CRS EPSG25832、resolution 10〜40m、格子/バウンズが固定ROI±40m内に収まること、3band以上や大量格子はSTOP。
- native raster `masked`・`isfinite`・非負近整数（|x-round(x)|≤0.001）の年別有効データ点数だけを集計。元値が全ての格子で有効と保証せず、数値が読めたpixel数・zero/p05/median/p95/maxを元source safe集計として記録。**件数の原年間の最大分母を勝手に365×72などと仮定しない**。同一格子なら年別の共通有効セルに限定した2019−2018元count候補差分も集計し、元頻度をdry-hour率と解釈しない。
- 既存v197/v209の固定3地点のモデルNoDataパターン（Wierumergrondenは24/24 source numericで、VlielandとWest Terschellingは低潮時NoDataがある）は**結果閲覧前のsource事実**。v213の年間有効点数を利用してこれら2つの時刻別欠測を正確に再現したと主張するには、両製品のresampling/downscaling・元WMS`_FillValue`/wetting-drying規則・年の統計カウントの定義をsourceで確認する必要がある。
- 3地点での時空間数値対応が出ても**同じBAWモデル内部の探索的source比較**であり、真の生物学的普遍性・現地測量・2018当時の予報ではない。

## 中止条件
元年別WCS / DescribeCoverage SHA drift・2018/19年取り違え・追加redirect・GeoTIFF sourceでない・EPSG/ROI/resolution不一致・整数でないカウントを源`count`として読み替える場合はfail-closed。部分値だけで肯定的なモデル比較を作らない。

v182の元Deltares 20m DEM実測日/鉛直NAP、鳥のGPSセルh(s,t)、干潟露出・採餌成功、太陽×潮汐とBoids力の因果推定は未実施・SOURCE STOP維持。
