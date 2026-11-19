# v207 真正原本結果｜2018/19年9月1日BAW WMS vs 原RWS measured NAPの別月照合

2026-11-19。v206の6月1日比較を見た後に独立した**9月1日の原データ値を開く前**に元3サイト×両年×6同UTC時刻の36 source requestsを固定。BAW official `sea_surface_height_2d_YEAR_NL` `Wasserstand` とRijkswaterstaat DDAPI2 `WATHTE cm NAP`を再取得し、site×year別の候補数値比較を行った。

- GitHub Actions [#44450157082](https://github.com/zuizui0223/boids/actions/runs/44450157082) SOURCE PASS・元WMS/RWS計36+6requests、全テストPASS。PR再実行 [#44450162527](https://github.com/zuizui0223/boids/actions/runs/44450162527)もsource-only workflow **SUCCESS**。元36 WMS HTTP・6 RWS site-year全source件数、NoData候補、6つの候補RMSE・Pearson値が2つのsource実行で完全一致。初期CIはユニットテスト期待日時が残存`June`のままだったことによるエラー（実source取得前に修正）。
- 前回v206 Jun1 site-year候補数値RMSEは5/6コホートがn≥3、0.05684〜0.09104（WMS数値mNHN/NAP**未証明の仮定**）。2019 Vlielandはn=2で不採用。
- Septemberの同源WMS36/36 HTTPソース成功、25/36 plausible numeric candidates、11/36 extreme NoData sentinel candidates。各native RWS original 48h=289件、完全同UTCでモデルの数値を対応させた。欠測時刻への補間はしていない。

| site-year | WMS plausible n/6 | extreme NoData候補 n/6 | 両方有効なexact-time n | Bias=model−RWS（m仮定） | MAE（m仮定） | RMSE（m仮定） | Pearson r (記述) |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2018 Vlieland Haven | 3 | 3 | 3 | +0.03000 | 0.06068 | **0.08126** | 0.99468 |
| 2018 West Terschelling | 3 | 3 | 3 | +0.01899 | 0.03337 | **0.03441** | 0.99846 |
| 2018 Wierumergronden | 6 | 0 | 6 | −0.00824 | 0.04172 | **0.04396** | 0.99799 |
| 2019 Vlieland Haven | 3 | 3 | 3 | +0.09938 | 0.09938 | **0.12174** | 0.98964 |
| 2019 West Terschelling | 4 | 2 | 4 | +0.04738 | 0.08855 | **0.09323** | 0.98802 |
| 2019 Wierumergronden | 6 | 0 | 6 | −0.07616 | 0.12277 | **0.15588** | 0.99939 |

**ソースの肯定結果**：6月に続く9月も固定3公表参照地点で、年別BAW WMS `Wasserstand`通常範囲の元数値は、同時刻RWS実測の振動に数値的に近く、同日6点の一部n=3〜6で大きな相関を示す。これは**本来の単位を仮定して**評価した物理的source一致に限る。9月2019 Wierumergronden RMSEは0.156mと6月より大きいケースもあり、地点/時期で誤差に違いがあることも保留せず出す。

**新規性の上限**：2025公表のレトロスペクティブBAW hindcastが2018/2019実測の一部にどれほど近いかのsource監査。RWSの同じゲージがBAWモデルの境界条件・校正などに使用されていれば、元RWSに合うことは独立な外部予測ではない。また2011 WEBTICS公表位置はnative RWS2018/19機器位置と同一点を証明しない。Native NetCDF元単位 `units`, `_FillValue`, native vertical NHN/NAP datumが未確認なので厳密なmNAP誤差の保証なし。小標本、共通潮汐周期、RWS測定機器歴史についての限界は継続。

モデルWMS 11/36 extreme NoDataは実水位が1e31mという意味ではなくsource欠測候補。元鳥GPS×15min ACC、真の局所`h(s,t)`, Deltares歴史20m DEM測量日/垂直datum、15min干潟アクセス、潮汐×太陽採餌の因果、社会Boidsは今回も**NOT_ESTIMATED / SOURCE STOP**。

v204/205の3地域BAW inter/supratidal地形SOURCE maskと年別水位境界の距離近接は、同一BAW製品内部のモデル処理の再現であり、実際の生息地消失の証明ではない。v206/v207を加えることで次段のモデル h(s,t) を使うSOURCE候補の現地NAP一致の可能性が具体化したが、個別鳥GPS地点の水位校正なしに実干出機構へ進むのは禁止。
