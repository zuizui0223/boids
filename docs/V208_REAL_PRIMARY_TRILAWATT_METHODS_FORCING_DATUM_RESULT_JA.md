# v208｜真正原著論文から確証したモデル製品の縦基準・強制・既存校正

2026-11-19。原著Lepper et al. (2025), *Scientific Data* 12:1746, DOI https://doi.org/10.1038/s41597-025-06211-1 (PMCID: PMC12589441) の公的Europe PMCの**真のオープンアクセスJATS fullTextXML**を、厳格なHTTPS標準CAと原DOI/PMCID/原題同一性のもと再取得し、122個の元原著パラグラフから以下の6つMETHODSを原XMLの原段落SHAつきで監査。

- GitHub Actions [#44452322358](https://github.com/zuizui0223/boids/actions/runs/44452322358) 及び [#44452360199](https://github.com/zuizui0223/boids/actions/runs/44452360199)：**2回SOURCE SUCCESS / 6/6元本文根拠合格**。
- Europe PMC original fullTextXML SHA256（第2run） `1c2946e4edeae5a886126c2ffa95cfebeb452598b508be5d6e3c6cd0ae7e614d`（DOI/PMCID/title一致）、GitHub Actions元source-safe ZIP SHA256 `a0acc80aa8be47341421ef81b74682360e7f580c9702f28c80d373330a34e2`。
- 元論文本文：
  1. 海域モデル出力`sea_surface_height_2d`は年別NetCDF / 約500m / 20分間隔。これは真のGPSでの水位検証ではなくモデルPRODUCT仕様。
  2. **製品levelの高さの基準 NHN はNAP相当**と原著が明記。元GeoJSON `Wasserstand`の単位・欠測値のnative NC attributesは未確認。
  3. 潮汐のopen boundaryは **FES2014b** 成分から復元する原論文method。観測値から完全独立のモデルではない。
  4. 残差補正に**HelgolandとRoscoff**実水位を使用して平均海面・季節・短期変動を合わせると原著は明記。**Vlieland/Terschelling/Wierumergrondenがその同じ境界補正へ使われたとは書いていない。**
  5. BAW原著自体が**実潮位観測所**と海面水位のモデルを比較しているので、v206/v207の3局数時刻の整合性は初めての広域validationではない。原著20代表局、M2振幅RMSE約5〜7cm、M2位相RMSE約12〜15min。ただしオランダ3局それぞれが原モデル**校正またはvalidation**対象であったかはこのv208元文章だけでは確定せずSOURCE STOP。
  6. **2019年からICON-EUへの気象強制切替**を報告し、storm surge等のバイアスや海面高の再現性が前後で変わり得る。生態的な2018/19変化と同時にモデリング条件も変わるので、年外予測解釈に明示。

## 既存v206/v207の数値結果への影響
- 2018/19 3公表地点×June/SeptemberのBAW WMS生`Wasserstand`と同UTC RWS WATHTE/cmNAPの元候補比較は既存6月5/6、9月6/6 cohorts n≥3、RMSE約0.034〜0.156**メートル仮定**、いずれも時刻やRWS元データに同期性がある。WMS本体の`units`,`_FillValue`/vertical attrsを未開封なので「源水位がmNAPで正しく測定された」ことをこの元論文だけで認定しない。
- モデルの境界潮汐/大気強制が実測資料に依存し、元論文自体に実測潮位検証があるので「3局と完全に独立の外部validation」とは呼ばない。元RWS観測そのものが入力として使われたかのsite-specific statusは**UNKNOWN**であり、Helgoland/Roscoffと混同しない。
- v169の2018 fit→2019 bird ACC heldout tide-height条件付き予測は、2019当時のprevious observed behaviorと2025公表retrospective tide fieldを利用可能な`retrospective conditional behavioral evaluation`として評価すべきで、当時利用可能な外部予報ではない。

## 次の物理→生態ゲート

モデル水位の低潮時NoData候補約1e31を、真正原RWS cmNAPの潮位と同時刻で照合するsource-only v209 #229を新規実装（**モデル欠測選択バイアスの検証**）。実測水位が低い時にsource欠測する可能性があるなら、単純なWMS欠測行dropは太陽×潮汐活動モデルで系統的サンプリング偏りを生む。

**本sourceにないこと:** original NetCDF`_FillValue`、2018/19 RWS機器の正確な座標、実鳥GPSセルの`h(s,t)`、historical 20m Deltares z native NAPと実測日、物理的な干潟干出・鳥採餌・群れBoidsパラメータ。これらを追加済みの肯定的生態学的結果としてmainへマージすることはしない。
