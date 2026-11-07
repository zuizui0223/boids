# v59 frozen source-only gate: genuine opposite-phase wild GPS pairs

Frozen 2026-11-07 JST, before inspecting any v59 original-source matched-pair counts. Stacked on draft v58 PR #71. The v58 model-input sign flip and v57 tidal bearing transfer are existing *post-result exploratory* predictive results from the same Eurasian oystercatcher cohorts; v59 is not independent replication.

## Research question

Are there actually observed rising- and falling-tide 2011 GPS movement episodes for the **same bird, same local starting location and comparable measured water level, season, diel clock and preceding movement**? Unlike v58, this asks for two *real* observations rather than flipping a covariate in one fitted model. **This phase is only source feasibility. Never compute, view or report next-heading effects while selecting pairs.**

## Original sources and fixed cohorts

Use the exact v56-v58 verified 2011 original Zenodo GPS B three-fix movement episodes (original GPS provider MD5 and pinned SHA256), original local RWS NAP measured 10-minute gauge and verified loader. Ameland is the predeclared primary (4,678 episodes, 5 birds), Schiermonnikoog the companion (4,948, 13 birds). Original RWS years 2009, 2010, 2011 have exactly 52,561 measured observations per station-year. Existing source QA and original within-site prediction replay must pass. Native GPS timestamp provisionally treated as UTC, unresolved UTC/GPS source ambiguity remains. Pair within each island and within 2011 only, never across birds or islands. No inferred waterline, prey-front labels, refits or data-driven alignment.

## Fixed matching rules; B and past A→B information only

Use original *native* GPS middle-B WGS84 positions. Fixed 1 km equirectangular spatial grid: origin (53° N, 4° E); earth radius 6,371,000 m; longitude scale cos(53.5°), integer floor of x/1000 and y/1000. Pair a real rising (+1) with a real falling (−1) original episode if both are the **same literal bird and cell**, plus all the following, sequentially:

1. absolute real measured water-height difference ≤0.15 m NAP;
2. original GPS B timestamp separation ≥24 hours;
3. circular day-of-year difference ≤30 days;
4. provisional UTC circular hour difference ≤3 hours;
5. angle between preceding own A→B 2D headings ≤45°;
6. preceding log1p(km/h speed) difference ≤0.40.

Deterministic one-to-one without replacement: for each rising row ordered by bird/cell/time, choose the eligible unused falling row minimizing summed squared normalized height, season, clock, prior-heading, prior-speed differences; break ties by earliest observed original B time. Count rising rows with a candidate surviving each sequential gate, distinguishing such potential candidates from final unique matches. Never optimize this match on observed next B→C direction or downstream accuracy. No changing thresholds or grids after source coverage.

## Fixed admission

An island can proceed to a *later separately frozen* heading study only if **≥60 independent matched pairs, ≥3 birds each contributing ≥10 pairs, ≥8 distinct ISO weeks and ≥3 distinct calendar months** across selected pairs. Failure is `NOT_ADMITTED_INSUFFICIENT_REAL_MATCHED_SOURCE_SUPPORT`, **not** a biological null or invitation to relax thresholds. Both sites are retained regardless of primary result.

Publish only total original episodes/birds, phase counts, sequential candidate counts, disjoint pairs, number of qualifying birds, distinct weeks/months, anonymized per-bird min/median/max counts, input source digests and the source admission gate. Never publish actual bird IDs, GPS locations, times, cell IDs, pair mappings, raw water readings or next-heading outcomes. A positive source gate is *not* positive ecological evidence. If feasible, register a new observational analysis before looking at future direction outcomes; v59 stops after eligibility.

Existing v58 positive transferred predictions remain intact. No tidal causation, prey-front response, or interindividual Boids alignment is claimed by this source-only work.
