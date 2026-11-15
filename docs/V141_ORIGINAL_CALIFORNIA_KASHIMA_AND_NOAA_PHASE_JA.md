# Boids v141：California 9地点×魚類コーラスの公開データの真正取得ゲートと実測潮位の空間位相差

**2026-11-15 実行、Source/APIベースの再現可能な検証。** 直前のv139–v140のRoscoff録音1地点の帰結（大潮小潮×昼夜の予測改善は月面照明率×夜との重複から区別できない）を踏まえて、異なる海域で独立検証するためのソースを審査した。**本v141には新たな魚の潮汐×昼夜モデル推定はない。**

## 1. カリフォルニア、鹿島のDryad原本アクセス

- California: Kim et al. 2025, [Marine Ecology Progress Series](https://doi.org/10.3354/meps14910)、真正公開データセット[DOI](https://doi.org/10.5061/dryad.q2bvq83sw)。Dryad REST APIでその最新版の**61ファイル**を列挙（魚類コーラスXLS/XLSX **60**＋README **1**、API version=**7**）。著者による既発表の研究全体は9録音地点・18.3累積録音年・5種類の魚類コーラス（2種類は未同定）、複数の録音配備2018–2023。
- Californiaのoriginal XLS/XLSXは各地点・設置期間の `Detection`（魚のコーラス開始終了 UTC）および `MetaData`（配備期間）を含むと原著データ公開説明に明記。これは**時刻付きのコーラス事象と録音機会を同じ配備IDで結合できる可能性**を示すが、時間外・停止・ノイズマスクを含めた全有効録音時間は原本確認が必要である。
- Kashima: Ota et al. 2026 [Methods in Ecology and Evolution](https://doi.org/10.1111/2041-210x.70230)、[Dryad DOI](https://doi.org/10.5061/dryad.zkh1893qn)。公式APIで**40ファイル**を列挙、うちZIP5件、IPYNB13件、R10件。`q25_autoChorusDetect4.zip`は発声コーラス区間に切り出したデータであり、0/非検出を含む終日の活動率用データとしては現時点で未適格。原著自体は5録音機を統合したホワイトクローカーの音響群サイズ・中心位置を推定しているが、5台は5独立沿岸ではない。
- **取得障害を検証**：両資料の原ファイル例6件（California CI01_01_fish.xls、MB05_01_fish.xlsx、README、Kashima q25 ZIP、ReadMe、file_names）は本GitHub Actions接続から **HTTP 401 Unauthorized**。従って**実際の魚のイベント行、全録音時間、時刻付きの潮汐×日周対比は今回未取得・未推定**。Dryad APIメタデータの取得成功をバイト/生データ取得成功と混同しない。原ファイルを認証抜きで迂回取得したとは主張しない。

### Californiaの録音設置単位（API上のファイル数）

| 9地点コード | 公開XLS/XLSX配備ファイル |
|---|---:|
| CH01 | 3 |
| CI01 | 8 |
| CI02 | 7 |
| CI03 | 6 |
| CI04 | 8 |
| CI05 | 7 |
| MB01 | 9 |
| MB02 | 7 |
| MB05 | 5 |

合計60。これは60独立生物研究や60個体ではない。9地点は同一研究内の地域的に依存し得る地点であり、3つの国立海洋保護区に入れ子になっている。将来の階層モデルには地点/保護区/設置期間と、季節・年・録音努力を別々に組み込む。

## 2. NOAAの真正実測潮位の独立取得（魚音との直接突合は未実施）

NOAA CO-OPSの [Data Retrieval API](https://api.tidesandcurrents.noaa.gov/api/prod/) を使い、**2019-06-01 00:00〜2019-06-07 23:00 UTC の実測・検証済み hourly_height**を、2018–2023年調査と重なる期間の具体例として取得。DATUM=MLLW、単位m、GMT。四つの潮位観測所に168時間ずつ欠測なし、合計**672実測時間**。

| 観測所 | 取得時間 | この週の潮位幅 | 対Montereyの最良1h刻みずれ | 同時刻Pearson r | 最良時刻ずれのPearson r |
|---|---:|---:|---:|---:|---:|
| Monterey | 168 | 2.191 m | 0 h | 1.000 | 1.000 |
| Port_San_Luis | 168 | 2.142 m | 0 h | 0.983 | 0.983 |
| Santa_Barbara | 168 | 2.24 m | -1 h | 0.942 | 0.993 |
| Los_Angeles | 168 | 2.252 m | -1 h | 0.877 | 0.989 |

ずれが**−1h**なら相手の水位時系列がMonterey基準時系列より早く対応するという符号規約。例えばMontereyとLos Angelesは同時刻r=0.877、対象時刻を**−1h**シフトするとr=0.989となる。Santa Barbaraでもr=0.942→0.993。これは**実測の湾・港間の潮位位相差**であり、厳密な伝播時間、沖合録音地点の真の水位/流速・魚の行動遷移ではない。1h刻みなので±数十分の細かな位相は解けない。**一つの潮汐時計を全沿岸に割り当ててはいけない**。

調査海域の音響測点から各潮位局までの正確な距離・水深・潮汐位相オフセット・レベル差が校正されるまで、地点に潮位局の潮位を直結して生物学的効果量を算出しない。絶対水位（MLLW）は観測所ごとに基準があるため、沿岸間で単一生物曝露として比較するには局所正規化・潮相・地形を必要とする。

## 3. 多地点の原本再解析に必要な最小単位と解析候補

**California**：対応する `site_id / sanctuary_id / deployment_id / start_UTC / end_UTC / instrument-active (recording gaps) / chorus start/end_UTC / chorus_type / masking / physical tide gauge mapping / actual solar zenith` から、魚コーラスの陽性・陰性録音時間を再構築。時刻と検出可能性の違いを分ける。元論文には夜間のみの検出が残るが、適切な陽性・陰性区分を原バイトで監査するまで未採用。分類群2種は未同定で、種単位の適応比較に入れない。

設計として各地点で `logit Pr(chorus presence | effort, night, local_tide_phase, tide_amp, lunar_illum, season, detection_mask)` を推定し、相互作用を**潮相×昼夜**と**大潮小潮×昼夜**で別々に評価。保護区を超えるheldout設計が必要。独立沿岸n≥3、互換効果量・SE・光の曝露・同質endpointが揃うまで全球メタ効果を算出しない。

**Kashima**：コーラス中の状態空間的中心位置・群規模と潮位/上げ下げ潮を結ぶことは可能だが、原著の成功例を『新しい昼夜×潮汐の独立効果』と偽装してはいけない。生息場所の中心移動と発声音開始率は別のestimandである。

## 4. 凍結結果・再現コード

- `validation_v141/source_probe.py`: Dryadの実データ一覧・アクセス401・元ファイル検証ゲート
- `validation_v141/noaa_tide_preflight.py`: NOAA 4観測所の実測168h×4と欠損検査
- `validation_v141/noaa_phase_compare.py`: 4観測所の整数時刻ずれの相関検証、相関曲線
- `validation_v141/results/original_dryad_two_datasets.json`: 61/40原本リストとダウンロード401記録
- `validation_v141/results/noaa_hourly_verified_reference_gauges.json`: NOAA原本参照の数値とSHA
- `validation_v141/results/noaa_gauge_phase_comparisons.json`: 実測時刻ずれ
- `.github/workflows/v141-real-coasts.yml`: 原本取得と凍結記録の変更検出（Dryad認証401を成功扱いにしていない）。

v140のRoscoff係数は変更せず、**global tide×solar meta effect = NOT_ESTIMATED**。
