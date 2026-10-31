# v45 — Do wild oystercatchers actually TURN toward a nearby bird's *past* direction?

**2026-10-31 JST, expressly POST-OUTCOME.** Previously known: v43 NEAR≤200m prior other-bird heading showed small uncertain vector prediction gain, FAR≥1km showed larger gain on an unbalanced near-only cohort; v44 compared the same BOTH-available original 18 birds / 68,232 heldout next-original-GPS steps and found NO robust near-versus-far vector-MSE superiority (near−far −0.000095997, bird CI [−0.000305408,+0.000137561]), despite both separate directional predictors improving the vector MSE. We now test **actual focal heading convergence** toward previous nearby versus far headings, a different orientation response than squared 2D velocity error. This CANNOT be independent field confirmation, because both comparison and source were chosen after earlier wild GPS outcomes.

## Data and immutability

Use precisely the original Zenodo 10053970 v4 `O_SCHIERMONNIKOOG` GPS from all seven 2008–2014 years (provider MD5, originally pinned SHA) and Rijkswaterstaat `schiermonnikoog.waddenzee` official astronomical WATHTE (cm NAP, 10-minute support) exactly as in v43–v44. No original animal files, ID/UTC timestamps, positions or raw tide curves persisted.

**Mandatory before new effect:** re-download all original data; verify original v41 ID/UTC, v42 200m spatial opportunities, original v33-D, v39 scalar outcome, v40 heading outcome, and the *ENTIRE* original source and per-bird/annual/month/vector/angular numerical v43 and v44 results (absolute tolerance 1e−12). Both original v44 S0..S3 trained ridge models and original SAME-episode eligibility must reproduce, with 18 birds/68,232 heldout BOTH-available episodes, then freeze the original v44 matched list and do not refit/tune v43 S-model coefficients. Otherwise **STOP** without emitting v45 effects.

Original frozen v43 timing/space source: focal's private past movement uses original 4 unique GPS fixes (prior i−2→i−1, future i→i+1), no overlap, both 5–30 min elapsed, 5–360 min gap, all four within 25km source gauge. Other-bird NEAR≤200m and FAR≥1km past movement pairs must END no later than focal forecast start, be at most five minutes old, and latest original source observation per other bird; never use other-bird future fixes or the focal bird itself.

## NEW fixed response on exactly the source BOTH-available episode cohort

For each original v44 matched heldout episode, define 2D unit vectors:
- **u_before:** focal's preceding disjoint original GPS step heading. Require original preceding step *displacement* ≥0.05km.
- **u_after:** focal's next original GPS step heading, observed only as heldout outcome. Require original future step *displacement* ≥0.05km, exactly v43/v44's direction-only threshold, not used as an ex-ante predictor.
- **n:** mean of all individually unit-norm NEAR other-bird previous step directions before focal starts, normalized to a 2D unit vector if resultant norm≥0.25. Otherwise exclude as direction-unreliable.
- **f:** equivalent mean FAR other-bird previous directions, likewise norm≥0.25.

No outcomes, birds, dates, locations or tide-phase categories are selected based on sign. Complete same-source comparison requires **all four** directions reliably defined and source near/far present. Report every gate count and excluded episode. No angle estimation from nearly zero displacements. The normalized near/far means are a **directional consistency proxy**, not evidence of flock membership.

**Single fixed PRIMARY orientation convergence contrast**
[
C_{NF}=(u_{after}-u_{before})cdot(n-f)
=[cos(	heta_{after}-	heta_{near})-cos(	heta_{before}-	heta_{near})]
-[cos(	heta_{after}-	heta_{far})-cos(	heta_{before}-	heta_{far})].
]
Positive means the focal's observed heading **converged toward the NEAR past direction relatively more than toward the FAR past direction** between the previous disjoint segment and next observed GPS step. This is an observational *turning association*; not proof of social attraction. Original source tide/clock/location/recording processes are not randomized, and choosing to be near another bird may encode shared preferred routes.

Prespecified secondary signed estimands are (C_N=(u_{after}-u_{before})cdot n) and (C_F=(u_{after}-u_{before})cdot f), with (C_{NF}=C_N-C_F). Report all including negative, equal-weight each original bird after averaging its own retained episodes. Main gate **≥12 whole original birds each with ≥10 fully eligible orientation episodes, ≥2,500 such original episodes, ≥6 UTC months, ≥2 original GPS years**. Otherwise `NOT_ADMITTED_ORIGINAL_DIRECTION_CONVERGENCE`, only counts, no signed effects, no relaxation to 10m or other source radius.

Uncertainty: 10,000 paired **whole bird** bootstrap resamples, RNG 20261031, exact one-sided *positive* bird sign tail, all individual sign counts and distribution. Monthly/yearly **descriptive** equal-bird and equal-calendar-month decomposition, including negative years, no cherry-picking. Month and bird are not independent ecosystems.

## Fixed time-alignment negative-control (secondary, separate support gate)

For the SAME orientation-eligible original episodes, form groups **original bird × UTC year-month × UTC 6-hour block × source astronomical tide rising/falling sign** using source original time/current tidal dH value. Only groups containing ≥2 original episodes are permutable; groups of one are excluded from this negative-control sample, NOT from primary. Preserve focal `u_before/u_after` and near/far source heading **pairs**; within each group, permute the pair of near/far heading vectors together, 100 deterministic permutations (RNG seed 20261031), breaking exact focal-time association while retaining each bird's near/far source direction distribution, coarse season/clock, tide direction and availability. Report observed equal-bird C_NF on **the same permutable subset**, mean and 5–95% range of shuffled equal-bird values, and observed-minus-mean-shuffle. Do not use these permutations as independent bird replicates or as confirmatory p-value; nearby source spatial habitat is not preserved by this shuffle.

Separate gate: ≥10 original birds each with ≥10 permutable episodes and ≥1,000 total permutable episodes. Else negative control `NOT_ADMITTED` with no sham effects, primary still reported when admitted. No alternative bandwidths, shifted days, tide-phase definitions or GPS direction threshold rescue after data.

## Purpose and limitations

- If C_NF>0 robust and same-time-shuffle much lower, that would be stronger **spatiotemporal direction convergence evidence** than v43/v44 pooled MSE, but still **not** direct causal Reynolds alignment, because path geometry, site, wind, tide and co-location remain observational.
- If null/negative despite both prior-direction features predicting vectors, this would strengthen the explanation that other-bird direction is **regional directional information**, not a direct turn-toward-neighbor rule in this field population. It would not refute all possible social Boids behavior.
- Neither current original study nor v45 tests 3D altitude, prey capture, actual mudflat exposure or between-species niche partition.
- Do not modify previous v29–v44 source data, code or results. Draft PR stacked on v44, no main merge. No eBird or TinyFish.

Deliverables: frozen protocol first, new source-free unit tests, code and read-only original-source GitHub Actions CI, anonymized aggregate JSON and Japanese study interpretation; all negative results retained.
