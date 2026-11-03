# v39 — Authentic measured tidal-phase versus historical year-ago placebo (two islands)

**Frozen observational receipt: 2026-11-03 JST.** This is a *post-v32/v34 diagnostic pre-frozen before its own outcomes*, NOT a new independent ecological discovery replication. The original RWS source was initially unavailable due to transport timeouts, not because of a negative hypothesis result. A transport-only change to quarterly original source requests and serial site execution passed; all v39 models, heldout year, source NAP/UTC and uncertainty estimands remain unchanged.

## Original authenticated inputs and admission

- Schiermonnikoog: original Zenodo O_SCHIERMONNIKOOG v5 2010/2011 GPS annual gzip; authenticated original provider MD5, independently calculated SHA256 for 2010 `8d7d0ac9cef0935e7351bcf9a525c0f9eeb7605dc603d227f9b09744dadd532d` and 2011 `297938bade48ca5502a4325105a64f0d6e0124a268bbcf2caa49676449f7946f`.
- Ameland: original Zenodo O_AMELAND v6 2010/2011 GPS MD5 matched; 2010 SHA256 `c92f1a21ee95c41f59e0c3ef4567a0d953b86b134bb895186cab40bb2e6cb61c`; 2011 SHA256 `f1fe4bc16eb8081ab0073326e3494af0ed4798a6044db3327b3fd0dcf9559875`.
- Original measured RWS WATHTE meting `schiermonnikoog.waddenzee` and `ameland.nes` in cm above NAP (converted to m), fixed UTC+01 even in summer. **52,561 valid unique ten-minute water levels in each 2009, 2010, 2011 source year at both stations**, original chunk boundaries/deduplication and strict units/datum checks succeeded.
- 2010 GPS training and completely withheld 2011 GPS testing. Original hourly first recorded source fix per bird; 0.5–2h displacement `log1p(km/h)`, historical gauge tide at start. 2010 source bird training and 2011 testing not necessarily disjoint identities; test is independent by calendar year, not independent individual source or geographic population.
- M0: true contemporaneous h(t)+h², source lat/lon, diel + annual cyclic terms. Mactual: M0 plus real observed ebb/flood phase(t) and phase(t)×h(t). Myear_ago: M0 plus **same station original observed phase(t−365 days)** and phase(t−365days)×**true** h(t). All identical GPS rows and true contemporaneous tide height. Frozen train-weight equal bird, ridge λ10, train-only standardization.
- Clock source metadata say UTC **or GPS time**: zero native offset is primary, −15s sensitivity performed. No original GPS coordinates, bird tokens or gauge raw observations committed.

## Exact v39 external-year primary results (naive native GPS interpreted UTC)

| Site | 2010 train steps | 2011 test steps | Held-out test birds | Test ISO weeks | M0 pooled equal-bird MSE | Myear_ago MSE | Mactual MSE |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Schiermonnikoog** | 70,561 | 46,653 | 13 | 53 | 0.163169228 | 0.163043641 | **0.158776139** |
| **Ameland** | 30,860 | 31,216 | 5 | 53 | 0.173722022 | **0.173389336** | 0.173718313 |

**The signed causal-free contrast is Myear_ago MSE − Mactual MSE:** positive is better instantaneous true-phase prediction than year-ago placebo.

| Site | Pooled equal-bird difference | Whole-bird bootstrap 95% for exactly pooled bird difference | Positive birds | Separate equal-week-then-bird difference | Whole-week bootstrap 95% for exactly equal-week mean | Positive test weeks |
|---|---:|---|---:|---:|---|---:|
| **Schiermonnikoog** | **+0.004267502** | **[+0.002489167, +0.006468112]** | **12/13** | **+0.002387492** | **[+0.001115301, +0.003402021]** | **50/53** |
| **Ameland** | **−0.000328977** | [−0.000603526, −0.000054428] | 1/5 | −0.000456713 | **[−0.001091337, +0.000050640]** | 23/53 |

These are *two different estimands*: never report the whole-week interval as if it were the interval of the pooled equal-bird difference. Confidence intervals are resampling intervals conditional on the fixed source/estimand and the few tagged birds, not causal identification or unconditional ecosystem replication.

### Baseline contrasts

- **Schiermonnikoog M0→Mactual** pooled improvement **+0.004393089** (12/13 birds, 49/53 weeks), bird-bootstrap interval [+0.002583363,+0.006612429]; week-mean +0.002438847, matched week-bootstrap [+0.001240391,+0.003438355].
- Schier M0→Myear_ago pooled +0.000125587, but the corresponding week mean +0.000051356 has a week-bootstrap interval [−0.000111522,+0.000215977] crossing zero.
- **Ameland M0→Mactual** pooled +0.000003709 with bird interval [−0.000163020,+0.000168705] and week mean −0.000103861 with week interval [−0.000404540,+0.000126441]. Weak/inconclusive.
- Ameland M0→Myear_ago pooled +0.000332686, 5/5 birds; week mean +0.000352852 but interval [−0.000003350,+0.000744572] crosses zero. **Do not infer a physical previous-year causal influence** or that Ameland uniformly favors the old tide.

### Fixed GPS-to-UTC -15 second sensitivity (not another replication)

- Schier: Myear_ago−Mactual pooled +0.004306093, 12/13 birds, 50/53 weeks, bird bootstrap [+0.002511412,+0.006520762], separate week CI [+0.001148681,+0.003436119].
- Ameland: Myear_ago−Mactual pooled −0.000299684, 2/5 birds, 24/53 weeks, bird CI [−0.000565577,−0.000033792], week CI [−0.001021357,+0.000072972].

## Scientific interpretation and evidence boundaries

1. **Positive temporally specific association at Schiermonnikoog.** Historical measured water levels and their contemporaneous ebb/flood direction carry transferable information about GPS-derived movement beyond water height, region, day/season controls, and the exact same station's measured previous-calendar-year phase. This is a stronger source-grounded negative control than assuming all clock/calendar patterns are irrelevant.
2. **Different site behavior: Ameland zero-lag true phase does not dominate historical placebo.** Under the frozen model its small positive-vs-M0 effect is indistinguishable from zero. The original v36 exploratory shift of gauge phase by −120 minutes *can* yield a positive value in the Ameland 2011 test, but selecting such a lag after observing earlier outcomes is not evidence of a true local delay. Independent 2012 external-year evaluation is needed.
3. **No prey-front or social-force inference.** No local measured mudflat elevation at a GPS fix, inundation age, food/prey availability, migration to an exposed area, behavioral state, or actual-neighbor-vs-ghost group forecasting is included. v35–v38 social source gates remain NOT_ADMITTED.
4. Original GPS time source remains UTC/GPS ambiguous; RWS station may be misaligned with local water exposure; tidal periodicity makes phase/lag association nonunique. At one site, nearby previous-year phase is not guaranteed to be a causally inert variable. Same species and Wadden Sea region only.
5. **Do not erase prior positive results.** v32/v33 show Schier actual source phase predictive externally by year; v34/v36 show site/lag heterogeneity; v39 adds temporal negative-control context rather than contradicting those outcomes.

## Source-based exact reproducibility

- [Original GitHub Actions v39 success, two distinct site jobs](https://github.com/zuizui0223/boids/actions/runs/41563908061), complete source original water-count receipts, test metrics and JSON artifacts, both jobs success.
- [Pre-outcome of v39 but post-v32/34 specification](V39_POSTRESULT_PREOUTCOME_ORIGINAL_TIDAL_YEARAGO_PLACEBO.md)
- [Source-only transport recovery A](V39A_SOURCE_TRANSPORT_RECOVERY.md) and [quarterly batch recovery B](V39B_SOURCE_QUARTERLY_BATCHING.md)
- `validation_v39/tide_phase_yearago_placebo.py` and `validation_v39/source_fetch_resilience.py` both on PR #52.
