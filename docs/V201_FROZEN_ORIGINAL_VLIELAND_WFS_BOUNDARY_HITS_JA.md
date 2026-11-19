# v201｜2018/2019年Vlieland参考地点の周囲10km四方でWFS高潮/低潮境界の実Feature件数を測る（SOURCE ONLY）

v200 original BAW WFS 2018/19高潮線・低潮線4 Native FeatureTypeのSHA/元XSD全部PASS (Actions #44430532133 / #44430539212)。元幾何はWFS 2.0の`gml:MultiCurvePropertyType`、原Horizontal CRS `EPSG:25832`。元WFS bboxは公表Vlieland地点を含むが、**カタログbboxと実境界地物の交差は別問題**。

## 事前固定プロトコル
- 対象reference site：WEBTICS (Rappoldt & Ens 2011) Vlieland Haven RD EPSG:28992 (135280,590000) を`pyproj`で `EPSG:25832`へ正しく転換。**鳥の元GPSではなく、2018年の原RWS機器位置とも限らない**。
- ROI：公表reference siteから固定±5,000m、四方10km四角形 in EPSG:25832。感度のため別半径を結果を見ながら追加しない。今回の指定ROIのwater boundary原地物件数のみ計算し、その外のワッデン海は推定しない。
- 元WFSの `GetCapabilities` URLはv199で原HTTP308`Location`から認証済み`https://coast.baw.de/geoserver/TrilaWatt_Wattflaechen/wfs?REQUEST=GetCapabilities&SERVICE=WFS`、原XML SHA `ea41b511a593b37e87bae1cc53dfc18c071f4e8769cbff93fa01f5a6618788b5` を厳格再照合。元WFS2.0.0、4 feature types原XSD `MultiCurve`の指定が全て存在してから問い合わせる。
- 真のオリジナル地物を1個もダウンロードせず、**OGC WFS2.0 `GetFeature&resultType=hits`** に限定し、Native FeatureCollection `numberMatched` 元整数件数、`numberReturned=0`、原HTTPS responseのSHA/Bytes/Content-Typeだけを取得。元地理元GMLの生座標もポリゴンも保存しない。
- 結果を見る前に対象を2018高潮・2018低潮・2019高潮・2019低潮の4つ全て固定。元FeatureType：`TrilaWatt_Wattflaechen:high_water_boundary_2018_nl`、`low_water_boundary_2018_nl`、同2019。WFS native CRSはEPSG25832、HTTP query`bbox=minE,minN,maxE,maxN,EPSG:25832`。
- 元`numberMatched`が未報告/unknown・XML ServiceException・HTTP不正・結果URLの非公的redirectなどのときはSOURCE STOP、成功と呼ばない。4つともSOURCE判定ができても全4区分で`n>0`とは限らず、0件も科学的に記録する。4区分とも1件以上なら**指定10km四角に各元境界線が存在する**というSOURCE結果に限って主張する。
- 地物件数は年別面積ではない。高潮/低潮線の形状が閉じたポリゴンになる保証、潮汐場と潮間帯面積の対応、GPS同所・採餌地点、元20m標高原NAP/実測日の一致を全く保証しない。Eemshaven等13局の外部予測結果に合わせてROIを変更しない。

v197 TrilaWatt水位WMS 17/24 plausible, 7/24 NoData extreme candidate。2018/2019モデル海面の`units`,`_FillValue`と元RWS実測からのバイアスは未校正、無効値を海水面0扱いしない。v182 SOURCE_STOP_LOCAL_EXPOSURE維持。
