# v207 | 6月v206を見た後に凍結する2018/19年9月1日BAW WMS vs RWS original source out-month検証

**v206の6月1日のSOURCE数値比較を閲覧した後、v207の9月1日の元観測実値を開く前に指定した事後・探索的な別月再現**。未開封の確認的な外部バリデーションではない。公開BAW hindcastは2025年に公表されたレトロスペクティブな2018/19モデルであり、2018年時点の未来予測ではない。

1. 同じ3サイト `VlielandHaven` (RWS `vlieland.haven`, WEBTICS RD 135280,590000)、`WestTerschelling` (RWS `terschelling.west`, RD 143870,597420)、`Wierumergronden` (RWS `wierumergronden`, RD 192882,614562)。2011 reference RDは2018/19 native RWS機器の実正確位置ではない。
2. **2018年と2019年の各9月1日**、元時刻UTC **00/04/08/12/16/20時の6時刻**のみ、3サイト×2年=**36固定BAW WMS GetFeatureInfo**。年ごと原WMS `sea_surface_height_2d_YEAR_NL`、cap SHA 2018 `386af7c9a75b66ef23017dfd49abe3afb71a530011e9f7bedbf3904281b7484f`、2019 `a52bf61de7bc50495ea75782a6e4bc5b4762ce3174e29a961cec1f697fe9b20a`。WMS1.3 EPSG4326 lat-lon軸順とINFO_FORMAT application/jsonを厳格維持。
3. RWS公式DDAPI2に各site-yearの元 **9月1日00+01〜9月3日00+01** の48h WATHTE/cmNAPを要求し、元UTC+01時刻をUTCへ正規化し、WMS同UTC exact timestampにだけ対応。年ごと/siteごとのRWS genuine n≥200が必要。時間内挿やモデル係数補正禁止。
4. 元v206と完全同じ `FeatureCollection features=1, properties={"Wasserstand": numeric}` SOURCEゲート。abs(raw)>=1e6→extreme NoData候補で除外、abs(raw)<=10→model plausible numeric source candidate (元native unit/mNAP未確認)、それ以外不採用。native WMS/RWS原SHA・site-yearのNoData率・n exact pairsを全件報告。
5. 固定6site-yearの各n exact numeric matched≥3でのみ、**model numeric WasserstandがmNHN/NAPという未証明の仮定**の下でbias/MAE/RMSE、Pearson記述値を計算。2018/19の9月同地点で閾値を変えず、scoreできないコホートはNOT_EVALUABLE。全36モデルSOURCE HTTP成功/6元RWS測定SOURCEが揃わないとsource総合STOPにするが、部分ソース情報は失敗も残す。
6. v206 June実測は5/6 site-year evaluable、3〜6点ずつの候補RMSE 0.05684〜0.09104m、native model unit/vertical datum未確認。v207は**別月のsource数値整合性の記述的再現**を見る。6月結果に合わせた係数を9月へ適用しない（そもそも元モデルに何も学習していない）。モデルがRWS局を校正に利用していた可能性、native source元WMS `_FillValue`未確認、2011 reference pointと2019実機器位置の不一致は残る。
7. 原RWS時系列、BAW水位の個別36個、元鳥GPS/ACC・地形sourceをGitHub artifactへ出さず、site-year aggregate/response SHAのみ。これは独立生物種または環境のマクロメタ解析ではない。局所干出/採餌/太陽×潮汐/群れBoidsは引き続きSOURCE STOP。

v206の実測SOURCE結果 docs/V206_TRUE_ORIGINAL_BAW_WASSERSTAND_RWS_NAP_RESULT_JA.md は変更・上書きせず、9月の結果を別版として記録する。
