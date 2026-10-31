# v41 — Does original wild GPS permit any synchronized CONSpecific heading comparison?

**Date:** 2026-10-31 JST. Source-only *opportunity audit* AFTER original v39/v40 outcomes already opened; no new ecological effect, GPS position or actual social neighbor info may be read in this phase. The goal is to decide whether source coverage makes a meaningful Boids **between-animal** direction-increment test even feasible.

## Original source, source-only data fields

Exactly the original Zenodo **10053970 v4 O_SCHIERMONNIKOOG** GPS-year gz files **2008–2014**, with v32 source-pinned published MD5, independent SHA256, expected original 602,396 CSV records / 39 bird identifiers. The source-only parser reads:
- `individual-local-identifier` (used transiently as bird key; NEVER saved in outputs)
- `timestamp` (original UTC, used transiently for condition checks; no timestamps in outputs)
- `visible`, `manually-marked-outlier` (quality filters from v33).
- CSV HEADER NAMES only.
**Never parse `location-lat`, `location-long`, `height-above-msl`, `ground-speed`, `heading` or original daily movement response.** No original bird coordinates, per-individual/private IDs, or timestamp arrays committed. No RWS water heights retrieved in this gate.

## Exact time-only preflight for possible social information

1. Original visible and not manually-marked outlier, nonempty valid original UTC+bird. Reject ALL original duplicate bird×timestamp records, not first or last wins. Group unique original observation times by bird, sorted.
2. A potential **focal prediction start** is original time point `t_i` for a bird with four original distinct timestamps `t_{i−2},t_{i−1},t_i,t_{i+1}` where `t_{i−1}−t_{i−2}` in **[5,30] minutes**, `t_i−t_{i−1}` in **[5,360] minutes**, and the known *future original recording gap* `t_{i+1}−t_i` in **[5,30] minutes**. Original future gap used ONLY to establish potential availability of observed test target, never as predictor.
3. At focal time `t_i`, an OTHER bird's heading would be available only if that other bird had **two prior GPS timestamps** `s_{j−1},s_j` satisfying `5≤s_j−s_{j−1}≤30` minutes, with its latest `s_j` in fixed **[t_i−5min,t_i]**. This guarantees no future OTHER bird GPS fixes are used in a prospective social predictor; **another GPS device's timestamp equal to focal t_i is permitted**. Count original focal starts with ≥1 available other-bird heading and ≥2 distinct others as upper bounds on future spatially local neighbor opportunities. Do not use other bird IDs/times beyond runtime and aggregate by original UTC calendar year only.
4. Source year/cohort gates: if original source **2010–2012** preflight has <**20 original focal birds**, <**10,000** source-time-supported focal starts with ≥1 other bird, or <**12 distinct UTC months** with supported starts, set `NOT_ADMITTED_SOURCE_SINCHRONY_FOR_SOCIAL_HEADING`, and do NOT proceed to GPS positions or any claim about social Boids. We choose this to match the prior v39/v40 21 bird/305257 time-forward target support as closely as possible; it is an *upper bound* only because geography, moving direction and exact held-out folds are not yet filtered. If the time gate passes, mark only `TIMESTAMP_COTRACKING_POSSIBLE_POSITION_UNKNOWN`.
5. Report all 2008–2014 year source-only counts, number of original individuals, raw fix/candidate/opportunity counts, fixed post-2010 gate values, and explicit no-coordinate flag. Do not attempt spatial co-location from time-only data or claim synchronized clocks identify interacting animals.

## Conditional Stage B, NEW separate protocol and output blind

If source-time gate passes, freeze a separate exact spatial rule (e.g. within 1km of current focal position), same held-out v40 21 birds and original 305257 episodes, and original co-observed other bird heading from its own PAST 5–30 minute GPS pair (other pair's END <= focal t). Require spatial/temporal overlap and minimum independent bird/month support *before scoring*. Compare fixed v40 V1 (own previous speed+direction, tide/time/place) with **V1+other-bird previous direction** on identical neighbor-supported next-step GPS vector targets. Use calendar time-block embargo, out-of-time model fit, whole-bird and time-block uncertainty; include a **stale/phase-shuffled other-bird negative control** to detect site-level common direction or tide-driven effects.

Even a conditional neighbor-vector gain does not identify Reynolds force, because common habitats, shared tide, wind and track schedules can produce correlated headings. Social alignment is only a candidate, not empirically detected interaction until detection process and alternatives are controlled. No eBird, TinyFish, main merge or alteration of earlier v39/v40 results.

## Deliverables

Read-only GitHub Actions original source SHA-gated timestamp-only code, pure temporal overlap synthetic tests, machine-readable admission/STOP status and public source-safe count receipt in separate draft PR stacked on v40.
