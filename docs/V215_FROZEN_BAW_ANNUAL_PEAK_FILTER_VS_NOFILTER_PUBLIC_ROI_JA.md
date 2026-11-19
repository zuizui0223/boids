# v215 | 同じ2018/19 BAW年統計`sea_surface_height_peak`の通常版 vs no_filter版（真のROI SOURCE比較）

v211〜v214でBAW原年統計20m WCS2の元2018/19 `nof_valid_data_points_YEAR_nl` を検証した。v214ではVlieland Haven公開1km参照区域の有効点数元画素1621/2500が全て26281、West Terschelling1283/2500のうち37画素が2018元26132→2019元26278、残1246は26281、Wierumergronden2500/2500が全て26281を原TIFF SHAを固定して再現。**しかし年統計WCSと20min WMSは別製品**で、年カウント値を単純に`h(s,t)`や冠水割合へ換算できない。次はBAW原年統計の**同じ指標のfiltered/unfiltered処理**がどのように収録画素を変えるかを直接比較する。

## 事前のSource-only固定
真正v211原WCS native layer namesから（ソース実取得前）固定した`sea_surface_height_peak`の年次・国`nl`4年×variant：
- 2018 filtered `TrilaWatt_Hydrodynamik_2018__sea_surface_height_peak_2018_nl`
- 2018 no_filter `TrilaWatt_Hydrodynamik_2018__sea_surface_height_peak_2018_nl_no_filter`
- 2019 filtered `TrilaWatt_Hydrodynamik_2019__sea_surface_height_peak_2019_nl`
- 2019 no_filter `TrilaWatt_Hydrodynamik_2019__sea_surface_height_peak_2019_nl_no_filter`

元sourceは正式BAW 2018/19 original年間`Hydrodynamische Kennwerte` WCS2。原source Cap SHA2018 `b22c4571435b5da1d4cc11dfcca985d536f447337a0bf869780b77d4360a6f28`、2019 `af18e4a3280e5bfaef58e525b7079f5e4c4d9b57beea6c7743ae9f2ac16143e4`、同じ公式redirectとCA verificationを再監査。実モデルの数値を見る前に固定した独立2011 WEBTICS公表地点は **Vlieland Haven (135280,590000), West Terschelling (143870,597420), Wierumergronden (192882,614562)**。各地点±500mの1km四角 source EPSG25832、6 site-year×各2 variants=**12オリジナルTIFF**。サーバが無効な地点を別地点へ差し替えない。

1. WCS2`GetCoverage`をsource exact native Year-CoverageId、元E,N bounds、`format=image/tiff`各最大5MBのみ。元URLを先に固定し、HTTPS正常CA証明書検証/unauthorized redirect拒否、source原GeoTIFF EPSG25832、native 10～40m、同じsite/yearの2版のshape/transform完全一致のみ対応。真の鳥GPSやRWS native観測点位置ではない。
2. `rasterio`源maskedとfinite数値及び`abs(value)<=100`（極端値はunknown候補として不採用）で変数本体の数値有効画素と元nodataを計数。`peak`という変数名を実測海面に変換しない。source original byte SHA、native pixel masks、年別/変数variantの有効数値n、5/50/95百分位等を集計し、生TIFF配列はrunner RAMのみ。
3. 同一site/year`filtered`対`no_filter`の**共通有効画素n、filtered only n、no_filter only n、両方masked n**を全2500 original ROI画素で数える。`no_filter`は年統計で常時水没フィルタを外した派生製品なので`no_filter only`画素が多いかを検証。任意の追加ROIやpixel選択はしない。各3地点×両年の6組で同じ算式。
4. `nof_valid_data_points`層の年別画素presence n（v214源から元数値を再取得してもよいが、今回は**原v214の集計確認済み1621/1283/2500を文脈として固定、raw annual count再ダウンロードしない**）を位置づけとして対比する。ただしこのsourceクロスレイヤー対比は独立実測ではなく同一BAW年間製品内の差である。
5. 年2018/19のfiltered vs no_filter SOURCE差が再現しても、**raw500m/20min WMS `Wasserstand`欠測約1e31の`_FillValue`を真に確認したことにはならない**。no_filterが正しい現場干潟面積や局所水深の地図になるわけでもない。年統計のフィルタによる**空間的な選択**と時刻別WMSの**時間的な選択**を別物として議論する。
6. Sourceゲートがどちらか1年/3地点でfailしても対象サイト・日付は変更しない。モデルNO_FILTERによりいつ乾いたかの正確な時系列は復元できない。原個体GPS/ACCと元20m Deltares歴史DEM true survey date/NAP、モデルの元NetCDF `_FillValue` は依然STOP。

**元WCS sourceのnew codeは後続PRにドラフトし、native 12ROIの結果が確認できてからだけ新しい数値結果を論文に採用する。**
