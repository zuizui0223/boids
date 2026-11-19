# v197 | 2018/2019原WMS WasserstandのNoData候補を独立SOURCE監査（24件・SITE×TIME固定）

## 前段と固定
v195の元GetFeatureInfo実測は2018年6月1日12:00 UTCが3/3とも有限、2019年同時刻は3/3レスポンスに`Wasserstand`数値があり、うちVlieland HavenとWest Terschellingで`9.999999848243207E30`、Wierumergrondenで`−0.9412793517`が返された。WMSから値が返ることと有効な潮位があることを区別する。約1e31は欠測またはnodata sentinel候補と推測するが、この数字とNetCDF原`_FillValue`はまだ照合できていない。

検証を実施する前に、公開2011年WEBTICS原RD参照位置の**同じ3地点**と、2018/2019年それぞれ**6月1日 00:00, 06:00, 12:00, 18:00 UTC**の固定4時刻、計**24点**を定める。場所も時刻も結果によって追加・削除・移動しない。元観測機器の2018/2019位置、GPS鳥の位置であると断言しない。

同じ元BAW WMS 1.3.0 original XML SHA 2018 `386af7c9a75b66ef23017dfd49abe3afb71a530011e9f7bedbf3904281b7484f` / 2019 `a52bf61de7bc50495ea75782a6e4bc5b4762ce3174e29a961cec1f697fe9b20a` を**再照合必須**。元レイヤー`sea_surface_height_2d_2018_NL`/`2019_NL`、`WMS1.3.0`、`EPSG:4326`緯度経度軸順、2011RD→WGS84変換、`GetFeatureInfo` JSON応答を固定し、URLと時刻を後から変えない。HTTPS公開BAW `coast.baw.de`のみ、標準CA検証有効。

## 元JSON応答の分類（元の型を必ず先に確認）
1. 元`FeatureCollection`で`features`ちょうど1、`properties.Wasserstand`ちょうど1つ、原JSON数値型/finiteのみ。非数値や欠測は無条件でNO_ADMISSION。
2. `abs(value) <= 10` を**plausible numeric candidate**（単位・NAPの同定ではなく単純な異常値排除）とし、`abs(value) >= 1e6` は`EXTREME_SENTINEL_CANDIDATE`（欠測の疑い）。その間は`OUTSIDE_PLAUSIBLE_UNRESOLVED`。`0.0`は真正な観測された「海面0」や「no water」を保証しない。
3. 全件元応答のHTTP/TLS/原SHA、原JSON構造、分類だけを公開。24件の元`Wasserstand`実値列、鳥GPS/ACC/DEM格子やRWS実測水位系列はGitHubに公開しない。年×地点別の4時刻のvalid/sentinel件数と範囲は報告可。
4. 欠測候補の数にかかわらず、これは**モデル水位Webサービス応答の可用性監査**であって、原NC `_FillValue`, `units`, `vertical_datum`, モデル独立RWS実測比較、地点ごとの真正干出は未認証。
5. 各年×地点の24HTTP成功がなければSOURCE_RESPONSE_INCOMPLETEを宣言し、取得できた部分だけで物理結果を称しない。HTTP成功でも年×地点で4件すべてが`EXTREME_SENTINEL_CANDIDATE`ならその局のモデル点水位は**0件**、干潟アクセスへ進めない。

TrilaWattは2025年公開のレトロスペクティブなhydrodynamic hindcastであり、2019年の実時間事前予報とは扱わない。文献 (Lepper et al. 2025, https://doi.org/10.1038/s41597-025-06211-1) は500m/20min、NHN (NAP相当)と記述するが、今回の数値がそのネイティブ単位に対応する証明には使わない。v182のDEM元z NAP/現地測量日/局所GPS干出SOURCE STOPは不変。
