# v30 — geographic holdout of next-day movement-state prediction across four duck studies

**Frozen on 2026-10-30 JST, before inspecting GPS positions or daily movement responses from the four studies below.** The v23 Bangladesh and v29 exact-yesterday outcomes are already known. This is a *new geographical cohort held out from earlier analyses within the SAME published Zenodo GPS file*, not an independently collected data release, random sample of continents, or blind validation of a previously public protocol. Do not rewrite v23/v29.

## Objective

Test whether the day-t−1 observed movement-spread state predicts day-t spread better than the history of OTHER ducks, including a same-taxon historical reference. Separately test whether a fixed multi-day personal mean or a 50:50 personal-history+previous-day combination improves on exact-yesterday persistence. Any negative outcome remains frozen. No parameter/model/region selection after opening GPS coordinates.

## Frozen source and groups

Original: Van Toor & Waldenström (2025), Zenodo [16940654](https://zenodo.org/records/16940654), `250823_LNU_dabbling_ducks_hourly.csv`, 46,324,165 bytes, published MD5 `1972d0ef08b83c2b88a169ba07bb48b3`, independently verified original SHA256 `001ec8ffe1e9be5258129dfb931b0abd6551785080e2c755cbd4c72cd79ec52e`. The fixed external archive is bounded to 120 MB. Only the original provider URL, byte count and both checksums are admitted; provider access/checksum failure means STOP.

Use **all four and only** these original `study.name` values, independently enumerated from v23's source-only ID/UTC audit before inspecting their GPS outcomes:

| Original study name | Source-only bird IDs | Source-only GPS fixes |
|---|---:|---:|
| Dabbling duck migration Mongolia (2020) | 31 | 30,173 |
| Dabbling duck migration Ottenby 2017 (Anas platyrhynchos, Anas acuta) | 34 | 32,781 |
| Dabbling duck migration Portugal 2018--2022 | 20 | 64,438 |
| Eurasian wigeon (Mareca penelope) Netherlands Lithuania 2018-2019 | 38 | 72,967 |

123 original study×individual IDs in total. **Exclude the already opened Bangladesh study without substituting another cohort.** No outcome-dependent inclusion of regions, taxon, sex, year or positive-result subset. Dates, taxon IDs and group counts are known from metadata; latitude, longitude, GPS quality and daily radii from these four source studies are *not* previously opened in this programme.

## Daily target and chronological unit

- Parse UTC `YYYY-MM-DD HH:MM:SS` and WGS84 finite latitude/longitude and finite original `gps.hdop` in [0,15]; require nonempty original study×individual ID and stable original taxon. Exclude **all** records from a duplicate valid bird+UTC timestamp, never take an opportunistic first/last. No interpolation or inferred flight neighbors.
- Qualifying day has ≥6 unique valid fixes spanning ≥8 hours. Compute *exactly* v23's daily horizontal GPS radius-of-gyration: `R=sqrt(mean(((lat−mean(lat))*111.2)^2 + ((lon−mean(lon))*111.2*cos(mean(lat)))^2))` km; response `y=log(1+R)`. This is within-day spatial spread, **not** route selection, food/resource niche, 3D altitude or distance traveled.
- Candidate day t requires a qualifying original calendar day t−1 for that bird. The MP predictor uses **exact** t−1 daily y, even if the previous day was not eligible as a scored target. Do not change that rule based on results.
- Prequential predictions: sort target dates in UTC, score **all** ducks at date t using histories strictly <t, and only afterward append date-t eligible events. Histories belong to the same original study; personal histories remain within bird. No current-day animal positions used to select another bird's data.
- Prediction admission for each target: ≥3 earlier eligible same-bird days (last 14 observations), ≥5 OTHER individual IDs in its study with ≥20 earlier eligible study×bird-day records. Both eligibility and model scores must be equal across all models, with no case-dependent filtering.
- Aggregate first within the original bird ID, equal bird weight within study, then **equal weight across four studies**. Keep per-study bird counts and actual future-day targets; neither observed days nor GPS fixes are independent ecological replications.

## Five fixed models (identical future targets)

- `M0`: historical source mean from other study birds, first mean within each external bird then average birds.
- `MS`: same, restricted to previous *same-taxon* other study birds if ≥5 external birds / ≥20 previous eligible bird-days; otherwise fixed fallback `M0`, with all fallbacks counted. Species labels do **not** imply independent experiments.
- `MI`: same bird's mean of last 3–14 earlier *eligible event days* from same study (may have calendar gaps).
- `MP`: exact yesterday's COMPLETE original GPS-day y, without refitting.
- `MH`: fixed `(MP+MI)/2`, no fitted weight.

Primary `MSE(MS)−MSE(MP)`, positive means persistence beats the taxon-matched (or explicitly fallback) external mean. Secondary 1 `MSE(MP)−MSE(MI)`, positive means multi-day history beats yesterday. Secondary 2 `MSE(MP)−MSE(MH)`, positive means adding fixed half multi-day history beats yesterday. Descriptive `MSE(M0)−MSE(MS)` measures same-taxon filtering. **All four signs, per-study values and absolute errors are retained regardless of result.** No additional climate bins, site clusters, decay windows, lag horizons or nonlinear fitting after opening data.

## Original independent study support and inference gates

A region is eligible only when ≥8 original scored birds and ≥80 original future bird-days satisfy the preceding rules. A full **four-study result** requires all four regions to pass and total ≥60 birds and ≥500 target-days. If not, report `NOT_ADMITTED` with source support for **every** region and export **no pooled ecological comparison**, without changing limits. Count MS fallbacks rather than screening them out.

Estimate each signed contrast per bird first, then its equal-bird mean by study and equal-study grand mean. Report 10,000 paired resamples of the FOUR STUDY-LEVEL mean gains, RNG seed 20261030, and the exact one-sided sign probability across four studies. With only four non-random study environments, this bootstrap is descriptive and the smallest all-positive one-sided sign p is 0.0625; neither bird-level nor day-level bootstraps justify a worldwide law. Include four separate regional gains and any sign disagreements, plus per-taxon support counts (descriptive only). Do not claim independent meteorological replications or fit a study-level causal effect.

## Falsification and claim boundary

- A positive primary across studies would support **geographic replication of short-state predictive information within the source archive**. It would not establish a cognitive state, intrinsic individual trait, time-invariant personality, competition or environmental selection.
- A secondary multi-day gain is conditional on this fixed predictor and does not identify cognition. A negative result preserves the v23/v29 original effects and documents a simpler sufficient forecast rule.
- Study cohorts may differ by species, tracking schedule, latitude and years. The output is not a measurement of prey patches, used/available food resources, actual neighbor interactions, social Boids forces, 3D altitude or transferable niche segregation.
- Historical data from the target individual's earlier days are allowed because this is **forecasting future days of known individuals**. It is not a prediction for an unseen individual or a prediction of long-term species distribution.
- **No eBird**, and no raw GPS locations, timestamps, real individual IDs, or per-day response values redistributed.

## Required implementation/verification

1. Make a source-only preflight on the fixed original manifest and listed group IDs, without opening GPS coordinates. Keep original checksums.
2. Add a pure calculation module and synthetic tests for exact t−1, missing-day gaps, same-day embargo, source ID+UTC duplicate rejection, non-leaking equal-bird and equal-study aggregation, species-reference fallback, and all-four-region STOP.
3. Freeze code and tests before loading four-region GPS positions. Then run complete original-source execution on GitHub Actions (actual provider SHA gate and strict limits), save only anonymized per-study aggregates and explicit successful/STOP status. Preserve v23 and v29 files untouched.
4. Keep this in a **separate draft PR**; do not merge or reclassify any earlier observed result. A Github CI green check confirms computations, not an independent field experiment.
