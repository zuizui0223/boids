# v202｜WFS original高潮・低潮線のVlieland周辺10km実LineStringを幾何的に切り出して照合（SOURCE ONLY）

2026-11-19。v201元BAW WFS2.0 `GetFeature resultType=hits` 固定10kmROIで2018 High=7、Low=52、2019 High=8、Low=50の元feature数を2回再現 (Actions #44431150507/#44431190920)。しかしWFS`BBOX`検索がインデックスまたは包絡矩形との交差を使う場合、数だけでは**真の曲線片がROIを通過したことの証明にならない**。次版はこのSOURCE構造の確認だけを目的とする**事後修正**であり、独立な未開封生態仮説検定ではない。

## source・固定条件
- v199 v200で真正元original WFS2 XML`ea41b511a593b37e87bae1cc53dfc18c071f4e8769cbff93fa01f5a6618788b5`と元4レイヤー`gml:MultiCurvePropertyType`のEPSG25832スキーマを確認済み。各runで再取得してexactSHA照合、CRSを厳格検証する。
- v201と**同一2011 WEBTICS Vlieland Haven公表座標 RD(135280,590000)**、EPSG28992→25832、同一中心から±5kmの正方形。結果を見てROIは変更しない。鳥GPSではない。
- 初回v201でWFS2 `hits` が正しいと確認された4つのオランダ高潮/低潮 boundary年次 FeatureType 2018/19 に対し、native source `GetFeature`を元bboxだけで**各1回**`count=100`、`outputFormat=application/json`、`srsName=EPSG:25832`、原source再SHA、各HTTP response最大8MB。4つのWFS件数合計 117 (=7+52+8+50)を固定。違う件数/欠測/JSON parser error/redirect/過大ソースはSOURCE STOP。欲しい結果が出るまで対象の地物を選択しない。
- 原公開ラインの座標配列はGitHubに保存しない。GitHub Actionsのメモリ内で`shapely`原曲線を厳密にパースし、同一ROI Polygonとの幾何学的`intersection`と**line length**を算出。実線片がROIの中に延びているfeature数・合計クリップ距離km、元BBOXで一致したが実線片が入らない件数のsource-safe集計だけを出す。座標の原水平系をネイティブEPSG25832で確かめる（WGS84経緯度が返った場合、地図表示の数値をメートルと誤認せずSTOP）。
- 解析ごとの`GetFeature`元Response SHA256、元バイト数、元feature数、Zプロパティがあっても意味を解釈しない（分類用と断定しない）を記録。元`features`には座標やGPSが含まれうるので、**原GeoJSON生データや線頂点をGitHubのCI artifactsに出さない**。
- `GetFeature count=100`上限、サーバー`numberReturned`/native`features`数とv201 HITSを厳密一致。ページングで欠けた個数を都合よく補完しない。
- 4つの元年次High/Low境界線が本当にROIで確認されれば、次段では**線の曲線構造と閉合性/沿岸海側・陸側のトポロジー**を監査したあとに限って年別潮間帯ポリゴンを作る。線合計距離が長い＝利用可能面積増加ではない。元WCS 2018/2019 NL topographyは2025公開retrospective modelであって当時実測z/日付ではない。

スナップショットは2018/2019各年の年別**モデル平均**の潮間帯線であり、20分/15分の干出・採餌可能時間を直接意味しない。原ミヤコドリGPS×ACCや社会的Boids力、環境分岐の因果推定は今段では実行しない。v182 SOURCE STOP保留継続。
