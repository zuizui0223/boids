# v43 FROZEN POST-v41 EXPLORATORY 2010 → 2011 directional replication

**2026-11-05 JST.** This protocol is **AFTER** the v41 original 2012 next-heading outcome was seen. It is a new **2011 out-of-training prediction comparison** with the exact v41 models and original source, NOT a fresh independent study/confirmatory hypothesis.

## Question
Does the tidal-phase increment for **next horizontal displacement direction given the bird's own immediately preceding heading and speed** recur in an earlier evaluation year (2011) at Ameland, and can Schiermonnikoog's 2011 GPS provide enough original **three-fix heading** episodes despite the predeclared 2012 source gate failing? Test both original oystercatcher study sites and all eligible source birds. No favorable-island selection.

## Immutable source/design from v41

- Original original-gzip MD5-verified `O_SCHIERMONNIKOOG` Zenodo v5 and `O_AMELAND` Zenodo v6 GPS **2010 and 2011 only**, source `visible` flag and fixed lat/lon site bounding gates. Authoritative fixed RWS local `schiermonnikoog.waddenzee` and `ameland.nes` **measured** WATHTE (original cm relative to NAP, fixed time UTC+01), original yearly quarterly download with source checks and count >=50k.
- v41 `original_three_fix_heading_episodes`: first visible original source fix per UTC hour; A→B and B→C original same-bird intervals each 30–120min, both displacements 0.4–120km/h, original GPS time provisionally UTC primary and -15s sensitivity. At B, previous unit east/north movement vector and own prior speed are features; B→C next unit heading is evaluation-only target; unknown source time standard/clock drift remains.
- M0 = observed water height h and h², source lat/lon, diel/year clock, own previous unit east/north heading, log1p(prior km/h).
- M1 = M0 + actual RWS rising/falling phase and phase×h. Trailing 20min slope ±.012m/h. Reuse **exact imported** v41 `forecast`, train-only standardization, equal source-bird training weights and ridge λ10. Do not alter outcome representation, threshold, hyperparameters or choose a lag.
- **Train all 2010 original qualifying source episodes; test all original 2011 episodes**, source year partition enforced. Minimum >=1k train, >=1k test, >=3 birds and >=4 ISO weeks in 2011; otherwise NOT_ADMITTED.
- Primary per-row outcome `0.5 × ((targetEast−predEast)^2+(targetNorth−predNorth)^2)`, pooled equal-bird M0−M1 signed test gain, 10k whole-bird bootstrap 95%, positive birds. Distinct secondary equal-week-then-bird mean and 4k whole-week bootstrap 95%, positive weeks. Fixed seed 20261105. They are **not the same estimand**.
- Report BOTH study sites and 0s/-15s clock scenarios, including failure/null/negative outcomes. No raw source GPS locations, source animal IDs or raw water series written to GitHub; only aggregate checksums, source counts and scores.

## Interpretation limits

A positive 2011 conditional direction result is additional retrospective within-study evidence that the original phase predictor transfers to a withheld **year within this new backtest fit**, but **2011 was already a training year in the earlier v41 2012 fit** and v41 outcomes informed the decision to run this backtest. It must not be counted as an independent preregistered study or a clean novel cohort. A negative 2011 directional result does not erase v41 2012 and original v32–v40 positive *speed* evidence. Source sampling/cadence, a few birds, uncertain GPS native UTC or GPS time, local RWS water propagation and ecological activity states remain unresolved.

A direction-vs-speed benefit, tidal-front chasing, true experienced prey availability, social Boids alignment and cross-species spatial niche divergence are NOT causally identified by this backtest. Those need same-episode matched movement-type comparisons and measured local resource/habitat data.
