# v46 frozen USFWS 14-label acoustic seasonal composition — NEGATIVE primary cross-site transfer

**Completed: 2026-11-19 JST.** Original [USFWS Actions 44527732339](https://github.com/zuizui0223/boids/actions/runs/44527732339) succeeded after five known-truth/no-lookahead tests. The prior test-only synthetic Excel date serial expectation error was corrected before numerical USFWS outcome opening; **no frozen source features, model hyperparameters, thresholds or endpoints changed**.

## Source authenticity and observational grain

Original USFWS ServCat Reference 112151 / DownloadFile 165800, 495,216,105-byte official ZIP. Exact final 65KB SHA256 \`69f4410f8b868849e6e17160b377e6f34fc65068e62f2590e31b598bc5f0fa59\`; original Nightly Pass Counts XLSX ZIP CRC32 \`3666e794\`, member size 2,171,863 bytes. The v45 33,168 original distinct \`AcousticSite×NightOf\` rows were retained; **no per-night WAC count / recorded operating hours field exists in this source night table**.

Original response-eligibility:
- 33,168 original night rows.
- 10,150 rows excluded because the sum of the **14 named automatic classifier labels** was zero; no true bat absence inferred. 
- **23,018 positive-classified night compositions**, **272 source site labels**, all 14 named labels positive somewhere, 9 source year labels (2010–2018).
- \`ALL\` total differs from the sum of the 14 named label counts on **14,166** eligible nights; do not silently normalize by \`ALL\` or claim every pass received a named species label.
- All original positive-classified nightly records from the original USFWS agency-filtered table were eligible under fixed field/count/data gates. No bat GPS, resource intake or biological individuals were identified.

## Frozen original M0 vs M1 prediction

M0 = training-night equal mean of 14-label classified-count shares (fixed +0.25 per class); M1 = train-only standardized \`sin/cos(2π day-of-year/365.2425)\` with 13-log-ratio Ridge(alpha=10), fixed +0.5 count pseudocounts. Target = nightly share among original 14 named classifier labels, conditional on classified-positive nights. Same rows, no weather, site IDs, years or selected favorable taxa as predictors. Endpoint = per-night cross-entropy in nats, then equally weighted across fully withheld groups.

| Frozen holdout | M0 loss | M1 loss | Gain M0−M1 | Positive groups | 95% whole-group bootstrap |
| --- | ---: | ---: | ---: | ---: | --- |
| **Whole recording site (PRIMARY)** | **1.792393** | **1.963544** | **−0.171152 nats/night** | **15/236** | **[−0.194166,−0.145439]** |
| Entire recording year (SECONDARY) | **1.778635** | **1.969803** | **−0.191168 nats/night** | **0/9** | **[−0.224804,−0.153147]** |

- One-sided exact sign p for *positive* improvement is approximately 1.0 in both comparisons.
- The primary positive gate (positive mean, lower CI positive, sign p<=.05): **FAIL**.
- 236 sites had at least 20 classified-positive nights; 9 years had at least 50. No post-outcome subsets or alpha/feature changes.
- 5 offline known-truth regression tests PASS, original full record source checksum **not** claimed (USFWS zip selected member CRC32 only).
- This is a genuinely new *out-of-source prediction comparison* (distinct from already-published source associations), but it is not a positive bat-wide biological finding.

## Interpretation boundary

**Retain the negative result.** A single shared sinusoidal seasonal rule of **relative automated acoustic species labels** was not transferable to the original USFWS's 236 heldout sites or nine years under the frozen model. This does **not** imply true seasonal ecology is absent or that bat behavior itself is random.

Several sources of disagreement are plausible but **not identified here**: study design and candidate species sets selected by source IUCN range masks + 50km, species-specific phenology requiring richer representations than a two-term shared sinusoid, heterogeneous local bat faunas, white-nose syndrome/recolonization across years, source classifier error, weather and prey availability, and nonuniform recorder effort. None is proven to cause the model's failure, and revising the model to rescue it on these outcomes would be post-hoc.

The study's \`ALL\` vs 14 species sum discrepancy and lack of original per-night WAC duration prevent interpreting these scores as a true total bat population abundance or absolute activity intensity. No results are fully independent geography/country replication; one USFWS source region is represented.

### Current scientific state and next data criterion

v42 full 100MB ZIP source cap STOP, v43 strict second Range STOP, v43a directory PASS, v44 original Nightly Counts+Metadata CRC32 PASS, v45 site-night grain PASS / WAC denominator STOP, **v46 conditional community seasonality transfer negative and frozen**.

Next meaningful universal behavioral test requires a new independent source with **validated site-night sampling effort, date/time, climate/habitat/prey covariates and comparable species classification**, preferably outside this USFWS region, then a *new before-outcome preregistered* year/site/country transfer. Do not fit a new favorable source-reused v46 feature variant as an independent confirmation.

Original \`batter\`, \`boids\` v30 negative acoustic increment, v37 morphology nontransfer and Finnish v39 positive-year-mean but nonconfirmatory exact sign remain unchanged.
