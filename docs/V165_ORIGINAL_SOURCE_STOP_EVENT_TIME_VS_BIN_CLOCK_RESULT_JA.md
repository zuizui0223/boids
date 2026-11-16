# v165 原本SOURCE STOPと時刻キーの監査（2026-11-16）

v165の[元GPS/ACC×本物RWS 2018 SOURCE実行](https://github.com/zuizui0223/boids/actions/runs/43883015545)はGitHub Actionsで**SUCCESS**したが、これは**生態学的なモデルで正の潮汐効果を確認したという意味ではない**。元v130の同じ193,088個体×15分ビン・35羽・17週・2018年6–9月を実測SOURCE SHAと合わせた時点までは成功。しかし「t−15分の元の分類イベント時刻と厳密一致する」個体観測は**1,904件**（約0.986%）で、結果前に固定したSOURCE入場25,000件に達せず、元のv165は停止した。

追跡してみると元v129の辞書キーは**native UTC 15-minute bin start**であり、元のv130が保存する `source_utc_event` はビン内の「最初に発生した分類イベント」の実時刻だった。元v129コードは event−binstart ∈ [0,900秒) の関係を保証する。したがって、v165の一致検索は「15分ビンの隣接」を確認しておらず、**この1,904件が希少だから野生のミヤコドリが連続して採餌しないという解釈は論理的に誤り**。

修正は別[PR #179](https://github.com/zuizui0223/boids/pull/179)へ分離し、元のv165のSOURCE STOPを無かったことにはしない。元イベント時刻のUTC 15分境界への切下げによって元のsource bin startを再構成し、**元のSOURCE入場25,000件・同じ月/週/鳥・元v130 Ridge/TIDE+0/3/7/11日**のモデルを変更せずSOURCEを再審査する。STOPでも成功でも旧結果の捏造をしない。

v165に新しい潮汐×太陽因果効果は**NOT_ESTIMATED**、動物社会的Boids力も**NOT_IDENTIFIED**。