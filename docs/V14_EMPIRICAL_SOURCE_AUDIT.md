# v14 実証データソース監査

監査日: 2026-11-22。対象は、同じ魚群における個体位置・群れの凝集度と、発声・音声再生の時刻を対応づけられる公開データ。

## 結論

**8件の検索と一次資料の確認では、直接的な発声促進・個体内の持ち越し効果と、音響を介した空間的フィードバックを識別できる、公開かつ再解析可能な結合データセットは見つからなかった。** データの不存在を示す結論ではない。候補には同時観測や公開ファイルがあるが、原データへのアクセス、共通時刻・個体識別、または実験デザインの確認が不足している。

この監査は v14 の実験的動機を補強する資料であり、モデルの実証的検証や生態学的パラメータの同定を追加するものではない。

## 候補と確認結果

| 研究・魚種 | 観測・デザイン | 公開状況と適合性 |
|---|---|---|
| [van Oosterom et al. 2016](https://doi.org/10.1038/srep19098)、bigeye *Pempheris adspersa* | 24尾×4群。再生10分・無音10分を7回反復。連続録音と60秒間隔の俯瞰画像を取得し、群れの占有面積と10分単位の発声数を集計。 | [本文](https://pmc.ncbi.nlm.nih.gov/articles/PMC4707522/)から原データの公開先を確認できず。目的に最も近いデザインだが、個体軌跡・発声個体・イベント時刻を結合した公開データは未確認。同時変化だけではフィードバック機構を識別できない。 |
| [Schulze et al. 2018](https://doi.org/10.1038/s41592-018-0144-6)、論文表記 *Danionella translucida* | 暗所での群れ行動と、雄間の闘争・発声を観測。[著者リポジトリ](https://github.com/danionella/schulze-henninger2018)に移動解析と発声検出のデモ。 | 移動動画は10秒の抜粋。別途公開された音声との共通試行・時刻対応は未確認。別々のデモを結合観測とみなせない。 |
| [Groneberg et al. 2024](https://doi.org/10.1242/jeb.247782)、*D. cerebrum* | 成長過程の録音と形態計測。[著者リポジトリ](https://github.com/danionella/groneberg_et_al_2024)にクリックデータと図生成コード。 | 公開ファイル一覧と図生成ノートブックを確認。原音声・検出コードは著者への依頼による提供。同期した位置・凝集度のデータは確認できず。HDF5本体・列構造は未確認。 |
| [Cook et al. 2024](https://doi.org/10.1073/pnas.2314017121)、*D. cerebrum* | 発音機構の研究。出版社の補足資料に、飼育水槽の動画と音声スペクトログラムを示す Movie S1（MP4、22.88 MB）。 | 同期した視聴覚資料の候補だが、説明文だけでは個体識別・群れの軌跡・再生介入・反復試行を確認できない。動画本体と直接のファイルURLは未確認。補足資料には Dataset S01（XLSX、30.34 KB）、S02（AVI、38.47 MB）、S03（GZ、8.66 MB）も掲載。 |
| [Azofeifa-Solano et al. 2026](https://doi.org/10.1038/s41598-026-38774-3)、*Dascyllus aruanus*・*D. reticulatus* | 野外の求愛発声を4本のハイドロフォンとカメラで観測。機器時計と同期用の打音で音声・動画を整列し、発声中の音源を定位。 | [本文](https://pmc.ncbi.nlm.nih.gov/articles/PMC12963378/)はデータを著者から提供すると記載。公開原データのリポジトリは未確認。発声中の音源軌跡は、無発声期間を含む全個体の追跡とは異なる。補足資料本文は取得できず、内部リンクも未確認。 |

## 公開ファイルの存在を確認できたもの

以下は著者リポジトリのファイル一覧で、名前・サイズ・取得先を確認した項目。**一覧への掲載確認は、ファイル内容の検証や、位置と発声の同期確認を意味しない。** 音声・動画および下記HDF5の本体は未確認。

### Schulze et al. 2018

| ファイル | サイズ（bytes） | 公開URL |
|---|---:|---|
| `movement_analysis/testvid.avi` | 8,148,198 | [取得先](https://raw.githubusercontent.com/danionella/schulze-henninger2018/master/movement_analysis/testvid.avi) |
| `movement_analysis/fish_track_analysis.m` | 5,742 | [取得先](https://raw.githubusercontent.com/danionella/schulze-henninger2018/master/movement_analysis/fish_track_analysis.m) |
| `vocalization_analysis/Fig2E_raw.wav` | 325,500 | [取得先](https://raw.githubusercontent.com/danionella/schulze-henninger2018/master/vocalization_analysis/Fig2E_raw.wav) |

### Groneberg et al. 2024

| ファイル | サイズ（bytes） | 公開URL |
|---|---:|---|
| `24hrec_CompiledClicks.h5` | 8,481,120 | [取得先](https://raw.githubusercontent.com/danionella/groneberg_et_al_2024/main/datafiles/24hrec_CompiledClicks.h5) |
| `RM_CompiledClicks.h5` | 13,801,976 | [取得先](https://raw.githubusercontent.com/danionella/groneberg_et_al_2024/main/datafiles/RM_CompiledClicks.h5) |
| `CR_100CenterClicks.h5` | 15,282,440 | [取得先](https://raw.githubusercontent.com/danionella/groneberg_et_al_2024/main/datafiles/CR_100CenterClicks.h5) |

[同じ公開一覧](https://api.github.com/repos/danionella/groneberg_et_al_2024/contents/datafiles)には `24hrec_Morph.csv`、`Adult_SL.csv`、`CR_Morph.csv`、`RM_Morph.csv`、`CR_example_traces.npy` もある。クリックデータは音響のみを対象とする探索には利用候補となるが、結合データとしての適格性は確認できていない。

### 掲載は確認できたが、内容を取得できなかった補足資料

Azofeifa-Solano et al. 2026 の [41598_2026_38774_MOESM1_ESM.docx](https://pmc.ncbi.nlm.nih.gov/articles/instance/12963378/bin/41598_2026_38774_MOESM1_ESM.docx)（2.4 MB）。本文によれば視聴覚例と対話型3D図を含む。補足資料の未確認部分に再利用可能なデータがないとは判断していない。

## 探索範囲

検索は次の8件に限定し、その後は候補の出版社・著者・データリポジトリを確認した。第三者の索引だけを、利用可能なデータの証拠とはしなかった。著者照会によるデータ取得は対象外。

1. `"10.1038/srep19098" supplementary data`
2. `"van Oosterom" bigeye fish acoustic shoal cohesion data supplementary`
3. `"Pempheris adspersa" ("data" OR "dataset") ("Dryad" OR "Zenodo" OR "Figshare" OR "OSF")`
4. `fish vocalizations shoal cohesion synchronized tracking playback data repository`
5. `"contact calls" fish "Data availability" cohesion`
6. `"Danionella" "vocalization" "data availability" tracking`
7. `"fish" "shoaling" "vocal" "dataset" trajectories`
8. `"Uncovering the acoustic ecology of sympatric coral-dwelling fish" data`

Mouy 2023 / OSF q8dz4 と、既に確認済みの toadfish の持ち越し・初期発声状態に関する文献は再監査していない。検索で見つかったbigeyeの聴覚特性（2013、Dryad）と聴取可能空間（2023、Figshare）のデータは、同一魚群の空間配置と発声を結ぶという条件から外れるため、詳細監査の対象外とした。

## v14 への適用

原データの公開状況が未解決の2016年bigeye実験を、機構の識別を考えるための主要な実験例として維持する。公開クリックデータや視聴覚デモを、空間的フィードバックの検証済み証拠として扱わない。v14 の結果は引き続き合成モデル内の結果であり、この監査によって魚群での因果効果や機構の実証的同定が成立したとは主張しない。
