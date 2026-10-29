# v23 — Independent wild duck GPS and prior-day ERA5

This is a real, independently sourced wildlife GPS prediction, NOT a calibrated Boids social-force model, resource niche or causal cognitive-memory demonstration.

## Source provenance

Van Toor and Waldenström 2025, Zenodo 16940654, original 46,324,165-byte duck CSV, provider MD5 1972d0ef08b83c2b88a169ba07bb48b3, independently computed SHA256 001ec8ffe1e9be5258129dfb931b0abd6551785080e2c755cbd4c72cd79ec52e.

The complete source contains 294,683 GPS rows, 181 study-by-individual IDs, 7 taxon labels and 5 research studies; 154 birds have at least 14 distinct observed UTC dates.

Independent ERA5 historical reanalysis was acquired for 2019–2023 at two source-independent Bangladesh wetland anchor locations: Baikka Beel (24.3503 N,91.6995 E) and Tanguar Haor (25.15 N,91.0667 E). Open-Meteo original daily gridded weather sources had 1,826 UTC days each and zero missing values. Canonical value hashes were independently replicated in two weather-only CI runs before GPS outcomes. These are weather reanalysis estimates, not locally measured prey/food/resources.

## Frozen prospective scoring

Only original Bangladesh ducks; GPS day requires at least 6 raw fixes over at least 8 hours. A prior day must be observed and its last GPS fix within 120 km of a fixed wetland. Weather is day t−1, no current-day climate or current/future movement appears in any predictor. Weather classes are prior-day precipitation >1mm and mean temperature >=25 Celsius, fixed before outcomes. Own prior daily movement uses the last 3–14 original eligible days.

All models predict tomorrow's log(1+observed daily horizontal GPS radius of gyration in kilometres): M0 other-bird past, ME past other-bird matching climate category, MI own prior movement, MEI fixed shrink (1−w)ME + w MI with w=n/(n+2). Original group independence is by individual ID, NOT day-fix or taxon.

**Observed:** 49 independently identified birds, 2,664 prospective future days, primary ME−MEI gain +0.173134 squared log kilometres, 44/49 positive, individual-level bootstrap 95% [+0.111878,+0.240944], about 33.28% MSE reduction. Absolute group-equal MSE M0=0.518971, ME=0.520229, MI=0.348176, MEI=0.347095. Weather matching alone M0−ME gain −0.001258 and fixed shrink MI−MEI +0.001081 both have intervals including zero.

**Interpretation:** individual historical movement contains predictive information not captured by these broad wetland-level historical gridded climate classes. The effect could reflect stable individual identity, species, sex/age, habitat, device patterns or learning. No measured social network, true resource preference, neural memory or a universal Boids coefficient was inferred. Original Bangladesh source includes seven taxon labels but 29/49 scored individuals are garganey, making species generality uncertain.

## Scientific/technical artifacts

- Original source contracts: docs/V23_INDEPENDENT_DUCK_SOURCE_CONTRACT.md and docs/V23_BANGLADESH_ERA5_WEATHER_CONTRACT.md.
- Canonical ERA5 weather source hashes: docs/V23_ERA5_SOURCE_CANONICAL_PIN.md.
- Fully pre-outcome model: docs/V23_FROZEN_DUCK_DAILY_GPS_ERA5_FORECAST.md.
- Full scientific report: docs/V23_OBSERVED_INDEPENDENT_DUCK_ERA5_RESULT.md.
- Original source and forecast code/tests in this folder.
- Source and results: results/independent_duck_gps_source_v23.json, results/original_era5_bangladesh_weather_v23.json, results/independent_duck_daily_ERA5_forecast_v23.json.

Reproduce with numpy >=1.26 and <3, with PYTHONPATH set to validation_v23. Run Python unittest discover for test_source_gate.py, test_weather_source_gate.py, and test_duck_daily_era5_forecast.py first; then run source_gate.py, weather_source_gate.py, and duck_daily_era5_forecast.py. Temporary original source files are downloaded and SHA-verified, not redistributed by GitHub.

Original successful GitHub Actions runs: source 40802874384, ERA5 source 40803511838, real forecast 40804057488. Full source ZIP and historical ERA5 API changes are hard-stop conditions, not occasions to re-tune the opened result.
