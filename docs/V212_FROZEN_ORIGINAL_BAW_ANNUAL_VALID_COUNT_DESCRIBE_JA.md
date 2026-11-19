# v212｜2018/19年BAW年間有効データ点数の元CoverageDescriptions：座標軸・単位・NoDataの原本確認

v211原WCS2 source-success Actions #44456179353/#44456220003で**2018と2019各201 native CoverageIDs**を同定。オランダ領域の正確な原native namesは次の通り：
- `TrilaWatt_Hydrodynamik_2018__nof_valid_data_points_2018_nl`
- `TrilaWatt_Hydrodynamik_2019__nof_valid_data_points_2019_nl`

2018と2019ともに実`no_filter`派生coverageも確認したが、元の`nof_valid_data_points`が**元20分格子の可用時刻数・年中有効時刻数・モデル水理分析のvalid valuesのどれを数えるか**は元Descriptionで確認する必要がある。数値範囲や単位を見ずに年間水没割合とみなさない。

## SOURCE条件を元数値を見る前に凍結
1. v211で確認したBAW元year WCS2経路をHTTPS/CA ONで同じGetCapabilitiesから再認証し、XML byte SHAを実元で一致させる。旧mdi→新coastの1度だけの公式redirectを許す。原version2.0.1、登録のnative年別CoverageIDsも再確認する。元2026年に仕様が変わったらSTOP。
2. source WCS`Operation name="DescribeCoverage"`を元OGC Capabilitiesで明示的に確認し、同一正規BAW path/host/yearの`REQUEST=DescribeCoverage`に、元xmlから取得した**exact** native`COVERAGEID`を指定。元XMLレスポンス最大2MB、HTTPS標準CA、redirect二度目禁止、DTD/XXE禁止、HTTP200かつ真の`CoverageDescriptions`であることを確かめる。
3. 元`CoverageDescription`単位で`CoverageId`を照合。原`gml:Envelope`または`gml:boundedBy`に記載された`srsName`（EPSG25832と推測して採用しない）、`axisLabels`、lower/upperCorner、`gml:RectifiedGrid`/offsetVector/sizeなど、元`rangeType`のfield, uom, nilValuesをそのままSOURCE-safeに保存。元座標を数値に変換していない段階ではGPSとのoverlapは主張しない。
4. 元`units`/nil/annual valid-count分母や元native grid axesが示されない場合は、その項目を**NOT_VERIFIED**。元WMS time-resolved `Wasserstand`の1e31候補の`_FillValue`と混同しない。元sourceが極端な値を用いる場合も、元モデリング乾出判定とは別。
5. 2年とも原coverage schemaがSOURCE PASSした場合のみ、次v213で公表WEBTICS3地点（Vlieland Haven, West Terschelling, Wierumergronden）から事前固定の小ROI内のsource raster値を取り、2018/19年間モデル有効時刻の**空間的配置**を比較する。原20m DEM, old vertical datum, true survey-day, actual birds are still STOP。

このversionでは原TIFF・WCS GetCoverageと時刻別WMSは**一切取得しない**。native source解釈の限界を保ったまま前進することが目的。
