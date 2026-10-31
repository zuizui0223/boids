# Exploratory archived deer R × X coupling check — 2026-10-31

**Status:** reproducibility of a new **post-outcome, descriptive** calculation on the existing 36-month derived aggregate CSV. No raw GPS was accessed. No new independent sample or confirmatory p-value. This does not modify the original source design.

## Exact input and definitions

CSV: https://github.com/zuizui0223/batter/blob/prospective/multitaxon-identity-ecology-v1/prospective/multitaxon_individuality/DEER_SEASONAL_RX_MONTHLY_2026_10_20.csv
- Repository: zuizui0223/batter, branch prospective/multitaxon-identity-ecology-v1
- Git blob SHA: `3d4e126de6ada1b6fb851ec0b3eda2203c59c0de`
- Exactly 36 source-year×month records (12 per year).
- R: `same_record_personal_weighting_gain`: anonymous-pool CRPS minus personal CRPS on matched held-out steps, in transformed-displacement CRPS units. Not a causal or universal information measure.
- X: `matched_R_cohort_X_5km`: within-month day-balanced 2-D occupancy overlap at 5-km grain on the **same monthly evaluated animals**. Not direct resource or simultaneous physical use.

## Recomputed descriptive Pearson r (12 months in each year)

| Year | n months | corr(R, X) | mean winter R (Dec/Jan/Feb) | mean summer R (Jun/Jul/Aug) | mean winter matched X | mean summer matched X |
|---|---:|---:|---:|---:|---:|---:|
| 2018 | 12 | -0.135356 | +0.00073248 | +0.00195223 | 0.188490 | 0.043655 |
| 2019 | 12 | +0.501004 | +0.00019630 | +0.00290803 | 0.099773 | 0.105539 |
| 2020 | 12 | +0.456314 | -0.00064683 | +0.00182233 | 0.099070 | 0.155916 |

All 36 months pooled: **Pearson r = +0.039499**.

### What the calculation supports

The naive unconditional expected **negative** R–X association does **not** show a reproducible sign even across these three calendar years from one source. Winter and summer average R ordering is the same in each year, but monthly X ordering differs among years when X is matched to R's month-specific eligible animals.

This cannot be interpreted as proof of no ecological relation: n=12 months/year are serially dependent, study and biological animals are reused, environmental availability is unmeasured, dates/year effects confound both variables, R is small and post-outcome estimator details matter. No Pearson significance or source-generalization claim should be made. The annual **constant-cohort** X sensitivity and per-animal paired R sensitivity used in the original source report operate on different subject sets and must NOT be relabeled a matched within-animal causal contrast.

### Minimal reproducibility recipe

For each year separately, take the 12 rows from the exact SHA-pinned CSV and compute the ordinary unweighted Pearson product-moment correlation between columns `same_record_personal_weighting_gain` and `matched_R_cohort_X_5km`. Take pooled r on all 36 rows. Mean values use month in {1,2,12} and {6,7,8}; this is a same-calendar-year grouping, not a contiguous ecological winter. Do not treat the correlations as independent site or species-level replication.

**Scientific implication:** no paper should assert that behavioral individuality universally means geographic partitioning or that the two are consistently negatively coupled. A prospective independent ecological opportunity moderator is needed before testing a real axis-conversion hypothesis.
