# v193 | TrilaWatt 2018/2019年オランダ・ワッデン海500m/20min水位場：真正出典・ファイルメタデータの監査（SOURCE ONLY）

**v192否定的幾何予測結果後の独立SOURCE候補探索。** これは元のRWS局ごとの位相遅延v190が通信停止したことを陽性とみなす代替ではない。2025年公表の事後モデル（hindcast）を、2018年/2019年の「当時入手できた未来予測」と呼ばない。

## 公開元資料・固定する真正SOURCE
- Lepper, Reinert, Gundlach, Weber & Kösters (2025) *A hydrographic dataset of the Wadden Sea as a foundation for a digital twin of the coastal ocean*. *Scientific Data* 12, 1746. https://doi.org/10.1038/s41597-025-06211-1
- BAW公式データDOI: https://doi.org/10.48437/7ca5ef-2e1287
- BAW公式登録ID `40936F66-3DD8-43D0-99AE-7CA5EF2E1287`、公式項目 https://datenrepository.baw.de/trefferanzeige?docuuid=40936F66-3DD8-43D0-99AE-7CA5EF2E1287
- 公式ページに示された配布ディレクトリ候補（**ネットワークで実在を要確認**）: https://dl.datenrepository.baw.de/7000/B3955.02.04.70237/Hydrodynamik/
- 論文が述べる元ファイル仕様：2015–2022年、領域nl/ger/dk、グリッド約500m、20分刻み、各1年netCDF、`tides`区分、変数`sea_surface_height_2d`。出力座標EPSG:4326、時刻UTC、鉛直NHN（論文表現ではNAP相当）。**論文の説明は各元NetCDF変数の属性を取得して確かめるまでは原本データの性状の代替証明ではない**。
- 2018/2019年 `nl` 領域のtidesファイル **だけ**を対象。まだ元ファイル名・サイズ・ヘッダー・SHAを取得したと報告しない。公的説明の一般例 `tides_2020_ger.nc` からファイル名を捏造しない。

## v193の凍結ゲート
1. 公式配布ルートが正真正銘の`dl.datenrepository.baw.de`にあることをHTTPSの一覧HTMLから読む。最大階層2、最大25のSOURCEディレクトリ表示、各レスポンス最大0.8MB。発見できたファイル名/URIは返ってきたhrefそのまま（加工された未知のファイル名を生成しない）。
2. 2018・2019を含み、`tides`と`nl`を**原ファイル名から**判断できるnetCDF（.nc）それぞれ**唯一の原ファイル**を特定。重複・曖昧・欠落はSTOP。
3. 原ファイルの**HEADメタデータだけ**を取得（HTTP結果、`Content-Length`、`ETag`、`Last-Modified`、必要なら`Accept-Ranges`）。巨大なモデルラスターをダウンロードしない。HEAD未対応ならSOURCE未検証としてSTOP。
4. 2年分両方が確実に到達できた場合も、これは**原ファイルの存在とHTTPメタデータ**の合格だけ。後続v194で範囲読み取りやNetCDF座標・時間・水位単位/鉛直基準を真正数値で検証するまでは`h(s,t)`の局所予測禁止。
5. モデル水位とRWS元観測局の水位は独立性（モデルの同化/境界調整に局の元データが使われた可能性）を検証してから比較する。2年の年外生物行動への転移は retrospective environmental hindcast conditioning であり、未来データが予測時点ですでに存在したとは言わない。

## 解釈
対象日本語論文主張は**「潮汐と太陽条件が時間ニッチに影響する仕組み」**。TrilaWattの2018/19物理場はGPS地点に `h_{model}(s,t)` を与える見込みがあるが、これは真正の現地観測水位ではない。20mの歴史地形 `z` と500mの水位を単純な差で局所実測冠水とみなさず、鉛直基準の厳密変換と地形の実測時点・変化誤差を先に解消する。先行WEBTICS(2011)も干潟潮位の補間とミヤコドリ生息地評価を既に実施しているため、単純な補間の新規性を謳わない。

原RWS水位/鳥GPS/ACC/生DEM・TrilaWattの巨大年次生モデルをGitHubには公開しない。v182のSOURCE_STOP_LOCAL_EXPOSUREが解除されるまでは生態効果を新推定しない。
