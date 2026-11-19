# v209｜BAW `Wasserstand` 約1e31 NoData候補は、RWS実測の低潮位時刻に偏るか（SOURCE-only）

**事後・探索的source診断。** v206/v207の候補Model vs RWSの小標本数値一致を見た後で、**実際の元RWS水位をNoData/validに分けて開く前**に「モデルNoDataは低潮時に偏る」と仮説を固定する。これはRWS観測とBAWモデルのwater data quality診断であり、原GPS地点の冠水・鳥採餌・太陽×潮汐因果の実証ではない。

## 既存sourceで凍結済みの時刻・場所だけ
- v206 June1とv207 September1、**2018/2019それぞれ**、毎日UTC時刻 **00,04,08,12,16,20** の6時刻、固定3サイト `VlielandHaven` RWS `vlieland.haven`、`WestTerschelling` RWS `terschelling.west`、`Wierumergronden` RWS `wierumergronden`。合計**72 original WMS site-time** & **12 site-month-year RWS48h original datasets**。元WMS URLと2年の原WMS Cap XML SHA、WMS1.3 EPSG4326 axis/time/source classification及びRWS WATHTE cmNAP QCをv206/v207と**そのまま再使用**。新しい地点・時間へ変更しない。
- 已知Source WMS原 sentinel counts (元v206 June/v207 Septemberから、解析前に固定): June 2018 Vlie3,West2,Wier0; June2019 Vlie4,West2,Wier0; Sep2018 Vlie3,West3,Wier0; Sep2019 Vlie3,West2,Wier0。合計22極端sentinel候補/72、50 plausible numeric candidates。毎site-year-monthの本source countsが違ったらSOURCE STOP。Wierumergrondenは4グループとも6/6 plausible numericの**源negative-control site**として必ず報告。
- 元RWS各source48hは固定コード、RWS原`WATHTE cm NAP`、UTC+01で n≥200、本v206/7では元289時点。全72固定UTC時刻でモデル分類とRWS実測高さを**一対一に結合**。RWS高さの実数個別値、元WMS数値時系列をGitHubへ保存しない。

## 閲覧前の対比・判定
- 既存source `Wasserstand` GeoJSONが`abs(v)>=1e6`かつfinite numericの時のみ`EXTREME_NODATA_SENTINEL_CANDIDATE`として分類し、物理的水位には使わない。WMS`abs(v)<=10`は`PLAUSIBLE_NUMERIC_MODEL_RESPONSE_UNIT_NOT_VERIFIED`。それ以外・HTTP error・RWS exact UTC欠測→SOURCE STOP（一部のクラスを意図的に捨てない）。
- 各 site×year×month（12グループ）の **RWS実測メートルNAP**を、対応するWMS元source `sentinel` と`plausible`の二分類に分ける。source有効な2 groupそれぞれ n≥2なら、**実測RWS `mean(h_RWS_mNAP | sentinel)−mean(h_RWS_mNAP | plausible)`** (m)と median差を保存。負は「低い実測潮位でモデルの欠測候補が現れやすい」と整合的。n<2の一方は`NOT_EVALUABLE`（異常値が一度も出ないWierumergronden×4が代表）。ゼロで埋めたり、同月の別サイトのRWSで代替しない。
- 従属な8つの対象沿岸source group（Vlieland・West Terschelling ×2年×2月）が事前のcountsで全てn≥2なので全8グループを報告。SOURCE整合性だけの**固定記述的判定**：8グループ中≥7でRWS sentinel group meanがplausible group meanより低く、8グループの差の中央値が負なら`SOURCE_NO_DATA_LOW_TIDE_DIRECTIONALLY_REPEATED`、他なら`SOURCE_NO_DATA_LOW_TIDE_NOT_SUPPORTED`。**独立した8標本p値は出さない**。もともと潮位系列とサイトは同じ潮汐周期で共通相関するため。
- オプショナルネガティブコントロール：Wierumergronden 0/24 sentinel（source既知）、これは水域モデル値が全て常時有効な場所の可能性があるが実測water depth/地形は確証されておらず「常時水没」と断言しない。
- 未処理・元native`_FillValue`属性は**今回取得しない**。1e31がNoDataであることやその原因が干出であることの確証は次のnative original NC metadataゲート。数字分類と元実測水位の統計的対応だけを意味する。

## 生態学的な意味
BAWのWMS欠測候補が低潮時ほど多いと示せれば、潮汐×動物活動の予測で**欠測行を単純にdropすると低潮時のデータが選択的に消え、行動ニッチの推定に選択バイアスが生じる**という方法論リスクが具体化する。これは**鳥の実際の行動が低潮時に多いことの証明ではなく、低潮時のモデルの予測上のデータ可用性が低い可能性**を指す。

BAW 2025原著はNHN≈NAP製品levelの根拠を与える一方、数値`Wasserstand` native unit、原実RWS校正で3サイトが使われたか、2019気象強制のICON-EU切替えを v208で確認。これらの制約を越えて2018fit→2019bird行動因果・社会Boidsを主張しない。
