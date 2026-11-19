# v205実測結果 | 同じBAW製品の地形マスク↔年別高潮・低潮線100m近接がVlieland以外2地域で再現

2026-11-19。v204 Vlieland 10km固定ROIで検出したmodel地形マスクと高潮・低潮境界の強いSOURCE近接を、**結果閲覧前に固定した別の2地点**West Terschelling / Wierumergronden（独立WEBTICS 2011公表RD参照位置）で実元WCS/WFSを再取得して検証した。

**真正SOURCEの2回実行PASS**
- [GitHub Actions #44448101079](https://github.com/zuizui0223/boids/actions/runs/44448101079)・[#44448107579](https://github.com/zuizui0223/boids/actions/runs/44448107579)：両方original HTTPのCA/TLS、native WCS2 EPSG25832 2018/19 original TIFF 2年×2地域、WFS2 2018/19 high/low curves source hit counts/geometry、合計4 SOURCE分類×距離ビンと事前固定≥90%基準を合格。先行失敗はユニットテスト関数名のimportミス（後修正）であり、source科学結果の否定ではなかった。
- Github Actions original zip SHA first run `3e4f791f4cc06e3f776748a3100e762a313f596bc0298775c22ba4fb07b6208f`、second `b97b052d1c75b210e779980a7cb66bc2f4dce3ab84b9f074e6ea7abe9c562343`をSOURCE実体ZIPから再計算して一致。結果内部のsite mask counts / replication gateは完全一致。全original TIFF byte SHAは同一サイト・同年の二CIで完全一致。WFS GeoJSON HTTP rawバイトSHAは動くが、`timeStamp`トップレベルのみ除いたsemantic GeoJSON SHAは全て（0件カテゴリは値None）完全一致。

## 元SOURCE実測された画素遷移の3地域比較

3地点とも同じ固定**10km×10kmのEPSG25832原10m格子**で数える。縦列は元GeoTIFFでfinite、unmasked、abs(z)≤100の数字が存在する画素。**これを潮間帯面積とは呼ばない**。

| 原公表reference地域 | 年 | 数字のあるsource pixels | 年変化した数字のあるsource pixelsのうち100m未満 |
|---|---:|---:|---|
| **Vlieland** (先行v204) | 2018/2019 valid 247437 / 219396 | lost31850、gained3809 | lost31433/31850=98.69%；gained3799/3809=99.74% |
| **West Terschelling** (本v205) | 2018 valid374620、2019 valid357832 | lost20723、gained3935 | **lost20569/20723=99.26%；gained3844/3935=97.69%** |
| **Wierumergronden** (本v205) | 2018 valid11576、2019 valid10829 | lost3676、gained2929 | **lost3538/3676=96.25%；gained2922/2929=99.76%** |

2新地域は、結果より前に固定した「lost≥100 & gained≥100 & 各100m近接割合≥90%」を**両方通過**。これは同じBAW modelの異なる公開参照地点のSOURCE処理パターンの地理的再現であり、生態学的な独立メタ解析ではない。

native mask classes：
- West Terschelling: both353897、2018_only20723、2019_only3935、neither621445（総1,000,000）
- Wierumergronden: both7900、2018_only3676、2019_only2929、neither985495（総1,000,000）

**正確な元WFS境界線の実地理SOURCE数**:
- West Terschelling: high2018=26、low2018=23、high2019=21、low2019=30。同ROIに原HIGH/LOW両方ある。
- Wierumergronden: high2018=0、low2018=7、high2019=0、low2019=7。こちらの固定10kmROIでは**HIGH線は検索結果0件でLOW線しか検出されなかった**。本地域のnear100mの再現は、元LOW境界線への近接を表す。HIGH線のないことはBAW製品の未収録や対象区域の違いであり、物理的に高潮が存在しないことを意味しない。

## Source original TIFF sha256
- West Terschelling 2018 `81c96206eaec75a59fc8a2c42f016dcb43c6ecc2e6069fef6b7a3f3e73847e50` / 2019 `d97ff7af7197684414eb0c7f2c3db646bfca87ea5146051af8e3121bbff764f7`
- Wierumergronden 2018 `888308084b5d6e55d770451436c012977660e5a987126902ffcb9a826dab8d57` / 2019 `f12400c62f4e0e650b3eb30db36e61147a9dca284867c60332cbd60f868415a2`

## 明示的な限界と次の決定的な科学的検定

BAW `topography_inter_supratidal` 年別有効画素が高潮線/低潮線付近で入れ替わる地理的パターンは、**同じ公開modelが地形マスクと線形境界の両方を生成した結果である可能性**が高い。異なる3地点でも、その事実が独立現地測量データの3地域再現になるわけではない。したがって「地形変化→干潟面積減少→鳥の採餌時間減少」という因果連鎖はこれらのsourceだけでは成立しない。

真の干潟の年別面積を推定するには、BAW annual intertidal/supratidal coverageの元source classification/physical units/nodata生成ルールとhigh/low水位線のトポロジー、独立標高/測量日を検証する必要がある。さらにGPS地点ごとの実測局所潮位・モデル誤差・個体ACC行動を確認してから、2018fit→2019heldoutの行動モデルを比較すべき。元sourceに含まれない鳥のGPS/ACC、実20m DEMの測量日、元WMS Wasserstandの`_FillValue`や垂直datum、潮汐×太陽による採餌因果・Boids相互作用は**未推定・SOURCE STOP**。

今回のSOURCE元TIFF・WFS GeoJSON曲線、原モデル水位、元個体GPS/ACCはリポジトリやCI成果物に保存していない。最新SOURCEの元JSONハッシュと集計だけを保存。
