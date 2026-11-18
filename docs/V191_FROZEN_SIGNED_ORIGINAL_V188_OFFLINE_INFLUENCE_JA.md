# v191｜署名済み元データ監査レシートを使うOFFLINE事後影響監査

**Frozen offline source receipt before inspecting posthoc resampling.** This is **a post-v188 explanatory sensitivity analysis**, not an independent ecological confirmation, not raw RWS data access.

## Original preserved input
- Genuine 2018/19 RWS WATHTE cm NAP 13-station LOO proof-source GitHub Actions run **#44249870280**, artifact `v188-original-Wadden13-2018-2019-spatial-station-LOO`, artifact ID **14403970497**, created 2026-11-18.
- GitHub Actions archived original ZIP digest SHA256 `49603b18df9cf6b791b6fe2a5e640e245bba4c8771f481243532d4dc30580380`, verified after downloading. The single contained SOURCE-safe original output `genuine_Wadden13_2018_2019_spatial_LOO_v188.json` 75,574 UTF-8 bytes has **independent content SHA256 `e249bd99dcb91c9a8eaf74d82820e1a90212fa721e8f9860563323a5aeb5a2b1`**. This exact JSON SHA is required on every v191 run; never trust only an artifact name or repackage digest.
- No RWS endpoint is called in v191, no raw tide timeseries, bird positions, ACC, DEM rasters or source selection. Reuse only the already authenticated 13×4 predeclared station-wise MSE, actual original RWS response SHA, and frozen 2011 WEBTICS geometry from v188.

## Strict gates
1. Original JSON SHA match; fixed **13** source sites × four month/years `2018-06, 2018-09, 2019-06, 2019-09`. The source v185 initial 5/15 STOP and v187 exploratory source repair must remain marked.
2. Original RWS response SHA256 on every one of **52 station-windows**, n real 10-minute NAP ≥200; exactly same genuine UTC observation cohort across all 13, n≥190 each window. Match v188 original source status as physical gauge-only.
3. Each hidden target excluded from its own geometric neighbor input; IDW3 weights nonnegative and sum to 1; triangles never use target and only when inside reference convex hull. Each individual MSE and group mean reconciles with original receipt within tolerance for 9-decimal rounded MSE.
4. **Posthoc** all-13 mean+median station gain, site sign counts, full 13 delete-one-site mean gains, and change in sign of all-site mean after deletion. No new model or data filtering by gain. No p-value or claim of statistical independence of 10-minute samples and 48h blocks.

GitHub workflow: use the original `gh run download 44249870280 --name v188-original-Wadden13-2018-2019-spatial-station-LOO` with **fixed original JSON SHA check** before Python. CI must fail on any change/absence, and must not call RWS.

Scientific status: v188 original-site predictive mean MSE nearest=0.072700386 vs IDW3=0.062228824 m² (Δ=+0.010471563, ≈14.4% reduction, 4/4 positive windows). Yet only seven of 13 target stations improve, six worsen; max positive Eemshaven drives sign of arithmetic mean. Removing Eemshaven leaves 12-station mean Δ≈−0.001868506 m². This diagnostic is **after observing v188 outcomes**, not a second confirmatory test.

As ever, 2011 RD reference coordinates ≠ verified 2018/19 native gauge positions; local bird GPS h(s,t), ground wet/dry, DEM native vertical NAP datum/survey day, tide×sun causal ecology, and social Boids parameters remain NOT_ADMITTED.
