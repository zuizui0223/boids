# v185｜先行WEBTICSの15観測所を固定し、真正RWS2018/2019年源の利用可否を監査

**SOURCE ONLY.** v184で確認した Vlieland Haven → West Terschelling の+30分遅延を、別の観測所へ外挿する前に、**独立した先行研究の15地点**を固定する。

元典：Rappoldt & Ens (2011), *Het effect van bodemdaling op het aantal scholeksters dat kan overwinteren in de Waddenzee*, EcoCurves report 12 / SOVON 2011/05, Appendix A Table A.1 (printed p.46) and geographical triangulation Appendix A.1.
<https://nam-feitenencijfers.data-app.nl/download/rapport/d360edf8-1955-4ee4-b0e9-58826d7e0a53?open=true>

従来WEBTICSはすでに**15か所の潮位観測所の幾何学的三角形補間により潮間帯干出時間を推定**しているため、「干潟水位の補間」という概念自体に新規性を主張しない。

## 結果を見る前に固定したサンプル
Den Helder, Den Oever, Kornwerderzand, Harlingen, Lauwersoog, Eemshaven, Nieuwstatenzijl, Delfzijl, Huibertgat, Schiermonnikoog, Wierumergronden, Nes, West Terschelling, Vlieland Haven, Oudeschild。2011年論文のEPSG:28992平面座標は全てソースコード定数として固定する。**2011年の標準位置≠2018・2019年の機器正確位置**。RWS原カタログのX/Y/座標系は別欄で保存し、移動の可能性を残す。

固定の正規化された station-name 完全一致のみを認め、同じ候補名が重複すると曖昧SOURCE STOP。未収録地点を近隣の都合のよい別観測所で置換しない。2018年・2019年各6月1日〜3日48時間、原 `WATHTE`、`cm`、`NAP`、元の定時時刻のみ。200件未満/元メタデータ不一致は不適合。源のバイトSHA、観測可能元件数だけ保存。候補のうち2か年とも通った地点が≥8か所なら、多地点SOURCEの存在を仮採用する。2018/19元値を選択やモデル調整には使用しない。

## 検証順序
1. 15候補の原名・元コード・座標を原RWS catalogから確認（今回）
2. 元2018/2019観測水位の48h品質監査（今回）
3. 十分な地点があれば次v186で**Leave-one-gauge-out**：15点の公開位置に基づく空間内挿の誤差を、完全に隠したその観測所で確認。出力は源の集計/統計のみ。水位予測の検証であり、GPS地点の真の潮位を直接検証したことにはならない。
4. v182 SOURCE STOPの地形鉛直NAP、2016/2017実測日、局所干潟地形変化などは独立ゲートとして残す。

`PYTHONPATH=validation_v110:validation_v183 python -m unittest discover -s validation_v185 -p 'test_*.py'`
`PYTHONPATH=validation_v110:validation_v183 python validation_v185/original_fifteen_wadden_gauge_inventory.py`

元潮位値/原GPS/ACC/DEM格子は一切リポに公開しない。
