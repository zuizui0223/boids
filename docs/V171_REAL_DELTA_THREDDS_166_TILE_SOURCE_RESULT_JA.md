# v171 公式Deltares歴史地形NetCDFカタログ原本確認（SOURCE-only）

2026-11-17。v170で2016/2019元候補が**BorndiepでありVlielandのGPS対象地域を覆わない**SOURCE_STOPを確認。公開元Deltares THREDDSの[従来の公式vaklodingenカタログ](https://opendap.deltares.nl/thredds/catalog/opendap/rijkswaterstaat/vaklodingen/catalog.html)をXML原本として取得。元XML **53,134バイト**、SHA256 `40a4881f4dad432e7b52e88fcff000b51943b81b0e256a3b09f68cb25f04f277`、総167 XML dataset/catalogRefエントリ（うち元NetCDF path **166件**、1件は`catalog.nc`メタデータ索引）。

従来カタログは本物の公開原本から取得して[Actions #44003986026](https://github.com/zuizui0223/boids/actions/runs/44003986026) **SUCCESS**。別の提供先`vaklodingen_new/catalog.xml`は**HTTP 404 SOURCE_STOP**だったが、こちらを現在の未検証のDEMへ自動代用しなかった。

このXMLには**測量元の真の各地点／ピクセルのz測量年の数値は含まれない**ので、タイルの名前`KB...`だけで2016年Vlieland干潟の標高が利用可能だとは結論できない。次にカタログに掲載された**catalog.nc**の元NetCDF地理索引を実際に読み、x/y投影座標とタイルURLを1対1で照合して候補地を選ぶ。元2018/2019の鳥GPSを元NetCDFに対応できる保証はまだない。実測RWSの港湾水位や元GPS/ACC生データをGitHubには転載していない。

元SOURCE-safe XML SHAとデータセット名・URLパス集計を `validation_v171/results/official_historical_vlieland_tile_catalog_source_v171.json` に固定。`python validation_v171/thredds_tile_catalog_source.py --check`で正式元XMLを再取得して完全一致検証する。

**生物学的干潟アクセス・潮汐因果×太陽効果・社会的Boids力はNOT_ESTIMATED**。
