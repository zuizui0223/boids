# v217｜実BAW時刻別TrilaWatt WCSの出力形式・時空間軸メタデータを原本検証する

v216元NetCDF由来のyear2018/19水位`sea_surface_height_2d_YEAR_NL`の**真正BAW WCS2**を、原WMS SHA/源WCS Cap SHA/native DescribeCoverage SHAで認証。**2018/19ともWCS元field`Wasserstand`のunit=m、正式source NilValue=`9.999999848243207E30`**が二度再現された。ただし元NetCDF配布ファイルの`_FillValue`や`units`を直接読んだわけではない。v217では元WCSからどの物理量の**time/space subset**と**NetCDF形式**を安全に要求できるかというネイティブ出典だけを調べ、まだGetCoverage本体を呼ばない。

## 結果の閲覧前に固定した出典source
- 元2018 BAW `https://coast.baw.de/geoserver/TrilaWatt_ncHydro_2018/wcs?service=WCS&version=2.0.1&request=GetCapabilities`; 元original XML byte SHA `7b439a8ad1af2fb1e341af5e7b4306535d134ed06d0315df99e2e5488f322388`
- 元2019 同year workspace: 元original XML byte SHA `a124a47f4ba037f1403f60b52c8b02750308ee201a88f026c42721f664def37d`
- native 2018 exact CoverageId `TrilaWatt_ncHydro_2018__sea_surface_height_2d_2018_NL`, DescribeCoverage original XML SHA `bf5976a6edd2365ff33b90bf0214042884e0d6d3fc9b3eb3dbb7c28a96245664`
- native 2019 `TrilaWatt_ncHydro_2019__sea_surface_height_2d_2019_NL`, DescribeCoverage source SHA `9a0bd587debfaba85fd877c788273a18c5ae6ea57a8a9efdb88c344da6ec1e91`
- 元WMS BAW official published original Cap SHA年別もv216 sourceと同じ条件のまま再検証（WCS2のみを取得してBAW元製品の同一性と称さない）。
- HTTPS default CA検証必須、元source cap/describe別々最大4MB/2MB、転送先は未許可、XML DTD/ENTITY禁止、model time dataやGeoTIFF/NetCDF raw全く取得しない。

## 原本から閲覧するSOURCE要素
1. WCS`Capabilities`のnative OGC service version, `CoverageSummary`全native CoverageId件数、native`ServiceMetadata`の`formatSupported`, `SupportedFormat`, `nativeFormat`, `CoverageFormat`等をそのままsource reportに記録。元`GetCoverage` operationの存在はsourceの公開能力であり、個々の`application/x-netcdf`が使えると捏造しない。
2. 元`CoverageDescription`から、root XML要素名一覧、`gml:Envelope`だけでなく`EnvelopeWithTimePeriod`、`boundedBy`、`domainSet`, `RectifiedGrid`, `Grid`, `ReferenceableGrid`、`axisLabels`, `gridEnvelope`, `low/high`, `origin`, `offsetVector`, `timePosition`, `beginPosition`, `endPosition`のsource-safe短い値だけを保存。元WCSのtrue空間extentと時間範囲が見つからなければSOURCE STOPとして、ユーザGPSの範囲を勝手に補うような構成はしない。
3. 元WCS`rangeType` field `Wasserstand`, native`uom`=`m`, NilValue`9.999999848243207E30`を元sourceで**再確認**。source値が改竄/更新された場合はSTOP。
4. 単に`GetCoverage`がadvertisedで`CoverageDescription`に軸範囲が存在しても、分割NetCDF元binary/CF attributeは未取得。時間・場所をsource軸と照らしてcropするには後続版で**固定元公開WEBTICS座標と元2018/19 6月1日12:00UTC**を使い、source supported formatに限定してbounded requestを実施。いまのv217はその前に元native CRS/axis/formatの構造を実証する。
5. もしnative`formatSupported`がNetCDFを宣言していなければ、WCS経由のNetCDF小領域切り出し可能と称しない。公式配布NetCDFとWCS serviceの変換の違いを保持。

### 研究目的・依然STOP
モデル元Nilが公式に定義されたことで、低潮時にWMSで欠測値が返ること(v209)と有効値のみ残す選択による元RWS潮位上方偏り(v210)のSOURCE解釈は強くなった。しかし**Nilがdry-cellの現地測量**であること、モデルNetCDF元`_FillValue`, 元水位のvertical NHN/NAP、historical 20m DEMの同じ縦基準と原測量日、タグ付きミヤコドリGPS-cell`h(s,t)`, 潮汐×太陽/社会Boids因果メカニズムはまだSOURCE STOP。
