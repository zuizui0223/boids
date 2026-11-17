# v172：公式Deltares NetCDFタイル索引 catalog.nc の原本を開く

v170の2016・2019NetCDF候補はBorndiep/AmelandでありVlielandの鳥のGPSへ割り当てられずSOURCE STOP。v171では、歴史的データを収録する真正Deltares THREDDS XMLを取得し、**166個のNetCDFタイル**が掲載されていることを原XML SHA \`40a4881f4dad432e7b52e88fcff000b51943b81b0e256a3b09f68cb25f04f277\`で確認した。新しい別URLは404だが、2026-03に更新された従来の正式歴史カタログは存在する。

v172では、カタログ一覧に見つかる**catalog.nc（公開カタログ表示で約40.97KB）**を公式Deltares THREDDS fileServerから原バイナリで取り出し、バイトSHAとNetCDFの変数・次元・元属性を検証する。もしINDEXに各タイルの真のRD New EPSG:28992の座標範囲が存在すれば、Vlieland近傍（検索窓のみx120–150km,y575–615km）を覆うタイル候補を特定して次段で原DEMのz/time/isourceへ進める。

本SOURCEゲートでやらないこと：**2016年のタイムスタンプとVlielandの20m標高がすでに一致したと仮定しないこと**、現行2025/26のタイル最新時点のzを2018/19年の地形として流用しないこと、元GPS鳥個体ID／位置を出力すること。

SOURCE-onlyコード \`validation_v172/native_catalog_nc_geoindex.py\`は公式原catalog.ncの元SHAと寸法・属性を保存し、\`--check\`で完全再取得照合する。元DEMやGPSの生物学的効果・Boids社会力・潮汐×太陽の因果係数は未推定。
