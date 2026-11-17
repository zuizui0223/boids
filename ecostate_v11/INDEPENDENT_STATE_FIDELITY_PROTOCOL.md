# v11 independent water-buffalo habitat-state continuity — conditional prospective protocol

**Scientific freeze:** 2026-11-17, before opening any source-derived GPS–raster habitat choices or generated alternative endpoint samples. **Current state:** source quality admission pending; all effects unmeasured.

## Why a new study?

The 2017 Scrafford wolverine original table gave an anomalous source-label signature: in worksheet 2 **17,338/17,338 used** rows had equal start/end road, stream, and traffic variables, compared with 2.63% of source alternatives. A one-binary-feature equality classifier improved whole-bear heldout log loss by **2.096 nats/group**. This strong cue is consistent with case-class-conditional source processing, not a proven physiological or ecological preference to maintain a state. Source location coordinates were redacted, precluding independent re-extraction. The v10c and v10d positive choice-prediction results remain **scientifically ON HOLD**, unchanged numerically.

New independent study: Forrest et al. (2025), *Ecography*, DOI 10.1111/ecog.07421. Original public Zenodo record **13749246** (published 2024), including 0 original 2018–2019 buffalo location fixes and separate native raster covariates. The published analysis demonstrates diel movement and time-varying habitat selection using 13 individual buffalo; it has *not* (from the inspected original report) been shown that an origin-dependent similarity term predicts candidate endpoints beyond fixed destination conditions and same-length movement geometry. This must not be claimed as new before direct comparison with the full original paper and secondary literature.

## Mandatory three-stage source gate

1. **MD5:** `buffalo.csv` 16,838,962 original bytes, provider MD5 `37d50a37a0271f4b9ee8ba1707d1d8a8`, 133,161 records, 11 headers (`timestamp`, `lat`, `lon`, `node` among them). The original node identifier must be independently verified to uniquely identify biological animals; multiple collars per individual or ID reuse would lower effective N.
2. **Symmetric GIS:** native `canopy_cover.tif`, `veg_herby.tif`, `slope_raster.tif`, each with provider MD5 and exact SHA; projected native raster CRS, nodata footprints, geographic overlap and `lat/lon` coordinate validity must pass. **Every observed and available candidate endpoint and its source state is sampled with the exact same raster extraction function**, without outcome-conditional transformation.
3. **Repeated hourly fixes:** source timestamp parsing, regularity and missingness, minimum 10 independent source animals and 100 source-defined valid movement transitions per animal. Any source grammar inconsistency, low raster coverage, mismatched CRS or incomplete candidate set => `SOURCE_SCHEMA_STOP` without field hypothesis verdict.

## Primary ecological endpoint (no result yet)

For each real consecutive location within animal `i` at time `t`, generate 20 alternative **bearing-only endpoints at the exact same observed step length** (at 2π/20 intervals around original bearing) and at **exactly the same start point**. These are geometric same-distance alternatives, *not a complete reachable habitat network or guaranteed accessible path*. Sample observed and alternatives at the same spatial raster and date. Include within-source actual movement geometry before niche attributes; a 10% alternative-endpoint nodata threshold is source-defined, not outcome-based.

Compare conditional choice among 21 candidate endpoints on heldout **entire animals**:

- M0: destination canopy cover, herbaceous binary, slope, turning angle (relative to previous real heading) and source-local hour/canopy interactions; match length exactly so length cancels within each observed step.
- M1: M0 + absolute canopy difference between start and destination + binary herbaceous state-change indicator. Source values are constant for all alternatives within each stratum; interactions with candidate destination make these differences testable.
- Primary gain = equal-animal mean `NLL(M0) − NLL(M1)` in nats/decision; 10,000 whole-animal bootstraps and 5 animal-disjoint folds. **Biological direction gate** requires both state-difference coefficients negative in ≥4/5 folds, mean gain lower 95% limit >0, and ≥65% of animal heldout gains positive. A sign-test/CI and full individual heterogeneity must be shown independently rather than conflated with this directional gate.
- Extra robustness after primary: deterministic full-time versus day/night, movement-kernel anisotropy and spatial block effects, *explicitly exploratory*; never use their results to change the primary.

**Stop/interpretation:** Even a positive M1 does **not** identify deliberate state regulation; a traversable corridor, landscape autocorrelation, heading persistence, and source-generated circular alternatives can induce environmental similarity. The source already documents strong diel dynamic habitat preference; this paper is an independent observational residual, not a claim of discovering diurnal selection. The same GPS study cannot be counted as multiple source replications.

## Recording

Source-only CI keeps original data and sensitive positions **off GitHub**; export only IDs cardinality, aggregate hour/coverage QA, source checksums and ecological group-level contrasts. No false 'success' claims from synthetic fixtures or metadata-only execution.
