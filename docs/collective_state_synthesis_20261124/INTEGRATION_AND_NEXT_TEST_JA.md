# 動的な集団情報：魚群運動と既存の生態学的成果を接続する

2026-11-24 JST。これは過去の凍結済み解析の横断的・探索的な再集計と新しい研究設計であり、独立実験・事前登録済み検証・メタ解析ではない。v41までの元資料とmainは変更しない。

## 統合する問い

生物の次の行動を予測する情報は、個体履歴・集団状態・空間的近隣・外部環境のどこにあり、どれくらい持続し、どの行動状態に依存するか。Boidsの分離・整列・凝集の因果係数を魚・鳥・音響で共通に推定したと主張しない。

### 共通の予測上の表現
予測時点までに利用可能な説明変数を用い、各データセット内で以下を段階比較する。
- H: focal history (自己の履歴)
- E: measured environmental state (外部環境)
- G: aggregate group state (集団平均)
- N: correctly matched local information (近隣の速度・位置等)
- Z: observable state (速度・旋回・潮位など)
- f(H,E,G,N;Z) predicts Y(t+h). ZによってNの追加予測力が変わるかを独立した群・地点・期間で評価する。ブロック順序に依存する追加改善であり、因果分解ではない。

情報の強度 S=(L_base-L_true)/L_base、情報年齢による保持 R(a)=(L_base-L_age(a))/(L_base-L_true)、対応関係への依存 Q=(L_control-L_true)/(L_base-L_true) を同一対象・同一損失・同一評価サンプル・同じ重みで定義する。SはL_base>0、RとQは真の改善>0の場合のみ解釈。R/Qは負または1超もあり得る。対照は本物の周辺分布・時空間構造を可能な限り保持するが、個々の対照が壊す構造は異なる。Qは因果効果割合ではなく、異なる対照間の生物学的ランキングでもない。

## 今回の再集計

[機械可読レシート](POSTRESULT_COMPARATIVE_RECEIPT.json)に全数値・元v41の固定コミットとblob SHAを保存。v33b, v168, v155, v157の報告済み同一評価集合の差分から算出したQ（報告値の丸め精度）。Roscoffでは正しい情報の追加自体が負なのでQ未定義。全結果を残す。

| 比較 | 真の追加改善 | 対照に対する改善 | Q | 本物>対照の評価単位 |
|---|---:|---:|---:|---:|
| トゲウオ短期 v33b (MSE) | 29.3105 | 28.3379 | 0.9668 | 12/12群 |
| トゲウオ遅延 v33b (MSE) | 140.1293 | 135.7620 | 0.9688 | 12/12群 |
| ミヤコドリ2019 v168 (MSE) | .007556600 | .001509039 | .1997 | 10/17週 |
| California UF440 v155 (nats/h) | .00470603 | .00081983 | .1742 | 5/9 site-years |
| California White Seabass v155 (nats/h) | .00023892 | .00019552 | .8183 | 6/12 site-years |
| Roscoff v157 (nats/h) | -.00027558 | -.00897434 | NA | 1/5 folds |

トゲウオは位置速度割当の巡回、ミヤコドリは+3/+7/+11日潮汐、Californiaは+3/+5日音型、Roscoffは別日対照。White Seabassは絶対値が極めて小さく、対照超過の符号も一貫しない。比率の高さだけを根拠に証拠強度を判断しない。ミヤコドリの位相特異性は元bootstrap区間がゼロをまたぐ。Roscoffは対照と共通の363観測時間を用いた値。Californiaの追加情報は同時音型で、厳密な将来予報でなく条件付き予測。独立研究数は各資料の数であり、評価単位数を研究数と扱わない。

v41の元12群ID順は独立監査コードで1〜12に固定されている。短期と遅延の5つの条件差、2つの指標の全組合せについてPearsonとSpearmanおよび同符号数、両方正の群数を追加集計。主な値（local beyond GLOBAL）:

| 条件差 | Spearman | 両方正/12 |
|---|---:|---:|
| 低速内の旋回 | .5874 | 7 |
| 高速内の旋回 | .6923 | 9 |
| 小旋回内の速度 | .3287 | 3 |
| 大旋回内の速度 | .6643 | 6 |
| 速度×旋回 | .5944 | 8 |

割当対照指標でも高速内旋回ρ=.7552、両方正9/12、交互作用ρ=.5385、両方正9/12。全10比較はレシートに格納。同じ実験群、同じ軌跡と関連した目的変数を共有するので、独立した再現性の証拠・有意性検定・因果的な情報伝達の持続時間とは呼ばない。

## 従来成果との接続と制約

- 個体状態の持続：カモ類の履歴による予測改善、ミヤコドリの直前15分状態、ネズミイルカのクリック陽性時間に限定した履歴効果。音響は個体追跡でない。ネズミイルカv162–163の時期メタデータ監査後も地点横断には肯定結果があるが年横断は弱い。
- 外部環境による運動：ミヤコドリの上げ潮・下げ潮に関連した方向の違い（2島、v60–63）、潮位の高さの追加情報（v168–169）。正確な潮汐位相への依存と内在時計は区別する。全球潮汐・日照の物理的共起（v100）には調和成分で説明できる強い反例があり、生物の時間ニッチとは同一でない。
- 集団状態と局所構造：v30/v32の魚群速度の情報年齢依存、v33bの近隣と位置の対応、v40/v41の状態依存。v33の空間共通外部場反例は社会相互作用ゼロでも近隣優位が発生することを示す。
- 音響コーラス：Californiaでは自己音型の前1h履歴が他音型の同時情報より安定し、Roscoffでも他音型の対照特異性は支持されない。同じ魚群の運動と個体別発声を同期観測した資料はなく、運動→発声→運動のフィードバックはシミュレーション仮説のまま。
- 既存のBatter・Minaなどは、個体差・集団の空間集中を扱う別階層の現象として接続可能だが、本レシートでは同一の予測課題を再解析していないので、共通法則の追加証拠に数えない。

## 次段階：反証可能な設計

仮説A：環境が安定し、個体の行動に持続性があるとき、自己履歴・共通集団状態が予測を担う。
仮説B：方向・速度などの状態が急変するとき、正しい局所配置の追加予測力が高まる。ただし空間的な共通環境場がこれを代替説明し得る。
仮説C：環境の変化時刻や近隣情報をずらしても予測できる場合は、固有の対応関係の説明力が小さい（対照の種類・強さを明示）。安定性・変化の速さ・空間相関を独立測定する。

次の独立テストは、未使用の魚群データにおける真の近隣/位置巡回の両比較について、速度と過去の旋回を連続量で条件化し、同一の損失・評価対象で予測する。焦点個体の過去情報・集団平均・環境（流れ・餌・壁）を条件づけ、whole-shoal holdout、時系列の漏洩防止、共通環境の対照と、利用可能なら独立したVR介入を要求する。旧データで閾値を選んでから同じ群で検証しない。音響への拡張は同期した動きと個体発声が揃うまで保留。

魚類3種の結果が比較的まとまった主論文候補：*Strength, persistence and state dependence of collective motion information in fish schools*. 横断研究は方法論的な展望・別論文候補とし、分類群をまたいだ単一効果量を推定していないことを明記する。

## 再計算手順
固定元コミット 63db9f617981eaf00ca5a5fb813f005d115e3c37 の
`docs/v41_verification/ORIGINAL_84_TRIALS_12_SHOAL_JOINT_SPEED_TURN_INDEPENDENT_AUDIT.json`（Git blob 836c12deb029f03250f6c64edd3ec285e07db718）から、両horizonの各contrast/metricのoriginal_12_group_signed_ppを順番どおり取得し、12個の値を平均・順位相関・符号比較する。以下は標準Pythonで再現する手順。

```python
import json
from pathlib import Path
from statistics import mean, correlation
j = json.loads(Path("docs/v41_verification/ORIGINAL_84_TRIALS_12_SHOAL_JOINT_SPEED_TURN_INDEPENDENT_AUDIT.json").read_text())
d = j["original_study_source_group_results_by_horizon"]
def ranks(x):
    return [sum(w<v for w in x)+(sum(w==v for w in x)+1)/2 for v in x]
for k, row in d["short"]["frozen_source_joint_conditional_contrasts"].items():
    for metric in ("local_beyond_GLOBAL","true_neighbor_identity_vs_ROT1"):
        a = row[metric]["original_12_group_signed_pp"]
        b = d["delayed"]["frozen_source_joint_conditional_contrasts"][k][metric]["original_12_group_signed_pp"]
        assert len(a) == len(b) == 12
        print(k, metric, mean(a), mean(b), correlation(a,b),
              correlation(ranks(a),ranks(b)),
              sum(x>0 and y>0 for x,y in zip(a,b)))
```

## 主な元記録
- [魚類v33b](../V33B_ORIGINAL_84_TRIAL_TWELVE_SHOAL_LOCAL_POSITION_ASSIGNMENT_RESULT.md)
- [魚類v41](../V41_ORIGINAL_84_TRIAL_TWELVE_SHOAL_POSTV40_JOINT_SPEED_TURN_OBSERVED_RESULT.md)
- [ミヤコドリv168](https://github.com/zuizui0223/boids/pull/183), [v169](https://github.com/zuizui0223/boids/pull/184)
- [California v155](https://github.com/zuizui0223/boids/pull/167), [Roscoff v157](https://github.com/zuizui0223/boids/pull/169)
- [潮汐物理v100](https://github.com/zuizui0223/boids/pull/114), [ミヤコドリ方向v63](https://github.com/zuizui0223/boids/pull/76)
- [ネズミイルカv163](https://github.com/zuizui0223/boids/pull/175)

本資料は保存済み集計値の二次計算のみ。元の動物位置、音響、個体別生データを再取得・再配布せず、モデルの再学習も実施していない。
