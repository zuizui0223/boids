# v219｜同一公開参照地点・同一時刻のBAW WCS生成NetCDF4格子とWMS GetFeatureInfo を照合する（SOURCEのみ）

**事後のモデル内一致・マスク原因診断。** v218成功後、元NetCDF4で `_FillValue=9.999999848243207E30` / `units=m` が確定。ここで問うのは、GeoServerの**別の公開インターフェイス**（WCS generated NetCDF4 vs WMS `Wasserstand`）が同じ地点・時刻で一致するか。これらは**同じBAWモデルソース**なので、仮に一致しても独立した現地validationやwet/dry観測ではない。

## 実数値を新しく読む前に固定
1. 2011年WEBTICS公開RDの**2地点のみ**：Vlieland Haven (135280,590000), Wierumergronden (192882,614562)。これは鳥GPSでも2018/19年RWS機器の真正な現在座標でもない。v218と同一の中心から `Lat±0.015°`, `Long±0.015°`、native WCS year-NL `sea_surface_height_2d_YEAR_NL`、形式`application/x-netcdf4`、source date **2018/19年6月1日**、fixed UTC **00:00 と12:00**のみ。計2サイト×2年×2時刻＝**8 WCS source要求**。12Zはv218 SOURCE成功済み、00Zはv197/v206固定済みの時間であり新たな結果を見て追加しない。時刻外・ROI外・別フィルタ・他海域への救済は不可。
2. 並行して同じ8 site×year×timeについて元BAW **WMS1.3 GetFeatureInfo** （以前v206で `get_approved_original_WMS_Wasserstand` と `frozen_WMS_model_request`に固定したUTC時刻と公表位置）を要求。元WMS Cap original byte SHA2018 `386af7c9a75b66ef23017dfd49abe3afb71a530011e9f7bedbf3904281b7484f` /2019 `a52bf61de7bc50495ea75782a6e4bc5b4762ce3174e29a961cec1f697fe9b20a`再確認。
3. 元WCS2 Cap SHA2018 `7b439a8ad1af2fb1e341af5e7b4306535d134ed06d0315df99e2e5488f322388` /2019 `a124a47f4ba037f1403f60b52c8b02750308ee201a88f026c42721f664def37d`、元DescribeCoverage SHA2018 `bf5976a6edd2365ff33b90bf0214042884e0d6d3fc9b3eb3dbb7c28a96245664` /2019 `9a0bd587debfaba85fd877c788273a18c5ae6ea57a8a9efdb88c344da6ec1e91`をbyte一致必須。違えばSOURCE STOP。
4. HTTPS normal CA検証ON、BAW `coast.baw.de`以外の通信禁止、無許可redirect・HTTP downgrade禁止。WCS単一応答8MB以下、HDF5 signatureとnative netCDF4、時間次元ちょうど1、水平緯度経度source coordinateを`lat`/`lon` 1D→native水位変数 `time,lat,lon`の同一gridとして検証。元WCS `_FillValue`が先行OGC NilValueに一致し、units=mであることを確認してから水位の分類を行う。source時間変数`units`等のnative metadataも保存する。
5. 本当に公表参考座標に最も近い**WCS native grid point**を探す（絶対緯度・経度差それぞれ≤0.012°）。この点の値は**WMSが照会した仮想pixelと完全同一とは限らない**：WMSのGetFeatureInfoは51×51 pseudo-imageの中心を通じたサンプリング、内部補間・mosaicの規則が違いうる。数値差・Nil分類不一致は結果として報告し、都合の良い隣接セルへ動かさない。
6. `WCS nearest`がnative Fillまたは絶対値≥1e6、WMSの`Wasserstand`も元正式Fill候補の場合は**Nil分類一致**。両方通常数値の場合は元差 `WCS nearest - WMS GetFeatureInfo` をm単位で報告（pre-fixed |delta|≤0.05mのみ `numeric approximate agreement` と記述）。分類が不一致なら負結果として保存。8件全sourceが取得できても8件全て一致することをSOURCE CI成功条件にはしない：仮説が否定されてもsourceは成功とする。
7. **元NC4生モデル配列・WMS生JSON・個体GPS/ACC・実RWS時系列はGitHubに保存しない**。source response SHA、格子source位置と公表参考点の差、nearest数値（有効なら丸めたm候補だけ）、Nil候補分類とabs deltaおよび8件の一致数だけ。元WMSのnative 1e31は物理水位として扱わない。native WCS cropが原出版full-year NetCDFの `_FillValue`と完全一致する証明ではない。

## 科学的帰結の上限
支持できるのは、**同じBAW time-resolved hydrodynamic modelのWMSとWCSが同地点・同時刻・近傍gridで同じ欠測状態や数値を返す範囲**の検証のみ。水位Nilの原因がdry-cellかどうか、wetted mudflat exposureか、標高20m Deltares `z`と同じNAP datum/survey-dayか、タグ付き鳥のGPS-cell水位とACC採餌/群れBoids相互作用を予測できるかは依然STOP。

v169の鳥ACC年外行動予測はRWS実測港湾潮位を利用し、今回のWMS/WCS処理による欠測とは別SOURCEのため、旧結果の因果機構へ昇格も否定も行わない。

次の生態学的検定：年外個体のGPS/ACCへ水位をjoinする前に、同地点WCS gridの残差/欠測と中心位置のgeometryをsourceで区別し、地形基準・餌条件・日の出/日長の独立信号と比較する。
