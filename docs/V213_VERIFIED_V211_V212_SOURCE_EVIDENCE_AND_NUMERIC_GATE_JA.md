# v211–v212独立SOURCE成功の固定レシートとv213定量確認の状態

2026-11-19。BAW official 2018/19年の**年別hydrodynamic Kennwerte**（hydrodynamischen Kennwerte）を、v195–v210で使った**時刻別`sea_surface_height_2d_YEAR_NL` WMSとは別データ製品**として確認。BAWは年別統計通常版を年間常時水没するモデル格子に限定し、元`*_no_filter`版はそのマスクを適用しないが集計valid datapointsが減るため、元valid-point-countを併記すると公文書で記述。これを時刻別WMSの正式`_FillValue`/dry-cell証明に転用しない。

## v211 original year WCS catalogue (2回SUCCESS)

- [GitHub Actions #44456179353](https://github.com/zuizui0223/boids/actions/runs/44456179353)、[#44456220003](https://github.com/zuizui0223/boids/actions/runs/44456220003)：2回とも元TLS確認、BAW legacy `mdi-dienste.baw.de`→公式`coast.baw.de`の1回だけの同year/path WCS移転後、2018/19 native original WCS2`GetCapabilities`取得成功。
- source原native WCS2 CoverageId **各年201件**、うち`no_filter`原レイヤー各57件、`nof_valid_data_points`元レイヤー各3件（NL/GER/DK）。
- 2018原WCS Capabilities XML SHA256 `b22c4571435b5da1d4cc11dfcca985d536f447337a0bf869780b77d4360a6f28`
- 2019原WCS Capabilities XML SHA256 `af18e4a3280e5bfaef58e525b7079f5e4c4d9b57beea6c7743ae9f2ac16143e4`
- **真正NL** ID 2018 `TrilaWatt_Hydrodynamik_2018__nof_valid_data_points_2018_nl`、2019 `TrilaWatt_Hydrodynamik_2019__nof_valid_data_points_2019_nl`。
- v211元source-safe archive run #44456220003 ZIP SHA256 `a93685f3718eee2036d77a61875dcbcac78ffb2bb75442c0367a79a2ec6c2982`。ZIP内原year coverage catalogue JSONと元source tokenのみを保存。

## v212 native DescribeCoverage (original source success)

- [Actions #44456836252](https://github.com/zuizui0223/boids/actions/runs/44456836252) では元二年の同一native year coverage `DescribeCoverage` がSOURCE PASS。
- 2018 native DescribeCoverage XML SHA `5a878c6b2920e2e7a24d608553bd4264a426227ac86867a47e86b834f492e5fb`、2019 `db2e57532ec6c7378dc1b7ff31fc18ea88f5820eb3290a6474d171fda9949dcf`。
- 両年**EPSG:25832**, axisLabels `E N`, 元native Envelope x = **182990.0–388290.0 m**、y = **5867694.6032–5978014.6032 m**。元GeoServer`RectifiedGrid` offsetVector `(20,0)`, `(0,-20)` → **20m×20m**、両年全く同じ格子原点・範囲。ネイティブの`uomLabels=m m`は**水平軸のメートル**であり、valid_countの物理単位ではない。
- `rangeType` `uom` `NilValue`は、v212で検査したnative元XMLには明示的な列として得られず、**元sample-countの分母・元NoData sentinel値はまだUNKNOWN**。そのため元20min WMSモデルの`1e31`が真の`_FillValue`と宣言したり、年カウントを時間水没確率`k/26280`などへ正規化しない。

## v213の実数値SOURCE検証の前に固定した3公表reference地点
- Vlieland Haven WEBTICS2011 RD(135280,590000)
- West Terschelling WEBTICS2011 RD(143870,597420)
- Wierumergronden WEBTICS2011 RD(192882,614562)

3地点ともnative年次WCS2のsource地理extent内に位置する。**2018/19実観測機器の精確位置ではない**。各点をEPSG25832に転換し、±500mの元1km squareでSOURCE raster値を固定して取得する。6 source sampleが本当にsource成功するまで数値結果を主張しない。

## 科学的ゲート
v210までのオリジナルBAW時刻別WMS×RWS `NoData`のvalid-only上方選択偏り（沿岸8グループ等重み+0.528645833mNAP）は、**時刻別モデル**とRWS measured sourceレベルの実結果。一方v211–v213は年別`Kennwerte`モデル統計SOURCE。両者は独立現場測量でも相互原因証明でもない。個々のGPSセルh(s,t)、元Deltares歴史20m DEM実測日/vertical datum、干潟露出・鳥の採餌・太陽×潮汐・社会Boids推定への昇格はSOURCE STOP。
