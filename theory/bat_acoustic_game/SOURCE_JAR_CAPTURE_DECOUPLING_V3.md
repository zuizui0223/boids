# Why less acoustic interference need not yield more prey captures

**2026-10-31 — SOURCE-VERIFIED SECONDARY 2020 MODEL-OUTPUT REANALYSIS.**
No new bat measurements, no faithful 2020 MATLAB forward-model run, no independent 2026 2D group-flight forward-model run, no prospective multi-paper causal confirmation. The original studies' outcomes and known explanations take priority. Freeze JAE/BE wildlife and other `boids` branches unchanged.

## Source-level numerical answer

Mazar & Yovel 2020, *eLife* 9:e55539, DOI [10.7554/eLife.55539](https://doi.org/10.7554/eLife.55539), Figure 2 numerical outputs. Publisher source files are byte-pinned:
- Correlation receiver `elife-55539-fig2-data1-v2.txt`: SHA256 `e36b0c461fc7aa448ecbd6d2fc8f724c0ac171f7ca972389f04a88cfe9c9c8b2`, **240** simulation-output rows.
- Filter-bank receiver `elife-55539-fig2-data2-v2.txt`: SHA256 `285867a96b3fefd395bb998c1061496aca519cc167b18244f07b0632c50279ad`, **240** simulation-output rows.

Both contain **20 rows per treatment arm per group size** for sizes 2, 3, 5, 7, 10, 20 (source prey number 20). Group-size and receiver were matched, but matched simulation **random seeds were not identified**. These are published model-output rows, **not 480 independently tracked biological bats**, and there are no valid population-level effect p-values here.

### Original source finite-mean contrast: JAR minus no JAR

| group size | correlation capture Δ | filter-bank capture Δ | filter-bank total-interference ratio Δ | filter-bank false alarm rate Δ |
|---:|---:|---:|---:|---:|
| 2 | −0.40 | 0.00 | −0.001933 | −0.002058 |
| 3 | +0.10 | +0.05 | −0.002380 | −0.002677 |
| 5 | −0.60 | +0.40 | −0.013625 | +0.000049 |
| 7 | +0.25 | −0.15 | −0.009725 | +0.005396 |
| 10 | +0.70 | −0.15 | −0.013210 | +0.003538 |
| 20 | −0.40 | +0.45 | −0.035210 | +0.003272 |
| balanced six-group arithmetic average | **−0.0583** | **+0.1000** | **−0.012681** | **+0.001253** |

**New secondary quantitative observation about published outcomes:** every tested group size has lower source-defined total interference ratio when JAR is present in the filter-bank architecture, **but four of six group sizes have a higher modeled false-alarm rate and capture gain has mixed signs**. The earlier 2026 group's published lower *potential misdetections* should not be equated to the 2020 filter bank's modeled detected false alarms or number of captured insects. Different detectors, definitions and tasks make those estimands non-exchangeable.

An **exploratory finite-point-estimate two-outcome screen** (captures higher, false alarms lower) classifies groups 2 and 3 as favourable to JAR, groups 7 and 10 favourable to no JAR, and 5/20 as capture/false-alarm tradeoffs. This is **not** established game equilibrium, reproducible biological regime threshold, population payoff or a significant separation. In particular, effect sizes are small relative to variation among original simulator rows.

### Critical original-simulation row variation audit

Absolute change in mean captures divided by pooled *row-level* standard deviation of the original two arms:

| group size | absolute normalized capture mean change | absolute normalized false-alarm change |
|---:|---:|---:|
| 2 | 0.000 | 0.231 |
| 3 | 0.033 | 0.141 |
| 5 | 0.290 | 0.002 |
| 7 | 0.115 | 0.222 |
| 10 | 0.136 | 0.142 |
| 20 | 0.399 | 0.189 |

Thus even the most visibly positive finite capture difference is less than 0.4 pooled simulator-output SD. The source does not provide an explicit full independent-run grouping or random-seed pairing crosswalk; do **not** fabricate bootstrap biological standard errors or promote these fragile signs into evolutionary strategy regimes. Only the descriptive **decoupling of source endpoints** is justified.

## Why 2020 and 2026 are NOT the same experiment

The original 2020 MATLAB `BatSonarDecision.m` has a JARMode branch whose observed activation is **gated by the current `IsHuntedPreyMasked` flag** (read-only SHA-pinned source audit). A different implementation could have different dynamics; the source uses sonar pulse duration, power and terminal-frequency state in search / approach / buzz behavioral phases.

Hase et al. (2026), *Proc. R. Soc. B*, DOI [10.1098/rspb.2026.0921](https://doi.org/10.1098/rspb.2026.0921), instead experimentally observed frequency adjustment under controlled playback of jamming stimuli (with **no measured prey-capture outcome** in that laboratory protocol), fitted a leaky-integrator model, and demonstrated reduced **potential** acoustic misdetections in its separate 2D group-flight simulation. Its full independent 2D simulation is not reproducible from the 15 source Figshare files alone (plot scripts and precomputed simulated trajectories are available; group simulation code is not independently confirmed present).

In contrast to mistaking these papers for opposing tests of the **same** JAR/capture treatment, the correct descriptive bridge is a sequence of different objects:

```
emitted spectral adjustment
    ↓ [conditional receiver/transmitted/ambient signal physics]
acoustic overlap or potential misdetection
    ↓ [actual detector false alarms, true prey misses]
behavioral sensor output
    ↓ [action/recovery cost, ongoing bat-prey dynamics]
prey capture and longer-term fitness
```

The arrows are **hypothesized or source-model specific**, not measured as one causal chain across the 2020 and 2026 papers.

## Conditional theorem already implemented and tested (NOT fitted to bats)

Under the idealized renewal-reward model with unadjusted false-alarm workload W0, fraction of genuine detection lost δ and ratio of costly false alarms under JAR to no JAR ρ, additional captures occur only if:

```
(1 - δ - ρ)*W0 > δ.
```

This is exact for the stated toy model, NOT an actual bat threshold. In particular, ρ from Hase's count of *potential* misdetections **cannot** automatically be used as the ratio of actual costly false alarm rates. Inverting fixed total workload and fixed per-event recovery assumptions reverses the example predicted group-size ordering. That sensitivity is part of the inference, not a model defect to be hidden.

**Novelty ceiling:** simply demonstrating that JAR does not improve capture is already Mazar & Yovel 2020; simply demonstrating that spectral separation may reduce potential misdetection is already Hase et al. 2026. Neither can be relabeled a novel standalone discovery. The next useful study is genuinely new source-constrained receiver/behavior mapping with **matched acoustic physics**, or a transparent statement that the common physical data and code needed for identification are unavailable.

## Execution / reproducibility

- [2020 original model archive, original 2026 R code and Figure source audit](https://github.com/zuizui0223/boids/actions/runs/41191217131).
- [2020 Figure 2 factor-only preflight](https://github.com/zuizui0223/boids/actions/runs/41191309489).
- [2020 original Figure 2 full stratified numerical recomputation](https://github.com/zuizui0223/boids/actions/runs/41191552790).
- [2020 source two-endpoint point-estimate classification](https://github.com/zuizui0223/boids/actions/runs/41191677355).
- [2020 source-row variation check](https://github.com/zuizui0223/boids/actions/runs/41191875666).
- [2026 original experiment low/high stimulus slope reanalysis](https://github.com/zuizui0223/boids/actions/runs/41190407233).
- [Toy/analytic 31-test model workflow](https://github.com/zuizui0223/boids/actions/runs/41190663862).

Source code / machine-readable receipts:
`original_model_preflight_v5.py`, `elife_figure_schema_v6.py`,
`ELIFE_FIG2_NUMERIC_CONTRACT_V1.md`,
`elife_fig2_source_analysis_v1.py`,
`elife_fig2_pareto_v1.py`,
`elife_fig2_row_variation_audit_v1.py`,
`ELIFE_2020_SOURCE_PAYOFF_LEDGER_V1.json`,
`endpoint_bridge_v2.py`,
`PUBLISHED_JAMMING_REANALYSIS_CONTRACT_V1.md`.

No original publisher source code, raw participant audio, original individual call table, bat GPS or sensitive study locations are redistributed through the committed files.

## Next-stage stop/go decision

**Next source-authoritative gate:** A headless fixed-physics rerun of 2020 original MATLAB detector/sonar logic, or a precisely documented and tested mathematical port of an actual source module, is necessary before claiming to explain the full 2020-vs-2026 result difference. Simply tuning the existing illustrative toy payoff to reproduce either published sign would be tautological, not a new scientific test. If 2026 group simulation implementation is unavailable, do not label any newly coded 3D model an exact replication.

The frozen bat field/behavioral manuscripts must not be altered to promote this theoretical inference; PR #36 remains draft until an independent common-physics result exists.
