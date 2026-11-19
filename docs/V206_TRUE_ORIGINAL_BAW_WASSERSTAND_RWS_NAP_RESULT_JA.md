# v206 真正原本結果｜BAW WMS Wasserstand vs RWS cmNAP同時刻12時刻×3地点（SOURCE only）

2026-11-19。原BAW official WMS year-NL GetFeatureInfoと、Rijkswaterstaat DDAPI2 WATHTE measured cm NAPを、固定3公開参照地点 × 2018/19年 × 6固定UTC時刻（00,04,08,12,16,20）で、元のまま同時刻照合。2011WEBTICS公表参照位置と2018/19 nativeセンサーの厳密な同一位置、元WMS GeoJSONの単位・縦基準は未確認であるため、**仮にモデル数値をmNHN/NAPとみなした場合の数値整合性**に留める。

## 真正SOURCE再現
- 初回GitHub Actions [#44449209772](https://github.com/zuizui0223/boids/actions/runs/44449209772) / PR実行 [#44449247210](https://github.com/zuizui0223/boids/actions/runs/44449247210) ともに全source取得と全CIテスト成功、以下の6site-year元SOURCE数値一致。
- 各site-yearのRWS native48hは**289点の元WATHTE/cmNAP/UTC+1**を使用。各年3局×6时点のWMS original source合計**36/36件HTTP成功**。通常範囲の数値候補合計25/36、abs(value)≥1e6のextreme NoData sentinel candidate計11/36。異常値を0や物理水位として代用しなかった。
- モデルの年別元WMS Capabilitiesはv194/v195 pinned original SHA 2018 `386af7c9a75b66ef23017dfd49abe3afb71a530011e9f7bedbf3904281b7484f`、2019 `a52bf61de7bc50495ea75782a6e4bc5b4762ce3174e29a961cec1f697fe9b20a`、original 2018/2019 NL water surface height layers、WMS1.3 EPSG4326 lat-lon BBOX、元native source RWS codesすべて再認証。

## 固定6 site-yearの候補数値と同UTC実測の一致（**unit仮定**）

| 場所・年 | Model plausible / 6 | 極端NoData候補 / 6 | exact-time n | bias (model−RWS、m仮定) | MAE (m仮定) | RMSE (m仮定) | Pearson r (記述) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Vlieland Haven 2018 | 3 | 3 | 3 | +0.08798 | 0.08798 | **0.08881** | 0.99975 |
| West Terschelling 2018 | 4 | 2 | 4 | +0.09035 | 0.09035 | **0.09104** | 0.99939 |
| Wierumergronden 2018 | 6 | 0 | 6 | −0.01460 | 0.05178 | **0.06608** | 0.99973 |
| Vlieland Haven 2019 | 2 | 4 | 2 | **NOT_EVALUABLE（n<3）** | — | — | — |
| West Terschelling 2019 | 4 | 2 | 4 | +0.01049 | 0.05454 | **0.05684** | 0.99350 |
| Wierumergronden 2019 | 6 | 0 | 6 | −0.03842 | 0.06222 | **0.08095** | 0.99803 |

**肯定的SOURCE知見**：native`Wasserstand`が極端なsource sentinelでないケースでは、同じ時刻の原RWS cmNAP観測に近い数値的な水位変動を再現しており、5の採用site-yearの候補RMSEは0.0568〜0.0910（WMSの数字をメートルとして読む仮定）。2019 Vlielandはn=2で数値スコアを不採用。原RWS48hデータの取得失敗は0。

## ここから言えないこと
- 各site-yearの有効な照合値はわずか3〜6点、時刻のばらつき・標本偏り・潮位の強い自己相関があり、Pearson r>0.99を**独立性や普遍的な精度の証明とみなさない**。
- BAW公開2025モデルがRWSの観測を境界条件・校正/同化等に使っていた場合、この現地水位との一致は完全に独立した外部テストではない。実際に用いられたmodel forcing/validation station listをまだSOURCEで確認していない。
- 2011年WEBTICS公開RWS地点RD参照位置は2018/19実際のRWS機器元座標とは厳密に一致していない可能性あり（v186 RWS catalogue X/Y null）。
- WMS GeoJSON `Wasserstand`の元NetCDF `units`/`_FillValue`/`vertical_datum`は未確認。論文level NHN=N​​AP相当という公開説明のみでは原数値の完全な地理校正とはみなせない。今回の11 extreme candidatesはnative fillの真の同定ではない。
- **v204/v205**のモデルの年次地形マスク変化が高低水位線の100m以内に98.7%程度集中する結果は**同一BAWモデル内部のsource processing pattern**。それ自体とv206の現地ゲージ数値照合を合わせても、原鳥GPS地点の15min局所水位/干出/採餌成功や、潮位×太陽の生物学的因果、social Boids forces はまだ未推定。元20m Deltares地形のfield survey-day/datumもSOURCE STOP継続。

次は**新しい日付・月を固定した追加のBAW/RWS同時刻比較**で、この候補整合性が異なる潮位期にも残るか、欠測候補が海岸側のsource条件でどう増減するかを確かめる。物理から生物への橋渡しは、元WMS単位・真のGPS地点h(s,t)・旧DEM基準を検証して初めて行う。
