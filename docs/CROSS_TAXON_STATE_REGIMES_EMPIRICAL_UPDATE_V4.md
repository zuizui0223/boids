# Same place, different ecological states — original-data audit and cross-taxon inference update v4

**Date:** 2026-11-15. **Scientific classification:** independent field-source audit + exploratory annual site-heldout predictive test; not a new fully confirmatory cross-species mechanism claim. Primary repositories' frozen outcomes remain unchanged.

## The biological question

When spatial locations overlap, does ecological state differentiation reflect identity-specific use, within-individual state retention despite changing environments, or turnover between resource states? Do these patterns generalize across independent units when predictor states are measured at the proper ecological decision timescale? These are separate estimands and should never be pooled as if they shared one unit or probability scale.

## Evidence by original system

| Research system | Original independent units | What is supported | Claim ceiling |
|---|---|---|---|
| Serengeti (ODSP Snapshot Serengeti) | 17 mammal species, 3 site folds | Site-adjusted species×time conditional information 0.2243 nats; permutation p=.005; cross-fitted gains 0.05724, 0.04516, 0.04514 | Detectability, camera sampling effort; not causal niche competition |
| Bats (`batter`) | 6 vertical-use panels, 4 taxa | 5/6 show individual height-profile shape identity after session-centered additive offset removal | Not a stable individual route, shared exclusion, learning or adaptation |
| King Rail (`louis`) | 10 independent birds, 190 matched events | Hydrological used-available coupling slope 0.162 vs matched pseudo-used 1.001 (83.8% attenuation); 173-event heterogeneity post-hoc analysis coefficient −0.0431 vs pseudo +0.2617, 7/10 bird coefficients negative | Not geographic-move causality or independent portfolio mechanism replication |
| Leizhou, China 2026 GPS+raster | Archive describes 16 original tracked shorebirds across 4 taxa | Original source stage implemented and 11 known-truth tests pass | **SOURCE_STOP**: anonymous Dryad API HTTP 401; public file-stream routes HTML. No wildlife effect estimated. One-date habitat raster cannot identify environmental portfolio exhaustion |
| Marais Breton (Secondi et al. 2026, France) | Original 18 sites and 90 siteyears, 48 bird species | Source-provenance verified by publisher MD5 and SHA-256; original bird data exist as site×year totals, NOT species×individual visit values | Same-visit community state transition, bird movement, or causal environmental selection **not identifiable** from this sheet |

Original article sources:
- Secondi et al. (2026), doi:10.1007/s10344-025-02051-x, original public data doi:10.5281/zenodo.18161913, CC BY 4.0.
- Zhang & Choi (2026), original public data doi:10.5061/dryad.51c59zwm3, CC0; associated paper doi:10.1016/j.biocon.2025.111256.

## New Marais field test: provenance and specific result

1. The original observed workbook's **site×year unit** was confirmed before any model output. The original author already investigated water/vegetation predictors for bird abundance, richness, functional diversity and turnover. The new test uses all 48 original species abundances as a composition and asks whether *annual environmental-state changes improve whole-assemblage prediction for a site excluded completely from training*.
2. Pre-outcome v3 required integer original individual-species abundances and exact total; it returned the recorded `SOURCE_SCHEMA_STOP`. Two original site18 year records (2019_18 and 2020_18) each contain noninteger entries among the 48 species and substantial disagreement between the displayed species sum and original total. We did **not** round or backfill; the independent amended v4 excludes the **entire site 18** after documenting source-domain issue, before opening any environmental model score.
3. V4 remains **exploratory post-domain amendment**, no longer fully prospective. Exact source MD5 and SHA-256 were checked twice. All 48 original species retained, 17 independent sites, 87 source siteyears, and 67 valid adjacent-year transitions (three potential transitions drop out when adjacent bird abundance is zero). Hold out entire sites, not rows or species. Source grouping (site) is the uncertainty unit; no species- or sample-size inflation.
4. The fixed baseline `M0` forecasts next year's 48-species assemblage from the **preceding year's observed composition** (0.5/species smoothing) and global next-year calendar coefficients. Fixed alternatives are `M1_water` (+annual change in water-area mean/SD and water-depth heterogeneity mean/SD), `M2_veg` (+vegetation heterogeneity mean/SD changes), `M3_all` (+both). All use Ridge alpha=25 fit only on other sites and training-only feature scaling. The outcome is next-year relative bird-species composition; loss is cross-entropy nats per relative bird abundance.

### Whole-site-omission out-of-source findings

| Fixed model | Gain vs M0 (nats) | Site bootstrap 95% CI | Positive sites/17 | Primary rule |
|---|---:|---:|---:|---|
| + Water state change | +0.0075481 | −0.0112219 to +0.0308836 | 8/17 | **FAIL**: CI includes zero, fewer than half positive |
| + Vegetation state change | −0.0079493 | −0.0133369 to −0.0026279 | 5/17 | Secondary: worse than baseline under this fixed model |
| + Water and vegetation | −0.0030969 | −0.0212397 to +0.0176603 | 7/17 | Secondary: not improved |

`M0` equal-site mean cross-entropy = 2.740438 nats. These numbers were independently reproduced *exactly* between local original work and [GitHub Actions source-replay run 43684805850](https://github.com/zuizui0223/boids/actions/runs/43684805850), original published MD5 `a08325ee4e24acfc159b1cd7c1fe425d`, SHA-256 `b8d5c2c845460972be81d67c5b3cbb1f5e71a657a3f9611bff510198930d6fd9`; Actions artifact ID `14149867947`, digest `sha256:8284d96cce719ffbd4526a4841b91f15bcc67c9603c5e6659aba2cfd874cd704`. Permanent per-site numerical receipt in `comparative_state/results/marais_annual_transfer_v4_receipt.json`.

**Interpretation:** Annual changes in site-wide hydrological heterogeneity did not provide robust out-of-site predictive improvements over last-year assemblage composition and calendar alone in this particular original dataset and fixed model. The vegetation-change increment was negative. This is neither support for a universal environmental-state effect nor evidence that hydrology is ecologically unimportant: the original author found habitat associations with taxonomic/functional diversity. Observation year summaries miss each survey's contemporaneous species choices; no measured accessibility or verified bird movement; original authors corrected for numbers of censuses, but this analysis of relative composition cannot remove species-specific detectability and season-/management-related confounding.

## Revised falsifiable synthesis

**State–decision-grain alignment (proposed, NOT supported yet):** ecological-state-use prediction should generalize when available environmental states are measured in the same time and spatial grain at which individuals choose habitat and when a relevant reachability/reference set is measured. Coarse habitat descriptors and annual aggregation may predict broad abundance or richness yet fail to capture next-state transitions or transfer to novel sites. This is a *new conjecture*, not a causal consequence of the contrast between Lake Erie (individual/event data) and Marais (site/year data): taxonomic composition, species pools, instruments, confounders and outcomes also differ.

**Specific independent falsification:** obtain a public, repeated site×survey dataset with site identity, multi-species counted occurrences, observed environmental water states, effort, and matched reachable availability for individual movement where feasible. Freeze both contemporaneous and deliberately year-aggregated predictors **on the same study, same heldout sites and same target**. If contemporaneous environmental state fails to outperform annual aggregation out-of-site, the decision-grain hypothesis is not supported. Never claim state-portfolio exhaustion without repeatedly observed, reachable alternatives. For causal competition, learning, adaptation or fitness an independent manipulative/pedigree resource dataset would be required.

## Paper-level verdict

This cross-taxon line is **not ready to publish as a universal causal ecological synthesis**. It has robust independent demonstrations of identity and state buffering, a genuine but exploratory **negative transfer** result for annual whole-community composition, and a blocked planned movement test. It can become original cross-taxon research with an *independent matched source* that tests the same predicted transition, not by concatenating distinct effects from temporally/biologically incommensurate systems.
