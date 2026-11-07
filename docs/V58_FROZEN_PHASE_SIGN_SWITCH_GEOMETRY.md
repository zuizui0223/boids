# v58 — conditional phase-switch geometry and original GPS directional validation

**Frozen 2026-11-07 JST before v58 phase-switch outcomes.** Stacked on v57. Original v57 already showed Schiermonnikoog (2010 fit) → Ameland (2011 test) transferred directional benefit using the actual RWS phase versus the same station's measured 365-day previous phase. All source cohorts, model coefficients, location alignment and angular errors from v57 are known. This is **post-result exploratory**, not fresh independently blinded field evidence.

## Question (two distinct parts)

1. **Model implication at exactly the same state:** For each original 2011 middle fix B, keep absolute measured tide height h(B), h²(B), B site position, clock, month/season and the bird's **own previous motion** identical, then evaluate the *same frozen fitted model* twice with tide-phase feature **+1** (rising) and **−1** (falling). What predicted difference in **next heading** (not acceleration) does the phase term yield in compass-space?
2. **Actual heldout GPS test:** On precisely the same original B→C test heading, is the prediction with **observed real ebb/flood sign** better than the prediction with its sign flipped? The flipped prediction is a *model sensitivity/negative-control probe*: not a physically realized counterfactual, a randomized experiment, or observed occupancy under the opposite tide.

Primary cohort: **2010 Schier fit → 2011 Ameland test** with the predeclared v56/v57 **2010-site-centre translation**. Companion: **2010 Ameland fit → 2011 Schier test** with identical translation rule. The unchanged full-source within-island model replays are required before new effects but not a newly confirmed ecology outcome. The raw-coordinate transferred condition remains v57 context, not another optimized primary.

## Source and fitting (unchanged)

Original O_SCHIERMONNIKOOG and O_AMELAND 2010/2011 GPS gzip MD5/SHA and original local RWS WATHTE **meting cm/NAP** measured at the same fixed +01 offset, 2009–2011, 52,561 unique ten-minute values per station-year. Source loading reuses v56 functions and the v57 same-source cache; authentic gauge station and original bird source years exactly replay v57.

Original three-fix source A→B→C: first source fix per hour, both intervals 0.5–2h and both speeds 0.4–120km/h; source original GPS clock provisionally UTC, original phase at B from trailing 20min gauge slope ±0.012m/h. The whole original 2010 source-island sample trains a single equal-bird-weight ridge λ10 model per route, after literal source ID collision removal. All original 2011 test GPS rows remain unchanged. The target-island **2010 unlabeled source GPS position centre only** aligns the original B coordinates by translation; no target next directions or target 2011 coordinates used to fit/align.

Use original v41 `forecast` (identical source train-only standardization, intercept, ridge λ10, 2D vector outcomes); no alternative hyperparameters, hidden lag, other-bird terms, new land-cover covariate, or target-refitted coefficients. Preserve v57 strict full-cohort model comparison and EXACT transferred 2011 angle/cosine metrics with abs tolerance ≤1e−9 before new phase-switch scoring:
- Schier→Ameland translated M0/M365/Mactual angles 72.93178509824226 / 71.35487793871758 / 65.7262909831397 degrees, test 5 birds, 4,678 episodes.
- Ameland→Schier translated 72.50932117199987 / 70.19593767636698 / 66.03068642794109 degrees, test 13 birds, 4,948 episodes.

## Frozen primary and secondaries

Build two copies of EVERY original heldout translated row with **all fields except the model's phase sign byte identical**. The original target heading at C never enters the phase-switch predictions. Also fit an **observed actual-phase** prediction in the same single trained call to verify row-by-row exact agreement with the corresponding phase branch to 1e−10. Any zero-length predicted vector ≤1e−10 → SOURCE/ESTIMAND STOP: do not fabricate an angle or silently remove rows.

For each row:
- `p_plus`: predicted 2D east/north unit-heading proxy under phase +1, **not normalized before loss** except to compute angular orientation.
- `p_minus`: analogous under phase −1.
- **Model-implied phase-switch angle** `rotation=atan2(cross(p_minus,p_plus), dot(p_minus,p_plus))` in degrees, positive counterclockwise (east toward north). Report per-original-test-bird average **absolute** rotation and paired whole-bird 95% interval, descriptive signed circular mean (with circular resultant length), fraction counterclockwise. This is NOT the measured angle through which a bird actually turned and NOT the magnitude of social/physical steering.
- At the bird's ACTUAL phase, compare observed B→C unit heading to `p_actual` and `p_flip` (its opposite sign) using **cosine loss** `1−cos(theta)`. Frozen **primary** difference `loss_flip − loss_actual`, positive means true tide sign gives more accurate bearing. Report equal-bird paired bootstrap 10,000, seed 20261107, and separate equal-week-then-bird paired bootstrap 4,000, seed+1, each with matching distinct point estimate. Also give mean angle error improvement in degrees with its matching paired intervals, and number of positive birds/weeks.
- The **same main contrast** is repeated in the opposite transferred direction as a companion, not substituted if primary is uncertain.
- Report the phase-switch angle and actual-versus-swapped predictive gain separately for original rising and falling test rows, minimum 200 rows, ≥3 birds and ≥4 weeks per condition; otherwise NOT_ADMITTED for that condition. Do not use subgroups to select favorable outcomes.

Source support: compute original 2010 training height quartile cut points `np.quantile(h,[.25,.5,.75])` using only source training water levels. For each quartile report authentic source phase ± training counts, and heldout phase-switch geometry and true-vs-flip gains only if ≥50 train rows of EACH phase and ≥200 test rows/3 birds/4 weeks. Do not change the primary whole-cohort gate, and do not drop rows based on support diagnostics. The quartile comparison is descriptive and **not** a causal same-height matched observed behavior test.

Overall source gate remains frozen v56: >=1,000 training original triples/3 birds, >=1,000 test/3 birds/4 weeks, target2010 location reference >=1,000/3 birds. Identity strings cannot overlap between source train and target test. If gate/source authentications fail, NOT_ADMITTED/SOURCE_STOP with no new ecology outcome.

## Mechanistic interpretation boundaries

The fitted 2D model contains a phase main term and phase×h interaction in **both east and north outputs**. Two predictions at one covariate state identify a deterministic **model-implied** directional difference, not observed two-time same-position realized bird behavior or a true tide-caused steering force. A positive actual-vs-flipped angular loss is additional out-of-year **predictive specificity under this already inspected cohort**. It does not identify exposed Wadden prey, the local waterline front, tidal current drift, causal preference versus correlated routes, real 3D flight/acceleration, or actual-neighbor Reynolds/Boids alignment. The GPS source UTC/GPS time and RWS local hydrodynamic lag remain unresolved; site-centre translation is not a physical habitat correspondence. Across two neighboring islands and one bird species no universal nature law is established.

## Reproducible plan

New files only in `validation_v58/`, `docs/`, and new workflow; old v56/v57 code unchanged. Source-only runner loads both sites once with v57 authenticated cache, verifies within-site replay and historical control, then fits same original cross transfer once for all 3 phase conditions (actual,+,−). Pure tests must detect phase-only mutation, no feature/time/target leakage, orientation wrap ±180°, phase sign symmetry, nonzero prediction, source gates, subgroups and paired bird/week bootstrap. Keep both positive and null/negative signs in all outputs; only aggregate stats to GitHub, no raw GPS IDs/coordinates/times or gauge time series.
