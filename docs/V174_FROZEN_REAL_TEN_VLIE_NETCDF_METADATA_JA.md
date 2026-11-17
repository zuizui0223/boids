# v174：Vlieland周辺10枚の真正歴史NetCDFタイルを実際に開くためのOPeNDAP原メタデータ監査

2026-11-17。v173ではDeltares公式の元NetCDF \`catalog.nc\` の165個の\`x/y/WGS84/timeCoverage\`と真のタイルURLを突き合わせ、Vlielandの大まかなEPSG:28992検索窓（x120–150km, y575–615km）と地理的に交差する**10枚の元歴史地形NetCDF**へ絞った。全10タイルはカタログのtimeCoverage期間に2016年を含むが、**各画素の2016年測量が存在するとは保証しない**。元レシートSHAは\`b4364e1d18ea3098ccef8fcbd9a9f3506e98264748c0fe9ce80697a9cb9a2193\`。

## 今回のSOURCEだけの検証

10タイルの元のOPeNDAP実URLへ\`DDS\`（型、変数、原time/y/x配列の次元）と\`DAS\`（元メタデータの単位・EPSG・NAP/vertical datum・元source記録）を個別に取得。**本物の\`Dataset {...}\` / \`Attributes {...}\`形式**を要求し、HTTP200のHTML偽ページを元NetCDFと誤認しない。各元DDS/DASの生レスポンスSHA256・バイト数と、ALTITUDE・TIME・ISOURCE等の実変数名、次元の時間層数をSOURCE-safeに保存。元文字列は属性に関係するごく短いSOURCE行だけ抽出し、地形標高配列・鳥GPSは転載しない。

10候補のうち、一部のOPeNDAPがアクセス不可ならそのSOURCE STOPを明示し、別タイルを想像で代用しない。DDS/DASを取得できても**元の標高zの実有効値・2016年画素・元NAPを現地潮位と校正したことにはならない**。そのため2018〜2019年ミヤコドリの実際の干潟干出割合は計算しない。

## 次の機構へのゲート

源メタデータに\`time\`・\`altitude\`と測量出自を示す\`isource\`などがあることを確認できた時のみ、次段で元2016年の実測時刻に合うtimeスライスを限定取得し、元SOURCEで有効な標高がVlielandの実GPS地点に重なるか調べる。その後、NAP標高とRWS港湾水位の整合を検証し、位相差や海域差と現実の干潟利用可能面積の不確実性を扱う。元地形のない鳥GPS点を都合よく埋めない。

これは**生態学的効果ではなくSOURCE監査**。元v168/v169の年外2018→2019年潮位高さの予測利得は維持するが、この版で干潟露出がその原因だと主張しない。Boids社会力・潮汐×太陽因果係数も未同定。

実行\`python -m unittest discover -s validation_v174 -p 'test_*.py' -v\`、\`python validation_v174/original_Vlie_DDS_DAS_source_schema.py --emit\`。初回SOURCE結果の固定後\`--check\`で再取得検証。原時刻イベント、鳥個体GPS、生DEM・元港潮位値は出さない。
