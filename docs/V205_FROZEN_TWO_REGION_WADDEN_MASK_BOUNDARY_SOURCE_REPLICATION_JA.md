# v205 | v204のsourceマスク-潮位境界近接を独立した2地域で地理的検証（結果閲覧前に固定）

**v204結果を見た後のexploratory spatial source replication**。v204の公開Vlieland Haven 10km ROI 2018-only mask 31,850のうち98.69%がBAW年別高潮/低潮線からラスタ近似100m未満、2019-only 3,809のうち99.74%が100m未満だった。v204の同じ原BAW製品内の年次マスクと年次high/low境界線なので、この結果は**モデルのマスク生成規則に由来する可能性**があり、独立な生態・侵食効果ではない。次は元2011 WEBTICS論文の既公表地点から、v204のVlielandとは別の**2地点**を固定し、場所による再現性を検証する。

## 年2点・場所2点を固定
- 地域A **West Terschelling**：WEBTICS 2011原公表RD EPSG28992(143870,597420)
- 地域B **Wierumergronden**：WEBTICS 2011原公表RD EPSG28992(192882,614562)
- 各々EPSG25832へ変換し、各点を中心に**10km×10km**固定四角ROI。v204 Vlielandとの間で距離近接はあるが、2地点のデータはv204のROIと同一ではない。WFSの元モデルエリア外/原有効標高不在ならそのまま報告し、別地点へ差し替えない。
- 年2018/2019、元BAW WCS topography`TrilaWatt_Wattflaechen__topography_inter_supratidal_2018_nl` / `_2019_nl`、WFS元高潮/低潮線`TrilaWatt_Wattflaechen:high_water_boundary_2018_nl`,`low_water_boundary_2018_nl`, 同2019、全4種類。
- 元source OGC WCS/WFS Capabilities SHAはv199-v204で確認された `55e531bbe17f8720b5b1aecc82130c1d8a29adb10738fe727ac3d4869f2afeec` / `ea41b511a593b37e87bae1cc53dfc18c071f4e8769cbff93fa01f5a6618788b5`。元URL`coast.baw.de/geoserver/TrilaWatt_Wattflaechen/wcs`/wfsのみに限定。HTTPS default CA検証ON、redirect禁止。

## 元SOURCE原本取得・解析凍結
1. 各地域×2018/2019：`GetCoverage`をEPSG25832の同ROIで`subset=E(min,max)`, `subset=N(min,max)`, `format=image/tiff`、各20MB以内に制限。原TIFF CRS EPSG25832、pixel 5–100m、100万画素以下、原有効値`finite & abs(z)<=100 & not masked`、2年同じgrid+transformのみ年次転移を評価。最低両年各1,000有効セルと≥1,000 common valid cellをSOURCEゲートとし不足時は`SOURCE_STOP_INSUFFICIENT_NATIVE_SUPPORT`と報告。元TIF生データはRAMから消し、GitHubに保存しない。
2. 各地域×4 native年高低潮線は先に`WFS2 GetFeature&resultType=hits`をsource取得。0件は0として記録（地理source absence）。native integer`numberMatched`が`0..500`のときのみ元`GetFeature`でbbox×count=500、JSON/WFS元CRS25832、最大15MB。`features`元件数がHITS一致、geometryがLineString/MultiLineString、元座標がnative metric EPSG25832であること、原ROI実clip長を全件で確認。0件は空ソースとして計上、都合よく大きなROIに変更しない。
3. 4種類から各年の本物の`high+low`曲線をShapely clipし、native raster transformへ`rasterio.features.rasterize(all_touched=True)`、`distance_transform_edt`。固定距離ビン0–50、50–100、100–250、250–500、500–1000、≥1000m。source original線データが0で距離定義不能ならsource STOP。
4. v204と**同じ4年次数値セルclass**：2018-only／2019-only／both／neither。近く100m未満に含まれる比率`n_2018only_near / n_2018only_total`と`n_2019only_near / n_2019only_total`を主記述とする。v204の既知参考値はlost98.69%、gained99.74%。地理的再現判定は**両年各n≥1000、lost≥100、gained≥100**を満たす各対象地点に限り、**両方の割合≥90%**なら当該新地域に「モデルSOURCEパターンが再現」と記す。母数不足は`NOT_EVALUABLE`であり、肯定数に含めない。
5. ネガティブや弱い出現率・取得失敗も必ず2地点とも記録。元曲線の元HTTPバイトSHAはv202で毎実行変化するため、生HTTP bytes shaとsemantic JSON fingerprint（トップ階層`timeStamp`のみ除く）を分けて報告し、出所・件数・clip長を必須。元TIFF byte SHAは同一ROIの2回のCI実行間で比較し、source公開時点であることを記録。結果に合わせてROIや年・サイト・距離帯を変更しない。

## 真の限界
同一BAW製品に対する異なる場所でのSOURCE再現はモデル処理ルールの広域共通性を示しうるが、**独立した現地フィールド測量の複数地域メタ解析でも、鳥類の実GPS採餌/潮汐×日照の因果機構でもない**。公開WEBTICS地点が2018/19年の観測所機器位置や鳥のGPSそのものと一致する保証なし。モデル地形原surveydays・native datum、時系列h(s,t)、捕食資源は別ゲート。原ラスタ/GeoJSON曲線/TIFF生値/個体GPS/ACC/RWS実測時系列は保存しない。
