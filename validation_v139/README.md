# Roscoff 2026 original acoustic source and tide-solar model check

Target primary study: [Roscoff kelp forest fish acoustic communities](https://doi.org/10.1186/s12862-026-02521-z), PMCID PMC13179613. Paper states 20 selected 24h sampling periods (480 scheduled h), 59 masked-by-flow h excluded, 421 analyzed h; 26 sound types and 6,172 annotations.

The original statistical-analysis workbook is downloaded and hashed in CI, then sheet names, sample headings and shapes are extracted. DO NOT infer 480 unbiased hours, individual fish counts or tide-specific acoustic detection from the original 421 observed hourly bins. Complete reanalysis requires explicitly marking missingness due to tide-related flow masking and retaining day or date as a cluster.

Results from this probe alone = inventory, not a pooled or empirical biological result.


## Two separate empirical interaction targets

The source is 421 retained hours, 20 source S24_num noon-to-noon blocks, and 59 nonrandom masked missing hours in 480 scheduled hours. The original four tidal coefficient levels contribute five selected 24h periods each.

Six prespecified grouped five-fold Poisson predictive models compare constant, night, night+physical water height, night+height+night×height, night+height+four tidal coefficient category main effects (three dummies), and night+height+coefficient×night. The physical-height interaction and spring-neap coefficient interaction are distinct. No claim of reproducing the published full negative-binomial GLMM with wind, wave or light; no unbiased acoustic rate in excluded hours, fish counts, causal effect, or globally pooled coefficient. All heldouts are complete selected 24h source periods, stratified across the four tidal coefficient levels.
