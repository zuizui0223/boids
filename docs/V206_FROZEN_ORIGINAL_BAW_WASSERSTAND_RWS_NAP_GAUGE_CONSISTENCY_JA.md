# v206 | TrilaWatt年別WMSのWasserstand数値と真正RWS実測水位の同時刻・同地点候補比較（SOURCE ONLY）

v195でBAW公式2018/2019年WMS original sea_surface_height_2dのGetFeatureInfoが数値を返すことを証明、v197元24個時刻地点では17通常範囲数値、7 extreme NoData sentinel candidatesを確認。BAW元論文(2025, doi:10.1038/s41597-025-06211-1)は元モデル高度NHN/NAP相当を記述するが、個々のWMS GeoJSON Wasserstand元値のnative unit/vertical datumは未検証。ここで真RWS WATHTE cm NAPとのSOURCE numerical consistencyだけを凍結して評価する。

## SOURCE固定
- RWS DDAPI2真正原観測局3個：v187で固定された VlielandHaven=vlieland.haven、WestTerschelling=terschelling.west、Wierumergronden=wierumergronden。元RWS native catalogueで唯一コードと名前を再確認。3地点はv195/v197でモデル応答の可用性を既に見た後に選ばれたので、本source比較は**事後的であり独立site holdoutではない**。Wierumergrondenだけ抜き出して結論しない。
- 空間位置はWEBTICS (2011) 公開RD原文献：VlielandHaven(135280,590000)、WestTerschelling(143870,597420)、Wierumergronden(192882,614562)。EPSG28992→WGS84、WMS1.3 EPSG4326 [lat,lon] BBOX。2018/19 RWS機器の正確な元位置とは限らず、モデル格子対近隣観測局の候補比較である。
- 2018年と2019年の6月1日UTC、**00:00/04:00/08:00/12:00/16:00/20:00**。年×3地点×6点=36回のBAW original GetFeatureInfoのみ。native20min time gridに合致する。結果で時刻・地点変更しない。元WMS Cap XML SHA 2018 386af7c9a75b66ef23017dfd49abe3afb71a530011e9f7bedbf3904281b7484f、2019 a52bf61de7bc50495ea75782a6e4bc5b4762ce3174e29a961cec1f697fe9b20aを全実行で再照合する。
- RWS各年×サイトの原48h WATHTE/cm/NAPを公式 DDAPI2 で取得（計6原 requests）、元+01時刻をUTCに変換しWMSの同UTCの元行だけ対応。**時間補間/モデルへの振幅・バイアス補正は一切学習しない**。
- WMS native GeoJSON FeatureCollection features 1 / props Wasserstand 1 / 数値型有限のみに限定。abs(v)>=1e6は極端NoData候補で有効扱いせず、abs(v)<=10のみplausible numeric **unit未確認**、それ以外未解決。原応答SHAは保存、生水位の36個リストは公開しない。
- RWS原元データがsite-year≥200、native units cmNAPならそのsite-year原SOURCEに限って検証。固定6UTCのWMSとRWS正確時刻でn≥3 pairedなら、WMSを仮にmNHN/NAPとみなした時の元値差のbias、MAE、RMSE、Pearson rを**記述統計**として出す。site-year n<3はNOT_EVALUABLE; no-matchesをゼロ埋めしない。全36 WMS sourceが取れなかった場合もその個数を出し、失敗したsite-yearを入れ替えない。
- Wadden hydro modelはRWSゲージで強制・校正された可能性があるので、元source比較結果が正でも**外的に独立な自然検証とは限らない**。小標本・潮位時間自己相関を考慮しp値やcausal ecologyは主張しない。

この段階は、モデル数値と現地RWS measured NAPの同時刻照合という**物理SOURCE整合性**であり、v205のモデル年別マスクと高潮/低潮線の共通処理ルール検証とは別系列。元20m Deltares DEM true survey date/native vertical datum、鳥元GPS地点のh(s,t)、15min干出・採餌・太陽×潮汐行動因果・社会BoidsはSOURCE STOPのまま。
