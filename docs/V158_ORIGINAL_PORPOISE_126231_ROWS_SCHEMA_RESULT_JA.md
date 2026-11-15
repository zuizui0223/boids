# v158 原本結果：北東大西洋ネズミイルカC-PODの25 MB Data S2を全数取得

2026-11-15、Stavenow Jerremalm et al. (2025) Ecology and Evolution DOI [10.1002/ece3.72566](https://doi.org/10.1002/ece3.72566)、PMCID PMC12664825のEurope PMC公式公開サプリメントZIPから、**実際のData S2 CSV**を全件取得。[GitHub Actions #43723385209](https://github.com/zuizui0223/boids/actions/runs/43723385209) **SUCCESS**。

## 1. 原本ファイルを厳密に確認

Wileyウェブ掲載ファイル名 `ece372566-sup-0002-DataS2.csv` とEurope PMC原本ZIP内の `ECE3-15-e72566-s002.csv` は異なる。最初のソース検証はファイル名不一致により**アウトカムを読まずにSTOP**した。原本アーカイブにある**明示的な1つの別名だけ**を後から許可して再実行した。モデル、応答、選別閾値の変更は行っていない。

| 項目 | 真正CSVでの値 |
|---|---:|
| Europe PMC元ZIPサイズ | 3,010,346 bytes |
| Data S2 CSVサイズ | **26,454,371 bytes** |
| Data S2 元CSV SHA256 | `972b43b0313cb29aa485733b2892fba1f42aea5543da08ab87f8389bb3b7addf` |
| CSVデータ行 | **126,231** |
| 真正CSV列 | **32列** |

元32列には `hr_day_year_SITE`, `SITE`, `COUNTRY`, `GROUP`, `buzz`, `regular`, `clicks`, `buzprop`, `hr`, `YDAY`, `week`, `month`, `year`, `sunrise`, `sunset`, `day_length`, `DPM`, `TempWEEK`, `LAT`, `LONG`, `DAWN.TIME`, `SUNRISE.TIME`, `SUNSET.TIME`, `DUSK.TIME`, `DDDN`, `TempavgWEEK`, `soavgWEEK`, `CHLavgWEEK`, `foraging_click` などが存在する。

## 2. 重大な観測努力の問題

各CSV行の `clicks` は**126,231行のすべてで有限の数値**として入力されており、**`clicks==0` と入力された行は0行**。一方、`buzz==0` と `foraging_click==0` はそれぞれ**22,669行**ある。

これは元Data S2をすぐ「全C-POD稼働時間の0/1出現」に変換できないことを示す。データは**クリック検出がある時間を条件づけた音響機会**としては評価可能かもしれないが、`clicks` が正の全行だけを分母にすれば、C-PODは稼働していたがイルカクリックがなかった時間が欠落する。元論文の総検出回数・データクリーニングによる除外を含めて今後説明する必要がある。

重要なのは `buzz==0` が「イルカがいない」ことではない点。クリックのある時間に検出された採餌buzzがゼロだったことを意味する可能性が高いが、実際の注釈定義と元モデルの単位を確認してから確定する。

## 3. 次段の正しい検証

一次研究は2009–2023年、43観測地点を**6地域**へ統合したネズミイルカ1種の音響採餌研究。一次研究の6地域・43観測点を、**今回source-onlyで元CSVのGROUP/SITE列値を数えて検証したと誤記しない**。次の段階で現地SOURCEの`SITE`, `GROUP`, `COUNTRY`, `year`, `YDAY`, `hr`の実際のユニークキーと時系列間隔を集計し、元論文の43地点×6地域と一致確認する。

新しい第1の生態応答は**クリックが検出された時間内に採餌buzzがあるか**（source定義を検証後）。連続1時間の自己状態は、同一レコーダーで`t-1`もクリック陽性として記録されていた場合のみ測る。未記録時間のclick=0やbuzz=0を勝手に捏造しない。

- 真の音響稼働努力の外部台帳がなければ「採餌buzzの割合（click-positive時間に条件づけた）」以上の人口密度・出現率・完全時間ニッチを論じない。
- `GROUP`や`SITE`が複数地域にまたがる可能性、元の`hr_day_year_SITE`と年・通日・時刻の重複を次段で監査する。
- 元論文で既知の「緯度・日周・日長・水温」の関連を新規発見にしない。潮汐と太陽の効果を分離するには、各地域の地理情報に適合した局所水位/流れの外部観測と録音機器稼働努力の比較が必要。

## 4. 保存

`validation_v158/results/source_43site_sixregion_schema_gate_v158.json` に、取得元URL・元ソースSHA256・32列名・列別非空・欠測・数値・ゼロセルを保存。Data S2の25MBをそのまま転載したり、個々のC-POD音響時刻・海洋哺乳類イベントをGitHubへ配布しない。

`python validation_v158/porpoise_source_gate.py --check` は元CSV再取得と完全スキーマ・内容SHA・分母監査の厳格な照合。今段階は**真正公開データ利用可能性**の肯定結果であり、新しい潮汐×太陽生物学的効果やBoids社会力は推定していない。

全球潮汐×太陽の統合的な行動生物学効果は **NOT_ESTIMATED**。
