# v10d post-result geometric-controls audit

**Post-result exploratory only.** v10c result, confidence intervals and original frozen PASS/FAIL remain exactly unchanged.

The original v10c road and traffic start–end similarity improvements are unexpectedly large (+0.630 and +0.153 nats per movement). This may arise because simulated alternatives differ in endpoint distance and network geometry from observed movements, or due to generic local continuity of any environmental surface.

## A. Same movement length, tested state continuity

For each original 1-used/20-alternative matched choice stratum, restrict comparators to candidate steps whose length is 0.8–1.2× the **used** step length, requiring >=2 alternatives. For road exposure, traffic exposure and a nonroad control (stream-distance), compute an exact candidate divergence rank of closeness to its own source state: `rank_j = P(other distance-matched candidates differ MORE from start than candidate j) + 0.5 × ties`. Crucially, a candidate-specific null is obtained by treating each of the 21 source-available candidates as hypothetical observed in turn, applying the **same length-matching rule**, then averaging each valid candidate's rank. This adjusts the expected null for length-conditioned candidate selection; the primary response is observed rank minus this pseudo-used mean, averaged within each original animal then equally across animals. Animals bootstrap 10,000 times. This is a post-result diagnostic, not a new preregistered test. If all variables show similar positive rank effects, generic spatial continuity remains an important explanation.

## B. Added value beyond generic stream continuity

Retain all original matched source groups and original 31 animal IDs. Refit two *new exploratory* conditional-choice models with the frozen M0 destination covariates and whole-individual folds: baseline M0 + `abs(log1p(stream_end)−log1p(stream_start))`, and baseline + `abs(log1p(road_end)−log1p(road_start))`. Compare same held-out labels; equal-animal average and 10k individual-bootstrap CI. The added effect can indicate road-specific information beyond a measured nonroad continuity covariate, but does not identify intention, independent causal selection, or true reachable options.

No model score from this diagnostic may be substituted for v10c's frozen primary PASS. No biological species-wide synthesis from one study.
