# v199 | BAW公式308で確定した新ホストの原WFS/WMS/WCS Capabilitiesを再監査

2026-11-19。v198 Actions #44429348878/#44429376545 は、BAW official `mdi-dienste.baw.de/geoserver/TrilaWatt_Wattflaechen/` の original WFS/WMS/WCS GetCapabilities が**すべてHTTP 308**で同一のBAW host `coast.baw.de` へ転送されると、TLS検証を無効化せず初回headerだけを読んで確証。**未知のredirectを自動追跡してはならない**というv196 STOPは科学的に正当だった。転送先の正確なオリジナル`Location`をv199の固定新SOURCEとして採用する。

## Fixed 3 new original destination URLs (v198 original headerに完全一致)
1. WFS `https://coast.baw.de/geoserver/TrilaWatt_Wattflaechen/wfs?REQUEST=GetCapabilities&SERVICE=WFS`
2. WMS `https://coast.baw.de/geoserver/TrilaWatt_Wattflaechen/wms?REQUEST=GetCapabilities&SERVICE=WMS`
3. WCS `https://coast.baw.de/geoserver/TrilaWatt_Wattflaechen/wcs?REQUEST=GetCapabilities&SERVICE=WCS&VERSION=2.0.1`

この3候補はバージョンやディレクトリを推測して作ったURLではない。v198 original URLの`Location` headerそのもの（元転送先を検証できたもののみ）であり、2026年に原BAWの年別TrilaWatt hydrodynamic WMSでも`coast.baw.de` hostを原本TLSで検証済み。よって`https`/CA通常検証有効でその3つへ**直接GET**する。

固定SOURCEゲート：
- host `coast.baw.de` exact/https/元URL exact、CA必須。今版も自動redirectは追わない。各元response最大4MB/HTTP200、XML DTD/ENTITYなし。
- 元OGC WFS/WMS/WCS Capabilities の種別と native version、元原XMLバイトSHA256、オリジナルFeatureType/Layer/Coverageのname/titleをsource-safe収録。HTTP error/再redirectはSTOP。
- 2018/2019、`NL`等の文字列がnative FeatureType名/Titleに現れているかだけSOURCEの事実として確認。現れなくてもyearが内部属性なら年次source候補あり得るので「年の元データがない」とは判定しない。
- 本段階ではGetFeature/DescribeFeatureType/GetCoverage、GeoTIFF/shapeの取得、2018/19の年別ポリゴン抽出・GPS交差は一切行わない。元NAMEだけで干潟位置や瞬時干出は作らない。
- BAW公表`2015–2021`年次干潟データの高低潮位線には±25cmの不確実性があるが、これは各GPXセルの水位の上下±25cmを実測したわけではない。

成功ならv200は、native WFS FeatureTypeの年別対応、2018/19 NL extent、small-bbox original geometry coverageと本当に対象GPS地理と重なるかを研究設計として検討する。v182 historical DEM z NAP & field survey-day / bird-local h(s,t) / tide×sun / social-Boids は依然SOURCE STOP。
