# v170｜Vlieland 2018〜19年のGPS行動へ接続するための2016年歴史的海底・干潟地形SOURCEゲート

2026-11-17。v169で明らかになった最も大きな観測的所見は、ミヤコドリ *Haematopus ostralegus* の前15分のACC分類と太陽・時計を説明しても、真正のRWS Vlieland Haven港湾実測潮位の**水位そのもの**が、2018学習モデルでの2019年の採餌ACCイベント比を改善する点（HEIGHT +0.007430798 MSE）である。ただし正しい時刻の水位が+3/+7/+11日の最良誤時刻より一貫して良いわけではなく、**水位が干潟への物理的アクセスを切り替えている**という機構はまだ未検証。

## 前段と外部SOURCEの確認

- 公式Rijkswaterstaat/Deltares Vaklodingenは20mの海底・干潟標高で、平面座標Amersfoort / RD New（EPSG:28992）とオランダNAP標高基準を使用する可能性が高い。しかし、年代、格子、座標基準は**対象元ファイルごとにネイティブ属性で検証**する。
- [Wadden Sea公式のデータ説明](https://www.systeemrapportage.nl/wadden/data.html)では、各年のエリアごとの実測を最新利用可能な画素で組み合わせて広域ラスターにしている。そのため「2016レイヤー」でも古い測量画素を含みうる。後年の最新2025/26ラスタを歴史的生息地へ機械的に当てない。
- [Rijkswaterstaat OpenEarth vaklodingen original](https://rwsprojectarchief.openearth.nl/downloads/kustgenese2/bathymetrie/Vaklodingen/)に個別の\`20160912_vaklodingen.nc\`、\`20190712_vaklodingen.nc\`（ファイルサイズは数MB）の公開原NetCDFが存在する。**ファイル名の年月≠元DEM各セルの真の測量年月**。2016年測量と記されていてもVlielandのGPS観測地を含むとは限らず、標高がNAPであるとも限らない。
- Deltaresの他のOPeNDAP [vaklodingenKB125_1110](https://opendap.deltares.nl/thredds/dodsC/opendap/rijkswaterstaat/vaklodingen/vaklodingenKB125_1110.nc.html)はEPSG:28992 20m x/y / 2016年候補source flagを持つが、bboxが**北緯53.498〜53.611、東経5.161〜5.312**なので、Vlieland西方の主な干潟へ無条件に割当てるのは禁止。実際のGPS・対象地理を原本で数えた上でどのタイルを使うか決める。

## この版で、解析結果を開く前に固定するSOURCEルール

1. Rijkswaterstaat/Deltares元の\`20160912_vaklodingen.nc\`と\`20190712_vaklodingen.nc\`を公式公開アーカイブから再取得し、**元バイナリのSHA256・実バイト数・本当にNetCDFか**を照合。
2. 元\`x/y/z/time/isource\`等の全変数のDIM、座標・時間・標高の単位、元\`crs\`、EPSGコード、地理的範囲、実測セルの件数をSOURCE-safeなaggregateへ出す。**ファイル名で2016/2019の各ピクセルを測量済みと決めない**。
3. EPSG:28992とWGS84 (EPSG:4326)で元座標範囲を再投影して、Vlielandの広域を**覆う可能性があるか**だけを初回確認。原GPSの実各地点が入る割合・使える過去測量セルの割合・RWS潮位基準とのオフセットはこの版ではまだ計算しない。
4. NetCDFが取れても、必要な**2016以前の測量履歴、当該GPS鳥が移動する標高範囲、格子の標高基準、各セルの元測量日**が一致しないなら、**地形×水位を生態学的結果として発表しない**。コンテンツSHAが変わったときも勝手に最新DEMを代用しない。
5. 元ファイルはユーザー公開リポにコピーしない。元DEMのSOURCE-safeメタデータ（元SHA、属性、座標範囲、歴史的地理一致の可否）のみGitHubに保存。

## 目的と次のSOURCEゲート

本当に2016年当時のVlieland GPS地点を覆う有効な20 m標高を実測原本で得られた場合にのみ、次段で標識個体の元GPS各位置（元v128/2018、元v126/2019）を正しくEPSG:28992へ変換し、同じ年代のDEMセルと照合して

\[
d(s,t)=h_{\mathrm{local}}(s,t)-z_{\mathrm{DEM}}(s)
\]

を構成する。ただし港観測所\`vlieland.haven\`の実測水位は、鳥がその時刻にいる場所の**局所水位とは限らない**。海域ごとの潮汐振幅・位相差に関する独立校正が必要で、港水位を局所水位の完全な代替と見なさない。zの不確実性（測量年・空間補間・地形変化）も評価する。

このSOURCE条件を満たしたときにはじめて、\`P(foraging | own previous behavior, solar, true dry/intertidal accessibility)\`の予測を、\`P(... | harbor height)\`や誤位相と同じ元観測機会で比較する。地形はアクセス可能面積の代理であり、餌量や実採餌成功の直接測定ではない。

## 先行モデルの保持と再現

v166–v169の真正ACC+GPS・RWS実測元結果、SOURCE STOP、2018学習2019保留MSEは変更せず、歴史的DEMのSOURCEを別PRとして監査する。今回のSOURCE-only版では**新しい潮汐×太陽の生物学的効果、実GPS干出割合、Boids社会的な個体間分離/整列/凝集は未推定**。

\`python -m unittest discover -s validation_v170 -p 'test_*.py' -v\`は合成NetCDFとEPSG:28992の地理範囲の既知真実を確認。

\`python validation_v170/historical_dem_source_gate.py --emit\`で公式元ソースを取得し、ファイル元SHA・属性を読み取る。初回結果の固定後は\`--check\`で元ファイルのバイトSHAと全SOURCEメタデータの一致を要件にする。原NetCDFや元個体位置をGitHubへ転載しない。
