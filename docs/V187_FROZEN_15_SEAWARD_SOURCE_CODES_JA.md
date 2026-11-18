# v187｜15地点原RWSコードを水位を見る前に固定（v185失敗後の探索的SOURCE修正）

v185では独立先行WEBTICS 2011年の15地点のうち、原2018・2019 `WATHTE cm NAP`両年利用可は5/15、事前閾値8に達しずSOURCE FAIL。
v186では**水位を全く取得せず**RWS原カタログ名称だけを監査し、Harlingen、Lauwersoog、Kornwerderzand等は多数の水側・湖側・港湾地名候補に分かれることを確認（original RWS coordinates X/Y fields null、coordinate system label ETRS89）。

このv187ではv186名だけを使って15個のexact native station codeを固定。3条件を変更しない：①海側明示を優先（Den Oever `denoever.spuisluis.buiten`、Kornwerderzand `kornwerderzand.waddenzee.buitenhaven` 等）、②v185で元2か年ソース通過した5コードは**不変**、③正式地名で裏付けられた候補名以外採用しない。候補1つに複数海側局があっても**潮位の成績を見て変更しない**。

2018と2019の6月1〜3日のRWS `WATHTE cm NAP` の原本品質（≥200実測）を各元15地点で判定。元SOURCE出典SHAと元件数のみ保存し、データがない地点はFAILのまま。他地点への代用は禁止。両年≥8なら広域ネットワークが探索的に十分というSOURCE確認だが、初回v185のSTOPを「初回から成功」に書き換えない。

**未解決の物理ゲート**：RWS原カタログに元局座標X/Yが出ておらず、2011のRD座標は2018/19の同じ観測装置の座標であると証明できていない。名称一致のみでGPSセルのh(s,t)や干出を作らない。元DEM10タイルのNAP鉛直基準・測量日もSTOPを維持。

再現：`PYTHONPATH=validation_v110:validation_v183:validation_v185 python -m unittest discover -s validation_v187 -p 'test_*.py'`、
`PYTHONPATH=validation_v110:validation_v183:validation_v185 python validation_v187/original_RWS_15_fixed_seaward_sites.py`。
