# v33 — Tide-conditioned movement state in the original Schiermonnikoog oystercatchers

**Exploratory, after the v32 GPS results were opened.** Fixed on 2026-10-31 JST before reading the new tide time series or tide-stratified movement associations. This cannot make old GPS outcomes or the environmental dataset newly independent. Keep the v32 result, positive v30 and source-only v31 STOP unchanged.

## New ecological question

Can **local water level and astronomical tides explain temporal organization of oystercatcher movements**, above yesterday-state persistence and same-bird history? Distinguish two physically different pathways:

- **Within-day exposure and movement timing:** half-day flood/ebb cycles may change the location/space the bird can occupy, independent of solar clock time (period M2 ≈12.4206 h, high water usually twice/day). This is a *contemporaneous association* if measured tide height is used and is NOT a real prospective movement forecast.
- **Spring–neap opportunity amplitude:** daily astronomical tidal range and its day-to-day change could condition *day-ahead* spatial spread. The future **astronomical** tide is predictable from orbital forcing; future **measured** water level is not known in advance and must not be silently passed as an ordinary forecast predictor.

Source landscape: original single Schiermonnikoog field study, Zenodo 10053970 v4 with 2008–2014 GPS. Exactly the v32 fixed source GPS and complete daily data quality rules (not reselecting birds). Do not make up actual tidal levels from solar astronomy alone or claim the tidal amplitude/phase at a nearby reference station without documented phase offsets.

## Preferred independently measured tide source (source admission first)

**Primary external source:** Dutch government Rijkswaterstaat WaterWebservices DDAPI 2.0 [documented API](https://rijkswaterstaatdata.nl/waterdata/) for site `schiermonnikoog`, water height (`WATHTE`), and distinction between `ProcesType=astronomisch` and `ProcesType=meting`. The exact station code and proximity are *not yet verified*. First source-only request the official catalog / 1-day tests for January 2010 and 2014. Use Dutch fixed winter time **UTC+01:00 in API requests**, including summer; translate every tide observation to UTC by actual supplied explicit offset and report any non-UTC mapping/duplicate values. This is not Europe/Amsterdam summertime. Verify any reported spatial station position against the named island or official station listing; no GPS-driven station choice.

- Check original metadata, site ID, WATHTE, `ProcesType`, units (cm/m relative to NAP, don't guess), datetime, numeric quality, and historical availability before using tide outcomes.
- No source changing to a place with a stronger fitted ecological effect. Lauwersoog can be a **declared source-availability fallback only**, and its use must be reported as a different station with a local water-level phase/amplitude caveat. If both fail, **SOURCE_NOT_ADMITTED** and no tide ecology or fake astronomical labels.
- The public Dryad [2024 original 1.43-GB reproduction archive](https://doi.org/10.5061/dryad.wm37pvmth) independently confirms local `water_schiermonnikoog.txt` measured 10-minute levels (from Rijkswaterstaat, 1982–2022). Do not silently download the massive archive or treat README claims as actual retrieved values. Other source possible only under a new, separate source-admission addendum, before any matched movement/tide outcome is analyzed.
- Historical *measured* (weather-influenced) tides and *predicted astronomical* levels must remain separate columns and report source coverage. Do not fit a future-day predictor using actual future-day **measured** levels.

## Source gates and frozen analytic comparisons

First stage source-only API response audit (≤5 response MB / 1-day request, ≤3 probes), no animal positional values. STOP and record if historical levels or station metadata/units unclear.

Only if source is admitted, after freezing executable model/test code and the original chronological cohort:
1. Hourly/daytime **association**: conditional distribution of each bird's original fix-level horizontal positional displacement versus independently measured tide phase (flood/ebb) and level; control at least for `UTC hour`/year and unequal GPS observation schedules; use *bird* or *bird-year* rather than individual fixes for uncertainty. Tide phase is a measured-environment covariate and does not identify causal shorebird foraging.
2. **Day-ahead forecast** (only for verified astronomical tide): compare v32 fixed `MP`, `MH=(MP+MI)/2` against a fixed linear tide-range/residual term on identical future bird-days. Declare one primary increment `MSE(MH)-MSE(MH+tide)` with β computed **only from past dates** (prequential rolling ridge, fixed α and burn-in); also report seasonal/solar-hour-only reference. Original frozen v32 cohort and M0/MP/MI/MH absolute errors must match v32's saved all-bird aggregate receipt within 1e−12 before any new ecological effect is interpreted.
3. Distinguish **tide availability and environmental association** from an actual prediction increment. No after-result favorable combinations of tide range, mean level, high/low phase or day/night. If required astronomical predictions absent, still possible to report a predeclared *measured-level descriptive phase association* only; no forward tide claim.
4. Mask observations with missing tide join rather than silently carry nearest unlimited historic tide. For association allow at most ±5 min to tide 10-minute sampling grid, and for daily astronomical range require ≥80% of scheduled 10-minute slots including all four daytime/nighttime blocks. No interpolation over long gaps. Report tide/GPS linked coverage per bird/year.
5. Inference is source-specific whole-bird paired bootstrap (10,000 draws seed 20261031), plus bird-year clustering/seasonal strata as sensitivity if support. GPS duty cycle, spatial landscape shifts, lunar/circadian confounding and tidal channel geometry must be discussed. Tidal water levels are **not** directly measured food exposure at every GPS point; tide height at one station is an indirect proxy for the availability of mudflat habitats.
6. Negative results remain fully reported. No source tuning, no empirical model selection, no eBird, no TinyFish, no raw GPS coordinates, original bird IDs, exact animal timestamps or individual daily outcomes exported.

## Return status

Report a machine-readable `V33_SOURCE_ONLY_...` result first, with station code, requested/returned periods, source type, valid value/time counts, quality metadata and failures. A green source probe is not a biological effect. Only after source admission should new tide-associated movement outcomes be computed. This protocol is dated after earlier v32 success, so any relationship found is post-v32 exploratory.
