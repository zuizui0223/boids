# v172 実際のDeltares小型NetCDFの地理索引を原本から検証（完了）

2026-11-17。Rijkswaterstaat / Deltaresの公式THREDDSにある真正 \`catalog.nc\` を取得した。[原本CI #44004479770](https://github.com/zuizui0223/boids/actions/runs/44004479770) **SUCCESS**。

| 真正原本項目 | 確認した値 |
|---|---|
| NetCDF原ファイル | \`catalog.nc\` |
| 元バイト | **40,976** |
| 元SHA256 | \`b4364e1d18ea3098ccef8fcbd9a9f3506e98264748c0fe9ce80697a9cb9a2193\` |
| タイル索引の元行 | **165** |
| 元データセット一覧 | \`urlPath\` 165件（別のXMLカタログでは\`catalog.nc\`自身を含め166件） |
| 正規座標データ | \`projectionCoverage_x\`, \`projectionCoverage_y\`, それぞれ(165,2) |
| WGS84メタ地理 | \`geospatialCoverage_eastwest\`, \`geospatialCoverage_northsouth\` |
| 元タイム範囲 | \`timeCoverage\` (165,2), metadata \`days since 1970-01-01\` |
| カタログ公開作成日 | 2026-03-03（**元測量年ではない**） |

このNetCDFはタイル名だけでなく、元各タイルが投影座標でどこを覆い、全歴史地形データにどの時間範囲を記録するかを調べられる。重要なのは、**indexに2016年の収録があっても、2016年に測量した有効なz画素がVlieland鳥GPS地点にあるという証明ではない**こと。元のEPSG:28992座標範囲を先に絞った後、候補タイルの実z/time/isource・NAP垂直基準と元GPS観測地点との整合を次段で検証する。

前版v170はBorndiepの2016/2019元2ファイルがVlielandを地理的に覆わないことを確認してSOURCE_STOP済み。そのSTOPを維持し、元2018/19の鳥の位置、ACC行動源、元RWS潮位値、元DEM標高画素をGitHubへ転載しない。

結果SOURCE-safe JSONは \`validation_v172/results/original_deltares_vaklodingen_catalog_nc_v172.json\` に固定。 \`python validation_v172/native_catalog_nc_geoindex.py --check\` で元SHA・元NetCDF変数・寸法を再取得し、完全一致を要求する。

GPS地点の2016歴史的干潟z測量値、実際の干出・採餌可能面積：**NOT_YET_ESTIMATED**。Boids社会的相互作用・潮汐×太陽の因果的な生物学的効果：**NOT_IDENTIFIED**。
