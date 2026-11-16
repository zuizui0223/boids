# v162 元研究のTable A1観測期間と真正CSV年月の一致検証＋保守的モデル感度（新しい効果の結果を見る前に固定）

2026-11-16。Stavenow Jerremalm et al.（2025, DOI [10.1002/ece3.72566](https://doi.org/10.1002/ece3.72566)）の査読論文**Table A1「Data from / Data until」**43地点の公表設置年月と、出版社付属Data S2の真正**元SITE×year×YDAY**を比較する。元CSVは126,231行／26.45 MB、SHA256 \`972b43b0313cb29aa485733b2892fba1f42aea5543da08ab87f8389bb3b7addf\`。新しいv162の予測効果をまだ見ていない段階で以下を凍結するが、v160/161の結果や一部SITE不一致は既知のため、**事後の保守的な品質感度**である。

## なぜ必要か：元公開記録の再現性だけでは生物学的な意味の確認にならない

原著Table A1ではSWEの**HONO**は**2022年10月〜2023年9月**、**NVSK4**は**2021年8月〜2022年10月**。一方真正Data S2ではHONOの2015〜2018、2020〜2021年、NVSK4の2019〜2020年にも元レコードが存在する。BHBの**LS4**にも公表2010年3月より早い2009年、FRANORTHの**AWAC**には公表2013年12月を超える2014年のレコードがある。また原著Table A1の最後のFRASOUTH SITE表記は**MSC4**だが、元CSV SITE列は**MRC4**である。

**この相違を元CSVの音響レコードが偽物・誤りと断定しない。** 同じSITEを別期にも使った、原著の表で一部デプロイを省略した、SITEコードの再利用、公開処理時のラベル割当、表の誤記など、解決していない可能性がある。重大なのは、**source行を数値として再計算できることと、公表デプロイメントに対応した生物学的同一地点×年度の記録であることは別**、という点である。

## 再現性を優先する固定手順

- 元論文Table A1の43地点の始期・終期を**年月単位**で手動転記、ICEは元CSVの17数値SITEコードと原TableのユニークなSKJAL/EYJA名末尾番号と照合。元MRC4は論文MSC4との名称差を明示（年月だけは対応可能と暫定設定）。
- 真正Data S2を元SHAで再取得し、全126,231行で元\`year\`と\`YDAY\`から実際の暦年月を厳密に再構成。各SOURCE SITEの原CSV先頭・末尾年月、公表Table A1の期間外の行数・年度をサイト別に列挙。
- **一次の保守的感度：元SOURCE SITEのどれか1行でもTable A1月区間の外側なら、そのSITE全体を学習と保留の両方から除く**。全43SOURCE SITEのフラグと、excluded source click-positive hoursを必ず保存。これは原元データの削除・訂正ではなく、新しいstrict subset感度。v160/v161元の固定SOURCE QCモデルと既存結果は変更しない。
- そのstrict subsetで、v160（同じGROUPの他SOURCE SITEで学習して1 SITE全保留）と、v161（同一SITEの過去年のみで後の元年を保留）を、**まったく同じモデル・ソース陽性／陰性ゲート・L2=C0.25・clock harmonic／クリック説明変数**で再評価。元SITEが少なくなり評価不能なら**STOP**して母集団を有利な方向へ変更しない。
- 結果は地域ごとのSITE等重みの予測proper log-loss利得と、SOURCE STOP数のみ。4地域が合格しても6の独立な検出状態法則・世界的潮汐×太陽法則とは呼ばない。
- 原CSVのクリックなし機器稼働時間は欠落。元Click陽性時間内の採餌buzzのみで、個体の実際の採餌、個体の記憶/社会性、局所潮汐は一切推定できない。

## 既存結果を更新する条件

1. 元データで公表月区間外のSITEがほぼ存在しなければ、v160/161主分析をそのまま残す。
2. HONOなどが異なる期間を含むことを全件確認でき、除くと**Swedenの前1h保留利得が消える/変わる**なら、先行の肯定結果の普遍性を必ず格下げする。
3. 論文のTable A1で本来その期間も含まれる追加原デプロイを確認できた場合、元本の情報源とともに別途**メタデータ改訂**として議論する。今回のstrict sensitivityの事後閾値をこっそり緩めない。

## 原本・機械検証

\`validation_v162/paper_tableA1_source_consistency.py\`（原CSV再取得/元SHA、全43公開年月、元月別数、厳格SITE除外、元v160/161の固定モデルを再学習・SITE/年全保留）。出力 \`validation_v162/results/original_tableA1_date_source_sensitivity_v162.json\`（source safe全SOURCE QAと保留スコア）、小型\`frozen_published_metadata_receipt_v162.json\`（初回全文モデルSHAとQA・地域結論）。

\`python -m unittest discover -s validation_v162 -p 'test_*.py' -v\`でSITE metadataの転記・年月ロジックをSOURCE非依存で検証。初回\`--emit\` →元結果の固定後\`--check\`で元CSV SHA完全一致、SOURCEカテゴリ一致、モデル再計算スコアのみ跨CPU最大差1e−7。

**新しい全球潮汐×太陽生物学的統合効果はNOT_ESTIMATED。個体間Boids社会力はNOT_IDENTIFIED。**
