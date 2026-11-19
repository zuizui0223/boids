# v208｜TrilaWattモデル強制・校正・鉛直基準の原著論文SOURCE監査（SOURCE ONLY）

**v206・v207のBAW WMS Wasserstand vs 実測RWSの正確時刻数値一致を見た後の、独立原著方法論ゲート。** 2018/19のBAWモデルが実測から独立した未来予測であるか、native WMS値のメートル・NAP同値が確定したかを混同しないための検証。元生物行動はここでは一切開かない。

## 原著・真正SOURCE（2026-11-19現在）
Lepper, R., Reinert, M., Gundlach, J., Weber, J. & Kösters, F. (2025). *A hydrographic dataset of the Wadden Sea as a foundation for a digital twin of the coastal ocean*. Scientific Data 12:1746. DOI https://doi.org/10.1038/s41597-025-06211-1. オープンアクセス公的保存本文 `PMCID: PMC12589441`（https://pmc.ncbi.nlm.nih.gov/articles/PMC12589441/）。原著本体のOPEN XML sourceはEurope PMC公式fullTextXML API `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12589441/fullTextXML` を対象とし、URLや文献を検索結果の良いものへ変更しない。HTTP200、HTTPS標準CA、元XMLのSHA256/byte count、正しいDOI・PMCID・タイトルを検証し、原本文の一部のパラグラフ中に下記五つのMETHODS事実があるかを**元sourceだけ**で判断。

### 凍結する原論文の方法論検証
1. モデル出力の`hydrodynamic data`は年別、潮位`sea_surface_height_2d`、約500m/20min、UTC、horizontal EPSG4326と明記してあるか。
2. 元データ製品の縦基準は**NHNでNAPに相当する**という原著の記述があるか。これは**論文・製品レベル**のvertical referenceであり、個別WMS GeoJSON `Wasserstand`元値や原NetCDF`units`/`_FillValue`を確認したことにはしない。
3. modelのopen-boundary潮汐が`FES 2014b`に基づき、残差補正に`Helgoland`と`Roscoff`の水位観測が使われたか。**この2地点からの観測依存があること**は方法論上の依存性だが、v206/207対象のVlieland、Terschelling、Wierumergrondenがopen-boundary補正に使われたとは書かない。
4. モデルのSSH/tidal dynamicsの**technical validation**に複数観測所の水位が使われ、原論文自体に観測水位との比較があるか。これは既存の事前研究であり、v206/207の小標本で「初めて現場潮位の精度が証明」と主張しない。同時にvalidation gaugesのリストをいまだ完全監査していない以上、3対象局が**校正**または**検証**に使われたかの個別判定はNOT_IDENTIFIED。
5. **2019年からの大気強制の変更**（ICON-EU）と、それに関連したstorm-surge/high water/temperature再現性の差を本文が記述するか。2018 vs 2019をそのままfield ecologyやterrain morphodynamicsの年差と解釈しない。原強制更新は潜在的年次confounderとしてモデル一般化に明記。

## 採用・拒否の独立SOURCEルール
- Europe PMC original full-textの`article` JATS XMLで元DOI`10.1038/s41597-025-06211-1`、元PMCID `PMC12589441`、原タイトルを厳密確認。5つMETHODS根拠ごとに元JATS paragraph位置・SHA256と、ごく短いsource cue（長文複製をしない）を集計。SOURCE XML自体は保存しない。
- 元XMLが404/403/大きすぎる/要素不足/HTTPS検証失敗→SOURCE STOP。元の条件を研究結果に合わせて緩めない。研究者ノートと文献の主張は区別する。
- 5箇所が原本文で確認できた場合でも、そのパスが許す結論は**製品レベルのNHN≈NAPおよび既存モデル較正・気象強制の文献による根拠**のみ。
- 今回の六site-year×June/Septemberのモデル-vs-実測数値比較（v206/v207）について、単位が当該native `Wasserstand`に一致するか、欠測候補約1e31が真の`_FillValue`か、地域局所のpixel-level正確性、校正に3観測所の値が使われたかの独立性は**STOP**。
- 2025 retrospective hindcastは2018時点で実時間2019未来予測として利用可能ではない。2018の鳥ACCで学習し2019を評価するなら`retrospective environment-conditional heldout behavior`と呼び、リアルタイムforecast/general ecological causalityと呼ばない。

## 真の生態学的な問い
元v169のミヤコドリ2018-fit→2019-test real GPS/ACC効果（harbor tide-height追加MSE改善~0.00743）は、2019時点の前行動が観測済みという条件付きのout-year ACC予測であり、潮汐による採餌機構の同定ではない。物理SOURCEの年次高さ・段差と個体動作を検定するためには、**生物GPSセルの局所h(s,t)、原DEM zの真のNAP/field survey day、対象GPSの本当に浸水/干出する領域、潮汐モデルの独立現地誤差**を先に揃える。光/潮汐/社会Boidsの仮説はその後の検証対象。

確認済み対象PR：v206 #225 June source-only、v207 #226 September source-only。**どちらもmainへ生態学的肯定結果としてマージしない**。
