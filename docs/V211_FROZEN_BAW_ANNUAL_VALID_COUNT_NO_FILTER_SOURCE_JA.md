# v211｜BAW年別水理指標から2018/19年「有効データ点数」と`no_filter`原WCSを監査

**v209–v210の低潮位時NoData偏在を確認した後の探索的SOURCE discovery。** v210のSHA固定オフライン計算では、沿岸8グループのBAW WMS通常値のみを残した場合に、元RWS実測NAP潮位が等重み平均で+0.528645833m上方選択された。これは生態学的因果の証明ではない。

## 重要な原製品の区別
**時刻別TrilaWatt Hydrodynamik** (`sea_surface_height_2d_2018_NL`等、500m/20min) と、**TrilaWatt Hydrodynamische Kennwerte** (2018, 2019の年別hydrodynamic statistics、20m GeoTIFF) は別の製品。BAWの後者の原2018/19説明では、通常の年集計は**年間を通して水没していた格子のみ**に制限し、`*_no_filter`版はこのマスクを掛けない代わりに、乾出する浅い海域では年平均に使えるデータ点数が減るため、原有効データ点数（`Anzahl gültiger Datenpunkte`）や潮の件数の指標も併せて提供すると説明する。**この年間統計のalways-wet filter仕様を時刻別WMSの約1e31へ直接推定・同定することは禁止。**

一次公式BAWの固定SOURCE：
- 2018年 original 20m annual statistics WCS2 `https://mdi-dienste.baw.de/geoserver/TrilaWatt_Hydrodynamik_2018/ows?service=WCS&version=2.0.1&request=GetCapabilities&REQUEST=GetCapabilities&SERVICE=WCS`、元BAW登録 ID `FE9AA7AE-7BAC-45E8-8918-A55BC6EEA645`。
- 2019年 original annual WCS2 `https://mdi-dienste.baw.de/geoserver/TrilaWatt_Hydrodynamik_2019/ows?service=WCS&version=2.0.1&request=GetCapabilities&REQUEST=GetCapabilities&SERVICE=WCS`、元登録 `49CA8C6A-A6F2-4847-91D6-77D01C0CDDBD`。
- original metadata description pages `https://datenrepository.baw.de/trefferanzeige?docuuid=FE9AA7AE-7BAC-45E8-8918-A55BC6EEA645` / `https://datenrepository.baw.de/trefferanzeige?docuuid=49CA8C6A-A6F2-4847-91D6-77D01C0CDDBD`。

## 凍結した原本検証条件
1. 固定original BAW URLsにHTTPS正常CA認証でアクセス。公式legacy `mdi-dienste.baw.de`のHTTPS 308/301等は、元`Location`が**唯一`https://coast.baw.de`でsame WCS year/path/query**の時だけsecond direct GETを許可。その他redirect/HTTP downgrade/TLS無効化はSOURCE STOP。
2. 2018と2019の元`WCS_Capabilities`または`Capabilities` XML、native version 2.0.1、`CoverageSummary` exact `CoverageId`/元タイトル/元Abstractとsource HTTP byte SHA/byte count/TLSを確認。最大8MB、DTD/XXE拒否。**元GeoTIFF・GetCoverageは一切呼ばない。**
3. native `CoverageId`実名から`no_filter`, `valid data count`、`anzahl/gültiger/valid`に関係する候補を全部列挙し、対応する2018/19 WCSの原CoverageId/ID数を報告。native名を先に捏造せず、予想に合う層を結果見ながら選ばない。
4. 2年両方に実CoverageIdがあり、`valid datapoint`を表す公式native metadataが明示されて初めて、次版で3既公開WEBTICS地点の固定ROIに`GetCoverage`対象を凍結できる。`no_filter`は**年間平均の集計母数**に関わる別製品仕様で、raw時刻別WMSの`_FillValue`証明ではない。
5. 元SOURCE未取得、native coverage name不足、TLS停止はすべてnegative/STOPとして報告。観測行動や鳥GPS、DEM survey dates、縦基準、原潮位時系列は開かない。獲得しても**同じBAWモデルに基づく二次データ**であり現地独立検証ではない。

公式source BAW: https://datenrepository.baw.de/trefferanzeige?docuuid=FE9AA7AE-7BAC-45E8-8918-A55BC6EEA645 ／ https://datenrepository.baw.de/trefferanzeige?docuuid=49CA8C6A-A6F2-4847-91D6-77D01C0CDDBD

**生態学SOURCE STOP継続**：native時刻別`Wasserstand` units・`_FillValue`・vertical datum、個体GPS地点h(s,t)、20m Deltares DEM survey-day/NAP、瞬間干出と採餌、太陽×潮汐・社会Boidsの因果効果。
