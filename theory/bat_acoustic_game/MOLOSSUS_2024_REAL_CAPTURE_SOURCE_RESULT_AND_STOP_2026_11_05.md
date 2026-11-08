# Bat social foraging: observed acoustic-density trade-off does not reliably transfer across individuals in this archive

**2026-11-05 · Completed original-source 2024 *Molossus nigricans* reanalysis. NO new field or laboratory measurements.** Original authors' results and data take priority. A model's failure to transfer within this source is **not evidence that the social foraging trade-off itself is false**, nor a proof of no individual differences or competition.

## Original independent bat source genuinely admitted

Krivoruchko et al. 2024 *PNAS* DOI [10.1073/pnas.2321724121](https://doi.org/10.1073/pnas.2321724121), public source [PMC11287165](https://pmc.ncbi.nlm.nih.gov/articles/PMC11287165/). We located its official Europe PMC supplementary archive: `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11287165/supplementaryFiles`, archive SHA256 `a1b353f7f32f2b1a465e8568d6dfea5282df399e1b501394b776433f22328c11` (1,785,107 bytes). Original supplementary Excel `pnas.2321724121.sd01.xlsx`, SHA256 `92acbc36cce42028bfd5a07ad1ec8aa8062121575d6d665dc7392b47222f562d` (163,865 bytes); one original worksheet **4,300 rows × 8 columns including header**. This is a DIFFERENT bat species and DIFFERENT publication from the previous 2026 Hase *Miniopterus* source.

Source headers `bat,sec_group,numel_5swindows,sum_attacks,sum_success,sum_cons,sum_commute,sum_disrupt`. Original source **10 biological bats, 4299 observed 5-second grouped rows, 1,354 acoustic-identified attacks, 1,006 successful attacks independently identified from chewing, and 57,943 other-bat calls**. Original source count and field definitions from the paper. Source primary publication **already showed** that successful prey capture per time is greatest in the presence of a limited number of neighbors and falls at higher density. This reanalysis does NOT claim that as a new ecological pattern.

## IMPORTANT: the wrong exposure assumption was detected and corrected before adopting any source predictions

The first, prerecord M0/M1/M2 version treated source `numel_5swindows` as an **exposure denominator**. Its sum 197,566 would have implied **274h** of original five-second flight observations, whereas 4299 ORIGINAL ROWS represent about **358 minutes** total and individual original source flight lengths 16.83–50.5min, matching the article. First-stage V1 Poisson scores are **INVALID AND QUARANTINED**. We have not silently deleted them.

Publisher-authenticated source index `sec_group` is incremented by 1 in the 9 source bats with no missing original intervals; 10th source bat has 414 observed rows indexed 1–421, with exactly **7 missing indices and no duplicates**. The missing source windows were not imputed. Individual 5sec rows have 0–4 original attacks (consistent with article) and neighboring call counts 0–245 (published >75 high-density category). This supports ONE OBSERVED ROW=ONE ORIGINAL FIVE-SECOND WINDOW as a source-compatible rate denominator. The meaning of `numel_5swindows` itself is not sufficiently justified, so it is NOT used as time exposure or as an ecological predictor.

Corrective source protocol [frozen before the corrected-score run, but AFTER seeing the invalid V1 outcomes](MOLOSSUS_2024_CAPTURE_CORRECTED_EXPOSURE_V2_PREOUTPUT.md) keeps original source 10 bats/4299 observed rows as primary and source-grain-consecutive nine bats/3885 rows as structural sensitivity. Same three numerical models, same penalty, same density variable and source quality, no model refitting to chase a desired direction.

## Supported source reanalysis of original real captures

Source density is count of **other-bat echolocation calls / original observed five-second interval**; it is NOT a headcount of different neighbors, nor a measured physical airspace overlap.

| Other-bat calls per original 5s | Observed 5s windows | Unique original bats | Attacks / 5s | Successful attacks / attack | Successful captures / 5s |
|---|---:|---:|---:|---:|---:|
| **0** | 1552 | 10 | 0.289 | 0.761 | 0.220 |
| **1–25** | 2008 | 10 | 0.314 | 0.792 | 0.249 |
| **26–75** | 627 | 10 | 0.381 | 0.649 | 0.247 |
| **≥76** | 112 | 8 | 0.321 | **0.278** | **0.089** |

The observed high-call regime shows **remaining attack activity** but sharply lower fraction of successful attacks. It is consistent with the originally published cooperative-search / encounter-opportunity versus high-crowding cost, but **it cannot identify whether the causal reason is spectral masking, physical collision/avoidance, prey exhaustion, prey-community variation, or behavioral state**. High density accounts for only 112 source windows and eight bats. Because original attacks/capture had already been reported in 2024, this descriptive table is a SOURCE REPRODUCTION, NOT a first discovery.

## The source-INTERNAL new test: hold out whole bat IDs

Before seeing the corrected score, three models were frozen to train on 9 original bats and predict the **entire withheld bat**:

1. **M0**: constant training bat catch rate (per original 5-second observed interval);
2. **M1**: Poisson capture rate with `log1p(conspecific calls)` and fixed quadratic predictor (the original paper already described nonmonotonic patterns);
3. **M2**: attempt-rate Poisson × successful-capture-fraction logistic, fitted entirely from other original bats. **This is statistical decomposition, not identified cooperation/competition causality.**

All models evaluated on identical held-out source rows with **bat-equal mean** of source Poisson capture-count deviance per original 5s window (smaller is better), and source-bat bootstrap difference intervals. Original source 10 distinct bats, not 4299 independent participants.

| Original bat exclusion | M0 density-blind | M1 direct density | M2 attack×success |
|---|---:|---:|---:|
| **All original 10 bats** | **0.76232** | 0.76498 | 0.76516 |
| **Nine time-index-complete bats** | **0.77317** | 0.77702 | 0.77682 |

**Result:** neither tested acoustic-density forecasting model improved average original-bat-heldout Poisson deviance. Relative to M0, M1 has source-bat mean Δdeviance **+0.00266** (better than M0 in **4/10** source bats; source bootstrap interval [−0.00092,+0.00659]); M2 **+0.00284** (better in **3/10** bats; source bootstrap interval [+0.00023,+0.00641]). On the nine-grain-complete-bat sensitivity, both models still have higher average deviance. Small differences, small biological sample and source reuse preclude general population inference.

A secondary mean absolute count-error-per-exposure metric is nearly tied and can yield a different ordering: on all 10 bats, M0 0.37155, M1 0.37109, M2 0.37140. The **primary** Poisson deviance choice was frozen before viewing corrected source outcomes; do not silently switch the target metric to claim a positive prediction. This metric-dependence is part of the assessment.

### Scientific distinction: average pattern versus transfer

The original averaged source capture-vs-density curve can be real and significant in the source model while a fixed source density rule **fails to forecast individual bats held out of that same study**, due to sparse high-density exposure (especially 8 bats), heterogeneity in time/patch prey, source observation state, and model misspecification. **The present source result does not uniquely identify which of these explanations is responsible.**

The registered new scientific objective, predicting whether social bat acoustic signals HELP find prey versus COMPETE during capture using a source-calibrated receiver model, is not achieved here. The source does not carry simultaneously calibrated emitted and received waveform spectra, physiological receiver classification, experimental conspecific spacing, or a causal manipulation. The paper's original published hypotheses are prior art. A novel individual-specific "bat ecology law" is **NOT** established.

## Source-of-truth and verification

- [Original source access and ZIP SHA, source only](https://github.com/zuizui0223/boids/actions/runs/41973405868).
- [Source XLSX first-row header and dimensions, outcomes unopened](https://github.com/zuizui0223/boids/actions/runs/41973604158).
- [Incorrect source exposure grain diagnosis](https://github.com/zuizui0223/boids/actions/runs/41974758994).
- [One original bat with seven missing sec-group bins](https://github.com/zuizui0223/boids/actions/runs/41975006854).
- [Corrected original 10/nine bat numerical forecast, seven invented-only tests](https://github.com/zuizui0223/boids/actions/runs/41975503666).
- [Permanent source original DOI/SHA/count/model-result ledger](MOLOSSUS_2024_CORRECTED_CAPTURE_SOURCE_RESULTS_LEDGER_V2.json).
- [Exact source SHA plus 10/9 bat ledger re-evaluation](verify_molossus_2024_corrected_capture_ledger_v2.py).

No original raw PNAS supplemental workbook has been redistributed to this repository, and no bat individual original IDs or source rows have been committed. Code and comparisons are a secondary, independently scripted reanalysis with 2024 original paper priority.

## What to do scientifically

**Close the current Molossus source as an honest published-positive / new prediction-negative comparative case.** Do NOT reopen thresholds and tune M1/M2 to turn ten bats into an artificial confirmation. Do NOT claim the previous flawed 197k-exposure preliminary scores. The next true bat-only publishable test of sonar-mediated group costs needs a genuinely independent accessible archived source with biological IDs and receiver/foraging task performance, or a physics-anchored, independently validated acoustic receiver model whose cross-bat holdout can generalize beyond one source/study. If none is available, keep the work as a rigorous source-verified methodological negative and source-conditional mathematical boundary, not a new universal bat ecological law.

PR #36 remains Draft; frozen `batter` JAE/BE article releases remain unchanged.
