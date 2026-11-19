# v218 真正SOURCE結果｜BAW時刻別NL水位WCS2が返すNetCDF4の属性と小領域データ

2026-11-19。v216/217で元BAW year2018/19年水位WCS2をSOURCEで二度認証（original source native SSH field`Wasserstand`, unit`m`, NilValue`9.999999848243207E30`, `Lat Long time`, source NetCDF4 MIME）。**初回WCS実データ取得前に**固定した2011WEBTICS公表2参考地点×2年×単一時刻June1 12UTC、±0.015°のsource-native Lat Long ROIについて、ネイティブNetCDF4を本当にWCS2から取得し、RAM内でsource変数attrsとFillマスクを読んだ。

## 出典2回再現・真正source
- [GitHub Actions #44475869713](https://github.com/zuizui0223/boids/actions/runs/44475869713) と [#44475927794](https://github.com/zuizui0223/boids/actions/runs/44475927794) は両方source/CI SUCCESS、4つの小領域WCS NetCDF4 bytes shaと属性・数値値域・mask counts **完全に一致**。
- 年2018/2019元WCS GetCapabilities & DescribeCoverage original SHAはv216/v217と完全一致。元WCS2が正式にadvertiseした `format=application/x-netcdf4`、`subset=Lat(...)`, `subset=Long(...)`, `subset=time("YYYY-06-01T12:00:00.000Z")`を使用。native WCS response Content-Type`application/x-netcdf4`、HDF5 magicで原source小NetCDF4を検証し、年間巨大full NetCDFはダウンロードしない。
- 4 source outputすべて、native float32水位変数（ただしWCS re-packagingで変数名はVlieland `sea_surface_height_2d`、Wierumer `Mosaic(sea_surface_height_2d)`）、`_FillValue=9.999999848243207E30`および`units=m`の**実NetCDF4変数属性を直接確認**。これは別のOGC source metadata(v216)と完全一致。
- native`time`次元は年×siteで**1**、空間元格子はVlieland `lat=7×lon=7`、Wierumer `lat=6×lon=7`。同じ原時刻の単一断面のみで、小データが真に時間・空間subsetされたことも確認。

## source 2018 vs 2019小領域の元時刻断面（真のNetCDF4数値）
| SOURCE native site/year June1 12UTC | native source格子 | `abs(h)<=10` 通常数値画素 | NetCDF4元極端Fill値の画素数 | source通常数値の中央値（単位m、真NAP校正なし） |
|---|---:|---:|---:|---:|
| Vlieland Haven 2018 | 7×7=49 | **39** | **10** | +0.163667 |
| Vlieland Haven 2019 | 7×7=49 | **27** | **22** | −1.018316 |
| Wierumergronden 2018 | 6×7=42 | **42** | **0** | +0.574807 |
| Wierumergronden 2019 | 6×7=42 | **42** | **0** | −0.943413 |

この元値は同一モデル製品が再出力したもの。VlielandのNetCDF4元Fillが2018年10/49、2019年22/49、Wierumerは両年0/42という空間的差を明示。**2018と2019の6月1日12UTCは潮汐位相や大潮小潮・2019気象強制も異なるので、Fill画素数の年差を「干潟減少」と解釈しない。**

Native source response SHA：
- 2018 Vlieland `29388442bf9183eb479381d628fcf99cf859cf2ce50aa14a465e04818321f4e6`
- 2018 Wierumer `01fb3b6defdf5240c13db178f8bf1e899f7ec179dd56ce5be01d9c46602534d4`
- 2019 Vlieland `c43c939f82698af57ce7519876e4e89827aab059ed32c466938c8181b6792cc1`
- 2019 Wierumer `23b82b670d89d1cad4c021ace1d5ba1004748a543e3e8445361b6a619ec1d600`.

## 科学的なSource STOP
本v218は**WCSが生成したfixed小NetCDF4の実変数属性を直接読んだ**ことを意味するが、公式BAW download repository配布の**巨大元年NetCDFそのものの同じ変数の`_FillValue`/unit metadata**を直接照合したことにはならない。また本native unit`m`はsource地理的NHN≈NAP製品level(v208)と整合的だが、2018/19実RWSセンサーlocal datum・lat/lon位置との完全一致、各鳥GPSセルのh(s,t)の検証とは違う。

特にNetCDF4の元Fill値の理由は**サービスsource no data**というメタデータの指定であり、すべてが物理的dry exposureではない。Fill箇所が水際の湿乾なのか、coverage mask・元グリッド領域・処理の結果なのかは今後別SOURCEで区別。v209/210は実RWS潮位が低い時にWMSの同じFill値が集中し、モデル通常値のみ残すselectionが元RWS mNAPのグループ平均+0.52865m選択差を生むと別SOURCEで示しているが、**実GPS上でdryflatが見えて個体が採餌したことの証明ではない**。

次は同じ正式WCS NetCDF4形式・source-bound public 3reference sites（Vlieland/West Terschelling/Wierumer）×年2018/19×June1固定UTC6時間で**元WCS水平格子に対するモデル数値可用率の時間変化**と同時刻元RWS cmNAP実測を結ぶ。源時間ニッチの予測誤差や群れBoidsの社会力は未解析。生元NetCDF4データ・元RWS/鳥GPS/ACCはGitHubへ保存しない。
