# Same place, different ecological states: a falsifiable cross-taxon synthesis (v1)

**Date:** 2026-11-15. **Status:** prospective comparative protocol + audited legacy evidence. **No newly calculated field effect**. This document does not change any frozen ODSP, batter, louis or boids primary result.

## Scientific question and novelty boundary

**When do animals with overlapping geographic distributions (A) retain their experienced environmental state despite a changing local environment, (B) retain predictable individual/species-specific patterns of state use, or (C) switch ecological states when accessible alternatives disappear?**

This is **not** a claim that spatial, temporal or vertical niche differentiation is new. Camera-trap temporal partition, animal habitat selection, movement-based niche segmentation and individual specialization already have substantial literatures. The testable addition proposed here is **the transition between state retention, non-exclusive identity differentiation and state replacement under measured changes in accessible local state portfolios**. The transition has **not** been empirically demonstrated yet.

An experimental or observational finding that animals merely select suitable habitat is not enough. Demonstrate a matched counterfactual against the specific states reachable and available at the same event/time, and a *pre-specified* independent evaluation that can fail.

## Formal decomposition; do not confuse these estimands

Let `x` be horizontal place, `a` an observed ecological state (time bin, altitude or water depth in different systems), `i` the organism/species identity, and `t` the observation time. `U_i(a | x,t)` denotes **use**; `A_i(a | x,t)` denotes time-matched **accessible availability** if measured. `A` must not be assumed uniform or silently inferred from used locations.

**Identity differentiation (not exclusion)**

`D = I(i; a | x)` can describe use-state differentiation among animals observed in spatial contexts. It is not an estimator of competition, fitness, a latent mechanism or corrected population activity without an explicit detection model. Its appropriate empirical test requires source-specific effort, valid independence filtering and *independent group* out-of-sample prediction.

**Matched environmental buffering**

For each bird, regress experienced used state `U_it` on mean same-event local availability `A_it` within that bird; construct `b_i^null` by choosing pseudo-used states from the same matched alternatives at each event. `B_i = 1 - b_i^used/b_i^null`, defined only for nonzero null slope. A high positive `B` indicates **decoupling of experienced state from local availability**, not direct proof of movement or optimization. A negative used slope can make B exceed 1. The existing published-source Louis pooled estimator uses a different weighting convention from the optional standard-library helper in this branch: **do not use helper output to reproduce its archived 0.162 figure**.

**Origin-matched categorical retention / replacement**

For *genuinely linked* observed movement step `s` with documented origin habitat `h0`, actual destination `h1`, and sampled available destinations `h_j`, define

`R_is = 1(h1 = h0) - mean_j 1(h_j = h0)`.

Compute per-individual means, then species summaries. `R>0` means excess retention, `R<0` means excess replacement, and `R≈0` means neither is detected. Missing exact origin/step identifiers, non-exclusive habitat categories, or incomparable random endpoint sampling are *hard stops*. A retrospective TRUE/FALSE paired habitat-profile ranking does **not** estimate `R`.

**Accessibility/exhaustion: a new empirical endpoint (not yet observed)**

Define a subject's prior reference-state interval from a **training-only window**, `Q_i=[q_i^- ,q_i^+]`; preregister tolerance and context. At an unseen time calculate `C_it = (# reachable independent habitat alternatives in Q_i)/(# reachable sampled alternatives)`. Identify portfolios that lose all compatible states `C_it=0`, *only with a sufficiently sampled or independently reconstructed habitat surface*. Compare future buffered vs replacement/relocation probabilities after loss of coverage, and adjust for available area, local environmental mean, habitat heterogeneity, season and individual. Predefine the accessible radius or graph by movement capacity, not by the observed outcome. Two Lake Erie random plots are insufficient for credible `C_it=0`; they can support a heterogeneity contrast, not proof of exhaustion.

## Existing field evidence — independent lanes, not a pooled meta-effect

| Lane and native response | Verified observation | Strongest allowed inference | Blocked leap |
|---|---|---|---|
| [ODSP / Serengeti](https://github.com/zuizui0223/odsp/blob/main/N2_EMPIRICAL_STATE_MATRIX.json), six 4-hour detection-time bins | 17 species; site-conditioned `I(species;time|site)=0.2242759874` nats, permutation `p=.005`; held-out site-fold gains `+.05724,+.04516,+.04514` | Predictable species-associated time use at camera sites | Competition-driven avoidance; fully corrected activity without effort/detectability validation |
| [batter / wild bats](https://github.com/zuizui0223/batter/blob/main/CURRENT_STATUS.md), within-session centered height shape | Five of six original panels preserve identity under session median-centering and null calibration; the focal Tadarida panel fails centering | Repeatable non-exchangeable individual state-use distributions across several systems | Mandatory vertical segregation, one stable route, universal process, inferred true tag offsets |
| [louis / King Rail](https://github.com/zuizui0223/louis/blob/main/README.md), used vs matched-random water depth | 190 matched events / 10 birds, pooled within-bird `b_used=.162` vs `b_null=1.001`; reported hydrological buffering 83.8%; 10/10 bird directions | Experienced-depth buffering relative to nearby time-matched hydrological opportunity | Identified geographic move-to-stay mechanism (coordinate-event join absent) |
| [louis / King Rail local portfolio](https://github.com/zuizui0223/louis/blob/main/results/lake_erie_local_heterogeneity_bird_robustness_v1.json) | 173 two-random events, pooled heterogeneity effect `−.0431` vs matched pseudo-null `+.2617`, post-hoc MC `p=.000020`; 7/10 per-bird signs negative; LOBO sign robust | Local state heterogeneity is a plausible **opportunity** for buffering | Independent replication, predictive accessibility threshold, general species response |
| [California waterfowl](https://github.com/zuizui0223/louis/blob/main/docs/california_waterfowl_step_state_preflight.md), intended source origin-to-destination contrast | Original FGDC metadata has 13 columns but no documented origin-state or step-origin join; four species | **STOP_ORIGIN_STATE_NOT_IDENTIFIABLE_FROM_SOURCE_METADATA** | Claiming any animal transition-state retention or replacement result |

Four or more species do not make four *replicates* of the same estimand. The Serengeti time state, bat vertical-distribution identity and King Rail continuous environmental buffering measure different properties. They can organize hypotheses, but their effect sizes are not numerically meta-analysable without a common eligible target.

## Prospective predictions and their potential falsifications

1. **Non-exclusive differentiation:** After controlling horizontal context, temporal/vertical state distributions may retain identity predictability without evidence of additional simultaneous spatial separation. Falsified as a general rule if independently held-out identity-aware state models do not beat properly matched identity-exchangeability nulls. Do **not** turn this into proof that competition was absent.
2. **Local portfolio buffering:** With accessible nearby reference states available, experienced conditions should respond less to fluctuating local mean conditions than do event-matched pseudo-users. Falsified in an external species/site if `b_used` is consistently indistinguishable from `b_pseudo` at its independent evaluation level.
3. **Portfolio exhaustion and response transition — THE NEW PRIMARY TARGET:** When the local reachable reference-state coverage drops below a predeclared threshold, probability of categorical replacement or broad relocation should increase, conditional on environmental mean and movement opportunity. Falsified if coverage has no incremental held-out predictive value over mean state, season, home-range condition and individual baseline. **Never use two random plots to classify zero coverage.**
4. **Retaining vs switching is not uniformly adaptive:** Some species may switch habitat even when a prior category remains available. A valid negative `R` in exact step-linked data is an informative counterexample. Do not select species-specific moderators or post-hoc habitat regroupings to rescue a universal-retention model.

## Minimal independent field design

**Protocol phase 1 (before state outcomes)**: Find one new *external*, not reused Lake Erie, cohort with: repeated individual identities, event time; matched used + independent alternatives per event (or repeated fine-resolution habitat surface); reliable coordinates/times defining reachable alternatives and, if testing transition, source-defined origin-step correspondence. Fix ecological state definition and exclusion criteria before inspection; verify checksum and source units.

**Phase 2 (locked baselines)**: M0 = environment mean, season, location, effort and individual/risk set baseline. M1 = M0 + spatial state-portfolio availability/coverage. M2 = M1 + frozen identity/history terms. Test M0 vs M1 for **incremental out-of-group prediction**, and M1 vs M2 separately for persistent individual policy information. Use independent **animals, years or study sites** for transfer; never split alternative endpoints or GPS fixes at random.

**Phase 3 (predeclared ecological response)**: `B` for matched continuous state buffering; `R` for exact origin-matched categorical retention. For coverage-exhaustion inference require repeated times with both `C>0` and `C=0` and adequate availability support; otherwise report **unidentifiable**, not zero effect. Assess detectability, pseudoreplication, habitat-map error, sensor/tag offset, species-dependent movement capacity and repeated-individual ownership.

**Phase 4 (decision criteria)**: Report per-group signs, held-out loss difference, cluster-bootstrap uncertainty, support/coverage of test covariates, and failures. Only report a generalizing new transition law if at least one external real system, with both retention and replacement opportunities and source-verified origin matching, shows a robust prospectively frozen incremental predictive effect. A synthetic ABM can demonstrate sufficiency or nonidentifiability, but cannot fill the external field-validation gate.

## The resulting manuscript choice

**Near-term honest format:** a hypothesis-driven empirical perspective/synthesis anchored by three incommensurate empirical lanes and a **missing** independent transition test. It is *not yet* a definitive four-system mechanism experiment.

**Full original empirical paper:** after obtaining and passing the external availability+origin gate, make portfolio exhaustion → state-retention/replacement transfer the paper's primary result, then use Serengeti and bats to show why identity differentiation and physical sorting need not be treated as one property.

**Possible working title:** *When accessible ecological states disappear: from individual-state persistence to habitat-state replacement*.

## Related work / novelty safeguards

- van Toor et al. (2016), *Temporal segmentation of animal trajectories informed by habitat use*, Ecosphere, doi:10.1002/ecs2.1498: temporal changes in availability and use have already been separated; no first-to-do-so claim.
- Swanson et al. (2015), *Snapshot Serengeti*, Scientific Data, doi:10.1038/sdata201526: multispecies camera-trap source.
- Camera-trap independence-filter studies: temporal structure is affected by herd behavior and repeat detections; a naive detection record is not an independent animal activity event (e.g. doi:10.1002/ece3.9408).
- Brewer et al. (2023), *King rail home range and microhabitat*, Ecology and Evolution, doi:10.1002/ece3.10043: primary published habitat-selection basis distinct from the later Louis matched buffering analysis.

## Code supplied with this protocol

`comparative_state/metrics.py` exposes three **generic descriptive/statistical primitives**: conditional state information, event-matched hydrological buffering, and exact origin-linked retention. `python -m unittest discover -v` exercises known-truth invariants (including a mandatory origin-missing failure). Passing tests is **software integrity**, not a new animal result. The immutable source endpoints and their limitations are registered in `comparative_state/evidence_manifest_v1.json`.

