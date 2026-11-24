# Boids 研究統合（v30–v37）：予測できる集団運動と、魚同士の因果的な相互作用は別問題

2026-11-24 JST。**研究ストーリーの統合文書。新しい統計的結果や魚の発声情報を追加したものではない。** 元論文公開の実測結果、後発の解析手法、および構成した数理反例を、証拠の強さに応じて分離する。

## Main question and original contribution boundary

**問い:** 群れの速度情報と近隣魚の配置から将来の個体運動をどこまで予測でき、その結果からBoids型の局所的相互作用を同定できる条件は何か。予測が可能であること自体を「魚が隣魚を感知し社会情報を伝えた」とは解釈しない。

元著者の公開ソースを再利用した本プロジェクトの実務上の前進は、原本認証された魚群追跡、異なる魚種を比較する共通0.2秒の予測仕様、**84録画を元著者の実際の12実験群IDに復元した完全群ホールドアウト**、近隣の正しい速度位置対応と遠方/固定割当入替の対照、さらにこれらの肯定結果に対する数学的な**社会因果矢印ゼロ反例**を同時に提示したことである。既存原著の魚群同調、Boidsモデル、PRX/PLOS 2026のVR実験そのものを新発見として帰属しない。

## 結果の検証階層

| 層 | 原生のソースと再現単位 | 肯定結果／反証結果 | 因果的解釈の限界 |
|---|---|---|---|
| (I) 速度情報の年齢 | テトラ原6録画、アユ原7録画、トゲウオ原3録画の同じG14/0.2秒速度/同じ未来窓を持つv30 | I(0.2秒) 短期テトラ0.3005、アユ0.4642、トゲウオ0.7829、遅延0.2189/0.4442/0.7771。3研究間の大小は統計・記録処理差と混同しうる | 動物の神経「半減期」ではない。3研究横断の正式メタ解析ではない |
| (II) 本物の群れへの外挿 | MacGregor & Ioannou 2021トゲウオ、**元84録画を著者Trial→Groupの12本物の群**へ分割し、全Groupを1つずつホールドアウト（v31–v32） | 現在群れ速度が0.2秒前より良い12/12群両未来窓、I(0.2)短期**0.8502**、遅延**0.8198**、最初の sampled age I≤0.5 =1.0秒。ただし群別の強度と持続率の必然的な負相関は不支持：Spearmanρ短期−0.1748、遅延+0.1608 | 1つの原著・元12群であり、独立野外個体群の一般化ではない |
| (III) 近隣の正しい位置と速度の対応 | 同じトゲウオ元84試行・12群、全体平均速度/G14を固定し、近い3尾、遠い3尾、他7尾速度の1巡回割当対照を完全群ホールドアウト（v33b） | GLOBAL以上の正しい近隣3尾追加MSE改善：短期**0.876%**、遅延**1.652%**、どちらも12/12群。正しい速度位置対応vs固定入替改善：**0.847%/1.601%**、12/12。遠方3尾との差は**0.175%/0.220%** | 空間的共通外部入力、source追跡平滑化、水槽境界などで説明可能 |
| (IV) 因果の同定可能性への反例 | **実魚データなし**の解析的ガウス共通場（v33） | 魚間の因果矢印ゼロでも、近隣追加・正しい速度位置割当優位・近隣＞遠隔の3条件が全て成立 | 社会因果を主張するための必要条件を照らす、実測の反証ではない |
| (V) 同調と凝集の最小機構 | **実魚データなし**の一方向仮想リーダーに追従する線形Boids型制御則（v37） | alpha+gamma>0,beta>0なら、ゼロのreal→virtual feedbackでもu*=0、e*=−gamma*Delta/betaへ収束。双方向の作用は安定結合や速度一致の数学的必要条件でない | 3D、感覚、流れ、リアル魚の運動係数にfitしていない理論例 |
| (VI) 制御された社会応答への次段 | 2026 PRX 1 real+4 virtualとPLOS 2R/C1/C2/C3の著者Figshare元データ（v34–v36 SOURCE-ONLY） | 2 PRX ZIP、2 PLOS小コード、PLOS四つの原DAT **合計194.35MB** を提供元MD5／バイト数／SHA256で照合。PRXデータZIPには実験軌跡候補。PLOS元DATは9数値列にヘッダなし。著者モデルコードは原DAT4条件を読まない | 元の列意味、真のtrial/session/個体ID、時間軸、対称ガウス平滑化状態が未確認。新たなC2/C3実験効果は**未算出**。Issue #250継続 |

## Main ecological synthesis

**集団運動の予測情報は、強度・時間持続性・空間的配置依存性の複数軸で記述される。** 群れ全体の速度が未来を予測することと、特定の近隣魚の現在速度配置が追加的に予測することは、統計的には異なる問い。さらにその両方が成立しても、水流等の空間的共通外部入力を除かない限り魚間の直接的相互作用を一意に推論できない。

**因果としてのBoidsについて必要な区別:**
1. PREDICTABILITY：現在の群れと近隣の記録から個体未来が予測できるか（v30–v33実測が扱う）。
2. SOURCE OF CORRELATION：観測されない流れ・水槽境界・共通刺激が同じ予測関連を生むか（v24/v33構成反例が示す）。
3. DIRECTED RESPONSE：本当に相手の感覚信号を変えた実験で個体応答が変化するか（現在のデータでは我々は**未測定**、2026著者VR論文の本来の貢献）。
4. GROUP ORGANIZATION：同調alignment・凝集cohesion・方向転換・垂直分配のいずれに向くか（単一のBoids相互作用係数で総括しない）。

## 研究に必要な対照実験（提案であり実行済みではない）

- 群れの局所水流・光・餌投下など、魚の位置で異なる外部刺激場を魚軌跡と**同時に独立に測定**する。これに条件づけてもv33正しい近隣速度位置対応の予測改善が残るかを群れ完全ホールドアウトで再評価。
- VRフィードバック有無（PLOS C2とC3）を研究する場合、**仮想魚の旋回率/予測可能性**と実魚の本来の速度選好を媒介要因として扱う。原著C2とC3は仮想魚の実際の転回運動も異なるため、両条件の総効果を「魚の社会的因果力を単純にON/OFFした直接効果」とはみなさない。著者がすでに報告した方向同調と距離の分離は新発見としない。
- v37の一方向 follower law は `e*=−gamma Delta/beta` を予測する。実魚の速度選好、実際の仮想速度、個体間距離を**独立試行単位**で観測できるなら、速度差と距離のスケーリングおよび相互作用強度の上限を検定できる。元PLOS DATのヘッダなし9列を根拠なく解釈しない。元コードと欠落した試行IDを取得するまで、独立の介入効果はSOURCE_IDENTITY_STOP。
- 魚の発声によるコーラスと連動させるには、誰がいつ鳴いたかを同期音源位置推定で得て、運動→発声、発声→運動の両方向を個体/群れ単位でテストすることが必要。現在扱った魚群元データに個体別の同期音源はなく、**Boids→chorus機構は未検証**。

## Main text と補足に分けるべき中身（原稿設計）

- **本文 Fig 1：ソースと独立群れIDの確認。** 元著者84 trial→12 Group IDとコホート定義、未来の予測単位はGroupであること。source-level non-fitted metadata.
- **本文 Fig 2：予測情報の強度と年齢曲線。** トゲウオ原12群を主な独立なsource test、他魚種の6/7録画結果は種差について控えめに併記。v32原GroupごとのMSE符号・Iを主張の中心にし、神経記憶と読ませない。
- **本文 Fig 3：局所・遠隔・速度位置入替対照。** v33bのG/GLOBAL/NEAR/FAR/ROT1/STALE六モデル、短期と遅延、実12Groupごとのpaired MSE。実験的な社会的操作ではないことを図注に明示。
- **本文 Fig 4：同じパターンを生む因果的に異なる系。** 社会矢印ゼロの空間的共通外部場と、一方向 leader/follower の速度選好による距離オフセット。どちらも **CONSTRUCTED** と明示し、原著魚データの新しい効果と混在させない。
- **補足/Methods：** 元source SHAとtrial→Group crosswalk、source速度・時刻、欠損NA、train-only Ridge、row→file→Group集計、v32 group bootstrap、速度置換不変条件、v33b sharded source canonical checks、v34–v36 source-only access STOP。
- **未検証/将来 Fig 5：** 水流/局所外部場の同時観測とVR reciprocal manipulation original session IDsを収集した場合のpredefined paired treatment test。元データが足りない現在、本文結果の図として架空のVR効果を描かない。

## 最終的な立場

この証拠で「魚の群れにBoids型の社会的な因果ルールを新たに推定した」「魚群行動が普遍的に0.2秒で反応する」「発声コーラスのBoids因果機構を示した」と書くのは**不可**。むしろ強い独自貢献候補は、**ソース認証付きの12群独立ホールドアウトにおける複数軸の予測情報と、そこから社会的因果を識別するために必要な条件の明確化**である。

元実験出典: MacGregor & Ioannou 2021 EIDC DOI 10.5285/08305a43-79b5-432f-ad20-2ddffe0d1077; Niizato et al 2024 Sci Rep; Puy et al 2024 PNAS; Escobedo et al 2026 PLOS Comput Biol DOI 10.1371/journal.pcbi.1014544; Kang et al 2026 PRX Life DOI 10.1103/18qw-sfyd. Original code and public DATA DOI are credited to those authors.

Main files: [v32 genuine 84/12 observed](V32_ORIGINAL_84_TRIAL_TWELVE_SHOAL_OBSERVED_RESULT.md), [v33b local/far/permutation original observed](V33B_ORIGINAL_84_TRIAL_TWELVE_SHOAL_LOCAL_POSITION_ASSIGNMENT_RESULT.md), [v33 analytic spatial source null](V33_NO_SOCIAL_ARROWS_SPATIALLY_CORRELATED_COMMON_INPUT_EXACT_COUNTEREXAMPLE.md), [v37 analytic nonreciprocal equilibrium](V37_CONSTRUCTED_NONRECIPROCAL_COHESION_ALIGNMENT_EXACT_RESULT.md), [v36 original author DAT source STOP](v36_verification/PLOS_2026_AUTHENTICATED_AUTHOR_CODE_NO_EXPERIMENT_DAT_LOADER_SCHEMA_STOP.json).

[PR #248](https://github.com/zuizui0223/boids/pull/248) must remain Draft until independently reviewed; main unmerged.
