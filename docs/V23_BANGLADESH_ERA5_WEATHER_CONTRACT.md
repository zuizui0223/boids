# v23-B original independent meteorological context source – fixed before any duck GPS movement outcomes

**Registered 2026-10-29 JST BEFORE opening source duck latitude/longitude, GPS speed, daily movement outcome or any weather predictor association.** The independently original Zenodo 16940654 wild duck source has now passed MD5+SHA and ID-date-only admission: 46,324,165 original CSV bytes; SHA256 `001ec8ffe1e9be5258129dfb931b0abd6551785080e2c755cbd4c72cd79ec52e`; 294,683 original GPS rows, 181 distinct study×bird IDs, 154 with ≥14 observed UTC days, seven species, five original studies. 58 birds in the originally published Bangladesh 2019–2022 study; source GPS latitude/longitude/speed were NOT read during that admission.

## Fixed independent environmental source

- Historical daily ERA5 **reanalysis**, provided by [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api), **NOT direct in situ meteorological measurements or prey/resource abundance**. ERA5 global ~0.25° weather gridded fields assimilate observations; a historical reanalysis is an estimated context, not an actual wetland moisture/food patch.
- Two **externally published wetland reference points** selected from Zenodo original Bangladesh capture-site description BEFORE examining bird GPS positions:
  - `baikka_beel`: **24.3503 N, 91.6995 E**, wetland coordinates from OSM/Mapcarta and Bangladesh local geographic references.
  - `tanguar_haor`: **25.1500 N, 91.0667 E**, Ramsar site 1031 coordinates (~25°09'N, 91°04'E).
- `padma` original capture location is geographically nonunique along a river and **is not assigned a fabricated fixed climate station**. A future bird-day whose previous observed GPS position lies more than **120 km from BOTH frozen reference points** is not eligible for this Bangladesh-wetland local-context test. Exclusion is based solely on location known at t−1 and original study label, not outcome GPS values.
- Open-Meteo fixed request: `https://archive-api.open-meteo.com/v1/archive`, `models=era5`, `timezone=UTC`, `start_date=2019-01-01`, `end_date=2023-12-31`, fixed daily variables `temperature_2m_mean,precipitation_sum,wind_speed_10m_max`, default °C, mm, km/h. Request exactly the two fixed wetland locations, no grid search or adaptive station choice. Record exact fully resolved URL and original response SHA256, source returned climate grid-cell coordinates, `utc_offset_seconds=0`, original `daily_units`, missingness and daily row counts. Response raw numerical values will NOT be associated with animal targets in this meteorological source-only stage.
- Strict rule: environmental features on date t to predict a day-t movement use only ERA5 **day t−1** meteorology from the location nearest to the duck's most recent observed day t−1 GPS fix. The t−1 GPS fix itself is allowed, but day-t actual GPS location or day-t ERA5 weather is **not** an input. Regional weather is still only approximate, with within-grid spatial and station-error uncertainty.
- Historical ERA5 can be revised by provider; exact API response SHA256 is part of the source receipt and future calls must match the frozen source bytes or STOP. Source use should acknowledge ERA5/Open-Meteo CC BY attribution/licensing.

## Later *separate* v23-C outcome-blind target

Only if both exact source and weather gates pass, freeze next-day duck GPS daily movement outcome from **measured original coordinates** and held-out individual histories. Candidate: log(1+daily observed spatial radius of gyration in km), with ≥6 independent recorded GPS fixes and ≥8 observed hours in a day, valid WGS84 and actual UTC. Compare external weather+calendar/day-of-year (trained only on other birds) against current bird's strictly prior daily movement and **fixed shrink** kappa=2 without response-tuned hyperparameters. Split whole birds and flight periods, with at least 20 eligible original Bangladesh individuals and ≥200 complete future bird-day targets.

NO social group network ID exists in the independent duck source; only **individual/environment** claims are admissible, not flock, hierarchy of actual animal interactions or force calibration. No current scientific causal effect or niche is established by data admission.

Do not reopen v13–v22 or infer 7 independent randomized species effects from one combined original GPS archive.
