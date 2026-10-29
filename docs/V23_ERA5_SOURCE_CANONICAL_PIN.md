# v23 frozen independent weather-source byte metadata before GPS movement outcomes

**Registered and independently verified 2026-10-29 JST, BEFORE reading any duck latitude/longitude or target day movement response.**

Two source-only GitHub Actions full re-downloads [40803490360](https://github.com/zuizui0223/boids/actions/runs/40803490360) and [40803511838](https://github.com/zuizui0223/boids/actions/runs/40803511838) each successfully reproduced exactly the same **canonical ERA5 daily data hash**, although the original HTTP response SHA256 changed because of the provider's `generationtime_ms` and other request-runtime metadata. Canonical data were constructed only from returned grid coordinates, original source UTC offset, fixed ERA5 model, full daily date/temperature/precipitation/wind arrays and original units, sorted JSON compact encoding.

| Frozen wetland grid | Reanalysis original grid (latitude,longitude) | 2019–2023 daily records | Canonical response-content SHA256 |
|---|---|---:|---|
| `baikka_beel` (capture reference 24.3503,91.6995) | (24.25,91.75) | 1826 | `b6c1fc7323cb6cb7275e9f5d31ea8ad1f9f4bea4b479eb93e9a13058057d9b54` |
| `tanguar_haor` (capture reference 25.15,91.0667) | (25.25,91.00) | 1826 | `c856bc0b884b5d13c1529003fc2a1d1d335c856559ae4d4ae7c097837eb54307` |

All original temperatures, rain and winds were available (zero missing); source original UTC offset 0, temperature °C, rain mm, wind km/h. Future v23 source acquisition MUST validate these exact canonical SHA256 values; if ERA5 reanalysis values are revised by provider, **stop**. No use of current target-day weather; only historical day t−1 is permitted.

**These SHA256 values certify a gridded ERA5 reanalysis source, not new field observations, true feeding resource availability or a causal duck movement effect.** The GPS outcomes remain unopened as of this pin. Code `validation_v23/weather_source_gate.py` and [registered forecast protocol](V23_FROZEN_DUCK_DAILY_GPS_ERA5_FORECAST.md).
