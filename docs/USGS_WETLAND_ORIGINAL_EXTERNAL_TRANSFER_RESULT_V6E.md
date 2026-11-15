# V6e independent-property water-depth CV original source prediction — fixed primary FAIL

**Date:** 2026-11-15. **Evidence class:** original USGS field-data reanalysis, but exploratory/post-program comparative work and **not a new causal experiment**. Original data: Hartman & Ackerman (2025), [USGS DOI 10.5066/P13UJQP5](https://doi.org/10.5066/P13UJQP5), `BirdUseCWHP.csv`. CC0. Original publisher MD5 `48965f5cefa6364a34b6e92894b76a9b`; observed original SHA-256 `51b9a7c1c686bd1f5895731b5f7297004ccb372464444b9a46db3a4cc672454a`.

**Original-source replay:** [GitHub Actions run #43697608622](https://github.com/zuizui0223/boids/actions/runs/43697608622) passed all steps, tests (11/11 for v6e and v6c fixtures), exact original-file MD5. Archived Actions artifact ID `14154628896`, ZIP digest `sha256:6cc2d471c6e113ccd97099c7065cebc1111f294685d75c31854832b965f57b1f`. Exact machine-readable result is `comparative_state/results/usgs_wetland_cv_transfer_v6e_receipt.json`.

## Original independent source quality and year-label amendment

- v6 first-source file inventory: `SOURCE_FILE_INVENTORY_ADMITTED`; v6b source MD5/header-only: `SOURCE_SCHEMA_ONLY_ADMITTED`, 240 rows, 38 distinct columns.
- Frozen original v6c stopped **before any ecology model was fitted** (`SOURCE_DOMAIN_STOP`) because original `Study year` labels are **Year1/Year2**, not calendar-year strings; no v6c ecological effect exists. **Important source-access caveat:** v6c had already parsed numeric bird/environment columns for domain validation before rejecting the year labels. Thus v6e is a transparent *post-source-access, pre-effect-estimate format amendment*, not a fully unopened-outcome prospective trial.
- Source-only v6d verified from provider original dates: `Year1` 136 rows corresponds **only to 2022**, `Year2` 104 rows **only to 2023**; all 240 dates parsed as `%m/%d/%Y`; 36 property keys, 118 compound wetland keys. Published release says 117 wetlands: site alias/provenance discrepancy is not resolved, no site relabeling attempted.
- Pre-outcome separate v6e document permitted only an exact year-label normalization; the original v6c model, alpha=10, original same-time variables, heldout-property scoring, two-sided bootstrap, group controls and the preregistered primary decision criteria remained unchanged. No response-dependent cleaning was done.
- v6e QC: all **240/240** original survey rows accepted, **0** missing exclusions, **0** invalid source-domain counts, 36 heldout properties, 118 native compound wetland identifiers, property visit counts 1–21. No raw site names or private location observations are redistributed.

## Frozen primary result

Response for each original visit: **`log(1+shorebirds) − log(1+dabbling ducks)`**. This is a count contrast, not a true chosen-location transition or trophic interaction measurement.

Compare matched M0 (`Region`, year, date, wetland type, size, flooded area, mean depth, vegetation and landscape controls) with M1 (all of M0 **plus same-visit Water depth CV**) using leave-one-**property**-out ridge with alpha=10 and train-only standardization. Group-balanced train weights and equal-property test aggregation; 20,000-property bootstrap fixed seed 20261115.

| Outcome | M0 MSE − M1 MSE (log-transformed squared scale) | Property 95% bootstrap | Properties helped | Sign |
|---|---:|---:|---:|---|
| **PRIMARY shorebird vs dabbling contrast** | **−0.035539** | **[−0.056213, −0.017547]** | **15/36** | **FAIL: CV addition deteriorates unseen-property MSE** |
| Secondary log(shorebird count) | −0.040735 | [−0.091691, −0.007685] | 17/36 | Negative |
| Secondary log(dabbling count) | −0.025221 | [−0.055760, +0.002024] | 19/36 | Uncertain |
| Secondary log(wading bird count) | +0.000811 | [−0.055610, +0.055780] | 20/36 | Uncertain |
| Secondary log(secretive marsh bird count) | +0.017090 | [−0.008885, +0.044423] | 18/36 | Uncertain |
| Secondary log(total waterbirds) | +0.055448 | [−0.051600, +0.204864] | 20/36 | Uncertain |
| Secondary log(species richness) | +0.005025 | [−0.008751, +0.023984] | 16/36 | Uncertain |

**Primary preregistered gate FAIL.** Do not retune alpha, add new interactions, select subregions, remove low-performance properties, switch MSE definitions, or substitute a secondary positive for the negative primary endpoint. In particular, v6e does *not* show that wetlands with more depth variation have less bird diversity; it shows the source-specific fixed additive regression's external property forecast becomes worse.

## Biological interpretation and novelty ceiling

The **same time-aligned, within-wetland physical CV** did not provide transferably positive incremental predictive information for the *relative* shorebird-vs-dabbling counts at new managed properties, over the selected mean-depth/landscape and time controls. The source original study **already identified water-depth CV and average depth as correlates of bird density and guild-specific distributions** (Hartman et al. 2025, *Ecology and Evolution*, DOI 10.1002/ece3.72032; 25% difference in total bird density across an illustrative CV range in its original fitted model). This reanalysis adds **out-of-property** predictive transfer evidence only; it does not refute the original within-region ecological effects. Alternative functional forms, measurement error, sample size and property contextual differences may explain failed transfer, but none is identified causally by this test.

This is a second environmental-data generalization failure accompanying the *different question* in King Rail v5, which failed a cross-individual simultaneous-vs-lagged state prediction test. **These are not common effect sizes or evidence of a universal failure law.** Neither assay tests a loss-of-accessible-options threshold, compensatory movement, individual behavioural selection or adaptation. The stronger general hypothesis remains untested, so the cross-taxon product is an **empirical synthesis with negative external falsification examples**, not yet a demonstrated universal mechanism.
