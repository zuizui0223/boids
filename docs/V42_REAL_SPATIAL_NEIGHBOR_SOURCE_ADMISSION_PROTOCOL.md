# v42 — Are source-time-cotracked wild oystercatchers SPATIALLY near enough for a social-heading test?

**Frozen 2026-10-31 JST**, after v40's directional GPS outcomes and after the v41 SOURCE-ONLY timestamp finding (21 birds, 276,946 co-timed original candidate focal starts in 2010–2012). This is a separate **source geometry admission test**, not a held-out behavioral relationship, causal social-force estimate, or independent original source.

## Immutable source and antecedent condition

Exactly the same original Zenodo 10053970 v4 Schiermonnikoog GPS 2008–2014 original seven published-MD5 + pinned SHA256 gzip files. At runtime, BEFORE reading any coordinates:
1. Replay v41's full ID×UTC/visible/manual-outlier source-only receipt, including source year counts and ≥1 other past observed heading candidate per source time. Require exact recursive match (float tolerance 1e−12) to `validation_v41/results/original_conspecific_past_heading_timing_v41.json`.
2. If it fails, STOP the spatial source gate and report no co-location opportunity. Never read coordinates before this source ID/time replay is complete.
3. Then decode original WGS84 coordinates under v33-D original source quality and all duplicate bird×timestamp rejection. Expect exactly 602,380 accepted source fixes / 39 birds, and identical published source SHA. **No original movement bearing/speed/response, future outcome prediction, resource or RWS tide level is scored in this gate.**

## Fixed real-space nearest-other recording support

- A potentially scoreable focal start is precisely the v41 four-time record: prior disjoint same-bird GPS pair [5,30]min, gap [5,360]min to focal current GPS, and original future next recorded pair [5,30]min. Require ALL four original fixes within **25km of the official RWS Schiermonnikoog gauge at (53.468937 N, 6.202908 E)**, the frozen v39/v40 geography. The actual future ending fix is consulted **only for source-cohort eligibility**, never as a prospective predictor.
- A potentially observable OTHER bird heading is defined by a distinct bird's original two consecutive GPS fixes **[5,30]min apart**, both within the same 25km gauge area, with latest endpoint timestamp in **[t_focal−5min, t_focal]**. Never use any other bird's future fix or same focal bird's heading. For each other bird, use only its **most recently observed valid past-pair endpoint** at focal time.
- Calculate haversine horizontal great-circle distance between the focal current fix position (known at t_focal) and that other bird's latest past-pair endpoint position. Classify potential other-bird spatial proximity by ALL three source-frozen cutoffs **≤0.1km, ≤0.2km (PRIMARY), ≤1.0km**. A distance is a co-location proxy, NOT actual causal interaction, shared flock, group membership, or directed response.
- Do not optimize thresholds based on bird movement outcome or retain only favorable directions/years. Report 0.1/0.2/1.0km overlap counts **for all seven original years**, number of different focal birds and 2010–2012 month support. Also report 0.2km source starts with **at least two distinct other birds** spatially within that same radius, using other birds' latest original fix.

## STOP and interpretation

Stage can progress to an observed social-heading comparison **ONLY** if within original 2010–2012 year window there are ≥**20** focal bird IDs, ≥**10,000** original source eligible future starts **with a past other bird ≤0.2km**, and ≥**12** UTC calendar months. (Each of these is still an upper bound on the final v40 month-fitted scoring support; the earlier v40 21-bird/305257 source heldout cohort must separately be intersected with close-other events before a behavioral effect test.) If fails STOP; do not switch to 1km to rescue.

No raw original GPS/individual IDs/UTC/original distance pairs or social heading arrays are exported. Save aggregate source metadata and yearly counts only. The one-site original observational population does not represent an independent ecosystem; source co-location by itself demonstrates zero animal social steering, and three-dimensional adjacency is not measured.

**Conditional future Stage B**: freeze a new predictive model before opening the new neighbor-vs-future-direction association. Baseline original v40 V1 includes private previous direction and private previous speed, current tide×phase, time, place, bird and device schedule. Add **only past-observed 200m conspecific heading** (from two past other-bird source GPS fixes; no future information) on exactly the SAME future focal episodes in each model, with fixed negative controls for common tide / observation-time co-motion. Only this out-of-time heldout increment, if robust over whole birds and calendar blocks, provides predictive information compatible with social steering; never call it identified causal Reynolds force.

No changes to PR #43/v40 and earlier sources, no merge. Source-only original spatial-gate Python code, synthetic known-truth tests, read-only GitHub Actions, STOP or source-safe original counts.
