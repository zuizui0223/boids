# v39-A — transport-only amendment after source failure (2026-11-03)

Two original GitHub Actions runs ([41414708919](https://github.com/zuizui0223/boids/actions/runs/41414708919) and [41414716341](https://github.com/zuizui0223/boids/actions/runs/41414716341)) failed with RWS source HTTP connection timeouts before calculating any published v39 bird or week prediction scores. Regression unit checks passed. **SOURCE_STOP is not evidence of a negative biological effect**.

This amendment changes only source delivery: original station, WATHTE meting metadata, cm/NAP conversion, fixed +01:00, monthly request boundaries, eligibility gates and all frozen M0/Mactual/Myear_ago model predictors/years/offsets/bootstraps are identical to the prior v39 contract. Network calls use up to **three** bounded retries for transport exceptions only (25s timeout each plus 1/2 sec backoff), no retries on datum/units/time violations. Original RWS monthly counts are reported; no raw time series or animal locations committed.

Each island now runs in an independent GitHub Actions matrix job with its own aggregate result artifact. If one source becomes unavailable, the other remains evaluable. No ecological score is reported until that site's authentic original source and eligibility gate pass. This amendment is after prior v32–v36 results and is not new preregistration of the ecological question.
