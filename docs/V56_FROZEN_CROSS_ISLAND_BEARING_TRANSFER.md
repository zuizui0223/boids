# v56 — cross-island and future-year transfer of tidal bearing prediction

Frozen 2026-11-06 before v56 cross-site outcomes. Base `52402d646634566c1f4f171d6ee1da5cde2212a9`, v55. Earlier within-site outcomes are known; explicitly post-result exploratory, not an unopened independent field study.

## Question and approaches
Can an original 2010 model learned on one island predict 2011 next movement headings on the other island, without fitting to that island's movement targets? Evaluate BOTH directions: Schiermonnikoog -> Ameland (primary, target chosen before scores) and Ameland -> Schiermonnikoog (companion). Same species and nearby Wadden sites; do not claim continental or species generality.

Unmodified absolute geographic inputs can put the target outside source locations. Therefore the PRIMARY transfer uses one transparent translation-only alignment: compute each site's 2010 mean B location, first averaging within source identity then across identities; replace target test B coordinates with source-2010 center + (target B coordinates - target-2010 center). Use the retained source training cohort for its center. Target-2010 data supply ONLY this unlabeled position anchor; no target next headings, speeds, tide outcomes or 2011 positions enter its estimation. Keep compass directions, physical NAP water height, clocks, own previous motion and all other features unchanged. No rotation, scale matching, coastline optimization or target-response tuning. This is position-calibrated transfer, NOT target-data-free zero-shot prediction and NOT habitat registration.

SECONDARY raw transfer keeps original absolute coordinates unchanged. Both conditions use exactly the same fitted source coefficients and target test rows. Concatenate raw and translated inputs and call the original forecaster once per model, then split forecasts. Do not choose the best alignment after results. Existing target-site-trained predictions are replayed as context, not used to tune transferred models.

## Source and splits
Only original 2010/2011 O_AMELAND and O_SCHIERMONNIKOOG source gzip data, published provider MD5 and pinned SHA; unchanged v41 genuine A->B->C hourly source parser (both gaps 30–120min, both speeds 0.4–120km/h, original visible and geographic gates). Source native GPS provisionally UTC; no new clock optimization or AHN2 filtering. Authentic RWS WATHTE meting cm/NAP original station years 2009–2011, fixed UTC+01, 52,561 values per source year. Source-specific gauge history merged by original timestamps, exact t-minus-365-day phase lookup. Require zero history-join row removals and exact original v52/v43 all-site 2010->2011 count/vector MSE replay at 1e-9.

For each cross-site pair, remove source-2010 rows whose literal individual-local-identifier occurs in target-2011. This is conservative collision removal across provider labels, not proof of true biological identity/re-tagging across studies. Report removed counts and zero remaining literal overlap; never publish identifiers. Keep every target2011 row unchanged. Require source training >=1000 rows and >=3 identities AFTER exclusion, target test >=1000 rows, >=3 birds, >=4 ISO weeks; target2010 position-reference cohort >=1000 rows and >=3 birds. Otherwise NOT_ADMITTED before new fitting, no rescue or threshold relaxation. No 2012 test in this stage.

## Frozen forecaster, outcomes and uncertainty
Reuse v41 forecast unchanged: M0 = h, h squared, latitude/longitude, cyclic diel/annual clocks, previous own east/north unit heading and log1p prior speed; Mactual adds true ebb/flood and phase*h; M365 substitutes true same-station phase exactly 365 days earlier, keeping current h fixed. Source-bird-equal training weights, source-training-only feature scaling, ridge 10, unpenalized intercept. Histories belong to the local station for each training/test site, never transfer the source station's hydrograph to target birds.

Use v53 summarize_models with cosine loss PRIMARY and absolute angular error (degrees) secondary; vector half-MSE diagnostic. Primary contrast M365 minus Mactual in translated Schier->Ameland, actual-minus-baseline benefit also reported (M0 minus Mactual). Report all three contrasts for both directions and both input conditions, even negative. Whole-bird paired bootstrap 10,000, seed 20261106; separate equal-week-then-bird 4,000, seed+1, each CI with its own point estimand. Undefined zero prediction bearing = no fabricated direction or row deletion.

No pooled p-value across two directions; no successful primary claim from a favorable secondary metric/condition. All losses are conditional on the source fit, not training-uncertainty intervals. Strict historical-control failure does not erase a baseline-relative gain. A gain relative to poor transferred M0 is not automatically good absolute prediction; compare actual error with replayed target-site-trained models.

## Prespecified covariate support diagnosis (not data selection)
For h, B latitude, B longitude, and log1p prior speed, count the fraction of target rows outside source training 1st–99th percentile ranges, before/after translation. Report union out-of-range fraction and per-feature fractions, no source/test rows removed based on these counts. These marginal ranges are descriptive, not a joint-domain guarantee. Translation only adjusts geographic origin; it cannot identify coastline geometry, local prey, water propagation or activity states.

## Interpretation
A successful cross-site result supports predictive transfer of this specific source rule to the nearby target domain. Failure can reflect domain shift, coordinate/landscape geometry, different source cohorts or limited training, not absence of tide response. Same-data exploration, no actual exposed-front pursuit, calibrated physical steering or Boids social interaction identified. Prior v55 and v32–v54 findings remain intact.

Method context: Roberts et al. 2017, Ecography 40:913–929, DOI 10.1111/ecog.02881, stresses validation aligned with temporal/spatial/hierarchical transfer and warns that blocking changes extrapolation/support.

## Implementation plan
New only: validation_v56/cross_island_transfer.py (pure alignment/split/paired forecast), validation_v56/run_cross_island_transfer.py (one original-source load for both sites), tests, source workflow, aggregate receipt and result note. Previous code untouched.
- [ ] Test first: no target outcome or test-year anchor leakage; bird-equal center; exact coordinate-only shift; no mutation; identity collision exclusion; gates before fitting; same 3 fits across both conditions; matched test losses and undefined bearing; support audit never filters rows.
- [ ] Run failing tests, implement, pass. Independently check angular arithmetic and source-to-target mapping on unequal synthetic groups.
- [ ] Source runner checks GPS/tide provenance, replays existing within-island outcomes, computes both transfers once. One workflow, no duplicate full-source matrix runs.
- [ ] Verify local/remote code, tests and original run outcomes. Preserve both directions, main unchanged, Draft PR and reproducible aggregate bundle only.
