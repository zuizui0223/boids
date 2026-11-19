# v221真正SOURCE結果｜ミヤコドリ原GPS/ACC 283,104行がBAW WCSの源Envelopeに入る一方、20分nearestに約半数未来参照リスク

2026-11-19。v168/v181元Zenodo＋RWS SHA-pinned原本を再取得し、2018/19の同個体previous-15min ACC観測を持つ**固定283,104 (2018 157,863; 2019 125,241) GPS+ACC source行**を、TrilaWatt 2025公開の2018/19時刻別水位native WCS source`Lat Long time`元Envelopeおよび20分源モデル時刻格子へ比較した。GPSや個体ACC反応・鳥ID・source UTC個別時刻をGitHubに含めず、元SOURCE cohort aggregateとSHA認証のみ保管。

## genuine source再現
- [Actions #44515363062](https://github.com/zuizui0223/boids/actions/runs/44515363062) と [#44515440082](https://github.com/zuizui0223/boids/actions/runs/44515440082) の**2回とも原source/全unittest PASS**、Zenodoタグ鳥GPS+ACCとRWS published original verified SHA、2018/19元BAW WCS Capabilities/DescribeCoverage SHAが再現。2018/19の元 source membershipおよび下記全年月/day/night集計一致。
- 元BAW年別水位WCS source Envelope（両年共通）**Lat 52.863260107482425–53.94115222955482、Long 4.176920490043966–7.3396245354662515**、axisLabels `Lat Long time`、元出力名`TrilaWatt_ncHydro_YEAR__sea_surface_height_2d_YEAR_NL`。あくまで**地理的外枠**の中に入る確率。
- 2018/19の実イベント時計は元GPS+ACC earliest event UTCをそのまま使用、標準20分カレンダー年初UTC00:00を元time grid knotに設定。`past=`時刻 `t`を超えない直前 knot、`nearest=`±10分の近い方（ちょうど10分は過去を選択）。WCSを近時刻へスナップすると「年外の未来モデル時刻」を使用する割合を隠してしまうため両方法を区別。

| 原source | 2018 | 2019 |
|---|---:|---:|
| 元15分直前ACC歴史付きGPS+ACC観測行（n） | 157,863 | 125,241 |
| 真の出現個体数 | 35 | 27 |
| native WCS原source **地理Envelope内** | 157,863 (**100%**) | 125,241 (**100%**) |
| 20分nearestが鳥イベント時刻より後の行 | **49.538524%** | **49.580409%** |
| 20分nearestの平均UTC絶対時差 | **299.933秒** (4.999分) | **299.486秒** (4.991分) |
| イベントより前の20分knotを使った時差平均 | **589.882秒** (9.831分) | **592.733秒** (9.879分) |
| nearest source lag ≤60秒 | 16,440 | 12,720 |
| nearest 60–300秒 | 63,361 | 50,693 |
| nearest 300–600秒 | 78,062 | 61,828 |

元2018月別 source GPS観測 n June25,214／July51,367／August55,022／September26,260、2019 June25,576／July34,658／August43,884／September21,123。元2018 day102,126/night55,737、2019 day81,408/night43,833。**元native clockと空間Envelopeへの適合判定はACC現在の採餌比率や水位効果を使った選択ではない**。

## source-only採用範囲
**肯定的に言えること**：実鳥GPS+ACCの2018/19 source cohort全283,104観測は、BAW source原地理的外枠に入る。未来の20分モデル knot 参照を禁止してオンライン条件付き推定をするなら、単純nearest採用では両年約半分が先の環境時刻を持ち込む。直前20分knotへ揃える方法の時間誤差は各年平均約9.8分。この点は15分ACC時刻×20分物理場という時間解像度の不一致のSOURCE証拠となる。

**まだ言えないこと**：外枠内の283,104元鳥GPSの全てでモデルsource`Wasserstand`がvalidであるとは限らない。v209/210の元model Nil候補はRWS実測低潮位に偏ると別SOURCEで検出され、v216–220で公式WCS generated NC4`_FillValue=9.999999848243207E30`とWMS Nil classの24/24一致を原sourceで確認した。GPSセルの`h(s,t)`、GPS時刻の公式Nil、実干出や採餌可能性を**本v221では一切結合していない**。

そこでv222 #245に事前固定pilot（年2018/19×月6～9の15日×UTC00/12・公表Vlieland周辺固定crop）を作成し、実GPS地点で**過去のsourceモデル20分knot**を参照する制限の下で初めてNil率を求める。ただし、v222実行中で結果がSOURCE成功するまで本ドキュメントにはv222のGPSモデルNil結果を掲載しない。

**科学的STOP**：BAW2025公表モデルは2018からのリアルタイム2019予報ではなく retrospective hindcast。v168/v169の2018-fit→2019-testは2019 previous ACCを使用可能なconditional nowcast。source coverageはタグ鳥活動の因果的メカニズムや昼夜・潮汐・社会Boidsパラメータを示さない。元20m Deltares DEMの測量日・NAP一致、実鳥GPS局所潮位、干潟アクセスと餌量は今後別sourceで校正する。
