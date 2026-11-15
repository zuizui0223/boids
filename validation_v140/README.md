# v140 source-fingerprinted lunar/weather confounding audit

Paper DOI 10.1186/s12862-026-02521-z; real Roscoff hourly source xlsx source SHA-256 `2df8fac5749d804b8d16d98db065ba19dc3796a4a01ce1cfa87c56f5d622d0d0`.

The prior v139 reported +0.03170542 nats per **retained** acoustic-hour for a fixed 5fold model adding tidal-coefficient-level × night, but that simplified Poisson comparison did not adjust for moon illumination, weather, seasonal sampling trend, or score overdispersion. This preregisters a **post-hoc exploratory robustness** check (not a prospective preregistration of original ecological hypothesis).

Fields taken from same XLSX table S1: original light lux, wave height, wind speed/direction, temperature, lunar illumination fraction, actual continuous tide coefficient, calendar date, category and water height. All are verified against original 421 acoustic-hour rows by exact keyed original date/hour. All source 59 flow-masked hours remain missing, **never zeros**. Missing weather covariates (if any) are imputed using each training fold only. 5 grouped CV folds hold out entire original 24-hour selection periods, one per source tide coefficient category.

Seven? **Eight** prespecified predictor models cross categorical-vs-continuous tide, weather/date adjustment, night×tidal coefficient and night×moonlight. Six paired comparisons, for sound annotation counts and number of sound types. Proper NB predictive scores use **training-derived common shape** for an additive/interaction pair; the mean model is regularized Poisson with fixed ridge 0.5, not a fitted NB GLMM. Also reproduce all 20 original periods and the ten unmasked Low+Medium blocks separately. No statistically independent multi-coast replication or causal physics attribution; no arbitrary p-values.
