# v186｜v185 15地点中5地点SOURCE肯定を維持したまま、原RWS観測所名だけを診断する

v185の正式名完全一致が許した両年`WATHTE cm NAP`観測所は5/15であり、事前に固定した閾値8には達しなかった。このSOURCE STOPを変更・抹消しない。

新たなコードは2011 WEBTICS 15観測所の**既に固定した地名部分文字列**を使い、Rijkswaterstaatの公式`METADATASERVICES/OphalenCatalogus`原カタログから名前が前後に伸びた候補（例：後置された外海・港湾記述）を検索する。元コード・座標値・座標系もそのままSOURCE-safeに保存。短いNesだけは独立単語で検索。

**元水位の時系列は1件も開かない。** 元値を見て観測所や座標を選ぶことは不可。候補複数は複数のまま出力し、自動で採用しない。2011の表のRD座標は2018年元局座標とは別物であり、原`Coordinatenstelsel`を検証するまで距離選択にも使用しない。原RWSに名前が存在しない場合は不在を記録する。

次v187で利用可否を照合するときも、元水位未開封の間に唯一の地理的位置対応を決定する。候補名だけを確認してもv185 5/15の水位原データSOURCE結果の確証にはならない。

Script: `PYTHONPATH=validation_v110:validation_v183:validation_v185 python validation_v186/original_RWS_catalogue_alias_probe.py`. Test: `PYTHONPATH=validation_v110:validation_v183:validation_v185 python -m unittest discover -s validation_v186`.
