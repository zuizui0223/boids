# v209 真正原SOURCE結果｜WMS NoData候補と実測RWS低潮位の対応

2026-11-19、v206 Juneとv207 Septemberの**元source既知72時刻**から、2018/19年×June/September×固定3公表参照観測所の72本のBAW WMS GeoJSON `Wasserstand`を再取得。RWS DDAPI2真正元12個site-year-month 48h (`WATHTE cm NAP`) の同じUTC時刻を必ず1対1対応させ、**モデルNoData候補の時刻には、実測水位が低いか**を事前固定source条件で比較。

### 原本出典と再現
- GitHub Actions [#44452986729](https://github.com/zuizui0223/boids/actions/runs/44452986729)、[#44453025281](https://github.com/zuizui0223/boids/actions/runs/44453025281) ともに**12/12コホート完全SOURCE PASS、全unit tests PASS、データ集計が完全一致**。生72個のBAW潮位数値とRWS測定72個をGitHubに一切保存しない。各WMS応答と元RWS provider responseにはSHA256元レシートがつく。
- 原GitHub source-safe ZIP SHA256 first `030feef85125f2e5cd25558928e47f810358a8dc7853988e49f6f7124d85b341`、second `4837dcca293654cdc731931b48e39833d75eebc15da66c82b0e6068eb97ce2d9`。中身の元集計JSON SHA256 first `5e4a492eae99e17b6f79444ac22a342ce5c88f570181fe44a8cc633b1932a62c`、second `be0d2200f5520a6fe5d670d4b3f856427b1a0b880ea9616b5cc374cfb87d04a9`。
- 独立Github2runで各site/year/monthの元RWS 48h真正source response SHAは**12/12一致**。BAW WMS個々HTTP raw response SHAは**72/72一致せず**（WMS GeoJSON response側に動的要素があることと整合するが、正確な元変動原因は未検証）。それにもかかわらず**72件のWMS巨大値候補vs通常候補、12組の原実測水位平均差、8/8の方向の判定は完全一致**。元HTTP byte SHAを「必ず値が変わった」と誤解しない。

### SOURCEの本検証
モデルWMS応答は72/72HTTP成功、元`Wasserstand`通常範囲候補 50/72、約1e31のextreme NoData sentinel候補22/72。WierumergrondenではJune/Sept×2018/19の全4グループで6/6通常値、0 sentinel = 対照グループであり、**常に冠水・乾いていないことの物理証明ではない**。

| original RWS site-year-month | NoData候補n / 6 | 通常候補n / 6 | RWS実測 `mean(h|sentinel)−mean(h|plausible)` (m NAP) |
|---|---:|---:|---:|
| 2018 June Vlieland Haven | 3 | 3 | **−1.17667** |
| 2018 June West Terschelling | 2 | 4 | **−1.46500** |
| 2019 June Vlieland Haven | 4 | 2 | **−0.94500** |
| 2019 June West Terschelling | 2 | 4 | **−1.35250** |
| 2018 September Vlieland Haven | 3 | 3 | **−0.98000** |
| 2018 September West Terschelling | 3 | 3 | **−0.93667** |
| 2019 September Vlieland Haven | 3 | 3 | **−1.24333** |
| 2019 September West Terschelling | 2 | 4 | **−1.47500** |

8/8の沿岸sourceグループ（各モデル候補2件以上×2カテゴリ）で、NoData候補が返る時刻の方が真正RWS cmNAP測定潮位が低い。**グループ等重みの水位差の中央値−1.21 m NAP**、凍結済み条件「8組中≥7かつ差の中央値<0」をPASS。全72の実測時刻を独立試行とみなさず、p値は出さない。

### 重要な数学的帰結と機構のSTOP

**model応答の欠測は潮汐位相/水位に強く依存する可能性があり、これを除外して推定するなら、低潮時のサンプルが系統的に抜ける危険がある。** その場合、予測対象の実測水位分布にも選択バイアスがある。次v210では元sourceレシートだけから「候補欠測除外→RWS実測潮位の平均選択上方偏り」を算術的に算出する（新しい元水位や個体データは開かない）。

未確定：元NetCDF`_FillValue`が本当に`9.999999848243207E30`か、真のdry cellによるnullなのか、BAW WMS `Wasserstand`のraw meter unit/vertical datum・元RWS sensor測地位置と同じか。BAWの2025原著は製品NHN≃NAPと境界の観測依存/FES2014b/2019 ICON-EU変更を説明する（v208）。低潮時のWMS異常値は**独立のGPSセルの物理乾出、鳥ACCの低潮行動、潮汐×日照因果・社会Boidsの機構の証明ではない**。

注意：元v169はBAW WMSではなく**真正RWS Vlieland Haven測定潮位**を利用したconditional ACC予測。v209のBAW WMS欠測はv169の結果を事後に無効化するものではなく、次にBAWモデル水位を実GPSセルへ結合する場合のSOURCE欠測リスクである。
