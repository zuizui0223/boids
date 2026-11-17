# v170 真正RWS歴史DEM原本結果：2016・2019の最初の2枚はVlielandではなくBorndiep。SOURCE STOP

2026-11-17。OpenEarth [Vaklodingenアーカイブ](https://rwsprojectarchief.openearth.nl/downloads/kustgenese2/bathymetrie/Vaklodingen/)から実元2016年、2019年NetCDFをバイト単位で取得・SHA256照合し、`EPSG:28992`として元x/yをWGS84へ変換。**ファイル名に2016・2019とあることをVlieland実GPSの地形と同一視しない**というSOURCEゲートを実行した。[GitHub Actions #44003764525](https://github.com/zuizui0223/boids/actions/runs/44003764525) **SUCCESS**。

| 元原本 | SHA256 | 実ファイルsource名 | 元RD Newのx,y標高範囲 | 元座標のWGS84範囲 | Vlielandの候補入場 |
|---|---|---|---|---|---|
| 20160912_vaklodingen.nc (3,052,812 bytes) | `e9b022c6a3976a920c4be5d1bdf6d67290fc8c3e4198b1ab520f325276b70cc7` | `_20160912_Borndiep16tt20.asc` | x155,390–175,030 / y604,810–620,230m | lon5.393–5.690 / lat53.429–53.568 | **STOP** |
| 20190712_vaklodingen.nc (3,594,788 bytes) | `9e6f902a3511495259f8f5cef06888d1724f78e3da58cd70c834432d5333c024` | `_20190712_Brndp19KG2tt.asc` | x155,390–175,350 / y602,190–620,070m | lon5.393–5.694 / lat53.406–53.567 | **STOP** |

両方のNetCDFの原metaはCRS`oblique_stereographic`、x/y投影座標、標高`altitude`（単位`m`）、元測量日には2016年9月12日〜10月31日／2019年7月12日が記載される。元標高内には有効な正/負数値があるが、**地理的にBorndiep/Amelandの別海域**。元ファイルはVlielandの粗い地域（lon4.7–5.3, lat53.15–53.53）とすら交差しない。よってこれらを2018/19年のミヤコドリGPSと結んで干潟露出モデルを作るのは禁止。

ここでの科学的成功は「2016年の地形データが存在する」という事実ではなく、**本当の原本の測量地点を検証して不適切なGIS結合を止めたこと**。実個体の干潟干出・餌アクセス・潮汐×太陽交互作用・Boids社会力の新規推定はまだしていない。

次のSOURCEは[公式Deltares OPeNDAP Vaklodingen歴史タイルカタログ](https://opendap.deltares.nl/thredds/catalog/opendap/rijkswaterstaat/vaklodingen/catalog.html)を原XMLから取得して本当のVlieland/Vliestroomを覆うEPSG:28992測量タイルを選ぶv171。特に今の2025/26最新地形を過去の2018/2019年GPSにそのまま当てない。元NetCDFは転載せず、SOURCE-safe元SHA/属性/地理範囲を`validation_v170/results/original_vlie_2016_2019_vaklodingen_source_gate.json`で固定。

再現`python validation_v170/historical_dem_source_gate.py --check`で公式元バイナリを再取得し、元SHA/内容/地理変換を完全一致で検査する。**GPS干潟アクセスと生態学的な効果：NOT_ESTIMATED**。
