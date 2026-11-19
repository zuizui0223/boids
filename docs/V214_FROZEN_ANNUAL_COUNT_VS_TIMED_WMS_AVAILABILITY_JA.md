# v214 | 年別BAW`nof_valid_data_points`画素値の全分布と時刻別WMS可用性は同じ指標なのか（SOURCE ONLY）

v213の真正SOURCE SUCCESS 4実行中、固定WEBTICS2011公開3地点×各±500m 1km四方でnative20m WCS`nof_valid_data_points`2018/19年原TIFFの数値画素を認証した。元結果はVlieland Haven=1621/2500、West Terschelling=1283/2500、Wierumergronden=2500/2500が両年共通、**数値存在画素の中央値/5%-95%/最大は両年とも26281**。この26281は365×72+1と算術上一致するが、native年統計の観測端点が本当にそう数えられていることは証明されていない。年別count製品を直接「干潟冠水時間率」とみなさない。

## 事前凍結した真正SOURCE
- v213 source成功 [#44457416843](https://github.com/zuizui0223/boids/actions/runs/44457416843) と [#44457625436](https://github.com/zuizui0223/boids/actions/runs/44457625436) が完全一致。今回WCS原TIFF六本の`GetCoverage`元byte SHAを以下の固定レシートと照合し、**違えばデータを差し替えずSOURCE STOP**。
  - 2018 Vlieland `2788e1f14a4c13fe779f744126faf238a8b5bf7168e0b8267ec349b7949c1ceb`
  - 2019 Vlieland `2788e1f14a4c13fe779f744126faf238a8b5bf7168e0b8267ec349b7949c1ceb`
  - 2018 West Terschelling `e298f1c71672588a5b46f6a04392728c21ad58ce6b332190fe1c8ac4571ccffd`
  - 2019 West Terschelling `fafc08190faff51edb724c00e0ac7c9956038ad45d73ea000ecfc3a65d11d10d`
  - 2018/19 Wierumergronden `0814f98bf4599c652a9d0f5441ae625b92537f1c9beea510ecfcb96a0cc43755`
- v211/v212元GetCapabilities/DescribeCoverage SHA年別2組、source native `TrilaWatt_Hydrodynamik_YEAR__nof_valid_data_points_YEAR_nl`、EPSG25832、20m grid、原source exact公表RD3地点1km boundsとv213 source summaryの数値画素数と一致をすべて検証。元source時刻別20min WMS `sea_surface_height_2d`は**別製品・別解像度**である。
- v209 source original RWS×BAW WMS fixed 72 site-time from original successful GitHub Action #44452986729、原JSON SHA256 `5e4a492eae99e17b6f79444ac22a342ce5c88f570181fe44a8cc633b1932a62c` をGitHub Actionsから読むだけ。v210に実装したoriginal SHA+RWS native source receipts+WMS時刻/分類のソース一致検査を再使用し、**新たなBAW WMS時系列やRWS実測原時系列は取り直さない**。

## 固定する分析と結果判定
1. 年×3source：元WCS TIFF内の全有効count integerについて`n count==26281`, `n count<26281`, `n count>26281`, `n count==0`, 最小値、最大値、distinct count values総数（原値ヒストグラムを公表しすぎず、最大20種類まで）をSOURCE-safeに集計。もし26281より少ない有効画素がごく少数ある場合も、中央値のみから「全年全画素ずっと有効」と過大主張しない。
2. 各公表reference地点を本当の20m GeoTIFF pixel row/colへ対応させ、**nearest native containing pixel**の`has_native_annual_valid_count`と当該count値（1値）を記録。中心がmaskedならNone。これは**実鳥GPS位置ではない**。
3. 年2本のsource TIFFは同一EPSG25832グリッドにあるときのみ、年別有効マスクが完全一致するか・countの有効共通画素が2018→2019で変化した数と割合を記録。年次の原モデル実測や自然侵食を推定しない。
4. v209 source-safe72モデル回答から、各公表地点の既知June/Sept・2018/19・毎6UTCの`WMS numeric candidates fraction`を計算。SOURCE母集団は固定 **各サイト24時刻**。Vlieland 11/24、West Terschelling 15/24、Wierumergronden24/24 と元sourceから再計算・確認する（値をハードコードしてsourceを偽造しない）。
5. 3地点×2年について、**WCS年別1km範囲でcount値がある画素の割合 vs WMS公開参照点24時刻のsource numeric割合**を併記する。これらの分母は「空間画素2500」と「時間24」で異なるため、相関・回帰・p-value/因果・年次inundation probabilityへ変換しない。両者の大小や並びが異なっても**別製品の可用性の次元が違う**事例として報告。
6. 元GeoTIFFはrunner RAMだけに保存、元native count histogram上限20、中心pixel値とSHAと集計だけをGitHubに収録。ソースエラー時はSOURCE STOP。例外に応じてROIを別地域に変更したり有効cellだけ恣意的に選択しない。

## 新たに支持できること／依然STOP
支持可能：BAWの年統計製品内、年別`nof_valid_data_points`layerにおける元画素値分布および空間欠損パターン、時刻別source model WMS欠測の別次元の可用性との定量的相違。

支持不可：native raw WMS 1e31が正式`_FillValue`、原20min WMSの欠測原因がdry-cell、元年間count26281を元時間分母とした乾出時間率、同一点の独立現地観測、ミヤコドリ実GPS・ACCの局所水位や社会Boids作用、潮汐×太陽の因果。v169のRWS港湾潮位によるACC年外条件付き予測は今回も保持する。

v214はv213の確実なSOURCE-positiveとは分けた**原データの追加QAと事後的な2製品の比較**で、mainへ未検証のメカニズムとしてマージしない。
