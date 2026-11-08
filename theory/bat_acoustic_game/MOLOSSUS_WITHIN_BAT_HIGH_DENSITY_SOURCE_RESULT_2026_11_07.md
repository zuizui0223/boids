# High conspecific-call density: an original-source within-bat capture-success audit

**7 November 2026 — completed secondary analysis of published 2024 observations; no new bat recordings, animal tracking, or fieldwork.** The original source authors already reported high-density impairment and used bat random effects; this does NOT establish a new effect absent from the literature.

## Research question, source and source-grain correction

Krivoruchko et al. (2024) *PNAS*, DOI [10.1073/pnas.2321724121](https://doi.org/10.1073/pnas.2321724121), original Europe PMC archived Dataset S01 `pnas.2321724121.sd01.xlsx`, exact SHA256 `92acbc36cce42028bfd5a07ad1ec8aa8062121575d6d665dc7392b47222f562d`. Public source comprises **10 Molossus nigricans bats, 4299 actually observed original five-second rows, 1354 attacks, 1006 successful captures**. Conspecific call counts (not head-counted animals) are available for each original row.

**Already established source grain:** use **one observed source row = one 5-s interval**, NOT the `numel_5swindows` field as exposure, which wrongly inflated total exposures to 197566 in the originally quarantined V1. Nine of ten bats have consecutive `sec_group` indices; the tenth has seven missing indices without duplicates. Never impute original missing rows. Source content is transiently read but neither source bat IDs nor original rows are exported.

The prior-stage heldout calibration found that at **≥76 calls / 5 s**, 36 attacks were observed, M2 forecast approximately 38.9 attacks, but among observed attacks it predicted approximately 22.6 successful captures whereas just 10 actually succeeded. This prompted a new narrowly limited question: is the original low attack-success proportion merely because different bats contributed to high and medium acoustic densities?

## Fixed before per-bat outcomes were opened in this analysis

[Source contract](MOLOSSUS_WITHIN_BAT_HIGH_DENSITY_PREOUTPUT_2026_11_07.md) locked the original published density categories and primary comparator before reading individual stratum results:
- high = **≥76 calls/5 s**;
- primary reference = **26–75 calls/5 s**; secondary 1–25 calls/5 s and 0 calls/5 s, all reported;
- success probability is **successful captures / attempted attacks**, not captured prey per unit time;
- only bats with at least one attack in BOTH compared groups contribute to within-bat risk differences;
- primary statistic equal-bat mean of within-bat risk differences; original 5000 resamples of whole bat IDs seed 20261107, not pooled-attack bootstrap;
- Mantel–Haenszel odds ratio and an **exact stratified hypergeometric allocation tail**, conditional on source bat marginals. The exact tail is a conditional exchangeability benchmark in nonrandomized observations, NOT a valid p-value for causal acoustic jamming;
- split every source bat's single observed flight into THREE pre-declared consecutive relative-time thirds; test high-vs-moderate allocation only in original bat×flight-third strata with actual attempts in both acoustic groups. Hard STOP if fewer than three source bats or eight high attacks. No changing density cutoffs, quarters vs thirds, or filters after outcomes.

## Original-source result: within-bat comparison

The original 112 high-density five-second windows were recorded from eight bats; TWO of these bats made no high-density attacks, leaving **six biologically paired bats** for attack-success comparisons. This distinction is important because conditioning on attempts can select the bats and behavioral state contributing to the response.

Among those six bats:
- **High:** 10 successful out of **36** attacks = **27.78%**.
- **Moderate:** 119 successful out of **173** attacks = **68.79%**.
- Individual-bat-equal mean of (high − moderate) attack success fraction: **−0.40193** (−40.2 percentage points), descriptive bat-bootstrap 95% interval **[−0.54377,−0.21233]**. Median source bat-level difference −0.43687.
- **Five of six bats** had lower success at high source call density, one was tied and zero increased; attack support per bat is thin in the high condition (minimum 1, median 6, maximum 14 original attacks).
- Bat-stratified Mantel–Haenszel success odds ratio **0.1589**, without arbitrary continuity correction.
- Exact lower-tail probability under CONDITIONAL success-event exchangeability within each original bat, **8.8003 × 10⁻⁶**. Original within-bat attack trials and acoustic exposure are observational, serially dependent and not randomized. **Do not treat this numerical probability as causal confidence.**

The same direction of within-bat contrast holds with originally fixed alternative references: mean high-minus-low (1–25 calls) success difference **−0.57083** across six eligible bats; high-minus-zero calls **−0.53461** across six eligible bats. These are *secondary* source comparisons, not additional independent studies.

## Within-flight temporal opportunity test

Each bat's original `sec_group` index was normalized within its own flight and divided into equally-sized first/middle/last thirds. Only bat×third strata with at least one attack in high and moderate groups were kept.

- **Six original bats, nine eligible bat×third strata**.
- All **36 high-density attacks** and 135 of the source moderate-density attacks remained in those matched time strata; none of the high-density attacks were lost.
- The exact lower-tail allocation benchmark **0.0049836** under exchangeability *within the original bat and flight-third*.

This makes the direction unlikely to be caused **entirely** by mixing different bats or by placing all high-call events in a different coarse third of the flight, **under the test's source-conditional exchangeability assumptions**. The model does not control within-third prey density, natural changes in bat state, local insect swarms or sequential correlations. It does NOT identify physical signal masking or causal competition.

The nine-bat no-sec_group-gap sensitivity retains **exactly the same six original attack-eligible bats** and produces numerically identical within-bat results. It is NOT an independent or substantive biological replication.

## What the original 2024 paper already knew, and what remains valuable here

The original paper already reported a decline in percent successful attacks at high call density, using individual bat random effects in a GLMM. We must not falsely present that published result as our novel first discovery. The current contribution is an **inspectable bounded reliability audit** for the distinct predictive failure: why an unchanged attack×success model estimated ~22.6 success events given 36 high-density attempts, whereas source records show only ten, and how many distinct biological bats and matched time strata genuinely support that disparity.

**Not established:** social cue informational gain, sensor-level jamming, individual learned or remembered hunting rules, a 3D spatial niche, causal prey depletion or general bat law. Source pooled stages and no-unseen-bat predictive gain from the previously registered M1/M2 remain unchanged; do not replace them with the descriptive within-bat conditional association as if the original prediction had succeeded.

## Artifacts, validation and stop line

- [Original within-bat analysis source and seven invented-only tests](molossus_withinbat_highdensity_v1.py), [test file](test_molossus_withinbat_highdensity_v1.py).
- [Complete original-source aggregate data ledger (no original IDs)](MOLOSSUS_WITHIN_BAT_HIGH_DENSITY_SOURCE_LEDGER_V1.json).
- [Original source tests + actual data run](https://github.com/zuizui0223/boids/actions/runs/42333699222).
- [Fresh original-data source and code SHA check, all six original source comparisons and nine time strata](https://github.com/zuizui0223/boids/actions/runs/42333905086).
- Original receiver/foraging comparison: [previous stage-score evidence](MOLOSSUS_STAGE_SCORE_LEDGER_2026_11_06.json) and [2024 source capture model correction](MOLOSSUS_2024_REAL_CAPTURE_SOURCE_RESULT_AND_STOP_2026_11_05.md).

**Next manuscript/strategy decision:** The new result still shares 100% of biological individuals and the high-density crowding direction with the original publication. No original bat-only ecology article should claim a newly discovered crowding effect or a newly identified mechanism. The useful remaining task, if publicly licensed data become available, is an independent receiver-versus-foraging experimental/archival prediction across other bats or species. Otherwise, this is a completed original-source audit. PR #36 remains Draft and all frozen `batter` manuscripts remain unchanged.
