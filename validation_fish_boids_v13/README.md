# Acoustic Boids v13 — 持続性と機構の監査

**完全に人工のモデル実験。魚の実測結果ではありません。**

結論と原著の訂正は [日本語レポート](../docs/V13_ACOUSTIC_FEEDBACK_AUDIT_RESULT.md) を参照してください。

- v12の12シードの数値を完全再現。
- 新規24シード、32個体、4000ステップ、216軌跡。
- 早い刺激の短期差は、終盤の平均ではほぼ消えました。
- 遅い刺激の終盤差は2シードに集中しており、一般的な自己維持の証拠とはしません。
- 平均場の二つの安定点と往復ヒステリシスは、仮定した方程式について確認しました。

## 実行

コードを取得したリポジトリのルートから実行します。Python 3.12を使用。結果ZIPには全時系列・集計表・図と、コードを特定するコミット情報を収録しています。

~~~bash
python -m pip install -r validation_fish_boids_v13/requirements.txt
python -m unittest discover -s validation_fish_boids_v12 -p 'test_*.py' -v
python -m unittest discover -s validation_fish_boids_v13 -p 'test_*.py' -v
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python validation_fish_boids_v13/run_audit.py --workers 4
python validation_fish_boids_v13/plot_audit.py
~~~

出力先の既存結果は、同じプロトコルの新しい実行結果で置換されます。別々に保持する場合は --output に新しいディレクトリを指定し、描画にも --results で同じディレクトリを指定してください。

## ファイル

| ファイル | 内容 |
|---|---|
| simulation.py | v12と同じ運動・発声方程式、可変の刺激開始時刻 |
| meanfield_audit.py | 接する根を含む固定点、完全な二状態の安定性、往復掃引 |
| analysis.py / run_audit.py | シードごとの対応付き比較、固定実験の実行 |
| plot_audit.py | 保存済み数値から図を生成 |
| results/audit_result.json | 全設定、窓ごとの数値、区間、数理結果、コードのハッシュ |
| results/summary.json | Gitに保持する主要結果の要約。全結果はZIP・CIアーティファクトへ |
| results/per_seed_windows.csv | 24シード別の生集計値 |
| results/full_traces.npz | 全216軌跡の発声個体率・凸包面積。ZIPとCIアーティファクトに収録 |
| results/trace_receipt.json | 全時系列ファイルのSHA-256とバイト数 |
| results/figures/*.png / *.pdf | 時間変化・機構比較・シード別の偏り・平均場の分岐 |
| v12_reference.json | 前回原本から保持した12シード分の比較値 |

NPZの seeds は行順を示します。各配列名は mechanism__timing__metric です。
mechanism は full / no_motor / no_hearing / neither、timing は none / warmup / early（earlyはfullのみ）、metric は call_fraction / hull_area です。各配列は24×4000。保存値は各ステップの更新後の値です。

ブートストラップはシード単位です。時間刻み・個体数を標本数として数えていません。時間・距離はモデルの任意単位であり、魚の実時間・実距離に較正されていません。

[固定プロトコル](../docs/V13_ACOUSTIC_FEEDBACK_AUDIT_PROTOCOL.md) ·
[数理導出](../docs/V13_MEANFIELD_DERIVATION.md) ·
[Draft PR #248](https://github.com/zuizui0223/boids/pull/248)

