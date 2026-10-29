# v23 real independent wild duck GPS + prior-day ERA5: individual history predicts tomorrow's spatial spread

**Observed source-backed, exploratory forecast, 2026-10-29 JST.** This is the first independent Boids test combining *original measured wild-bird GPS positions* with **separately sourced, time-aligned and source-SHA-pinned gridded meteorological reanalysis**. It tests a prediction architecture, NOT the causal origin of bird movement, cognition, a social network, environmental selection or Reynolds/Boids steering coefficients. All v13–v22 empirical and simulation outcomes remain unchanged.

## 1. Two independently verified original data sources

### Duck telemetry

Van Toor & Waldenström (2025), [Zenodo 16940654](https://zenodo.org/records/16940654), DOI `10.5281/zenodo.16940654`. Original `250823_LNU_dabbling_ducks_hourly.csv` is **46,324,165 bytes**, published MD5 `1972d0ef08b83c2b88a169ba07bb48b3` matching the downloaded source; independently calculated SHA256 `001ec8ffe1e9be5258129dfb931b0abd6551785080e2c755cbd4c72cd79ec52e`.

The [original ID/UTC-only source contract](V23_INDEPENDENT_DUCK_SOURCE_CONTRACT.md) and [passing source workflow 40802874384](https://github.com/zuizui0223/boids/actions/runs/40802874384) established **294,683 original GPS source rows**, **181 study×bird IDs**, **7 taxa**, **5 field study components** and **154 birds with ≥14 GPS-observed days**. UTC timestamps were completely parseable; the full source contained 256 repeated bird/timestamp observations, not 256 independent events. Actual original header is lowercase `study.id`; the source parser was corrected from the prose version `study.ID` **before any GPS position or behavioral outcome was read**.

### Regional atmospheric environment

Independent daily ERA5 gridded meteorological **reanalysis**, distributed by [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api), at two geography-specified wetland anchors from the original Bangladesh capture-site description:

- Baikka Beel fixed 24.3503°N 91.6995°E; ERA5 returned grid 24.25°N 91.75°E. Canonical daily data SHA256 `b6c1fc7323cb6cb7275e9f5d31ea8ad1f9f4bea4b479eb93e9a13058057d9b54`.
- Tanguar Haor fixed 25.15°N 91.0667°E; ERA5 returned grid 25.25°N 91.00°E. Canonical daily data SHA256 `c856bc0b884b5d13c1529003fc2a1d1d335c856559ae4d4ae7c097837eb54307`.

Each source has **1,826 UTC days (2019-01-01 through 2023-12-31)** and no missing temperature, precipitation or wind variable. Exact canonical SHA256 for each daily array was independently identical in [weather CI 40803490360](https://github.com/zuizui0223/boids/actions/runs/40803490360) and [40803511838](https://github.com/zuizui0223/boids/actions/runs/40803511838), **before original bird movement outcomes were opened**. Open-Meteo includes varying transport response runtime metadata `generationtime_ms` in the raw JSON; the pinned **canonical actual meteorological values** are stable. [Frozen source/weather pin](V23_ERA5_SOURCE_CANONICAL_PIN.md).

**Critically:** ERA5 is historical gridded, observation-assimilated weather *model data*, not directly measured conditions at every original duck or wetland food/resource abundance. No NDVI, prey, flooded-wetland availability or measured energy was joined.

## 2. Predetermined original-GPS and before-t movement prediction

The [v23-C full outcome protocol](V23_FROZEN_DUCK_DAILY_GPS_ERA5_FORECAST.md) was committed BEFORE decoding duck GPS latitude/longitude and derived daily responses.

- **Original geographic cohort**: only the source-defined `Dabbling duck migration Bangladesh 2019-2022` study, rather than selecting a favorable species or region after seeing model outcomes. Of its original **58 bird IDs**, 56 had at least one qualifying daily raw GPS set. Among its **94,248 original CSV rows**, 4 location-quality-invalid rows were dropped and **360 duplicate bird+UTC rows** were discarded entirely, not first-wins; no GPS points or times were interpolated.
- **Daily target:** same bird's next UTC day's original-measured **horizontal radius of gyration** (within-day spread around its daily observed centroid) as `log(1+radius_km)`. A measurable day requires **≥6 distinct original fixes spanning ≥8 observed hours**, producing **6,154** qualifying original individual-days (before regional support screening). This is neither a route bearing nor a true food-use niche.
- **Prior-day environmental site:** the nearest of the two fixed wetland reference locations using only the LAST observed GPS position on day `t−1`, at distance ≤**120 km**; no target-day GPS position determines the weather site. There were 3,180 otherwise qualifying future days beyond the predeclared radius and 127 without qualifying prior-day GPS, leaving **2,847 candidate days** from **49 original birds**. The distance threshold was not changed to optimize forecast results.
- **Weather features:** source original ERA5 **day `t−1`**, not target-day climate. Rain class `precip(t−1)>1mm`; warm class `T2m(t−1)≥25°C`, 4 fixed bins. Wind was source-verified but not a selected predictor in this first test.
- **Historical transfer:** for every target date `t`, every other-bird predictor is estimated from only its earlier dates, and **all ducks on date `t` are scored before ANY current-day outcomes are incorporated**. Each bird uses its own last 3–14 qualifying earlier days only. Source support requires ≥5 other previous bird IDs and ≥20 earlier historical source bird-days, with the same weather-class ME fallback allowed only on past-data scarcity. This is proper chronological pseudo-prospective prediction, not an unseen-future forecasting claim.
- **Hard source gate** (all passed): ≥20 ducks, ≥200 future individual-day targets and ≥20% source-weather matching not falling back. Actual matched support: **49 ducks, 2,664 future original GPS days**, **150/2,664** weather-matched class fallbacks (5.63%), **94.37%** environmental-class source support. All tests and comparison models evaluate exactly the same 2,664 days, then average first within duck and **equal-weight 49 duck IDs**, not GPS fixes.
- **Uncertainty:** whole-duck bootstrap 10,000 resamples, frozen seed 20261029; this does NOT create independent weather regimes, places or seven randomized species.

## 3. Frozen four-model results

Each model predicts `log(1 + within-day horizontal GPS spread in km)`; mean squared prediction error is in squared transformed-log-km units (**smaller better**).

| Preregistered predictor | Equal-duck future-day MSE |
|---|---:|
| **M0** prior histories of other ducks in the same fixed wetland region | **0.518971** |
| **ME** matching previous-day gridded temperature/rain categories in other ducks' prior histories | **0.520229** |
| **MI** own individual's last 3–14 previously observed day spreads | **0.348176** |
| **MEI** ME + MI with externally frozen reliability shrinkage `w=n/(n+2)` | **0.347095** |

| Prespecified signed gain | Equal-duck mean (squared log-km error saved) | Positive original birds | 10,000-duck bootstrap 95% |
|---|---:|---:|---|
| **Primary:** ME−MEI, added private movement history beyond climate-matched others | **+0.173134** | **44/49** | **[+0.111878,+0.240944]** |
| **Secondary:** M0−ME, climate bin added to other-bird histories | **−0.001258** | **21/49** | **[−0.024656,+0.021189]** |
| **Secondary:** MI−MEI, benefit of fixed shrink over unpooled private history | **+0.001081** | **34/49** | **[−0.006978,+0.009308]** |
| **Secondary:** M0−MEI, total private+gridded-climate model beyond all-other-bird history | **+0.171876** | **41/49** | **[+0.114179,+0.235742]** |

**Main observation:** Adding a bird's **own past GPS daily spatial spread** to an external past-weather-matched reference lowered the equal-bird mean MSE by **33.28%**, and the advantage was positive for **44/49** actual birds. This is a genuine independent wild telemetry predictive result, not re-use of the opened guineafowl source.

**Equally important negative results:**
- The tested fixed coarse previous-day ERA5 climate categories **did not improve** other-bird forecast MSE versus the source's overall external historical baseline. This is not evidence that weather is biologically irrelevant; gridded exposure, climate bin coarseness, migration, species/habitat differences and forecast metric may limit detectable added weather information.
- MEI's fixed shrinkage **did not reliably beat MI's raw individual-history predictor**, although MEI was numerically lowest. Thus v22's finding that a partial pool beat unpooled group history in the same guineafowl population **does NOT generalize as a confirmed reliability rule to independent wild duck individuals**.
- The result does **not** show increased or decreased reliance on private history under experimentally varying weather quality. It shows prediction increments of fixed models with imperfect reanalysis context.

## 4. Original taxon and weather support – descriptive after-outcome safeguards

**Post-outcome taxon-count inspection only, not new preregistered subtests**. The 49 eligible original birds were distributed across **all seven** taxon labels but very unevenly: `Anas querquedula` accounted for **29/49** birds and 1,887/2,664 targets. Other labels each had 1–7 birds. Primary signed gains were positive for 25/29 garganey and 19/20 remaining individuals; **this is NOT formal validation independently across seven taxa**, given tiny other subgroups, source time/site dependence and unmodeled taxonomic/ecological differences. This cohort is one original Bangladesh study in two wetland source areas, not six independently randomized countries.

A post-result leave-one-bird-out descriptive check and source taxon means are preserved in the aggregate JSON with explicit labels; neither changes the original full 49-bird primary. A taxon-matched external forecast was NOT preregistered and cannot be invoked after observing this result as an independent confirmatory claim.

## 5. Biological interpretation and connection to Boids

The data provide evidence for **repeatable individual-level predictive information** in a wild duck's daily spatial movement spread beyond a static other-duck population reference conditioned on broad prior-day climate. Individual birds may differ persistently in site preference, activity, tracking schedule, physiological condition, history or movement strategies. **This forecast cannot distinguish cognitive memory/learned policies from stable individual effects, sex/age, species or repeated wetland habitats**. Nor does it test simultaneous neighbors or recover Reynolds separation/alignment/cohesion force parameters.

Compared with previous Boids tests:
- **v15** another 2026 pigeon short-turn current neighbor had no transferable gain over stale (negative); **v16** independent 2016 pigeon short-turn current neighbor predicted movement in 7/8 flocks (positive). These are observed individual/focal *GPS heading* endpoints, not daily spatial spread.
- **v19** 2026 independent pigeon pair memory test: individual historical route improved over pooled pair history, while other-pair population baseline retained the lowest overall MSE. This measured future **route direction**, not daily activity magnitude.
- **v20** 2020 wild guineafowl derived group-season spatial fidelity +0.002648 for history-shrunk model; **v22** same-population seasonal-regime context showed no consistent primary added historical group gain, but shrinkage beat raw group history in 18/23. Both guineafowl analyses were the **same biological population**, not independent replication.
- **v23 independent field wild ducks** extend the prediction framework to raw actual bird GPS + separately retrieved ERA5, with strong predictive increment for individual daily movement history while source weather bin alone and shrink-specific improvements were not supported. This is **cross-source variation in information utility**, not established one shared mechanism.

The next confirmatory goal is different sources with **independent used+available habitat/resource patches and a model that controls taxon, sex, age and device observation process**, plus measured prior-day water/vegetation context. To identify social/niche formation would additionally require actual individual flock/partner contacts and a separately calibrated 3D position error process. Neither a 7-species source file nor these 49 ducks provides those missing mechanisms.

## 6. Reproducibility and redistribution boundary

- [Original duck ID/time source quality JSON](../validation_v23/results/independent_duck_gps_source_v23.json)
- [Independent prior ERA5 grids, exact canonical SHA256, source-only JSON](../validation_v23/results/original_era5_bangladesh_weather_v23.json)
- [Full 49-bird numerical source/forecast result and descriptive subgroup summary](../validation_v23/results/independent_duck_daily_ERA5_forecast_v23.json)
- [Frozen original data/behavior contract](V23_FROZEN_DUCK_DAILY_GPS_ERA5_FORECAST.md)
- [Original dataset/ERA5 source workflows](https://github.com/zuizui0223/boids/actions/runs/40802874384) and [second weather validation](https://github.com/zuizui0223/boids/actions/runs/40803511838).
- [Full actual new original wild GPS+weather forecast GitHub Actions run 40804057488](https://github.com/zuizui0223/boids/actions/runs/40804057488): original source checksum, both meteorological canonical arrays, **pre-outcome known-truth and temporal no-leakage tests**, strict source support and complete original results all succeeded. Original CI artifact ZIP SHA256 `c8fd2e48f9950036a5fe664056c60f1db9f5b6d28a2c6cb78cbb918ce2d3f3b4` (ZIP digest, not duck source digest).

**No original duck positions, animal IDs, animal fix records, timestamps, ERA5 weather value rows or original unpublished raw source files were re-distributed to boids.** Weather and GPS original provider rights/attribution are respected separately; scientific results cite their source publications. Frozen previous empirical/theoretical results remain unchanged.
