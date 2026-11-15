# V4 source-unit anomaly amendment — exploratory, after source-domain inspection, before model outcome scores

**2026-11-15.** The immutable v3 annual transfer contract in `MARAIS_BRETON_ANNUAL_TRANSFER_FREEZE_V3.md` terminated at source admission after detecting **noninteger species abundance cells**, without any annual environmental predictor score. Source MD5 stayed verified `a08325ee4e24acfc159b1cd7c1fe425d` (Secondi et al. 2026 https://doi.org/10.5281/zenodo.18161913; CC BY 4.0).

Original workbook's 90 site-years includes two anomalous exact source keys `2019_18` and `2020_18`. At these two siteyears, both last species columns contain noninteger values, and the sum of the 48 displayed species columns differs materially from the source `Abondance` total. Neither exception appears elsewhere. Their original siteyear IDs and the source checksum are sufficient to reproduce the QC, without changing any response to suit environmental predictors.

**Frozen correction for a separate exploratory calculation:** exclude *all* rows of original site 18, not just the two affected years; do not fill, round, interpolate, borrow totals, replace outcomes or recode species. Remaining 17 sites × 87 site-years yield at most 70 adjacent-year transition observations. The previous v3 scientific stop is retained as the original result. If the exact anomalous IDs, checksum, or data-quality failures change, v4 must also stop.

Analysis otherwise preserves all v3 definitions, taxon roster (48 original columns), predictor roster, Jeffreys smoothing 0.5, Ridge alpha=25, next-year calendar baseline, own prior-year composition, whole-site holdouts, water M1/vegetation M2/all M3, equal-site cross-entropy, seed 20261115, 10,000 site resampling, and conservative primary pass condition (95% lower site-bootstrap >0 and >half sites positive).

**Claim status: EXPLORATORY_POST_SOURCE_DOMAIN_AMENDMENT**, because the v3 source outcome domain was inspected and the exclusion was decided thereafter, even though no predictor-effect scores had been seen. This cannot qualify as a fully prospective confirmatory field result. Still no migration, causal animal selection, future environmental forecasting or direct state-maintenance evidence.

Authors of the linked 2026 European Journal of Wildlife Research paper already analysed richness, abundance, functional diversity and species turnover; the new endpoint is the *entire relative species composition* out-of-site environmental increment over previous-year composition.
