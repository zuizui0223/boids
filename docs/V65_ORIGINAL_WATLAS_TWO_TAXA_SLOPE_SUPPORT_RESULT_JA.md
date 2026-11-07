# v65 original-data result: two shorebird species source-labelled using measured published waterlevel slope

**2026-11-07 JST, source-backed GitHub Actions [#42338765395](https://github.com/zuizui0223/boids/actions/runs/42338765395) SUCCESS** (red knot + sanderling separate jobs). 15 tests each passed (8 v65 known-truth + 5 v64 + 2 v38). Initial run [#42338707901](https://github.com/zuizui0223/boids/actions/runs/42338707901) stopped due to a **summary key typo** `original_TAG_count` vs `original_tag_count` (both original sources fetched; no ecological result). The final patch changed **only that output receipt key** and did not change data, predeclared gates, tide derivative or numerical source count. The official RWS external waterlevel has **NOT** yet been independently checked; slope here derives from the published WATLAS West-Terschelling source `waterlevel` column.

## Fixed original 30-second, actual 3-fix B movement source (no next-heading outcomes ever scored)

- Red knot *Calidris canutus*: Figshare DOI [10.6084/m9.figshare.26553446.v1](https://doi.org/10.6084/m9.figshare.26553446.v1), original provider MD5 and SHA256 `f8ef4f488a1f7f77182da59a0350b761c1b3aaa935fc5f99c3caa7ef4d15afff`.
- Sanderling *Calidris alba*: Figshare DOI [10.6084/m9.figshare.26553443.v1](https://doi.org/10.6084/m9.figshare.26553443.v1), original MD5 and pinned SHA256 `d26674dc3a02f3e6f2e68d40658c7243b4a871fdd610593e6f3f7a13851c2c70`.
- v64 original published QC/data grain and all source-only speed/movement stages are **identically replayed**. The published `tidaltime` bin values are **all positive**, not signed before/after high tide as v64 had conservatively required, hence v64's gate could not pass. Original accepted bins have `tidaltime` ranges red knot **277.89–504.74 min** (median 416.79), sanderling **275.29–501.56 min** (median 398.55), so v64's not-admitted outcome is a **label convention/source support issue**, *not* negative bird movement ecology.
- v65 uses **only genuine original source records**: TAG×30-second bins; same tideID; three consecutive fixes with both gaps 30–180 sec; both prior and future displacement **speed magnitudes** 0.2–30m/s; tideID/covariates complete. At each middle B time, find closest actual noninterpolated *published* same-tideID gauge-linked waterlevel 10–50 min earlier and later (target ±30min, earliest source on ties) and compute cm/hr slope; rising≥+3, falling≤−3, else slack/unbracketed. **No B→C heading angle or fitted ecological effect was computed.**

## New source-only signed physical-waterlevel findings

| Frozen source and support metrics | Red knot | Sanderling |
|---|---:|---:|
| Original published source localization rows | 7,595 | 6,509 |
| Distinct original tag IDs (anonymized aggregate) | 5 | 5 |
| Original tag×30s source location bins | 1,093 | 1,837 |
| Original source tide-metadata moving triplets (v64 exact replay) | **194** | **572** |
| Source rising (published linked waterlevel +≥3cm/h) | **87** | **222** |
| Source falling (−≤3cm/h) | **68** | **212** |
| Source slack bracketed | 5 | 6 |
| Source unbracketed/no nearby real gauge-linked records | 34 | 132 |
| Total source moving triples with measurable non-slack direction | **155** | **434** |
| Individual birds with an eligible source phase | 5 | 5 |
| Distinct source tideID cycles with source phase | **3** | **9** |
| Source cycles each with ≥20 eligible triples | 2 | 7 |
| Distinct cycles supplying rising and falling phase | rising 3 / falling 3 | rising 9 / falling 9 |
| **Frozen source admission** (≥120 triples, ≥3 birds, ≥4 cycles, ≥30 each phase, ≥2 cycles each phase, ≥2 cycles with ≥20) | **NOT_ADMITTED** (only 3 cycles) | **SOURCE_FEASIBLE** (all gates pass) |

Published tide-linked source slope distribution among B moving triplets with both true gauge observation brackets, **not ecological bearing effects**: red knot 160 brackets, 5th–95th percentile −41.0 to +71.0 cm/h; sanderling 440 brackets, 5th–95th percentile −37.0 to +68.7 cm/h.

**Positive data-quality result:** sanderling meets every previously frozen *source opportunity* threshold for separately evaluating a movement direction endpoint across held-out original tideIDs. **Not yet a positive ecological tide effect.** Red knot has enough rising/falling source instances, but fails the independent original tide-cycle support criterion; this does not mean red knots have no ecological tide response.

## Important scientific boundaries and next gate

The original [Bijleveld et al. 2022](https://doi.org/10.1186/s40317-022-00307-w) Fig. 9A/B home-range datasets were described for **12–19 August 2018**, five red knots and five sanderlings, **not** the authors' separate population-wide 221-red-knot movement dataset. Their WATLAS measurement error, receiver density, 30min coastal water propagation offset and `tidaltime` source treatment differ from v41–v63 oystercatcher GPS. The published `waterlevel` was recorded from the West-Terschelling gauge-associated series, but **it is not independently fetched, authenticated Rijkswaterstaat original data in v65** and may incorporate a source-specific timing offset. NO cross-taxon 2010/2011 model coefficients can be directly transferred to UTM31 30-second trajectories.

**Next preregistered v66:** source-only independent Rijkswaterstaat West-Terschelling 2018 *original WATHTE meting cm NAP* validation of rising/falling phase for the 434 original sanderling instances, no bearing outcomes, source time ±30min propagation sensitivity stated separately. Only if the independent original gauge source confirms enough non-slack paired phases and original tide-cycle holdout do we preregister v67 observed 3-fix *heading* forecast and out-of-tideID heldout comparison. Never weaken a failed gate to obtain a positive result.

## Reproduce and safe release

- [Successful source-backed GitHub Actions #42338765395](https://github.com/zuizui0223/boids/actions/runs/42338765395): originals fetched, MD5/SHAs verified, 15 tests × two jobs.
- Aggregate-only source artifacts: `v65-gauge-linked-source-red_knot` ZIP SHA256 `43b0ae12b2c81987a6655ae637bf4700c03d059a161ac8c4181387cbf23bb0ac`; `v65-gauge-linked-source-sanderling` ZIP SHA256 `42a35e176eb9ba8f043d1b33e0c086f02c9cc20d78824e4ae79d89db6ec58f73`.
- [Frozen method](V65_FROZEN_ORIGINAL_WATLAS_WATERLEVEL_SLOPE_SOURCE.md), `validation_v65/watlas_original_slope_source.py`, `validation_v65/test_watlas_original_slope_source.py`. No individual source TAGs, exact location/timestamps, per-tide/trip headings, site GPS or raw waterlevel series committed.

**No causal tide, prey-front, social Reynolds/Boids steering or niche split is estimated in v65. Preserve historical v43–v63 real oystercatcher positive predictive findings unchanged.**
