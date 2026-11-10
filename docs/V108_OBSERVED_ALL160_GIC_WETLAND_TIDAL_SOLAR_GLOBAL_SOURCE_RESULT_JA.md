# v108 observed result: 160 authentic 2019 sea-level gauges are now paired with original 2017–2019 GIC tidal-wetland probability pixels (122 fully supported coastal regions)

Date 2026-11-10 JST. The successful original source run is [GitHub Actions #42739452977](https://github.com/zuizui0223/boids/actions/runs/42739452977); four known-truth source/identity tests passed. Real original UHSLC 2019 (v94 #42616065580) and true original 2017–2019 GIC pixel bytes (v107 #42738720185, source GCS MD5 verified per downloaded tile) with 8 prior true original selected-source pilot values EXACTLY reproduced from v106 #42737938244.

## What is observed — and exactly what it is NOT

- **True public original 2019 source frame:** 564 UHSLC unique gauge IDs in RQDS metadata, 160 annually/monthly quality-eligible measured sea-level station IDs; 354 quality excluded, 50 external transport failures **outside 160**. No selection of sites by temporal tide-solar effect, GIC wetland RF value or habitat abundance.
- **True global geographic habitat source:** GIC 2017–2019 native 30-m \`twprobabilityEnd\` RF agreement values 0–100 from original Google Cloud Storage TIFF tiles; geographic WGS84 tile CRS verified, provider MD5 per original tile, 10-km geodesic original source mask/values. This is **tidal WETLAND class encompassing tidal flat, tidal marsh and mangrove**. Pixels are native RF classification agreement, **not probability-calibrated hectares**, not measured water-depth accessibility, not within-tide dry area and not bird feeding behavior.
- **Real original 160 station-count coverage:** 152/160 source sites have FULL 10-km radius contained within exact downloaded original native tile, with ≥1 unmasked original pixel; 4/160 one-tile source polygons TRUNCATED/MASKED (not valid site-scale 10-km denominator), 4/160 outside the native registered GIC grid (not proved wetland absent). **No source metadata row disappeared from 160.**
- **True 100-km coastal independence:** original 160 sites pre-clustered by source geographic connected components into original 130 coast groups (same as v95). **122/130** are fully complete source 10-km GIC-buffer groups, **1/130** only partially covered, **7/130** have no complete source. A source-limited/edge group is not a zero-wetland region. All original v106 8 pilot sites replay exact real RF pixels and water-level F/M.
- Equal 122 fully supported coastal group means: native mean RF wetland agreement **8.2986156 /100**; mean fraction of **unmasked pixels** with RF agreement≥50 **0.0378027** (~3.78% of these sampled valid source pixels, not an exact marsh/flat area fraction). The more permissive 123 groups with at least one complete station produce native mean RF agreement 8.3217169 and RF>=50 fraction 0.0379018.

## Descriptive physical versus static source correlations (122 fully supported ORIGINAL geographic clusters)

| Co-region variable pair | Source-backed 2019/2017–19 descriptive Spearman rho | Interpretation ceiling |
|---|---:|---|
| 2019 physical ocean form factor F vs observed 2019 low-gauge-water×sun daily absolute opportunity deviation | **+0.867379** | Physically unsurprising: v100 surrogate four-harmonic no-organism control produced an equally strong/higher F–M association |
| 2019 source F vs 2017–19 independently mapped native 10-km GIC RF tidal-wetland score≥50 pixel fraction | **−0.214700** | Weak negative source-description only; may reflect geography, marsh/mangrove/flat mixture, classifier bias, coastline measurement/coverage; no causal ecological restriction inferred |
| 2019 source daily |M| vs 2017–19 native 10-km GIC RF score≥50 pixel fraction | **−0.227105** | Weak negative; not a test of organism time niche, not actual accessible habitat-hours |

The source-incomplete sensitivity that allows one complete site per 100-km region produces rho(F,RF50)=−0.220612, rho(|M|,RF50)=−0.232443, and rho(F,|M|)=+0.870007 (n=123). This does NOT add 123 independent biological communities; they are coastal geographic source groups.

**Scientific conclusion:** The tidal-form factor explains physics of daylight–low-water time coincidence, but does **not** automatically imply proportional nearby mapped tidal-wetland RF score. These are distinct environmental dimensions. Because original RF values are not dry mudflat area or species resources, the weak cross-gauge negative association is not proof that animals avoid high-F coasts; it merely refutes the casual assumption that a tide gauge time window directly indexes accessible foraging habitat everywhere.

## Critical falsification from predecessor analyses

- v100 original UHSLC 130 coast sites: observed F–physical|M| rho **+0.8578**, median of 32 synthetic four-harmonic-phase-only environmental coasts **+0.8944** (all 32 as high as or higher than observed), and F vs residual physical opportunity **−0.0920**. The 2019 strong tide-form correlation can be reproduced by known physics without animals, prey or local habitat. Do not sell this as a new ecological law.
- v103 real original UHSLC 2018 temporal holdout: 2019-only source and geographic-band training predicts 2018 new-source original tide-solar physical opportunity for **108 eligible original 2018 stations in 88 connected 100km coastal groups**. Baseline latitude/hemisphere/total tide amplitude MSE **0.004284**, adding F MSE **0.002738** (36.08% decrease), BUT same-station 2019 |M| used as a trivial environmental persistence benchmark MSE **0.0001496** (far better). Site-source rank correlation between 2019 and 2018 |M| **0.97739**. This is a retrospective hindcast not future forecast, and it further argues against claiming unfamiliar biological dynamics from a stable physical clock.
- Earlier original 2010 Wadden oystercatcher (same species/two near islands) tidal-stage×light interaction produced one observational positive on **monthly model-relative ranked GPS position** and one observational negative on **observed GPS in WMR mapped mid/high flat class**; these are different response variables and not confirmation of same two-stage mechanism. Original full v91 decomposition is **still not available** after RWS API 429. New Yalu 2 species original Dryad source is **still inaccessible HTTP401**, no actual cross-taxon biological confirmation.
- Thus independent species and direct activity-state observational support for biotic time niche partitioning remains missing.

## Next falsifiable ecological thesis

**When does externally known tidal×solar opportunity become an actual biological time niche?** It requires at least (1) moment-by-moment accessible substrate/water-depth/prey space from coastally referenced DEM \`z(x)\` and locally measured water height \`h(x,t)\` (not Q25 or static GIC probability), (2) a species-specific light/vision/thermal/predation utility curve, (3) a reachable alternative-habitat portfolio and response lag, and (4) source-verified time-stamped activity/foraging/resting observations plus detection process in independent taxa and coasts.

The test is **biological behavior beyond resource-opportunity geometry**, not another tautological tide-spectrum F versus derived M regression. A legitimate model compares \(M0: P(\mathrm{activity},x|A_s(x,t),\mathrm{light},\mathrm{effort},\mathrm{history})\) against \(M1: M0+\mathrm{tide\ phase}\times\mathrm{solar\ state}\) and a physically cycle-preserving ghost control, scored in untouched whole bird/site/tide-cycle/year studies. If only source tide and habitat map are available, biological outcome is **NOT_ESTIMATED** rather than zero.

### Original sources and code
- True full source and 8-pilot pixel replay [run v108 #42739452977](https://github.com/zuizui0223/boids/actions/runs/42739452977).
- Genuine MD5-verified original 160-site GIC pixels [run v107 #42738720185](https://github.com/zuizui0223/boids/actions/runs/42738720185).
- First 8-site admitted source/pixel pilot [run v106 #42737938244](https://github.com/zuizui0223/boids/actions/runs/42737938244).
- UHSLC independent source year physical [run v103 #42735425701](https://github.com/zuizui0223/boids/actions/runs/42735425701).
- Four-harmonic 2019 physical null [run v100 #42733494418](https://github.com/zuizui0223/boids/actions/runs/42733494418).
- Original GIC 2017–19 RF source ecosystem class: Murray et al. 2022, Science, https://doi.org/10.1126/science.abm9583 ; https://www.globalintertidalchange.org/data-usage

**Title candidates with justified claims**: (a) "A global physical atlas of tidal–solar opportunity and its separation from mapped coastal wetland context" (environmental source methods paper only, if uncertainties and comparisons support it); (b) "When two environmental clocks organize biological time niches" is a later **testable hypothesis**, not an evidenced ecological results title.
