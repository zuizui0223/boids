# v222｜実ミヤコドリ GPS/ACC観測地点におけるBAW水位NetCDF4のNilを、事前固定の16時空間断面で監査

**v221の正規SOURCE/CI成功結果を見た後、しかし今回の16枚の元BAWモデル小領域NetCDF4の値を開く前に固定した exploratory source-only pilot。** v221は2018年157,863／2019年125,241の原GPS＋ACC（元同個体previous15min観測あり）全283,104行が正式BAW WCS地理的Envelopeの中に入り、15min行動観測に最寄り20min時刻を対応させると**2018年49.538524%、2019年49.580409%が未来時刻**になると元SOURCEを二度確認した。今回は先行15分行動Y自体の値では観測行を選ばず、BAWモデル水位がGPS場所の過去時刻に実際に**数値を持つか／正式Nilか**のみを固定した小標本で調査する。

## 事前凍結した源source cohort／時間・場所
- 元2018訓練・2019未開封の真の後期行動ACCとの対応行：v168で2018`157863`／2019`125241`（元common source 193088／155387）。元正規Zenodo GPS/ACC+RWSを事前SHAチェックするAPIと出典5件は**v221の全く同じpublisher元コード**を使用。`source_input_and_replay`, `verified_2019_source`, `corrected_previous_bin`,`source_receipts_exact`は元v168/v221と同じ。Private bird ID / exact GPS / ACCラベルはActions RAMだけ。
- 1km等のROIはモデル上の独立公表参照点を用い、実鳥のGPS都合で選ばない。中心を**Vlieland HavenのWEBTICS2011公表RD(135280,590000)**→WGS84として、**Lat ±0.15°, Long ±0.25°**の固定矩形ROI。v217公式BAW native NL年次水位の水平source envelopeはLat52.86326–53.94115、Long4.17692–7.33962。このcropは元Grid約500m級の**高々10,000 pixels**以内に収まる予定。もしWCSが広いcropを拒否しても、矩形サイズ・地点を結果に合わせて変更せずSOURCE STOP。
- 年`2018`と`2019`、月は`June`(6),`July`(7),`August`(8),`September`(9)、**各月15日**、元モデル時刻UTC **00:00 と12:00**、両年合計`2×4×2=16`枚の小さな正式BAW WCS2`GetCoverage`、native`TrilaWatt_ncHydro_YEAR__sea_surface_height_2d_YEAR_NL`, format=`application/x-netcdf4`,`subset=Lat(min,max)`,`subset=Long(min,max)`, `subset=time("YYYY-MM-15THH:00:00.000Z")`のみ。
- **元鳥のイベント選択は事前固定**：各年×各月15日、00:00≤UTC event<00:20、および12:00≤UTC event<12:20。源`source_utc_event`は元15min ACC intervalのearliest real event timestamp。**環境値を行動時刻より未来から取らず**、各20分枠の先頭にあるモデル水位0:00または12:00を採用する。モデルは2025公開の2018/19 hindcastで、当時のリアルタイム予報ではない。これら元source時間窓の行動応答値・餌/日照の効果を解析しない。
- 今回の元行選択はACC陽性/採餌回数や水位状態によらず、**年・月・日・時刻・GPSが固定矩形に入るか**だけで行う。元モデルNilを見た後でGPS点/年/月/時間を追加・削除しない。ハード閾値で`n>=何件`を要求してデータ取得を誘導しない。
- year2018/19公式BAW年別WCS Caps SHA v216/v217と一致（2018 `7b439a8ad1af2fb1e341af5e7b4306535d134ed06d0315df99e2e5488f322388`、2019`a124a47f4ba037f1403f60b52c8b02750308ee201a88f026c42721f664def37d`）、native Describe SHA2018 `bf5976a6edd2365ff33b90bf0214042884e0d6d3fc9b3eb3dbb7c28a96245664`／2019 `9a0bd587debfaba85fd877c788273a18c5ae6ea57a8a9efdb88c344da6ec1e91`、`Lat Long time`, source`uom=m`, native OGC Nil `9.999999848243207E30`。
- WCS GetCoverageは真HTTPS/normal CA、source正規`coast.baw.de`のみ、redirect無し、original NetCDF4 HDF5署名、各8MB以下、元`time=1`, `lat`/`lon`1D、最大10,000元`time×lat×lon`grid pixels。float32 native`_FillValue`がOGC Nilに一致、`units=m`のときだけsource gridのNil/通常値分類を認める。
- 元鳥GPSの固定矩形に入るイベントだけを、一意にnative NetCDF4`lat`/`lon`の**最寄りモデルセル**へSOURCE-geometryで割り当てる。Native角距離が**各軸0.003°以下**のときだけ`MODEL_CELL_NEAREST_ADMITTED`、それ以外は`NEAREST_GRID_TOO_FAR`（都合の良い隣接セルや値のある近傍セルへ動かさない）。元モデル対象ROI外の元鳥GPSイベントは`OUTSIDE_FROZEN_VLIELAND_ROI`と明示して分母に残す。
- **Nil値はモデル水位がそこで得られないというSOURCE statusであって、その鳥が水上／干潟へ滞在したと断定しない**。すべての公表地理Envelope内でも水位はNilになりうる。源標高DEM zのdatum・field survey day、モデルNil=乾出、観測餌量・実ACC現在Y・太陽×潮汐、Boids社会forceは未推定。
- 16元source NetCDF4の`original response byte SHA`,native cropのsource numeric/Nil pixel数、選ばれた元鳥観測の総n、固定ROI内n、nearest accepted n、accepted中official Nil/numeric n、元source timestamp binに入る個体数（鳥ID出さずaggregate unique count）は、**年×月×0/12UTCの16群だけ**をレシートに保存。元鳥GPS/UTC/ACCラベル/individual IDs/hash・生モデル配列/生NC4バイナリ/RWS実潮位はGitHub artifactsへ一切保存しない。small nも否定的な結果として残し、n=0も0と明示。
- SOURCE PASS条件は**16枚の真正WCSが取得・認証できたこと＋両年の元283104GPS source row membership preserved＋16群全てのsource分類完了**だけ。モデルNilが多い／少ない等の方向・最低行数でsourceCIの成否を変えない。**同じBAWモデルの2018/19 retrospective slice**を使うため、これは真の独立物理現地調査でも予測モデルのテストでもない。

## 後続
元v222でNilのGPS条件付き「観測可能率」のpilot結果が再現した場合に限り、季節・day/night・潮位（RWS measured）と源Nilの関係を行動結果に触れずに検証する。そして原ACC`Y`を使うなら**2018年fit→2019年holdout**を保持し、源選択`O(s,t)`と源行動`Y(s,t)`を別の過程としてモデル化する。結果に合わせてモデルを変えない。
