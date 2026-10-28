# v22-B preregistered historical-group versus observed seasonal-environment context forecast

**Frozen 2026-10-28 JST, AFTER source-only structural verification but BEFORE reading numerical group fidelity response values or v22 predictive outcomes.** This is a **new exploratory within-population companion dataset**, not independent biological replication of v20. The v20 source and all v13–v21 results stay frozen.

## Original 2021 source and exact provenance

Papageorgiou, Rozen-Rechels, Nyaguthii & Farine (2021), *Seasonality impacts collective movements in a wild group-living bird*, *Movement Ecology*, authors' repository `DanPapageorgiou/ranging_seasonality` at pinned Git SHA `2a3aec308bb4a8449d1eeb16beed4aff8f387116`. Source source-only v22-A gate verified:
- `df_dhor.Rdata` **1,911 bytes**, original Git blob SHA1 `a365bea412cdb6eb3f7b4c76bb0f9dda2268ea8a`, original downloaded SHA256 `d08864e91a543403cb1e8abf1bf9ea84247543181b8d4f4464ceb03929c0fa83`.
- data.frame `df` has exactly **143** distinct original `groupss_ × season` cells, **26** different group IDs, **11** chronological categories and **4** source-missing `fidelity` values. **16** groups observed in ≥3 seasons. Group-season keys have **zero** duplicates.
- Original environment `season_type` has exactly **4 categorical states:** `dry`, `intermediate`, `wet`, `wet_breeding`. Every original season has **exactly one** regime category, shared by all groups in that season. It is not a group-specific precipitation measurement; physical rainfall/NDVI magnitudes are not part of this table.
- Labels `year_one_1 ... year_one_6, year_two_1 ... year_two_5` are ordered chronologically using first reported study year before second and increasing numbered season within each. No model-derived reordering.

**Dataset overlap:** this 2021 study used the SAME `Avulturinum_Farine` Movebank population as the 2020 summary analyzed in v20. The seasonal samples may overlap. Therefore positive/negative agreement with v20 does **not** count as external biological replication.

## Target, independent units and eligibility

Response `Y(g,s)=fidelity`: author's derived **within-season day-to-day group spatial-use overlap**, dimensionless expected [0,1]. Do not call this feeding resource occupancy, GPS prediction, individual neural memory or a 3D niche.

One measured source group-season row is one candidate response. Exclude the four original missing `fidelity` responses *only* because no target exists, never because of forecast error. At a target source season `s`, only source observations strictly earlier than `s` can be fitted. Require ≥1 earlier observed same-group fidelity and ≥3 distinct other original groups with observed earlier fidelity. The target's observed weather category (`season_type`) is assumed externally supplied as a **conditional regime scenario at forecast time**; since the category is based on the season itself, this test is a **held-out seasonal-response conditional forecast**, NOT an operational pre-season weather forecast.

Pre-outcome hard STOP if fewer than **8** original independent group IDs or **30** future group-season fidelity targets remain, or if original group-season duplicate keys/environment labels change.

## Four fixed predictors: same future target rows

Use only original prior seasons (within-group historical observations) and original season-type metadata; all response averages give each other group equal weight, not rows:

- `M0` = **external pooled prior**: for each other group (not focal g), average its observed fidelity over *all strictly prior* seasons; then average the other-group means equally. This has no environmental conditioning.
- `ME` = **external regime-conditioned prior**: for each other group, use only *earlier* observed seasons with the same `season_type` as the target source regime; average those group means equally. If fewer than **3** other groups have prior data in that regime, **fall back to M0** solely based on source historical support, record fallback counts, and still score all four models on the **same** target. Do not borrow any other group's contemporaneous fidelity in the target season.
- `MG` = **own-group prior**: average the focal original group's fidelity over all strictly prior observed seasons, no current/future source values.
- `MEG` = **regime plus fixed group-history shrinkage**: `(1-w)ME+w MG`, where `w=n/(n+2)` and n is number of earlier observed source fidelity seasons of that group. `kappa=2` fixed before opening the source values; no hyperparameter tuning.
- No current/future same-group response, target season other-group response, published paper model coefficients or post-processed future smoothed covariates are used. The regime label is shared within a season and thus cannot identify group-by-season-specific weather exposure.

**Primary** contrast `G_hist = MSE(ME)−MSE(MEG)`: does own-group history help *conditional on recorded environmental regime*? **Secondary** `G_env=MSE(M0)−MSE(ME)`: do regime labels improve over pooled other-group history? **Additional registered** `MSE(ME)−MSE(MG)` (raw group-history vs regime) and `MSE(MG)−MSE(MEG)` (fixed shrink vs unpooled) preserve absolute model ranking.

## Score, uncertainty and fully disclosed repeated-season context

MSE is squared fidelity prediction error; average all scored future seasons within each original group ID, then equal weight across original groups (not 143 source rows as iid). Report absolute MSEs for all four models and signed gain for every registered contrast, positive group counts, **10,000 whole-group bootstrap** with fixed seed `20261028`, and original target/fallback support.

As an **a priori descriptive diagnostic**, report full per-season equal-group effect (including negative), and leave-one-entire-season-out means. Group bootstrap is not independent climate uncertainty because many groups share season type and weather within each source season. No inference about natural climate causal mechanisms from categorical wet/dry labels alone.

If the regime-conditioned model does not transfer, retain a negative result. Do not retune kappa, favorable subgroup, season cutoffs, environment class labels, or eligibility based on observed results. A result on this already-related Movebank population is **exploratory companion evidence only**.

No raw GPS, individual bird states, calibrated sensor altitude, prey resources, socially directed forces or Boids separation/alignment/cohesion coefficients are measured here.
