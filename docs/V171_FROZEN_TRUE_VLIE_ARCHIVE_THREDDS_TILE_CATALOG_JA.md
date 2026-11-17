# v171 — 歴史的Vlieland干潟に対応する正しいDeltares Vaklodingenタイルの公式カタログSOURCE監査

2026年11月17日。2018学習→2019年のミヤコドリ行動予測v169では、実測RWS Vlieland Haven港潮位の「高さ」1項が自己履歴・太陽・時刻の後でもSOURCE予測MSEを減らした。ただし**鳥のGPS地点の干潟標高・実際の冠水**は未測定である。

## v170の重要なSOURCE STOP

Rijkswaterstaat/Deltares OpenEarthの真の公開アーカイブから\`20160912_vaklodingen.nc\`と\`20190712_vaklodingen.nc\`を直接取得・元バイトSHA照合した。前者の元データ名は\`_20160912_Borndiep16tt20.asc\`、後者は\`_20190712_Brndp19KG2tt.asc\`であり**Borndiep/Ameland周辺**のデータだった。2016元NetCDFはEPSG:28992のx **155,390–175,030m**、y **604,810–620,230m**、2019元NetCDFはx **155,390–175,350m**、y **602,190–620,070m**にあり、WGS84再投影でもVlielandの想定地域(東経約4.7–5.3°/北緯53.15–53.53°)を**覆わない**。従ってこの二ファイルを鳥の元GPSに割り当てて「干潟露出」を計算するのは**SOURCE STOP**。元の観測結果を得るために現代DEM等で穴埋めしない。

## 正しい元歴史的地形データの次候補

- [DeltaresのVaklodingen公式説明](https://publicwiki.deltares.nl/spaces/OET/pages/308413096/Dataset%2Bdocumentation%2BVaklodingen)は、20m格子のEPSG:28992形式の歴史的NetCDFが、NetCDFタイルごとにOPeNDAPから取得できることを説明。
- 公式インデックス\`https://opendap.deltares.nl/thredds/catalog/opendap/rijkswaterstaat/vaklodingen/catalog.xml\` および2020以降の新バージョン\`.../vaklodingen_new/catalog.xml\`の**XML自体**を初回SOURCE取得し、元SHA・URL・タイル名・source pathを出す。名前に\`KB\`等があっても、その名称だけでVlielandを覆うと決めず、必ず次段で実\`x/y\`属性・元\`z\`の\`time/isource\`・NAP垂直基準を検査する。
- 正しい地理の概念上の近傍はEPSG:28992でx約120,000〜150,000m、y約575,000〜615,000m。ただしこの値はVlielandの広域のメタデータ検索窓であって、鳥の個体別GPS原本座標ではない。実際の動物GPS元点のどれが標高セルに収まるかは別のSOURCE入場となる。
- 公開のWadden Sea統合地形は最新測量ピクセルを寄せ合わせるため、**2016年の名目データでも古い時代のピクセル**があり得る。また2018/2019より新しい2022/2025測量値を歴史的な鳥の行動地点へ遡って適用しない。

## 今回の分母・観測ゲート（生物学的結果の前に固定）

1. 二つの正式THREDDSカタログXMLを取得し、本物のHTTP応答を確認して元バイトSHA256を保存する。HTMLエラーページを真のカタログと誤認しない。
2. 公式元XMLの\`dataset\`、\`catalogRef\`だけを列挙し、元NetCDF URL path、候補名と数、2016/2019またはVlieを含む候補名をSOURCE-safeに保存する。
3. XMLがタイルの真の地理範囲・測量年・NAP/標高単位まで証明するとは主張しない。**次段で当該NetCDF原本の時代と有効測量画素を確認するまでSOURCE_STOP**。
4. 公式カタログのアクセスに失敗したらその状態を記録。都合のいい別のデータへ自動フォールバックして2018/19の干潟地形と誤認しない。
5. 個体別元GPS座標、元RWS実測水位・NetCDFの海底標高配列そのものはリポジトリへ転載しない。

**現段階での結論の上限**：Vlielandの正しい歴史的DEMタイル候補のSOURCEに進めるかどうか。干潟アクセスの物理機構、潮汐×太陽の因果効果、実個体間Boids社会力は未同定。

\`python -m unittest discover -s validation_v171 -p 'test_*.py' -v\` で合成THREDDS XMLのSOURCE名前/元内容判定を検証。
\`python validation_v171/thredds_tile_catalog_source.py --emit\` で正式カタログを取得し、元XMLのSHA＋候補リストを出す。取得できた本体を初回レシートに固定して\`--check\`で再計算する。
