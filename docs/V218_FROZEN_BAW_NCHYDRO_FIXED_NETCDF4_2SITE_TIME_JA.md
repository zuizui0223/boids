# v218｜2018/2019年BAW時刻別水位を固定小領域×単一時刻のNetCDF4として直接取得し、生成NCの欠測属性を検証

**v217のネイティブNetCDF4形式・Lat Long time軸の出典確認後、初回WCS GetCoverage実数値を見る前に固定。** 原BAW WCS2は2018/19の同じ水位CoverageIdに対し`application/x-netcdf4`を元Capabilitiesで宣言し、`Lat Long time`の元Envelope、2018/19それぞれのUTC年範囲を提供。v216でfield`Wasserstand` uom`m`、公式OGC NilValue `9.999999848243207E30`を真SOURCEで2回検証済み。今回の新目標は、**WCS2が再生成して返す小領域NetCDF4**の`_FillValue`/units/時間変数を直接読むこと。**BAWのdownload repositoryにある年間元NetCDF binaryの原attrsそのものとは混同しない。**

## 初回GET前のSOURCE固定
- BAW元年別時刻別WCS2 Capabilities（2018 SHA `7b439a8ad1af2fb1e341af5e7b4306535d134ed06d0315df99e2e5488f322388`、2019 SHA `a124a47f4ba037f1403f60b52c8b02750308ee201a88f026c42721f664def37d`）、native NL水位CoverageId（`TrilaWatt_ncHydro_YEAR__sea_surface_height_2d_YEAR_NL`）、native DescribeCoverage 2018 SHA `bf5976a6edd2365ff33b90bf0214042884e0d6d3fc9b3eb3dbb7c28a96245664`、2019 SHA `9a0bd587debfaba85fd877c788273a18c5ae6ea57a8a9efdb88c344da6ec1e91`を元XMLで再照合する。
- 新たに6月1日12Zの1時刻だけ、**2018-06-01T12:00:00.000Z**、**2019-06-01T12:00:00.000Z**。年次source時間軸内・20min格子と一致。後で値の得やすい時刻へ差し替えない。
- 公開2011 WEBTICSの独立参考RD2地点のみ：**Vlieland Haven RD(135280,590000)**（v195時刻別2019 noonは元WMS Nil候補）、**Wierumergronden RD(192882,614562)**（v195時刻別noon両年通常値候補）。EPSG:28992→WGS84の同じsource座標変換、実鳥GPSや実RWS機器2018/19の元位置ではない。
- 各地点中心から WCS native `Lat` **±0.015°**、`Long` **±0.015°**の矩形（格子約500m級でわずか数pixel）。年2×地点2=**4元SOURCE GetCoverage**、全て同じ`format=application/x-netcdf4`、`subset=Lat(min,max)`,`subset=Long(min,max)`,`subset=time("YYYY-06-01T12:00:00.000Z")`。システムに合わないなどのsourceエラーがあればそのままSOURCE STOP。元WMSモデルの異常値に合わせて変数/時刻/位置/範囲/formatや大きな領域へ変更しない。
- 元HTTPリクエストは`coast.baw.de`の同じ認証済year WCS2`/wcs`のみ、default CA TLS ON、redirect一切拒否、各レスポンス最大8MB、HTTP200とnetCDF4 HDF5 signature`\x89HDF\r\n\x1a\n`必須。WCS2が異なる形式・例外XMLを返したらストップ。年間生NetCDF全部の取得禁止。

## SOURCE-native NetCDF4の内的構造に関する事前検証
- `netCDF4.Dataset(memory=original_response_bytes)`でRAMだけで開き、native`dimensions`と各`variables`の名前・ncattrsを取り、**元WCS出力NetCDF4**の`Wasserstand`または`sea_surface_height`に対応する唯一の水位変数を原実名から指定。複数の場合は選別禁止でSTOP。
- 時間次元があれば**高々2**サンプルのみ許可し、元時間軸のvaluesと`units/calendar`を取得し、年2018/19の固定UTCと照合できない場合はnative time SOURCE_UNVERIFIED。空間画素が10,000以上あれば、WCS time/space slicingが失敗したとみなしSTOP。
- 元`_FillValue`, `missing_value`, `units`, `coordinates`, `standard_name`, `grid_mapping`を**存在したものだけ**SOURCE-safe記録。もし元NC4にmissing attrsがなければ、その属性は今回のNetCDF4生成経路では判定できないと報告。元値を仮の`m`/高さとして扱う際も、WCS field unit m / paper NHN≈NAPという別SOURCEと区別。
- ネイティブ水位変数の整数/浮動 dtype、源空間shape、source masked/finite/sentinel/通常範囲候補pixel数、source応答SHA256/bytesのみ保存。生モデル配列やNetCDF4 binaryはGitHub CI artifactに含めない。
- 2018/2019×2地点の元GetCoverageが失敗した場合、その原因を報告し、**片方の成功例だけでモデル水位の普遍性やdry cell現象を主張しない**。
- 正常なWCS4応答を得ても**これはWCSが再出力したサブセットNetCDF4のattributeの元証明**。年間配布元NetCDFの元`_FillValue`/unitsそのものの元バイナリ未取得・確認は依然別工程。2018/19のモデル水位が実RWSで校正された可能性も維持する。

## 後続
真正元NetCDF4のタイムスライスが得られた場合、次段で**同時刻のWMS GetFeatureInfo（v195固定）とWCS本体のsource value/NoDataを、WCS格子とWMSの位置解像度・pixel mappingを確かめてから**比較できる。そこまで行っても現地実鳥GPS h(s,t)／Deltares20m z原測量日・垂直datum／干出時間・採餌ACC／潮汐×太陽・Boids社会力の因果検証ではない。

PR文書・source結果はdraft stackに留め、sourceにない生態肯定結果としてmainへマージしない。
