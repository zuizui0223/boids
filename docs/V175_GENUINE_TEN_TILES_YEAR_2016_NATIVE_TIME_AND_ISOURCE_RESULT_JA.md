# v175 Vlieland全10タイルに実際の2016年time層が存在。ただし「測量日」ではなく年次索引ラベル

2026-11-17。Deltares／Rijkswaterstaat公式THREDDSの元10 NetCDFタイルを、各々本当の**OPeNDAP NetCDF4 1D time座標**を読み取ってSOURCE監査した。各原データのDDS/DASはv174で真正取得・SHA保存済み。元真正OPeNDAPのtime（単位\`days since 1970-01-01\`）から得た時間ラベル全数をSOURCE-safe JSONに保存。[初回真正原本出力 #44006283303](https://github.com/zuizui0223/boids/actions/runs/44006283303) SUCCESS、時間ラベルの意味を明示的に修正して再取得した[Actions #44006485370](https://github.com/zuizui0223/boids/actions/runs/44006485370) SUCCESS。

| 元source結果 | 真正数値 |
|---|---:|
| 元\`time\`ベクトルを全件読み取れたタイル | **10/10** |
| time層の総SOURCE長さ | 各8〜39層（元DDSと一致） |
| 2016年timeレイヤーを本当に含むタイル | **10/10** |
| 2016年レイヤーの元時刻ラベル | 全て **2016-01-01** |
| 2017年レイヤーもあるタイル | **3/10**（KB123_1514, KB123_1716, KB124_1716） |
| 2018以前の最新timeラベル | 7枚は2016、3枚は2017 |
| 各元SOURCEに\`isource\` | あり、**[time,y,x]の3次元** |
| 各元SOURCEに\`z\` | あり、**[time,y,x]の3次元、単位m** |
| CRS | 元\`crs.EPSG_code=EPSG:28992\` |
| 標高データ本体 | **本段階では未取得** |
| RWS港水位との同一垂直NAP datum | **未検証** |

重要な正確さ：2016年のtime値が\`2016-01-01\`だからといって「2016年の1月1日に地形測量が行われた」と断定できない。他の古いレイヤーは厳密な月日（例えば1992-08-01、2000-09-27等）を含む場合があり、2016-01-01は年次の代表時間ラベルである可能性がある。**2016年の各z画素の実際の有効測量・個別測量日の証拠はまだない**。

\`isource\`は以前予想したような「各測量時刻の単一源番号」ではなく、**個々のピクセルごとのSOURCEインデックスが入る3次元グリッド**。従って次段は、ある1時刻の\`z\`と\`isource\`を同じ画素で照合し、空白・有効値・元sourceの差を数え、実GPS地点の地形データを後から対応させる必要がある。元SOURCEの時刻ラベルが2016でも全域の測量が2016年である保証はなく、誤った直結を避ける。

全10元SOURCEのtime座標の元浮動値SHA256、正規日付ラベル、\`isource/z\`の次元は\`validation_v175/results/original_ten_vlieland_survey_time_source_v175.json\`に保存。生DEM・元タグ鳥GPS・元ACCイベント時刻・RWS実水位値は転載していない。以後\`python validation_v175/native_actual_survey_time_source.py --check\`は真の10元NetCDF time座標を再取得して完全一致を要求。

このSOURCE-only段階で干潟のGPS点ごとの標高・冠水の機構や、因果潮汐×太陽／社会Boidsパラメータは**NOT_ESTIMATED/NOT_IDENTIFIED**。
