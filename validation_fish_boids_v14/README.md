# Acoustic Boids v14 — 刺激による到達の前進と状態維持の区別

**人工モデルの前向き計算監査。魚の実測結果ではありません。**

v13と同じ24シードを16000ステップまで追跡し、刺激終了時に相互作用を切る比較を追加します。パラメータやシードの探索は行いません。

- [固定プロトコル](../docs/V14_ACOUSTIC_MAINTENANCE_PROTOCOL.md)
- [日本語結果報告](../docs/V14_ACOUSTIC_MAINTENANCE_RESULT.md)
- [配置を固定した確率近似の導出](../docs/V14_GEOMETRY_DERIVATION.md)

## 再現

リポジトリのルートからPython 3.12で実行します。

```bash
python -m pip install -r validation_fish_boids_v14/requirements.txt
python -m unittest discover -s validation_fish_boids_v12 -p 'test_*.py' -v
python -m unittest discover -s validation_fish_boids_v13 -p 'test_*.py' -v
python -m unittest discover -s validation_fish_boids_v14 -p 'test_*.py' -v
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python validation_fish_boids_v14/run_audit.py --workers 4
python validation_fish_boids_v14/plot_audit.py
```

既定の結果出力先は`validation_fish_boids_v14/results`です。`--output`で変更できます。既存結果の再利用オプションはなく、各実行で固定192軌跡を計算します。`--v13-reference`には記録されたv13の`full_traces.npz`を指定でき、その既知SHA256が一致した場合だけ追加の原本比較に使います。指定がなくても、v13の関数による全24組の4000ステップ再現を必ず行います。

## 結果ファイル

| ファイル | 内容 |
|---|---|
| full_traces.npz | 全192軌跡の発声個体率・面積・刺激、および位置・速度・発声状態の4時点のスナップショット |
| per_seed_windows.csv | 4機構×4観察窓×2指標×24シードの比較 |
| arrival_records.csv | 3閾値×2条件×24シード。確認時点、打ち切り、刺激前の高活動状態を保持 |
| geometry_diagnostics.json | 実際の配置192レコードについての確率近似、上下端点、残差、安定性 |
| audit_result.json | 全設定、集計、区間、検証、実行前後で照合したソースハッシュ |
| summary.json | 主結果と主要な補助結果 |
| trace_receipt.json | NPZのSHA256とサイズ |
| figures/ | 3種類の図、各PNG/PDF |

NPZには`seeds`と`snapshot_steps`が含まれます。他の名前は`mechanism__timing__field`です。mechanismはintact/motor_cut/hearing_cut/both_cut、timingはnone/pulse。時系列は24×16000、位置・速度は24×4×32×2、発声スナップショットは24×4×32です。スナップショットsはs回の更新が完了した状態で、時系列のs−1番目と対応します。

## 解釈上の範囲

同じv13シードの追跡であり、独立再現ではありません。シード・ブートストラップ区間は生物学的な母集団区間ではありません。高活動の確認時点は、指定200ステップ窓の平均が閾値に達した最初の完了時点で、定常状態への移行時点ではありません。到達判定関数は本実験の32個体による1/32刻みの発声個体率を想定し、一般の実数列の閾値同値判定への拡張は検証していません。

配置を固定した写像は平均確率の近似です。確率的な二値発声の正確な期待値、魚の生物学的応答、移動する全系の吸引状態を同定したものではありません。刺激終了後に受音→発声を切ったときの一致は式から予測される負の対照です。

コードはGitHubで、全数値・図は結果ZIPとActions artifactで保持します。PR #248はDraftを維持します。
