# Post-outcome within-bat acoustic-density capture test — 2026-11-07

**Pre-output source analysis contract**, written AFTER the 2024 authors published their findings and AFTER we inspected pooled density-band outcomes and leave-one-bat-out prediction. NOT an independent preregistration, new field observation or new mechanism proof.

## Scientific question

Does the decline in `Molossus nigricans` success among actual attacks at very high original other-bat call density also appear **within the same bat**, rather than arising entirely from different bats contributing to high vs moderate source acoustic conditions? Is the within-bat contrast still estimable when conditioning on coarse within-flight time?

This question is narrower than and overlaps the original published 2024 PNAS GLMM, which already included bat ID random effects and showed lower successful attack proportions with increased conspecific calls. Do not claim the within-bat high-density direction is new without establishing a distinct contribution.

## Original source and eligibility

Krivoruchko et al. (2024), PNAS DOI `10.1073/pnas.2321724121`, PMCID `PMC11287165`, original public Europe PMC supplementary `pnas.2321724121.sd01.xlsx`, source workbook SHA256 `92acbc36cce42028bfd5a07ad1ec8aa8062121575d6d665dc7392b47222f562d`. Ten original bats, 4299 observed grouped **5-second** rows, original `sec_group` chronological index, `sum_attacks`, `sum_success`, and `sum_cons` other-bat call counts per group. Source `numel_5swindows` must NOT be used as exposure (its 197566 total caused the invalid V1). One of ten bats has 7 absent `sec_group` indices, no duplicates; never fill them. Original source data records are read only transiently, no raw bat IDs, single-bat count crosswalk or source windows in any GitHub artifact.

Use exactly existing original source density bands:
- `high`: **≥76** conspecific calls per 5s (original paper's >75);
- **primary reference** `moderate`: 26–75 calls per 5s;
- **secondary reference** `low`: 1–25 calls per 5s;
- `zero`: 0 calls per 5s, separately descriptive only.

On every original row attacks=A, confirmed successful captures=Y, require `0<=Y<=A`. Only **attacks** (not source 5s rows) are denominators for conditional success. For each bat and each contrast, include it only if it has **≥1 original attack in each compared group**; retain zeros in other groups for support metadata. If fewer than three biological bats are eligible for a given contrast, report `SOURCE_SUPPORT_STOP` without replacing categories, choosing a different cutoff or computing pseudo-odds.

## Fixed primary within-bat statistics

1. Per eligible original bat `d_i=(Y_high/A_high)-(Y_reference/A_reference)`; report **equal-bat mean** and median risk difference, n eligible bats, sum eligible high and reference attacks and source bat-level min/median/max support **without individual labels**, and fixed-seed (20261107) 5000 whole-bat percentile bootstrap 95% interval. This is descriptive and depends on the existing published source.
2. Mantel-Haenszel common success odds ratio from original per-bat 2×2 counts `(Y_high, A_high-Y_high; Y_ref, A_ref-Y_ref)`. Report undefined if denominator zero; do NOT use post hoc 0.5 continuity correction.
3. **Exact stratified conditional lower-tail success-allocation probability** from convolution of per-bat hypergeometric conditional success allocations, conditional on bat attack totals, condition sample sizes and pooled successes. This is a descriptive conditional-exchangeability benchmark, not a randomized treatment p-value. A small value does not identify causal sonar interference, because density was observational and attacks were not randomized.
4. Repeat exact contrast in nine bats with consecutive `sec_group` as **overlapping** structural sensitivity, not independent replication.

## Predefined flight-time control

Within each bat, define coarse chronology as `(sec_group-min)/(max-min)`, and label three source flight thirds `[0,1/3),[1/3,2/3),[2/3,1]`. For high vs moderate only, create bat×flight-third strata, retaining those with ≥1 attack in both source acoustic groups. Run the exact hypergeometric conditional allocation on these eligible time-matched strata. Report number of eligible original bats, strata, covered high attacks, uncovered high attacks and support condition. HARD STOP interpretation if fewer than 3 distinct bats or <8 high attacks remain covered. No width adjustments, fallback to half-flights, temporal interpolation or stratified regression added after seeing results. Do not claim temporally adjusted causal evidence: only broad flight-time phase, prey fields and bat behavioral state remain unobserved.

## Claims, stop conditions and intellectual contribution

- This is a **robustness/attribution diagnostic** on the already published acoustic social-foraging trade-off, not new finding of that trade-off.
- Prior 2024 original article reports a stronger effect of high conspecific density on attack success. The new reproducible information is support limits, individual-bat and within-flight time opportunities, and the relation to our previously documented **22.6 predicted vs 10 observed successful attacks conditional on 36 observed high-density attempts**.
- Never claim observed calls directly equal number of neighbors or physically measured acoustic overlap. No receiver false alarms, prey availability, flight velocity or direct jam mechanism are available in this table.
- Never infer universal biological strategy, competition cause, remembered policy, or population prevalence from one original 10-bat source.
- Do not add a new fitted model, source density boundary or outcome filter. If insufficient within-bat/time support, report the failure precisely and end source-specific mechanism search.
