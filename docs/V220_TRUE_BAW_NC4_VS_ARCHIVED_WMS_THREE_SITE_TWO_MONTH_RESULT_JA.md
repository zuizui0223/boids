# v220 真正SOURCE結果｜3公表地点×2018/2019×June/September×00/12UTCでBAW WCS NC4 Nil vs WMS 24/24一致

2026-11-19。v216年別水位WCS sourceのField unit=m / NilValue `9.999999848243207E30`、v218 true WCS generated NC4 source`_FillValue`、v219 WCS vs WMS original same-time 8/8の後、**事前固定の新しいWest Terschelling地域とSeptember時期を含めたseason×site source replication**を実施。

## 真のSOURCEと再現性
- [GitHub Actions #44513059990](https://github.com/zuizui0223/boids/actions/runs/44513059990)、[#44513129807](https://github.com/zuizui0223/boids/actions/runs/44513129807) は、いずれもユニットテスト/原source SHA/24 bounded NetCDF4取得/厳密なsource scientific gate **SUCCESS**。2回のsource実行の**24全UTC classと各小領域Nil数が一致**。補助データはGitHub Actions v209成功run #44452986729のSHA固定元 `original_RWS_tide_mNAP_vs_BAW_WMS_extreme_NoData_72points_v209.json`（SHA256 `5e4a492eae99e17b6f79444ac22a342ce5c88f570181fe44a8cc633b1932a62c`）に保存されたWMS original classified source-onlyであり、**今回新たなWMS 72時刻やRWS実潮位は取得しなかった**。
- 年2018/19 BAW WCS Cap/Describe元source byte SHA(v216–219)は再照合、NetCDF4の真の原 WCS generated NC4で`units=m`と`_FillValue`と緯度経度/time=1を実測。HTTP TLS標準CA認証ON・本物のHDF5 NetCDF4だけ受理、原binaryはrunner RAMのみに留めてGitHubにはSHA/種類/格子カウント以外保存していない。
- WCS nearestへの座標変換は2011 WEBTICS RD公表3点（VlielandHaven, WestTerschelling, Wierumergronden）→WGS84、同じ±0.015° crop、中心座標に一番近い元native格子のみ。**WMSのvirtual image centerとWCS nearestが一般に同一格子とは限らない**ことを認め、全結果・不一致・不足を正しく記録。

## 24件の元source consistency結果
- **24/24** site/year/month/hour: WCS generated NetCDF4 nearest-classとv209原本WMS時刻別classが完全一致。
- **6/6** original WMS extreme ~1e31 candidate は実WCS nearest元`_FillValue`と一致。
- **18/18** original WMS usual numeric classes は元WCS nearest通常数値と一致。
- **class discordance 0/24**。本v220は元WMS生数値をロードしていないため、v219の5件と異なり**数値そのもののWCS-WMS差は計算していない**。一致したのはあくまで原source valid-vs-Nilという二値分類。
- Wierumergrondenは対象8UTC全てで通常数値(8/8)かつ小領域sourceのNil画素0。
- VlielandHavenは選択8UTCのうち、2018June00、2019June00/12、2019September00がNil、他は通常数値：**4/8 Nil**。
- West Terschellingは2019June00/12のみNil、その他6/8通常数値：**2/8 Nil**。

## 元小領域のSOURCE Nil画素は地点source Nilとは異なる
- West Terschelling2018June00/12は小領域のNilが約27 source pixels（本crop native cell集計）存在しても、**公表地点の最寄りモデル格子は通常数値**。2019June00/12では周囲Nil39 source pixelsで最寄り格子もsource Nil。これは**時刻別局所のモデル格子値が得られるかどうかと、任意の近傍領域の空間的Nil割合が同じものではない**ことの具体例。
- 同様にVlielandは2018June12では小領域Nil10 native pixelsを含むがnearestは通常数値、2018June00ではNil11を含みnearestもNil。これは単に小領域Nil値が1個でもあれば公表地点もNoDataと判定することの反証である。
- 以上のnative model Nil fractionは**本来のモデルcoverageの一部分**であって、真の干潟の浸水面積や餌利用可能面積ではない。

## 既存知見との結合と主張の上限
v209ではBAW WMS source Nil22/72が実RWS measured NAPの低潮時に強く偏り、8/8沿岸sourceグループで sentinelとusual numericが分類された実RWS潮位差はgroup median −1.21m。v210ではそのSOURCEを単純除外するだけでsite-year-monthの原RWS水位平均が沿岸8群等重み+0.52865m高くなるという**算術的選択差**をSHA固定集計で確定した。今回のv220はそのWMS NoData分類が**小さな正式WCS generated NetCDF4の元格子Nil**と本地域×時期の24件において一致することをsourceで強く確認し、*単なるWMSレンダリングの不具合だけ*で説明するのが難しい点を示す。

それでも**モデル格子Nilの元因果は未確定**。wetted/dry grid、計算範囲外、補間処理やcoverage maskなどの複数要因を分ける必要がある。WCS generated NC4 `_FillValue`が公式配布年NetCDFの元属性を直接検証したことにもならない。2025公開retrospective hydrodynamic sourceなので2018時点のforecastではない。原Deltares20m DEMのtrue survey day・vertical NAP、真のタグ鳥GPSセル`h(s,t)`, 小スケール餌分布/採餌ACC、日光×潮汐と群れBoidsの因果解析は依然SOURCE STOP。

**次段はsourceだけ増やすのでなく、実鳥GPS/ACCとモデルNil/heightをどうjoinできるかの入力・検出過程を監査すること。** 最大の新規性は、潮汐による行動時間ニッチの真の分化と、低潮時の環境値が欠測するために生じる見かけの分化を同一の行動データで区別することにある。重複する物理ソース検証を独立生態効果と二重計数しない。

本source-positive branchはDraft PR #243のまま保持し、mainへ因果効果としてマージしない。
