# v173 本物のVlieland歴史DEM候補は10タイル：公式NetCDF索引の真正地理・年範囲から確定

2026-11-17。[Deltares公式 THREDDS NetCDF index](https://opendap.deltares.nl/thredds/fileServer/opendap/rijkswaterstaat/vaklodingen/catalog.nc) の元40,976バイト・SHA256 \`b4364e1d18ea3098ccef8fcbd9a9f3506e98264748c0fe9ce80697a9cb9a2193\`を再取得し、元\`projectionCoverage_x/y\`、\`geospatialCoverage_eastwest/northsouth\`、\`timeCoverage\`の**165行を1対1で対応**させた。初回[本物SOURCE Actions #44005165023](https://github.com/zuizui0223/boids/actions/runs/44005165023) **SUCCESS**。

## 交差した公式10タイル（原source URL・地理情報はSOURCE-safeレシートへ保存）

| タイルの場所（原ファイル名の最後） | 元RD New xの範囲 | 元RD New yの範囲 | 本研究の粗いVlieland窓との交差面積 |
|---|---|---|---:|
| KB123_1312 | 120,010–129,990 | 600,010–612,490 | 124.5504 km² |
| KB123_1514 | 120,010–129,990 | 587,510–599,990 | 124.5504 km² |
| KB123_1716 | 120,010–129,990 | 575,010–587,490 | 124.5504 km² |
| KB124_1312 | 130,010–139,990 | 600,010–612,490 | 124.5504 km² |
| KB124_1514 | 130,010–139,990 | 587,510–599,990 | 124.5504 km² |
| KB124_1716 | 130,010–139,990 | 575,010–587,490 | 124.5504 km² |
| KB125_1312 | 140,010–149,990 | 600,010–612,490 | 124.5504 km² |
| KB125_1514 | 140,010–149,990 | 587,510–599,990 | 124.5504 km² |
| KB125_1716 | 140,010–149,990 | 575,010–587,490 | 124.5504 km² |
| KB125_1110 | 140,010–149,990 | 612,510–624,990 | 24.8502 km² |

元10タイルは、いずれも**元カタログのtimeCoverage範囲には2016年を含む**が、実際に2016年に測量された元標高が各画素で利用可能なことは**全く確認できていない**。また、x=120,000–150,000、y=575,000–615,000mは原2018/19年の鳥の実GPS生息地範囲ではなく、10候補をSOURCE前選別するための大きな検索窓だけ。元タグ鳥が各タイル内にGPS記録を持つことも未検証である。

## v170から何が変わったか

元の最初の2016/2019年独立NetCDF2枚はBorndiepという別海域であり**SOURCE_STOP**。今回の10候補は、ただ2016のファイル名から拾ったのではなく、本当の元NetCDF座標インデックスを検証して地理的に絞り込んだ結果。次にこれらのnative tilesを実際に開き\`x/y/altitude/time/isource\`の元定義と元属性・2016年測量された有効セルの数を確認するまで、干潟露出や潮汐アクセスの効果を計算しない。

元SOURCE-safeレシートは \`validation_v173/results/genuine_vlieland_historical_tiles_shortlist_v173.json\`。元カタログをバイトSHA完全一致で再取得する\`python validation_v173/historical_vlieland_tile_shortlist.py --check\`により完全再現可能。

**GPSと標高の実際の結合、2016年地形からの冠水推定、野鳥行動への物理アクセス、潮汐×太陽の因果効果、個体間Boids力：NOT_ESTIMATED。**
