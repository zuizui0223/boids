# v215｜真正BAW年統計の通常版とno_filter版で、空間的な有効データ範囲が大きく変わる

2026-11-19。正式BAWの2018/2019オランダ領域年別`Hydrodynamische Kennwerte` WCS2、native source `sea_surface_height_peak_YEAR_nl`のnormal filteredと`..._no_filter`を、別文献WEBTICS 2011に掲載された公開3地点の**同じ±500m（1km²）**×20m元格子へ取得して比較。**時刻別500m/20min WMS`sea_surface_height_2d`ではない**。

## 再現性・真正SOURCE
- [GitHub Actions #44465244478](https://github.com/zuizui0223/boids/actions/runs/44465244478) と [#44465250185](https://github.com/zuizui0223/boids/actions/runs/44465250185)：12 original source WCS TIFFの native HTTPS CA source取得、全3地点×2年の2版同一グリッド比較・SOURCE値が完全一致、GitHub Actions **SUCCESS**。
- 初回CIではテスト側で命名した関数が実装名と違うエラー、その修正後のsource runではScientific SOURCE PASSだったが最後のCI検証でフラグキー名が違うエラー。修正済みの上記2 runは元scientific gateまで全てPASS。データの成功に関係しないコードのエラー履歴は隠さず保存。
- 年WCS Cap source原SHA2018 `b22c4571435b5da1d4cc11dfcca985d536f447337a0bf869780b77d4360a6f28`、2019 `af18e4a3280e5bfaef58e525b7079f5e4c4d9b57beea6c7743ae9f2ac16143e4`を両source実行で確認。元native BAW CoverageIds exact names、年・NL、EPSG25832、native singleband TIFF、年内variant同一20m gridを強制。
- original TIFF 12個のbyte SHA、native raster shape/bounds、native source accepted/masked/extreme counts、共通・追加・除外画素数を結果のSOURCE-safe JSONに保存。生GeoTIFFピクセル・元RWS実測時系列・鳥GPS/ACCは保存しない。

## 3公開地点×2年×年統計1km²の結果

| 公開参照地点 | Year | Normal filtered 数値画素 /2500 | `no_filter`数値画素 /2500 | `no_filter`で新規に数値を持つ画素 | `normal`のみ有効 |
|---|---:|---:|---:|---:|---:|
| Vlieland Haven | 2018 | 1052 (42.08%) | 1530 (61.20%) | **478** | **0** |
| Vlieland Haven | 2019 | 1108 (44.32%) | 1506 (60.24%) | **398** | **0** |
| West Terschelling | 2018 | 12 (0.48%) | 1117 (44.68%) | **1105** | **0** |
| West Terschelling | 2019 | 105 (4.20%) | 1117 (44.68%) | **1012** | **0** |
| Wierumergronden | 2018 | 2500 (100%) | 2500 (100%) | 0 | 0 |
| Wierumergronden | 2019 | 2500 (100%) | 2500 (100%) | 0 | 0 |

**SOURCE内部の明確な結果**：全6sourceコホートで通常版の数値画素は常にno_filterにも含まれた（filtered only=0）。沿岸2地点×2年の4/4組ではno_filterによりsource数値範囲が大幅に拡大し、対照的なWierumergrondenでは両年とも全2500画素で一致。West Terschelling2018ではnormalの数値範囲はわずか0.48%であり、**通常版だけで沿岸物理環境を地理的に比較するとモデルproduct-specificな場所の選択が非常に強い**。

## 2つのavailability指標の間にも相違がある

v214の年別source`nof_valid_data_points_YEAR_nl`の有効画素数は、Vlieland Haven **1621**、West Terschelling **1283**、Wierumergronden **2500**。本v215の年別no_filter`sea_surface_height_peak`は、同じ1km²でそれぞれ **1530/1506**、**1117/1117**、**2500/2500**。**同じBAW年統計製品内でも、count値が収録された格子と別の変数no_filterに数値がある格子が必ずしも一致しない**。モデル製品内のmissingnessは単一の二値wet/dryフィールドで説明できるとは限らない。

元v209時刻別WMS`Wasserstand`で2年×6月・9月×6固定UTCの通常数値候補はVlieland **11/24**、West Terschelling **15/24**、Wierumergronden **24/24**。これは**元500m/20min海面時刻値**という別製品・別空間分解能・別時間母集団であり、年統計20m`no_filter`面積からWMS時刻の欠測確率を直接代入しない。

## 科学的限界
- BAWが公開する年別統計の`no_filter`は「年全期間を常時水没したセルだけを残すフィルタ」を外すことを意味するが、この結果から**真の現地干潟面積・乾出時間割合・個体採餌利用可能時間**は定義できない。年別`peak`も独立実測水深ではない。
- 2018/19のoriginal NetCDF`sea_surface_height_2d` raw`_FillValue`が`~1e31`であるか、元WMS値のnative`units`/NHN/NAPをピクセル単位で検証したかは依然**NO**。
- 2011年の公表reference siteは当時の実測センサーまたは鳥GPSトラックの真の局所座標ではない。v169の旧鳥行動モデルはBAW WMSではなく**真正RWS測定港湾水位**を使い、今回の年次WCS sourceマスクはその旧行動予測結果の更新ではない。
- サイト間のSOURCEパターンは同じBAWモデルproductで得られた処理ルールの違いであり、独立現地測量やマクロ生物間相互作用の普遍性を実証するメタ解析ではない。

**次の物理→生態SOURCE条件**：年統計と時刻別WMSを同列に扱わず、まず元NetCDFの個別raw`_FillValue`/unit/vertical datum、時刻別局所h(s,t)とhistorical地形zの同一基準・実地測量日、欠測の生成理由を確定する。欠測した時刻を単純除外せずselection modelを生物行動モデルと分けて検証する。群れBoidsの社会力や潮汐×太陽による時間ニッチの因果はまだ新たに推定していない。
