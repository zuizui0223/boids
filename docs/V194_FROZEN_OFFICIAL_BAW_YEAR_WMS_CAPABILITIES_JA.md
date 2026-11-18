# v194｜BAW公式2018/2019 TrilaWatt WMS・TLS原本メタデータ監査（SOURCE ONLY）

2026-11-18。v193の2回の原本検証 (Actions #44302181422 / #44302225095) は、**GitHub ActionsのPython標準TLS CAで公式ダウンロードサーバー `dl.datenrepository.baw.de` を検証できず**停止（`CERTIFICATE_VERIFY_FAILED: unable to get local issuer certificate`）。実在しないNetCDFと判定されたわけではない。全2018/2019 NetCDFの真正バイナリ、原ファイル名、SHA、native water levelsは未取得。SSL検証を無効化して進めない。

## 一次公式根拠
BAW公式TrilaWatt元データ <https://datenrepository.baw.de/trefferanzeige?docuuid=40936F66-3DD8-43D0-99AE-7CA5EF2E1287> は2015–2022年の水理モデル出力、500m/20min、各年の`nl`領域tides NetCDFを説明。元配布先の公式link `https://dl.datenrepository.baw.de/7000/B3955.02.04.70237/Hydrodynamik/` はv193で原ネイティブHTMLを取得できなかった。

それとは別に、**公式BAWが各年ごとに明示する別ホストの地図サービス**：
- 2018 `https://coast.baw.de/geoserver/TrilaWatt_ncHydro_2018/wms?service=WMS&version=1.3.0&request=GetCapabilities`
- 2019 `https://coast.baw.de/geoserver/TrilaWatt_ncHydro_2019/wms?service=WMS&version=1.3.0&request=GetCapabilities`
- 2015–2022年度統合の公式別サービス `https://mdi-dienste.baw.de/ncWMS2_Trilawatt/wms?REQUEST=GetCapabilities&SERVICE=WMS`（年度別サービスと同じ現物とは仮定しない）。

いずれもBAW公的検索・メタデータで公開されているURLである。新しい任意URLや非公式ミラーを使用しない。

## 結果前に固定したSOURCE/TLSゲート
1. `urllib.request` + OS標準の証明書検証を**有効**のまま、各公式HTTPSサービスへ WMS `GetCapabilities` GET だけ。サーバ証明書の検証に失敗したものは `SOURCE_STOP_TLS`。HTTPへdowngradeしない、`verify=False`や`ssl._create_unverified_context`を禁止。
2. HTTPSリダイレクトも、最終ドメインが`coast.baw.de`または`mdi-dienste.baw.de`に属する場合だけ許可。ホストを変えた場合は証明書を再検証。レスポンス上限4MB、タイムアウト30秒。生WMS地図画像や本体のtides NetCDFは取得しない。
3. 真正のOGC WMS `WMS_Capabilities` / `WMT_MS_Capabilities` XMLか、DTD/external entitiesなしで厳格解析し、元XMLのSHA256・HTTP結果・WMS version・Name付きレイヤー総数・レイヤー名の上限付き一覧・Time dimensionの原スニペット/ハッシュ（元時間数列は転載しない）・CRS/bboxだけに限定して出力。
4. 年別双方のオリジナルXMLが真に取り出せた場合でも**レイヤーや年次のWMS存在確認**まで。水位グリッドの数値・時刻・NAP/NHN基準、RWS実測一致、Vlieland GPS地点の実際のh(s,t)、干潟の干出、鳥行動予測は `SOURCE_STOP`。
5. TLSルート原因の診断は`curl`（検証必須）や公的CA bundleの相違を集計のみ記録し、証明書・秘密鍵・API tokenを原ファイルとして公開しない。信頼できるルートで取得できたデータだけを取り込む。

本解析は**2025年公表のretrospective hindcast**の2018/2019年度を用いる可能性の検証であり「2018年時点で2019年を事前予報した」ことにはならない。v182のhistorical 20m DEMのnative NAP/survey-date校正も依然STOP。

この段階ではモデルのボックス地理範囲とGPS軌跡が本当に重なるか検証せず、GPS/ACCデータ、潮位の生時系列、DEM原ラスターは一切開かない。
