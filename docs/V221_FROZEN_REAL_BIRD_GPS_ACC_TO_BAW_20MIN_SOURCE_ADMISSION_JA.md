# v221｜実ミヤコドリGPS・ACCの2018/19年15分行動観測を、TrilaWatt 20分モデルの時空間軸へ結合できるか（SOURCE入場判定）

**v220の真正BAW時刻別水位Source Nil分類が3地点・2ヶ月・24/24でWMS分類と一致した結果を見た後、元生物学的な2018/19 GPS/ACC原コホートの環境データ結合に進むための事後的・探索的source gate。** 鳥のACC分類や潮汐の効果を結果に合わせて選別しない。モデル水位の`Nil`の真の物理原因/干潟湿乾をまだ確証できていないため、**この版は鳥GPS/ACCの源地理・時計がTrilaWatt native軸に入るか、何分ずれるかだけを測る**。WCS本体のGetCoverageも、個体の元生GPS/ACC座標も公開しない。

## 紛れなく真正sourceを固定
- 元2018年訓練用ミヤコドリGPS+ACC source cohort: Zenodo O_VLIELAND original source全193,088集計BIN、**前15分の同個体行動値が実観測された157,863行**だけを観測対象にする。元2019年holdoutは全155,387同源BINから、**先行同個体15分の実観測を持つ125,241行**を年全体の対象にする。これらはv168（2018で一度だけfit、2019全期間未学習テスト）、v169（RWS実測潮位高さの2019予測利得）、v177/v181（原GPS座標と歴史標高SOURCE対応）で独立source SHAと元観測同一性が検証された既存コホート。モデル予測Y値を開く前に対象行は固定されている。
- 実Zenodo GPS/ACCとRWS 2018/19 sourceのPublisher MD5/SHAを既存code `source_input_and_replay(v128,v129)`、`verified_2019_source(v126gps,v126rws,v127)`、`source_receipts_exact()`、`corrected_previous_bin`で再照合する。事前の元receipt artifactsは既存GitHub v168/v181の**同じ5 original source runs**のみをGH Actions downloadして使用：
  1. v128 run `43463270204` （2018 ACC/GPS）
  2. v129 run `43579877533` （2018 ACC forage+RWS+solar）
  3. v126 run `43220491868` のGPSとRWS source artifacts
  4. v127 run `43461048062` （2019 ACC+RWS+solar）
  すべて2026-11-17以前にsource-verifiedであり、元現在ACC行動YやGPS sampleの良い場所を選ぶための新規ダウンロード先に置き換えない。
- BAW真時刻別native WCS2 `TrilaWatt_ncHydro_2018__sea_surface_height_2d_2018_NL` と2019同名、source Cap original SHA2018 `7b439a8ad1af2fb1e341af5e7b4306535d134ed06d0315df99e2e5488f322388`,2019 `a124a47f4ba037f1403f60b52c8b02750308ee201a88f026c42721f664def37d`、元DescribeCoverage original SHA2018 `bf5976a6edd2365ff33b90bf0214042884e0d6d3fc9b3eb3dbb7c28a96245664`,2019 `9a0bd587debfaba85fd877c788273a18c5ae6ea57a8a9efdb88c344da6ec1e91`。BAW native `Lat Long time`, UTC 2018/19年全期間、水平source envelopeは同じ二年で **Lat52.8632601075–53.9411522296, Long4.17692049–7.3396245355**。原著後方計算model 20min interval（source V217の元WCS時間軸で確認）。元source範囲や20minを結果に応じて変更しない。

## 判定式と固定集計
1. 元GPS/ACCの各有効 previous-quarterhour 行について元`source_utc_event`（actual最初の ACC event の生UTC日時）・元`source_lon`,`source_lat`と`source_month`を使う。各年6・7・8・9月、日・夜の元source classのみ対象。**元GPS行動Yラベルの値や波の結果では、対象行を選択しない**。
2. Source geo-envelope入り判定は lat/lon **両軸とも元WCS native閉区間内**という単純なSOURCE geographic potential。境界内でもWCS水位値が有効か（Nilか）を示すものではない。個体GPS点の真の元格子`h(s,t)`もこの版では取得しない。
3. Source 20min model clockは年初UTC00:00から1,200秒格子とする。各元UTC event時刻`t`から、`k=floor((t−年初)/1200)`をsource **過去のmodel時刻**、`k+1`を未来のmodel時刻とする。**nearest**は残差が600秒以下なら過去、600秒超なら未来（正確な10min tieは過去へ）。観測イベント時刻がモデルの未来時点を参照する頻度を報告し、将来情報リークを見逃さない。
4. スナップ距離（絶対秒、≤600s）の固定区分：**≤60s, (60,300]s, (300,600]s**。モデル前時刻への遅延`lag_past∈[0,1200)`秒の平均、nearestに**未来時刻が必要な行数**、年・月・day/nightごとのsource位置範囲被覆・時刻距離をSOURCE-safeにまとめる。
5. 2018/19の元定義済み対象157863/125241行すべてが分類できること、元source GPS lon/latと日時が有限、同一source年6〜9月、元`private_bird`IDはRAMのみに保持して**個別GPS・元ACCラベル・鳥ID/ハッシュをGitHubへ一切公開しない**。aggregateで年別鳥数のみ記録できる。
6. native 2018/19`BAW source Cap/Describe` SHAが1byteでも違えばSOURCE STOP。元Zenodo/RWS live source MD5やpublisher SHAが違えばSOURCE STOP。結果を良くするための場所・年・月・太陽条件の恣意的フィルタを加えない。
7. 年外ACC予測は`2018fit→2019all`だが、WCS2モデルは**2025公開の過去再解析（hindcast）**であり、2018時点の2019年未来予測を提供していなかった。前ACC15分の真の行動historyがテスト時観測済みという条件付きの年外nowcast、真の従属関係の因果でないことを保持。
8. SOURCE集合が成立しても、この版には元BAW `GetCoverage`モデル実水位や元標高z値をjoinしない。**時刻別model Nilは低潮時に偏る**(v209/210)、真の鳥`source_utc_event`がmodel上Nilになる頻度を確かめるにはさらに大規模source time/position切り出しとGPS位置のnearest native格子確定が必要。

## 真の科学的帰結の上限
これで答えるのは「**実鳥GPS×ACCの元観測がhydrodynamic環境予測のnative地理的領域と20分のタイムステップに何割、どのようなずれで対応するか**」。これが結合可能なsource母集団の定義となり、将来の`O(s,t)`（観測/モデルのデータ可用性）と`Y(s,t)`（ACC行動）を分けて偏りを評価する準備をする。モデルのNilを干出・採餌不可へ変換したり、鳥GPSで直接の局所水深を測ったと主張しない。

次段真の生態学的な予測は、**元ミヤコドリGPSの空間・時刻×TrilaWatt model格子をsourceで一致させ、同じモデルNil選択で落ちるACC観測がday/night/tide phaseで偏るか**。その後に元DEM z native survey day/datum・実験的送餌条件を加え`P(forage|tide,sun,space)`の機構へ進む。社会Boids forceは今回測定しない。
