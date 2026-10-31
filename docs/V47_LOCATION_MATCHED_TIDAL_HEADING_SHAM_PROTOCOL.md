# v47: Original-location-matched spatial–tidal sham of *geometrically corrected* NEAR-vs-FAR wild GPS turning

**Protocol frozen on 2026-10-31 JST after seeing v46 corrected mean +0.03752884 (17 wild source birds/4,660 focal episodes), and after v45 naive convergence −0.097949.** This is a **POST-OUTCOME robustness/falsification audit on the SAME GPS**, not independent field confirmation, not preregistered before all previous animal data, and not a causal Reynolds Boids-force intervention. The source is the same 2008–2014 original Schiermonnikoog oystercatcher archive and official astronomical tide, no eBird or TinyFish.

## Scientific question

The positive v46 *geometrically corrected* near-relative turn could be due to **spatially persistent movement corridors/path geometry or common wind/tide response** rather than moment-to-moment attraction or alignment to the ACTUAL nearby conspecific. v45 time shams only preserved bird×month×6h×rising/falling, **not local focal coordinates**. Test a tighter but feasible **within-local-location** counterfactual: how different is the focal's corrected turning alignment to the truly observed near/far other birds than to the *other birds' headings at a DIFFERENT original event, sampled in approximately the same place and environmental phase*?

## Mandatory original source and record immutability

Before any spatially conditioned outcomes:
1. Download and verify original 7-year Zenodo 10053970 v4 GPS provider MD5 and source-pinned SHA256, original 7-year 10minute RWS \`schiermonnikoog.waddenzee\` astronomical tide, same UTC/daylight semantics as v33–v46.
2. **Fully replay the original v41/v42/v33-D/v39/v40/v43/v44/v45 wild original source+ALL anonymous per-bird/vector/angle/year/month/sham numerical receipts** within absolute difference 1e−12.
3. Fully replay v46 source and every fixed geometric-null result (17 birds/4,660 matched turning episodes, signed C_raw, C_geom, C_excess, all bird means, initial alignment, 1000 fixed symmetric left/right shams and month/year) with numerical tolerance 1e−12 against \`validation_v46/results/original_wild_inertial_geometric_turning_null.json\`. No v47 effect if either receipt differs.
4. V47 original main cohort must remain **exactly the previous v46 17 birds/4,660 disjoint original focal turns**; no new 50m thresholds, new neighbor distances, altered source or favorable bird/season selection. All previous other-bird heading pairs have already ended by focal prediction start (near≤200m, far≥1km and source ≤5min old); do not use future animal telemetry. Only ORIGINAL focal **start positions** of the previously selected 4,660 episodes are additionally opened for spatial matching. Before source geometry is used, verify EVERY start \`(bird internal key, exact original UTC)\` equals the fully SHA-pinned GPS source record, no inferred coordinates or missing keys.

## Fixed geographic spatial–time–environment keys

Transform the original **focal START** WGS84 position through PROJ \`EPSG:4326 → EPSG:25832\` with \`always_xy=True\` and original official station (lon=6.202908,lat=53.468937) as a **pre-fixed grid origin**. Grid index \`(floor((X−X_station)/2000),floor((Y−Y_station)/2000))\`: **2-km square fixed cells**, not selected/optimized by observing sham results. Never reuse the focal **FUTURE GPS endpoint** to classify locations.

Per original event, frozen matching key is **(focal original bird, source UTC calendar year, calendar quarter [Jan–Mar etc], 6-hour UTC clock block [0-5,6-11,12-17,18-23], source astronomical \`dH/dt\` sign rising/falling, 2-km grid X, 2-km grid Y)**. Discard exact-tide-slope-zero cases from the sham only; retain them in the full original v46 primary. Require >=2 source events per cell to be permutable. No adjustment for current wind/habitat or conditional prey availability.

**No new animal outcomes/models refit.** Compute v46 original geometrically corrected per-episode excess using EXACT v46 \`geometry\`, same actual own before/after headings, near and far mean previous other-bird headings. For each group, shuffle the original paired (NEAR,FAR) heading direction **together** among other episodes within that key (not within the same event); preserve focal own heading, absolute turn angle and source status. Repeat exactly **500 shuffles**, RNG 20261031. Pair preservation is essential to keep overall near–far angular difference and observation counts.

**Primary sham contrast:** conditional-on-source-permutable population, whole bird equal-weight
\[
\Delta_\mathrm{local}= E_\mathrm{bird}[C_\mathrm{excess, actual\ original\ headings}]
- E_\mathrm{500\ shuffled\ within\ local\ cell}[E_\mathrm{bird}(C_\mathrm{excess, local\ sham})].
\]
Positive means a **time-specific** corrected directional correspondence remains relative to the same place/season/clock/tidal-direction previous-bird heading distribution. Negative/no effect indicates the v46 positive excess may be explained by location-specific preferred pathways and shared environmental direction. This is **NOT** a new animal dataset, definitive social causation or an original cross-site validation.

**Fixed gate for ANY new sham effect:** at least **10 whole focal bird IDs**, each with >=10 permutable original v46 episodes; >=**1,000** total permutable v46 episodes; at least **4 calendar months** and both **2010 and 2011 original years** represented. Otherwise return \`NOT_ADMITTED_LOCAL_MATCHED_SHAM_SUPPORT\`, with source cohort QA only, no numeric C values, no threshold relaxation to 4km/8km, no tuning on earlier v46 positive signs. Note 500 Monte Carlo draws are not independent birds or confidence intervals.

Report observed and mean sham separately, 5–95% empirical sham quantile, observed−mean sham, 10,000 **paired whole-bird** bootstrap interval for the difference of actual and *fixed mean per-bird sham* (RNG 20261031), and bird sign counts + one-sided positive bird exact sign tail. Single-source year means including negative years, source years/focal counts/UTC months and grid class count; no original grid labels or exact animal positions in GitHub. Report absolute original full v46 primary +0.03752884 separately as previously known, not re-label the sham-cohort effect as its substitute.

## Additional pre-fixed falsification detail: non-mirror source effect

For every source event, direct geometric corrected excess can be written as
\[
C_\mathrm{excess}=(u_\mathrm{after}-c\,u_\mathrm{before})\cdot(n-f),\qquad c=u_\mathrm{after}\cdot u_\mathrm{before}.
\]
No raw/naive negative C_obs endpoint is used for shuffling, as naive raw sign suffers the initial-direction geometric bias already identified in v46. Verify per-episode identity between residual-vector dot product and v46 \`geometry(...)\` to abs1e−12 before running shuffles.

Interpretation limitations: 2-km squares can span distinct mudflat/roost patches, repeated paths create source matching, original source fix timestamps/foraging unknown, and an actual bird can follow another within a similar habitat even if shuffled field matches—either pattern is observational. The source includes one coastal location. No social attract/repel or Reynolds force deduction from p-values or synthetic shuffle.

## Repo and safety

Separate draft PR stacked on finished v46 PR #50, main and PR #45–#50 unchanged, no raw GPS, source animal IDs, time series, tide arrays or raw per-episode directions committed. Source-only known-truth tests and read-only GitHub Actions run the full original source check first. Report a STOP transparently if geographic source matching lacks support.