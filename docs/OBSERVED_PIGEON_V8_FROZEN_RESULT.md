# v8 observed pigeon forecasting result — archived and independently replayed (2026-10-27)

**Evidence status:** exploratory observed-data held-out forecast. **Primary contemporaneous-partner benefit NOT supported.** No prior `batter`, `ODSP`, `mina`, or `louis` results were altered, and no v8 model/hyperparameter was revised after opening outcomes.

## Data and frozen methodology

- Official public GPS archive: [Zenodo record 5010830](https://zenodo.org/records/5010830), original research DOI `10.5061/dryad.53f4b` (CC0). The exact original ZIP had 35,052,731 bytes; MD5 `8c8e95641182363ea7ad6d0a9a50a3b1`; SHA256 `959d6a9d277363e763aeabfb995f4d6b8d0a76675744126495d433b1b9b14ca0`.
- v7/v8 structural admission yielded **197/199** matched two-tracker pigeon flights (197 flight *episodes*, not independent biological pairs), 320,723 matched position pairs under the time/proximity gate; the observed median sampling interval was **1.0 s**, not nominal 0.2 s.
- Outcome-blind v8 [forecast contract](PIGEON_SOCIAL_FORECAST_CONTRACT_V8.md) defined 1-second **horizontal** turning (not vertical flight or 3D niche), exactly one common target set per predictor, own/route baseline, present-time partner, and 10-second-stale *same* partner. Fixed ridge penalty **30**, holdout by graph-connected bird identities across sites, 10 group-level folds, 10,000 seeded whole-group bootstrap replicates and an exact one-sided group sign test.
- Source data were downloaded and checksum-verified within the [successful public GitHub Actions run 40323282974](https://github.com/zuizui0223/boids/actions/runs/40323282974). **Raw GPS was not redistributed.** The exact output is pinned as [`validation_v8/results/pigeon_social_forecast_v8.json`](../validation_v8/results/pigeon_social_forecast_v8.json); its SHA256 is `509bd4748056ff952fed15c4a0155ed7bb17a6f80e959f8cfdeec461e24124b6`.

## Frozen primary result

| Held-out whole-bird-component predictor | Mean squared horizontal turning error (rad²) |
|---|---:|
| Own motion/route only | 0.019869452 |
| Own motion/route + partner 10 s earlier | 0.019646018 |
| Own motion/route + partner at the matched present time | 0.019559329 |

- **Primary actual-present vs 10-s-stale:** error gain `+0.000086690` rad² (relative reduction 0.441% vs stale model); whole-bird-component bootstrap 95% interval **[-0.000032368, +0.000217885]**, **6/10** groups favorable, exact one-sided sign **p=0.376953**. **Does not pass** the prespecified primary rule.
- **Secondary actual-present vs own-only:** gain `+0.000310123` rad², bootstrap 95% interval **[+0.000191535, +0.000419003]**. It was positive in **9/10** bird-connected groups and corresponds to a 1.56% MSE reduction from own-only. This supports predictive information associated with the partner/route/context but **not** a contemporaneous social response after the stale partner control.
- The cluster observations are 10 bird-identity-connected groups, not 197 independent pigeons or 320,723 independent samples. Even among different bird components, shared routes or release environments can violate ecological independence.

## Restricted structural information available in the original v8 receipt

For each training fold, two selected standardized **lateral** social-feature columns (a cohesion-like relative displacement and an inverse-cubic separation-like column) had reported condition numbers between **1.00466** and **1.00525** (median **1.004996**). These two columns were not algebraically near-identical on the *training feature rows*. **This narrow diagnostic does not establish full-model numerical identifiability, unique physical steering forces, or causal social influence.** It is consistent with the v7 known-truth warning that prediction of a trajectory and recovery of individual force coefficients are separate questions.

## v9 independent arithmetic/provenance check

[`validation_v9/audit_v8_receipt.py`](../validation_v9/audit_v8_receipt.py) verifies the exact byte digest, recomputes all group and pooled MSEs, all three contrasts, the pre-existing seeded bootstrap interval, the exact sign test and per-flight uniqueness **without downloading or refitting biological data**. Six fail-closed tests exercise mutation and aggregation errors. Its derived receipt is [`validation_v9/results/v8_consistency_audit_v9.json`](../validation_v9/results/v8_consistency_audit_v9.json). This is *not* a second independent empirical experiment.

## Ecological scope and next independent test

This one-species short homing-flight experiment tests **short-timescale partner-associated movement forecasting**, not sustained individual specialization, competition, resource specialization, species-level overlap or vertical/temporal niche partition. In particular, a useful partner predictor does **not** prove separation/alignment/cohesion forces, and a failed contemporaneous contrast does **not** prove social behavior absent.

The mechanistic link to other independent work remains prospective:
- [`batter`](https://github.com/zuizui0223/batter) establishes repeated bat individual vertical strategies without obligatory spatial segregation; these do not identify the causes of short-step turning.
- [`ODSP`](https://github.com/zuizui0223/odsp) distinguishes added ecological-state thickness from partition and independent held-out transfer; converting short turns into such distributions requires substantially longer, unbiased 3D/temporal observation.
- [`louis`](https://github.com/zuizui0223/louis) measures environmental-state buffering against matched local availability; route-following without matched habitat does not identify that mechanism.
- [`mina`](https://github.com/zuizui0223/mina) measures effective breeding-component concentration beyond a fixed-composition count null; this demographic endpoint is not a predicted outcome of the pigeon steering model.

**Stop rule:** retain the v8 primary failure. No alternate lag, ridge strength, binning, altered split, subgroup rescue or new favorable endpoint is authorized on this v8 archival source. Future Boids coefficient tests require *new data or a separately justified outcome-blind observation/geometry design* with independently assessed localization error and suitable context variability. No broad species-niche generalization has yet been observed.
