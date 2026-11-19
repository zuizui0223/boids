# v214 SOURCE結果｜年別有効データ点数の全画素分布と時刻別WMS可用性は別の次元

2026-11-19。真正BAW annual derived `Hydrodynamische Kennwerte` 20m native WCSの2018/19 `nof_valid_data_points_YEAR_nl` 6 bounded TIFFを、v213元source byte SHA6本で再照合。さらにv209で元RWS×BAW WMS72時刻を独立確認したoriginal source-safe GitHub Actions run #44452986729 JSON SHA `5e4a492eae99e17b6f79444ac22a342ce5c88f570181fe44a8cc633b1932a62c`を元GitHub archiveからのみ読み、時刻別WMS`Wasserstand`の巨大NoData候補/数値候補の元source分類を、**原RWS/BAW time seriesを新たに開くことなく**集計した。2025公表のBAW ANNUAL countと500m/20min WMSは**別製品**。

## 真正元SOURCEの再現性
- [GitHub Actions #44464064868](https://github.com/zuizui0223/boids/actions/runs/44464064868) と [#44464116781](https://github.com/zuizui0223/boids/actions/runs/44464116781) の2回とも全ユニットテスト・source scientific QA PASS、元6 GeoTIFF byte SHAと元WMS72 source classが一致し、以下の全cell histogramと中心画素が完全再現。
- v213で公表済の1km²固定公開3参照地点・両年同native EPSG25832/20m raster, 各2500セルをそのまま使用。入力は元sourceバイナリからActions RAM内で処理し、生画素や原水位時系列をGitHubに保存していない。

## 数値が入る画素の有効点数全値ヒストグラム

| 公表source参照地点 | 年 | native count値=26281 | native count値<26281 | その他masked/no-value | 下回る具体的値 |
|---|---:|---:|---:|---:|---|
| Vlieland Haven | 2018 | 1621 | 0 | 879 | なし |
| Vlieland Haven | 2019 | 1621 | 0 | 879 | なし |
| West Terschelling | 2018 | 1246 | **37** | 1217 | **26132（37セル）** |
| West Terschelling | 2019 | 1246 | **37** | 1217 | **26278（37セル）** |
| Wierumergronden | 2018 | 2500 | 0 | 0 | なし |
| Wierumergronden | 2019 | 2500 | 0 | 0 | なし |

West Terschellingの**同じ37 native pixel**で年別有効データ点数が+146（26132→26278）変化した。他の同一公表1km ROIでは年別native valid-count値と有無の差は0だった。これは**年間モデル統計のsource sampling availabilityの年差**であり、現地の干潟面積や地形侵食/鳥の採餌回数の年差ではない。実元間隔の計算端点やサンプル母数は元DescribeCoverageにない。値26281が365日×72(20分ステップ)+1と数学上一致しても、正式な年間湿潤率の分母`26281`と断定して年確率へ正規化しない。

3サイトの公表2011 RD reference pointを元GeoTIFF内の**rasterio floor規則で一意に選んだ中心セル**の年別値はすべて`26281`。中心がセルの境界近くなら登録の仕方に敏感であり、さらにWMSとWCSの格子解像度が異なるので「同一cell」の比較ではない。

## 年別20m空間presence vs 時刻別500m WMS source numeric coverage（別分母）

| Site | WCS 20m年間count数値presence（2500セルのうち） | 20min WMSモデル数値候補（2018/19 June/Sepの計24固定UTC時刻のうち） |
|---|---:|---:|
| Vlieland Haven | 1621/2500 = **64.84%** | 11/24 = **45.83%** |
| West Terschelling | 1283/2500 = **51.32%** | 15/24 = **62.50%** |
| Wierumergronden | 2500/2500 = **100%** | 24/24 = **100%** |

**地点間の順位すら一致しない**：年統計countの有効画素割合はVlieland>Westだが、20min WMS数値可用率はVlieland<West。両者は分母・対象時間・モデル処理・解像度の異なる指標であり、相関・回帰・p値・実際の湿潤時間率に変換しない。これは統計的に別製品を取り違えたモデル欠測補完を防ぐSOURCE反証である。

## 次の真のSOURCE条件
真の時間別WMS `~1e31`の`_FillValue`はまだnative NetCDF attributesで確認していない。BAW年統計`*_no_filter`について公式原文書はマスク除去/有効点数低下を説明するが、それは**20m年間統計の空間フィルタ**であって、時刻別500m WMSの乾出原因ではない。v215 #238では同一年度の`sea_surface_height_peak_YEAR_nl`通常版と`..._no_filter`の実Source TIFF数値presentを同じ3地点×2年で直接比較する（いずれも単年度モデル派生量）。

**生態学的な未解決事項**：個体GPS h(s,t)、原Deltares historical20m native z datum/field survey day、真正鳥ACCとの局所干出・採餌成功、太陽×潮汐・群れBoidsの因果。v169の真正RWS measured harbor tideによる条件付き2018-fit/2019-test ACC予測は独立して維持し、今回のBAW WMSの欠測問題をその旧解析へ遡及して適用しない。
