# v220｜2025公開BAW時刻別モデルの欠測分類は、3地点×2年×6/9月のNative WCS格子でWMS原本と再現するか

**v219 2回のsource-success結果（8 original matched UTC class, numeric5/5差≤5e-8m, Nil3/3）を閲覧後の探索的地理・季節source replication**。今回はWMSを再照会せず、**v209の2つの真正元GitHub Actions原source-safe JSONのうち、事前にSHAを固定した1本**にあるWMS 72時刻のclassを再使用する。元RWS実潮位・元WMS水位数値は再取得しない。

## 公開結果を追加取得する前のSOURCE固定
- 対象は以前v195/v206/v209で**独立公表された2011 WEBTICS RD3地点**：VlielandHaven (135280,590000), WestTerschelling (143870,597420), Wierumergronden (192882,614562)。2018/19真正RWS機器位置/タグ鳥GPSではない。
- 年**2018・2019**、月**June1・September1**、UTC時刻**00:00・12:00**だけ。3地点×2年×2日×2時刻=**24 genuine original WCS2 GetCoverage**。2時刻は元v206/v207の凍結6時刻の部分集合。nullを見て新時刻や別ROIへ移動しない。
- Source WCS `TrilaWatt_ncHydro_YEAR__sea_surface_height_2d_YEAR_NL`、`application/x-netcdf4`、source `Lat±0.015° Long±0.015°`、`time("YYYY-MM-01T00:00:00.000Z")` または12Z。WCS native `Lat Long time`、uom=m、OGC NilValue `9.999999848243207E30`。BAW元native WCS Cap SHA2018 `7b439a8ad1af2fb1e341af5e7b4306535d134ed06d0315df99e2e5488f322388` /2019 `a124a47f4ba037f1403f60b52c8b02750308ee201a88f026c42721f664def37d`、元Describe SHA2018 `bf5976a6edd2365ff33b90bf0214042884e0d6d3fc9b3eb3dbb7c28a96245664` /2019 `9a0bd587debfaba85fd877c788273a18c5ae6ea57a8a9efdb88c344da6ec1e91`、公式WMS Cap SHA v194 と一致必須。
- 元WMS分類のSOURCE：v209成功run `#44452986729`の `original_RWS_tide_mNAP_vs_BAW_WMS_extreme_NoData_72points_v209.json`、**bytes SHA `5e4a492eae99e17b6f79444ac22a342ce5c88f570181fe44a8cc633b1932a62c`**。GitHub Actions archiveからのみ取得、v210 `exact_original_source`で12グループ×6UTCのsource receipts、各3地点×2018/19×June/Sepと合計72 source classesを認証。生元RWS水位やWMSバイナリ取得はしない。
- 年×公開座標の元NetCDF4はv218/v219同様1時刻・数十native 500m相当格子の小領域のみ。native HDF5 signature、HTTP200、HTTPS default CA verification ON、redirectなし、各8MB以下。出力`time=1`、`lat`と`lon`各1D、nearest **SOURCE格子点を公表参考点から幾何的に固定（abs delta lat/lon≤0.012°）**。元水位変数`sea_surface_height_2d`または`Mosaic(sea_surface_height_2d)`の一つのみ、`units=m`, native float32`_FillValue`一致必須。
- 出力native nearestの`_FillValue` vs 有効数値を原WMS source-safe JSONの**同UTC分類**と比較する。`NoData/NoData`および`numeric/numeric`はclass positive、`NoData/numeric`はdiscordant、両者のsample geometry/ interpolationが異なる可能性を明記。**一致率をソースCI通過条件にはしない**（負の結果・West Terschelling時刻などを除外しない）。native crop内`n_Nil/`n_numeric/total`は各source同UTC・固定ROIの descriptive value として報告するが、干潟面積・潮汐ハビタット面積ではない。
- **24ケース全てに対応するv209保存済みWMS分類が必要**。元WMS classが1e31でsource`EXTREME_NODATA_SENTINEL_CANDIDATE`であればv216～218のWCS source Nilが正式に証明されたため`WMS_NIL_CLASS`として比較してよいが、実際のdrycellの原因は依然未解明。
- 全24 native NC4のHTTP response byte SHA/source分類結果のみGitHub artifactに保存。各元WCS生成NC4 binary、元格子水位配列、v209元RWS tide raw、鳥GPS/ACC、元Deltares DEMは**保存しない**。

## 採用できる科学的結果
同じBAW物理モデル製品における`year×month×site×hour`の**時刻別源モデルNil/number提供状況**が、WCSとWMSでどれだけ一致するかを測るsource内部の再現性。これは3地域・2ヶ月の**配信方式の一致**であり、独立した物理・生態的メタ解析ではない。WMS/WCSの `_FillValue` が物理的な干出で生じたか、局所水位を実RWS/鳥GPSへ正確に移せるか、historical zの縦基準/測量日、低潮・日長・Boids社会力による実行動ニッチはSOURCE STOP継続。

v209/210の低潮位選択バイアスは源RWS measured NAPが独立変数で、ここでは新たに検定しない。逆にv169の旧鳥の実測港湾水位を使った2018fit/2019testは本SOURCE欠測モデルとは異なるため、旧観測結果を無効にしたとも主張しない。
