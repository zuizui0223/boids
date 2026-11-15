# v145 constrained temporal cooccurrence null (source-real)

The analysis is not a new causal tide- or moon-related fish effect. It is an actual-data robustness examination for observed within-site fish chorus coincidence in the complete original California 9-site/60-deployment corpus (source: Kim et al. 2025, DOI 10.3354/meps14910; original Dryad DOI 10.5061/dryad.q2bvq83sw).

Primary concern: v144 found e.g. CI01 bocaccio×UF440 O=1,084 recorded co-chorusing hours, 107 expected if clock/season ignored, 773 expected with month×hour-of-day, 893 expected with year×month×hour. But this hourly expectation ignored long chorus bouts, daily observation changes and source audibility.

v145 restricted shifts retain only locally complete 24h days with no explicit Off effort/Noise overlap, split into site/yearmonth/contiguous-day runs of >=7 days. In each run circularly shift an entire type-B 24h-by-day profile by a random number of whole days, preserving daily clock niche and most multi-day chorus autocorrelation (except wrapping). Type A remains fixed, so the observed original simultaneous hour count is compared to the null. Calculate exact mean across all possible independent within-run shifts, and 1,999 deterministic Monte Carlo shifts by block for exploratory compatibility. Screening requires >=60 retained days, each type >=100 observed positive hours and expected overlap >=10; all filtered and unfittable conditions are retained.

P-values are **not tests of true interspecific acoustic cooperation** because run exchangeability is not guaranteed with weather, environmental forcing, detection processes, anthropogenic noise and unsampled days. Treat q-values as adjustment *under the chosen shift null* only, no global meta p-value. The number of contiguous run blocks and fraction of actual source effort retained must be published.

No raw XLS/audio source files redistributed; original 60 SHA checks run again; old v144 result frozen.
