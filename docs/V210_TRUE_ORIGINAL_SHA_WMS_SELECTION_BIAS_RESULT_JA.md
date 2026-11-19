# v210真正SOURCE・SHA固定オフライン結果｜BAW WMS欠測候補を除外するとRWS実測潮位が上方選択される

2026-11-19。v209真正原BAW WMS（source classify: 22 extreme ~1e31 NoData candidates / 72, 50 plausible numeric）とRWS真正源 measured WATHTE/cmNAPを対照させた2回のsource-success original Aggregatesから、**モデル通常応答行のみ残す**という処理で**元のRWS実測潮位の平均がどれだけ変わるかを数学的に計算**した。新規の原RWS API、BAW WMS、鳥GPS/ACC/DEMは取得していない。

## SHA-locked input evidence
- Source1 run #44452986729, original JSON SHA256 `5e4a492eae99e17b6f79444ac22a342ce5c88f570181fe44a8cc633b1932a62c`
- Source2 run #44453025281, original JSON SHA256 `be0d2200f5520a6fe5d670d4b3f856427b1a0b880ea9616b5cc374cfb87d04a9`
- 元v209再実行間の全12 original RWS provider-source raw SHAは一致、全72 original WMS exactUTC/classは一致、**WMS HTTP生JSON SHAは72/72不一致**。元response byte差からその原因を断定しない。出所誤りや分類変更を偽陽性にしないようv210は全固定source control合致時のみSOURCE PASS。
- v210 [GitHub Actions #44454060999](https://github.com/zuizui0223/boids/actions/runs/44454060999) と [#44454063880](https://github.com/zuizui0223/boids/actions/runs/44454063880) が**同じ元2つのv209 source-safe original artifactの厳密SHA・12 RWS出典・72 WMS類別を検証してSUCCESS**。初期テスト版のsource JSON key名が実元`original_fixed_UTC`と異なるエラーは結果を閲覧前に修正済みで、過去CIの失敗はソース改変ではない。

## 固定された算術的な推定量

元6時刻の真のRWS実測水位を`h` (mNAP)、BAW WMSの`Wasserstand`数値候補が返るとき`O=1`、extreme NoData候補となるとき`O=0`とする。v209に保存された`d=mean(h|O=0)-mean(h|O=1)`、元`n_s=n(O=0)`、元`n_v=n(O=1)`から**新しい実測生水位取得なしで**以下が厳密成立：

[
Delta = ar{h}_{O=1} - ar{h}_{mathrm{all six}} = -rac{n_s}{6}d.
]

この`Δ`は**source selection bias in RWS measured mNAP**, **not model Wasserstand bias**, model WMS `units`/NAPが未確認でもRWS自身の単位で意味を持つ。ただしBAW欠測候補がdry地形セル由来かは依然UNKNOWN。

| original group | source extreme NoData n/6 | `Δ` = WMS valid-onlyによる実測潮位上方選択差 (mNAP) |
|---|---:|---:|
| June2018 Vlieland Haven | 3 | +0.58833 |
| June2018 West Terschelling | 2 | +0.48833 |
| June2019 Vlieland Haven | 4 | +0.63000 |
| June2019 West Terschelling | 2 | +0.45083 |
| September2018 Vlieland Haven | 3 | +0.49000 |
| September2018 West Terschelling | 3 | +0.46833 |
| September2019 Vlieland Haven | 3 | +0.62167 |
| September2019 West Terschelling | 2 | +0.49167 |

**8/8沿岸グループで上方選択差 >0**。グループ等重みで平均 `+0.528645833m`、中央値 `+0.490833334m`。Wierumergrondenは4グループNoData n=0で算術的な選択差`0m`。12グループ等重み平均 `+0.352430556m`、中央値 `+0.478333334m`。

ここでの「等重み」はsite-year-monthグループを同じ重みで平均したもの。**72点のRWS全観測平均と50点に選別したRWSのプール平均の差ではない**。各グループの絶対RWS平均値はv209 source-safe JSONに保存していないため、全件プール後の差はこのaggregationから識別できず、新しい実測生水位を開かない方針を守る。

## ここで言える科学的結論とSTOP

**新しく具体化したsourceリスク：**BAW WMS近岸水位のextreme NoData候補が実際の低潮位時刻に強く集中するので、将来実鳥GPSセルにhydrodynamic mapをjoinし、観測可能WMS時刻だけでACC活動率を推定すると、低潮期の環境が過小収録され、見かけの環境・行動相関が変わる恐れがある。

**未確定の科学的な原因と範囲：**原NetCDFのnative `_FillValue`が1e31であるか、WMSのNoDataがdry cellか、2011公表位置と2018/19 RWS真測点の距離、実鳥GPS地点への外挿、元Deltares20m DEMの実測日/NAP鉛直基準、15min干出/採餌、潮汐×太陽/社会Boids個体行動メカニズム。これらは新たに証明されていない。BAW原著2025製品reference NHN~NAP、observed forcing、2019 ICON-EU切替はv208 primary-sourceで認められるが、モデルの原`Wasserstand`個別属性や校正局の詳細は未確認。

**既存v169保護：**v169の2018fit→2019testミヤコドリACCの追加実測港湾潮位のMSE改善は、**BAW WMSモデル出力ではなくRWS元Vlieland Haven measured water height**に基づく。今回のWMS源欠測はその既存推定を無効化するものではない。次の時空間モデルでは欠測`O`自体を物理環境に依存するSOURCE選択過程として分け、IPWや感度分析をする前に**真のGPSセル水位・元欠測因果・独立元NAP鉛直資料**を得る必要がある。
