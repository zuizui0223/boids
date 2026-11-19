# v210 | BAWモデルNoData候補を除くと残りのRWS実測潮位はどれだけ高く偏るか（v209真正SOURCEレシートだけ）

v209は**事後的・探索的**ながらBAW original WMSの約1e31 NoData候補が元RWS実測の低潮位側に8/8沿岸site-year-monthグループで集中（平均差`sentinel−plausible`のgroup-median−1.21mNAP）と報告した。**解析前に固定するv210の目的**は、生original WMS/RWS水位をもう一度取得せず、v209の**2つのSHA固定したsource-safe JSON**だけから、`WMS数値が得られた行だけ残す`という処理が元RWS実測潮位の平均をどれだけ変えるかを数学的に算出すること。

## Source固定
- source success GitHub Actions run **#44452986729**、original artifact名`v209-BAW-WMS-original-NoData-vs-RWS-2018-2019-June-September-lowtide-source`の元JSON原SHA256 `5e4a492eae99e17b6f79444ac22a342ce5c88f570181fe44a8cc633b1932a62c`。
- source success GitHub Actions run **#44453025281**、同アーティファクトでoriginal JSON原SHA256 `be0d2200f5520a6fe5d670d4b3f856427b1a0b880ea9616b5cc374cfb87d04a9`。
- 両者のsource原RWS publisher response SHAは12/12一致し、original BAW WMSの72個のraw HTTP SHAは一つも一致しない（生GeoJSONの動的時刻等のメタデータが原因である可能性あり。ただし原因は特定していない）。**RWS水位のグループ平均差、12元グループclass counts、72個source WMS plausible/sentinel class、元6UTC time列は両実行で完全一致**していることをv210で独立検証する。SHAの片方が変わるとSTOPし、別実行/ネット取得で元レシートを入れ替えない。
- GitHub Actionsで`gh run download`のみ、オリジナルRWS/DDAPI2やBAW WMSへのHTTP source要求禁止。原生水位・bird GPS/ACC/DEMは絶対に再取得しない。

## 数学的な固定推定量
一つのsite-year-monthコホートの原6時刻にRWS元実測潮位 `h_i` (mNAP) がある。BAW WMSモデル`Wasserstand`が plausible source numeric である時刻を`O=1`、極端NoData候補を`O=0`とする。`n_v+n_s=6`。v209の元SOURCE集計から`d=mean(h|O=0)-mean(h|O=1)`を保存してある。

**BAW WMS有効候補行だけを使った元RWS水位の平均上方選択差**を厳密に
[
Delta_{m selection} = {m mean}(hmid O=1)-{m mean}(h)
= -rac{n_s}{n_s+n_v}left({m mean}(hmid O=0)-{m mean}(hmid O=1)ight)
= -rac{n_s}{6}d
]
とする。両種類それぞれ元2時刻以上の8沿岸コホートを主対象とし、NoData候補が0のWierumergronden4群は**コントロールの選択差=0**（当然・数式的）とする。12群の`site-year-month`を同じ重みで平均/中央値算出する。8沿岸群も同じ重みで別集計。**全72の全観測を一括プールし「選択後50点の実測平均−元72点の平均」と称しない**（group間のmean hが異なり、元集計ではrecover不可）。これは原本から数学的に証明できるgroup内差のみ。
- 8グループ全てで`Δ_selection>0`、中央値>0なら、BAW model valid-only SOURCE表に残る実測潮位が**各グループで高く選択されている**とSOURCE-safeな算術結果として報告。これは新規独立統計検定ではなく、v209の差を別の定義に変換したもの。p値・独立性・生態学的因果なし。
- 元site-groupの`n_s`、`n_v`、`n_paired=6`は真のv209出典と照合、native RWS response SHA256 source code/時刻一致、72個WMS source class一致を要求。結果をよくするためのreweightingや site選択をしない。
- 元BAW`Wasserstand` raw unit / native`_FillValue`が1e31である確証は未取得。今回の`Δ`の単位は**RWS観測 mNAP**なのでモデル値の単位未確認でも算術的なSOURCE選択差を解釈できるが、`O=0`が実地形の乾出かどうかは判定しない。
- 欠測分類でWierumergronden源が全0 NoDataなのもmodel productのlocal behaviorであって恒常的な実験的水没証明ではない。

## 物理・生態学的意味
この解析は**低潮位の条件に応じてBAWモデルWMSの値が欠測しやすい結果、valid-only選択がどれだけ潮位分布を高い方に寄せるか**を具体化し、将来のGPS局所`h(s,t)`や鳥15分ACC予測が`drop_missing`によって干潮期を落とすリスクを示す。v169の既存鳥ACC予測は真正RWS measured harbor高さを使っており、**その既存推定がこのWMS欠測で直接汚染されたとは言えない**。

BAWモデル原著(2025) NHN≈NAPという製品level vertical reference・FES/Helgoland/Roscoff observed boundary forcing・2019 ICON-EU切替はv208で確認。native `_FillValue`と鳥GPS実地点のモデル地形水深/採餌因果/社会Boidsは別SOURCE STOPのまま。
