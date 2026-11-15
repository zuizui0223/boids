# Independent field annual-community hydrology transfer: pre-outcome contract v3

2026-11-15: source checksum and schema/ID inspected, **before reading any original species abundance counts**. Source: Secondi et al. (2026) [Zenodo 18161913](https://doi.org/10.5281/zenodo.18161913) CC BY 4.0, linked paper [10.1007/s10344-025-02051-x](https://doi.org/10.1007/s10344-025-02051-x).

## Why the previous v3 visit-state test is not available

The original workbook has 7734 subunit×visit environmental rows, but the actual 48-species waterbird abundance dataset is **site×year aggregated**: precisely 90 records = 12 sites monitored 2015–2020 + six sites monitored 2018–2020, 18 site units total. The first two rows are group labels and exact header; 48 raw species columns K:BF, `Abondance` BG. No observed bird abundances at individual visit dates are given, so **visit-matched community state switching is not identifiable from the original source**.

Revised *separate* prospective target: do source-observed **year-to-year changes** in water area / water-depth heterogeneity improve held-out-site prediction of relative bird-species assemblage composition compared with previous-year community persistence and common year effects? This does not imply animal movement, experimental causality, or individual state portfolio mechanisms. The original publication already described variation in taxonomic/functional waterbird diversity by hydrological/vegetation heterogeneity; the incremental endpoint here is the separate **year-transition predictive transfer** to unseen independent sites.

## Frozen source and sample

Original workbook provider MD5 `a08325ee4e24acfc159b1cd7c1fe425d`, original SHA256 `b8d5c2c845460972be81d67c5b3cbb1f5e71a657a3f9611bff510198930d6fd9`. Must match. Only use sheet `Bird by survey`; exact 90 rows / 18 sites / 48 named species in K:BF and exact original environmental predictors E:J: WA.mean / WA.sd (water area level and heterogeneity), VH.mean / VH.sd (vegetation height heterogeneity), WDH.mean / WDH.sd (water-depth heterogeneity). **WDH.mean is an index of depth heterogeneity, not mean water depth**. Year/site parsed directly from `Survey_ID` (`YYYY_SITE`). Any missing, negative or noninteger species counts, nonfinite environmental value, source total mismatch or duplicated site/year => STOP, no imputation. Exactly adjacent years only, both yearly totals strictly >0; need ≥50 transitions across ≥12 sites, otherwise scientific `PRIMARY_NOT_ADMITTED`. Expect max 72 transitions, not 7734 independent observations.

## Fixed analysis

For each adjacent site year `t->t+1`, source-wide 48-species count vector `c_{s,t}`. Baseline forecast composition starts from Jeffreys-smoothed previous-year profile `p_prev,j=(count_prev,j+0.5)/(total_prev+24)`. Target is the **48 species within-site change in centered log compositions**, `log(p_next)-log(p_prev)` mean-centered over species, with +0.5 smoothing. A multioutput Ridge regresssion estimates common (across sites) residual change, with L2 alpha=25, intercept unpenalized, each independent training site given total weight 1, no hyperparameter selection from real data. Holding out a SITE for every fold, train only on other sites, standardize environmental predictors on training fold only, predict target log-ratios and add them to heldout site's observed last-year log profile, then renormalize with softmax. The last-year profile is observed at the prediction origin; it is not test-year information.

- M0: next calendar year indicators only (2016–2020). This is a year-trend-adjusted *composition persistence* baseline.
- M1 primary: M0 + **four year-to-year water state changes**: delta(log1p(WA.mean)), delta(log1p(WA.sd)), delta(WDH.mean), delta(WDH.sd).
- M2 secondary: M0 + delta(VH.mean), delta(VH.sd).
- M3 secondary: M0 + all six deltas. No state variables chosen using new outcome scores.

Scoring: per site-transition cross-entropy `-sum_j (observed_next_count_j / next_total) log(predicted_p_j)`, in nats per bird-count, then mean within each held-out **site**, followed by equal average across sites. Primary gain `CE(M0)-CE(M1_water)`; + means better water-state-based out-of-site transfer. Report M2/M3 even when negative. 10,000 bootstrap resamples of sites, fixed seed 20261115, percentile CI 95%; primary positive only if **lower CI>0 and >half of sites positive**. Never treat bird counts, species, site-year, or habitat subunits as independent replication units. Source totals are compositional, and survey effort/detectability variation remains unmeasured. This is cross-site retrospective transfer with next year's environment observed; it is **not an operational future forecast unless future environmental states are separately predicted**.

## Hard claim ceilings

Do not say 18 sites are 18 species-level or individual-movement replications; 48 species are not 48 independent effect samples. No inference for the abundance of species in a given visit, or movement switching under time of day. Environmental predictors and responses are year aggregates, affected by habitat management and incomplete observer effort, so correlations do not identify selection, memory, dispersal, state accessibility, causal competition, or climate change response. Regardless of the effect sign, carry original negative results and publication precedence into interpretation.
