# v60 frozen: authentic paired rising-vs-falling wild next-heading concordance

**Frozen on 2026-11-07, after the v59 Ameland SOURCE-ONLY result (168 disjoint real pairs, five qualifying birds, 46 weeks, 11 months) but BEFORE opening any next-heading outcome on that matched cohort.** Parent PR #72 is source-only; its published v59 matching code and frozen numerical thresholds are never tuned in this study. Historical 2011 birds and v43-v58 full-population bearing outcomes have previously been examined; this is an explicitly exploratory *new matched observational estimand*, not an independent sample or preregistered confirmatory experiment.

## Question and admissible evidence

v58 shows the *fitted model* forecasts a different compass direction if measured rising/falling sign is synthetically switched. v59 finds at least 168 source-verified **real rising/falling GPS trip pairs** for the same bird and small location under comparable contemporaneous water level/season/diel time/own previous movement. New primary question: **Do the two *actually observed* next headings in such pairs differ along the tide-phase directional contrast specified by a model trained only on the preceding 2010 year?**

This is not equivalent to observing the same bird twice in an experimental intervention; matching remains imperfect and cannot identify tide causality, exposed tidal resources or a Reynolds/Boids social force.

## Source, frozen controls and source gate

Primary original **Ameland 2011**: all v59 4,678 wild 3-fix B->C episodes from five birds. Original RWS `ameland.nes` 2009-2011 WATHTE measured NAP, 52,561 authenticated 10-min measurements each station-year. Reuse unchanged original original GPS publisher MD5 and pinned SHA256 / `load_site('ameland')`, which replays prior v41/v43 original full cohort. Fit the exact v41 2D ridge `forecast` with lambda 10 and training-only scaling on **Ameland 2010 only**, never any 2011 target information; source-year 2010 can contain some same original bird identity strings, so this is strict time holdout but NOT identity-disjoint validation. Do not use Schier 2011 for this primary test, and do not substitute a target-domain fitted model if source transport fails.

Reproduce v59's original 2011 match **without observing outcomes during matching** using exact `validation_v59/matched_tide_support.py` same-bird/natively anchored 1km cell and all original height (15 cm), 24h separation, 30-day cyclic season, 3h UTC clock, 45° previous movement heading, 0.40 log-speed thresholds and same greedy one-to-one tie breaks. The freshly reconstructed pair-list is private and must match the old v59 immutable aggregate precisely: 168 disjoint pairs, 5 birds each with >=10, 46 ISO weeks, 11 months, and the old source eligibility stage counts [1991,1319,1303,942,550,240,182] in protocol order. Any mismatch means SOURCE_STOP, not an opportunity to select a better subset. Recompute original source GPS/provider, gauge source, full cohort replay. The v59 companion Schier field was SOURCE_STOP due to RWS API timeout and remains unscored.

Only after all source gates can true original next-heading unit vectors be read for matched pairs. Neither a model's predicted direction nor the B->C outcome can determine which original observations are matched. No new grid shifts, alternative clocks, dynamic lag search, bird selection, removing disfavored pairs, environmental outcome filtering or extra hyperparameter tuning.

## Frozen single primary endpoint

For each of 168 ordered pairs (real **rising** trip indexed +, real **falling** trip indexed -), let `y+` and `y-` be the **two actually observed** B->C unit east/north headings.

For both real original B states (not synthetic spatial relocations) evaluate the single frozen 2010-trained ridge predictor with all state variables unchanged other than a **model input sign toggle**, producing predicted unit directions `pplus(B)` and `pminus(B)`. Set

- `g = ((pplus(B+) - pminus(B+)) + (pplus(B-) - pminus(B-))) / 2`: fitted tide-phase direction-switch contrast averaged over both *actual matched B states*.
- `d = y+ - y-`: **observed** difference between real rising- and falling-phase next headings.
- `T = dot(d, g) / 4`, bounded [-1,+1] since each normalized vector is unit length.

**Primary estimand: equal-original-bird mean of within-bird mean T**, all five source-qualified matched birds weighted equally; positive means observed paired directional differences concord with the already-frozen 2010-trained predicted phase contrast. This is *not* an estimate of the observed physical turning angle due to tide or the signed compass rotation. If predicted model headings are zero-length or nonfinite, hard SOURCE/ESTIMAND STOP and do not prune any unfavorable pair. A valid zero `g` is **scored T=0**, not excluded.

Inference: deterministic 10,000 whole-bird percentile bootstrap (seed 20261107), and number of birds with positive mean T. Secondary same frozen T with equal ISO-week-then-bird weighting using each pair's original rising-B ISO week as its assignment, 4,000 whole-week bootstrap, same explicitly distinct point estimate. Do not report a row-wise bootstrap or treat 168 pairs as 168 independent animals. Compute a one-sided all-bird-level sign-flip sensitivity value by enumerating all 2^B bird sign combinations; this is an associational symmetry check, not a randomized-tide causal p-value. The finding is **directionally supported** only if equal-bird T>0 with bird-bootstrap lower 95%>0; report exact bound (negative, zero or positive) no rounding and irrespective of weeks.

## Frozen secondary interpretations (never substitute for uncertain primary)

1. Unconditional real pair-wise observed next-heading angular separation `acos(dot(y+, y-))` degrees, equal bird means and bird 95% CI. A positive absolute separation is *descriptive only*; movement stochasticity makes angles positive even without a tide effect.
2. Pair-matched **actual measured phase vs synthetic flipped phase** cosine-loss gain, averaged across the two observed episodes, from the single 2010-fitted model. This re-expresses v58 predictive specificity on a better B-state matched cohort; it is related to (not statistically independent of) T.
3. Signed *orthogonal* projection `dot(d, R90(g))/4` as geometrical diagnostic, not another selection criterion. Record how much the matched state still differs in water height, previous heading, clock and season (aggregate means/medians only), but do not change admission.
4. Report negative, near-zero or positive results, all bird/week intervals, source sample counts and limitations.

## Reproducibility and public-only aggregate

Use `validation_v60/` containing an independently checked match-index reconstruction, outcome scoring on isolated ephemeral in-memory original GPS, known-truth synthetic regression tests and original-source CI workflow. Check reconstructed v59 source receipt before reading heading targets; the CI must fail closed on any mismatch, unknown bird IDs, shape or zero-length predictions. Never commit IDs, pair indices, exact timestamps, coordinates, full GPS tracks, gauge time-series or per-bird directional outcomes; only aggregate statistics and original source SHA256. The same source has already been used in v43-v58, so neither empirical multi-taxon niche generality, direct prey-front pursuit, 3D velocity control, social alignment nor causal intervention is demonstrated by a positive result.

**Next independent step after v60:** a new bird species/shoreline with comparable measured tidal gauges, untouched before forecast construction, and a separately source-admitted spatially matched design. Do not reinterpret synthetic v13 Boids social effects as field-confirmed.
