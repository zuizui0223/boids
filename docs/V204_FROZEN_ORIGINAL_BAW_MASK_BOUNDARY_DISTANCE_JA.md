# v204 | Vlieland固定10km区画のWCS地形マスク入れ替わりは高潮・低潮境界付近に集中するか（SOURCE ONLY）

v203でSOURCE認定された2018/19年BAW `topography_inter_supratidal` WCS native10m地形を同じEPSG25832 grid（1000×1000、同一x/y）で比較すると、2018年有効247437、2019年219396、共通215587、2018のみ31850、2019のみ3809である。しかし**有効地形画素の減少は干潟面積の減少とは限らない**。地形製品のマスクの年差が、高・低潮線に近い場所に集中するかの検証を、v203結果を見た後の**探索的SOURCE診断**として実行する。

## 新たなoriginalデータを開く前に固定する6 SOURCE条件

1. **事前のSOURCE-replay異常（v204実データを開く前に確定）**：v202の2つの成功済みGitHub artifact（run #44431779227 と #44431817558）では、4つのGeoJSON HTTP応答のraw-byte SHAが全て異なるが、同じ4 original geometryのHITS件数とROIクリップ線長が全て一致した。従ってraw JSON byte SHAは原HTTPレスポンスの識別レシートとして各実行で保存するのみとし、同一性ゲートは元OGC Capabilitiesの不変SHA＋元WFS4 types＋v202源件数＋source clipping length（1e-5km許容）と、トップレベルtimeStampを除く**semantic JSON SHA**を別々に記録・2 CI実行間で比較する。違いの原因が必ずtimestampだと推定はしない。v204そのものの元データの結果を開く前にこの修正を凍結しておく。prior v202 source HTTP byte shaの初回・2回目も保存し、内容一致に使わない。参考のv202第二回GeoJSON raw SHA：2018 high `4f3d9911234641d846ad43c5adc9e311b4fc48303580583b35baae6d6227c847`（7本）、2018 low `084e654278b56976097570879505d5b5c9b204b6a7fd85621eef056ecb67b349`（52本）、2019 high `b0ed2e8fab7fd1ece9a09678ebf5a921208c8ed34852e30651115b613ca52d23`（8本）、2019 low `c68a7332afc497e57753f7ecb3b32726db76d77d8ef902e102d`（50本）。
固定のv202原曲線ROIクリップ長：2018 high=30.715113km、2018 low=131.948330km、2019 high=28.668077km、2019 low=127.491236km。clip lengthの一致はジオメトリの完全同一性の十分条件ではないためsemantic hashも併記。
2. v203 original WCS EPSG25832 10m GeoTIFF 2018 `3630b3a732efb79bc5a85a6d1c8bc0c63cff992783ca86142360837cd318ba4f`、2019 `e666c271b3d3cab98aaa8d0ca7ba3c076b7bd363036f9a15e58593ffa8994e37`。元WCS/XML SHA `55e531bbe17f8720b5b1aecc82130c1d8a29adb10738fe727ac3d4869f2afeec`、元WFS/XML SHA `ea41b511a593b37e87bae1cc53dfc18c071f4e8769cbff93fa01f5a6618788b5`。生バイナリの各SHAが違ったら、最新ソースで自動置換せずSOURCE STOP。
3. 同じWEBTICS 2011 Vlieland Haven RD(135280,590000)をEPSG25832に変換した**v202/v203と同じ10km四角ROI**。モデルを都合よく別の場所へ広げない。鳥の元GPS位置ではない。WFSは2018/19 high/low各2組、前回と同じ `GetFeature count=100` (生配列はrunner RAMのみ)。WCSはv203と同じ `GetCoverage EPSG:25832 subset=E(...), N(...)` (各年20MB上限、RAMのみ)。native original CA TLS ON、redirect追跡なし。
4. 2018/19 original地形の有効画素を v203と同様に `isfinite & not masked & abs(z)<=100` とする。厳密に v203 sourceの `n2018=247437`, `n2019=219396`, `ncommon=215587`, `n2018only=31850`, `n2019only=3809` を照合。不一致はSTOP。真の波の当時測量日や標高NAP校正はここで証明しない。
5. 4本群の本物の曲線を同一ROIでShapely clipし、GeoTIFFのネイティブ10m gridへ `rasterio.features.rasterize(...,all_touched=True)`。4カテゴリーすべての合成境界から `scipy.ndimage.distance_transform_edt` で、各セル中心の最寄り元境界画素までの近似距離を推定する。近接距離固定カテゴリ: **0–50m,50–100m,100–250m,250–500m,500–1000m,≥1000m**。10mラスタ化による距離誤差が生じうるため、これを厳密な曲線距離や汀線移動と呼ばない。
6. SOURCE-safe集計は全1000000セルを、`2018 only` (lost numeric support), `2019 only` (gained), `both` (stable numeric), `neither` (both masked) の4クラス×6距離ビンに分類。**2018年有効なセルのうち2019年に無効となった割合**をビン別に出す。固定した主記述対比は近傍 **d<100m** と遠方 **d≥500m** の比較（near/far loss probabilityおよびrisk ratio）。他に四象限（E/W×N/S）のlost, gained, stable, neitherを全件記録。全ての組合せ・負の差を開示、p値は付けない。分母が0ならNone/STOPであり、有意になるまでしきい値を動かさない。

## 解釈の限界

今回、境界近くで2018/19の有効地形マスクが変われば、これは独立な生態機構ではなく、**同じBAW製品内の年別潮間帯定義・バッファ・マスク処理**を反映している可能性が高い。公開モデル出力からの空間的関係の証拠に止まり、原地形の実測年月日、海底侵食、干潟面積の減少、実測局所冠水、ミヤコドリ採餌可能範囲へは一切直結させない。Eemshavenなど他地点へ一般化しない。

原TIF/GEOJSON生座標、鳥GPS/ACC、RWS 10分実測原時系列はGitHub/Actions artifactへ保存しない。v182の元DEM垂直datum/survey day/GPS h(s,t)、太陽・潮汐行動因果・群れBoidsはまだSOURCE STOP。
