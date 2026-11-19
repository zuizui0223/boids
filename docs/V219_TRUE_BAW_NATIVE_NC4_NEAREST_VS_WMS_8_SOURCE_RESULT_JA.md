# v219 真正SOURCE結果｜WCS生成NetCDF4のnearest原格子点はWMS元地点照会と8/8で一致

2026-11-19。v216–v218にて2018/19年別真正BAW `ncHydro` WCS2の`Wasserstand`の`units=m`、OGC NilValue`9.999999848243207E30`、WCS生成NetCDF4の変数`_FillValue`も一致することを元SOURCEで確証した。v219はこれを元の**WMS1.3.0地点照会**と、事前固定の2011 WEBTICS公開2地点（Vlieland Haven, Wierumergronden）×2018/2019年×June1 UTC00:00/12:00で真正原本値として照合した。

## 真正SOURCEと2回再現
- [GitHub Actions #44511898187](https://github.com/zuizui0223/boids/actions/runs/44511898187) と [#44511972691](https://github.com/zuizui0223/boids/actions/runs/44511972691)：両方SOURCE/CI success、BAW元2018/19 WMS/WCS Caps・WCS Describe source SHA厳格照合済、固定8個元NetCDF4を小領域取得→RAM内で原`lat`/`lon`座標のnearest gridpointを選択。8 WMS GetFeatureInfo native response数値/正式極端Nilと比較。**8/8 source分類一致、5/5双方数値ケースの差が0.05m以内、3/3両者Nil**。2source runでこの集計と時刻×サイトの分類は全て一致。
- 2回のsource-safe ZIPは別SHA (run44511898187 `4ddbb421a8a75a604e8258a6f1b873246cb6400478ad704568f724b9b33aaf83`; run44511972691 `c0076d846ca516c6e38b4eac5cc1088abd2ff2ef09bd8e35dcb8e41c9d17fcf8`)、WMSの動的HTTPレスポンスSHA変動を考慮して**source-safe ZIPの同一byteをCI合格条件とはしていない**。元sourceが示した物理的分類と数値差が同じことと、レスポンス全バイトが同じことは異なる。

## Native源同時刻8組のWMS vs WCS
固定時刻はすべて6月1日のUTC。

| 年 | 地点 | 時刻 | WCS生成NetCDF4 nearest | WMS GetFeatureInfo | 数値差WCS−WMS（m） |
|---|---|---|---|---|---:|
| 2018 | Vlieland Haven | 00Z | 正式源Fill値 | 約1e31源Nil候補 | — |
| 2018 | Vlieland Haven | 12Z | 通常数値 | 通常数値 | `+1e-8` |
| 2018 | Wierumergronden | 00Z | 通常数値 | 通常数値 | `+3e-8` |
| 2018 | Wierumergronden | 12Z | 通常数値 | 通常数値 | `+4e-8` |
| 2019 | Vlieland Haven | 00Z | 正式源Fill値 | 約1e31源Nil候補 | — |
| 2019 | Vlieland Haven | 12Z | 正式源Fill値 | 約1e31源Nil候補 | — |
| 2019 | Wierumergronden | 00Z | 通常数値 | 通常数値 | `+2e-8` |
| 2019 | Wierumergronden | 12Z | 通常数値 | 通常数値 | `−5e-8` |

元WCS small NC4 nativeは同じ原sourceで`units=m`、正式`_FillValue`が約1e31、時間次元はちょうど1。WCS nearest格子点とWMSの51×51 virtual image center queryは*一般には同じcellと保証されない*が、今回の固定8件ではNilの分類と数値が見事に一致。これは原モデルを配信する2つのOGC方式の**数値再現性**を強めるもの。

## 時刻・場所の一般化を狙う次のSOURCE
v220ではWest Terschellingを追加し、2018/19×June/September×00/12 UTC×公表3サイトの**固定24 source cases**をWCS NC4で取得。元WMSの同時刻分類はv209真正SOURCE run #44452986729のSHA固定archiveをダウンロードして再使用し、WMS/RWSの生値取得は行わない。各原NC4の`_FillValue`とunits属性はnative元source checksで確認し、source分類が一致した数・不一致を全24件記録する。ソースが未取得またはCI queuingの場合は新たなpositiveを主張しない。

## 科学的STOP
1. この結果は**同じBAWモデルのWCSとWMSの内部再現**。独立な現地RWS測定による局所・粒度別のNetCDF4検証とは違う。v206/207の別原RWS数値比較では、2018/19のメートル仮定の暫定RMSE（~0.034–0.156）があり、原NHN≈NAPはv208原著製品levelの記述に限る。
2. WCS原source `_FillValue`が存在するから、Nilが本当に水の引いた干潟であるという確証はなく、元coverage grid外・GeoServer masking・model wetting/drying等を区別できていない。
3. 同一GPS cellの物理`h(s,t)-z(s)`は historical Deltares 20m `z` native datum/field survey dayとモデルlocal tideの場所変化を別途出典で整合する必要あり。ミヤコドリACC、花や昆虫、日の出と潮位の相互作用、Boids社会力による行動時間ニッチの因果はまだ検証していない。**結果をmainへ因果肯定としてマージしない**。

この結果によってv209/210で報告した低潮に集中する元WMS NoData候補が、少なくとも8件で実際のモデル格子のNilと一致することが分かったが、v209/210の統計を新たな独立テストと見なして二重計数しない。
