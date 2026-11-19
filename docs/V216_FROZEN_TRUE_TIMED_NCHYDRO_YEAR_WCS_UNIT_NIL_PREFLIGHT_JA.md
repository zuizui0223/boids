# v216｜TrilaWatt時刻別NetCDF（2018/2019）のWCSを出典経路として監査：native単位・Nil・_FillValueを混同しない

2026-11-19に**v215の実SOURCE結果を閲覧後**、原native `sea_surface_height_2d` units/NetCDF `_FillValue`/vertical datumが未検証の問題を解くための固定SOURCE preflight。成果は正否・非対応も全て報告し、モデル出力を結果に合わせて拡張しない。

## 原本が証明していること（今回より前）
- BAW公式データセット `TrilaWatt: Hydrodynamik (2015–2022)`, DOI `10.48437/7ca5ef-2e1287` は、年ごとにオランダ海域の `tides` の水位/流速をNetCDFで配布すると記載。これは**配布製品レベル**の証拠であり、未取得2018/19原NetCDFのattributeではない。
- BAW公式GeoServerの**WMS** year2018/19についてのみ、`coast.baw.de/geoserver/TrilaWatt_ncHydro_YEAR/wms` の原OGC Capabilities XMLをv194でnative SHA2018 `386af7c9a75b66ef23017dfd49abe3afb71a530011e9f7bedbf3904281b7484f` / 2019 `a52bf61de7bc50495ea75782a6e4bc5b4762ce3174e29a961cec1f697fe9b20a` と認証。原native water-layer `sea_surface_height_2d_2018_NL` と `...2019_NL` が存在する。
- v209/210は元WMS `Wasserstand`が約1e31の時刻に原RWS cmNAP実測潮位が低いという**モデル源availability**と選択差を定量化。**ただし約1e31を元NetCDF `_FillValue`と確定したわけではない。**
- 別のBAW **年間**`Hydrodynamische Kennwerte`製品（20m）はv211–v215において、通常版/`no_filter`間の空間的フィルタ差を実証。これは500m/20min元Hydrodynamik`sea_surface_height_2d`のnative欠測符号を証明しない。

## 先に凍結するSOURCE経路と否定結果
BAW公式はWMS URLを掲載しているが、**同一GeoServerでWCSが公開されていると公式に保証していない**。そこで、公式WMSから派生するWCS**検証候補**だけを明示的に記録：
- `https://coast.baw.de/geoserver/TrilaWatt_ncHydro_2018/wcs?service=WCS&version=2.0.1&request=GetCapabilities`
- `https://coast.baw.de/geoserver/TrilaWatt_ncHydro_2019/wcs?service=WCS&version=2.0.1&request=GetCapabilities`

これはWMSのURLから同じ公式ホスト・workspaceに置くWCS endpointの**candidate**であり、**公開済の元WCSとしては未認証**。SOURCE probeはこの2件だけをHTTPS・通常CA証明書検証ON、no redirects、レスポンス最大4MB、各time-out 35sでGET。
- HTTP404/OGC exception/元WCS2でない場合は`SOURCE_STOP_CANDIDATE_WCS_NOT_ADVERTISED`。WMSにだけ存在してWCS非対応であれば、そのSOURCE negative resultを結果として残す。元`/ows`や非公式mirrorへ事後救済で移行しない。
- BAW元WMS sourceの再取得SHAがv194と同じ、WMSの元height-layer存在確認ができなければこの候補を試さずSOURCE STOP。

## WCSが真正OGC原serviceだった場合のみ
1. WCS2 `Capabilities version=2.0.1`・`CoverageSummary`原`CoverageId`リスト/タイトルを採取し、HTTP SHA/bytes、native op`DescribeCoverage`等を記録。DTO/ENTITYと誤HTMLをreject。
2. 元height`sea_surface_height_2d`、年2018/19、`NL`の三条件を**native CoverageId/Titleから全て満たす唯一の対象だけ**選択する。曖昧/元CoverageIdなし→STOP。
3. 元operation`DescribeCoverage`をadvertiseしている場合だけ、同一candidate WCS pathに厳密なnative`coverageId`を付けてSOURCE XMLを取得。原`CoverageDescription`の exact CoverageId/Envelope/time axes/`rangeType` field `uom`/nilValuesだけ保存する。ネイティブWCSの`NilValue`が`1e31`かどうかは客観的記述として検証するが、それでも**元NetCDFの `_FillValue` 属性を直接読んだ証拠ではない**。
4. WCS`GetCoverage`や元NetCDF実体のダウンロードは禁止。WCSの`uom`はnative WCSサービス出力のメタデータであり、`_FillValue`や`units`が元nc`sea_surface_height_2d`変数に正確に対応するかは別に原NCのダウンロード・ヘッダー検証が必要。

## SOURCEの科学的な上限
新たな肯定結果を言えるのは**元BAW WCS公開有無、CoverageId、Envelope/units/nilが原OGC上で読めるか**まで。WMS`Wasserstand`の極端値は現時点でもNoData候補。独立の物理干出・鳥GPS`h(s,t)`/20m Deltares z鉛直NAP/survey-day、潮汐×太陽/社会Boidsの因果検定はSOURCE STOP。不正なTLS回避・WCS以外への自動フォールバックは禁止。

原著 Lepper et al. (2025), doi:10.1038/s41597-025-06211-1は製品レベルのNHN≈NAP、モデルに観測値の強制と2019 ICON-EU入力変更があることを説明。2018fit/2019testの将来予報と取り違えない。
