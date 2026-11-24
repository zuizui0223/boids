# v26d original third fish taxon: age of collective-motion predictive information differs from first two sources

**2026-11-24 JST — source-authenticated, original observed fish movement; exploratory 3-RECORDING holdout, not three independent shoals or a new causal experiment.**

Original *Gasterosteus aculeatus* fish data from MacGregor & Ioannou (2021), EIDC DOI https://doi.org/10.5285/08305a43-79b5-432f-ad20-2ddffe0d1077, 8 fish in native 25fps records. [Original 2021 ecology paper](https://doi.org/10.1098/rsos.210655) documented collective-motion dynamics across 12 shoals but the published numbered source files do **not** provide a verified 84-file-to-12-shoal identity mapping. Our pre-selected 3 file IDs are **01.txt / 02.txt / 105.txt**. No individual animal positions or time-series redistributed to GitHub.

## Frozen primary question

In a heldout **whole source FILE** (training on the other 2 files), is the current other-fish mean relative velocity more informative about focal future 2D velocity than otherwise identical predictors based on that same group's 0.2, 0.4, 1, or 2-second-old other-fish velocity? Current focal own 0.2s speed and older movement, group geometry and test rows are identical across age models.

[Pre-result frozen protocol](V26D_STICKLEBACK_3_RECORDING_FORECAST_FREEZE.md), commit [39f82c0ba9102e38ac686174bb0445b2243427d6](https://github.com/zuizui0223/boids/commit/39f82c0ba9102e38ac686174bb0445b2243427d6). Original XY order and last-column frame mapping source-verified independently in [v26 source audit](V26_EIDC_STICKLEBACK_ORIGINAL_SOURCE_RESULT.md), after the initial first-column false-clock STOP. No ad hoc imputation, no source file selection by target scores, no ID guessing.

## Actual source-authenticated 3-file original result

[Original GitHub Actions #45333770519](https://github.com/zuizui0223/boids/actions/runs/45333770519) **SUCCESS**: six independent synthetic source/clock missingness tests passed; all 3 original EIDC file SHA256/size checks passed; full original last-column frame step +1 verified, all 8 fish's XY available at each source/response timestamp in the eligible cohort; complete-recording holdout Ridge(alpha=10) with train-only normalization. Original source frames retained for forecast construction: 01.txt **6,966**, 02.txt **8,015**, 105.txt **5,567**; all produce 8 fish×frame targets per eligible native frame. These are overlapping/autocorrelated fish-time rows, NOT independent animals or schools.

The age-specific normalized incremental MSE improvement index is defined as I(age)=[MSE(G)-MSE(G+other-fish-age)]/[MSE(G)-MSE(G+other-fish-current)] when the denominator is positive. **I(0)=1**. This is NOT actual mutual information, social signal retained or memory timescale.

| Source/original future-velocity target | I(0.2 s) | I(0.4 s) | I(1 s) | I(2 s) | First sampled age at I≤0.5 |
|---|---:|---:|---:|---:|---:|
| **Stickleback 0–0.2 s future** | **0.7829** | **0.5620** | 0.1525 | −0.0616 | 1.0 s |
| **Stickleback 0.6–0.8 s future** | **0.7771** | **0.5907** | 0.2572 | 0.0291 | 1.0 s |

**Current-versus-age contrast is positive in every one of the 3 original files at all four ages and for both future targets.** This is a source-recording directional recurrence, not a 3/3 independent-population significance test.

Absolute original native velocity MSEs (squared pixel/sec, **never pool** with Puy cm/sec or Niizato unknown coordinates):

| Original target | Geometry-only | current other-fish | 0.2-s-old | 0.4-s-old | 1-s-old | 2-s-old |
|---|---:|---:|---:|---:|---:|---:|
| Stickleback 0–0.2 s | 2804.1859 | **2751.3501** | 2762.8211 | 2774.4908 | 2796.1298 | 2807.4396 |
| Stickleback 0.6–0.8 s | 8324.0861 | **7848.8282** | 7954.7741 | 8043.3441 | 8201.8622 | 8310.2605 |

The **source-specific absolute current advantage over geometry is modest** for the short target (~1.88% lower MSE); a high normalized retention value does not imply much predictive variance explained. For the delayed target, current is ~5.71% below geometry. Source case handling, behavioral paper's tracking corrections, repeated school identities and external common stimuli remain important limitations.

## Comparison with previously analyzed original fish sources (not a formal meta-analysis)

| Independent published fish data source | I(0.2s), short future | I(0.2s), delayed future |
|---|---:|---:|
| 2024 Puy black neon tetra: 6 recording files, 8 fish | 0.3224 | 0.2209 |
| 2024 Niizato ayu: 7 recording files, 10 fish | 0.4321 | 0.4396 |
| **2021 MacGregor & Ioannou stickleback: 3 recording files, 8 fish (exploratory)** | **0.7829** | **0.7771** |

The two earlier source studies first fell below I=0.5 at the sampled age of 0.2 seconds; stickleback remains above 0.5 at 0.4 seconds and first falls below at 1 second. Because the source-specific targets, native frame rate (50/30/25 fps), group geometry predictors, fish species, movement contexts, original upstream tracking treatments and **group-ID reproducibility differ**, the distinct curves do **not** by themselves establish a biological species-specific time scale. In addition, stickleback uses short+delayed 0–0.2 / 0.6–0.8s, whereas the former studies used 0–0.2 / 0.5–0.7s. The stickleback half-threshold is **discrete sampled age**, not a continuous half-life.

**Evidence-led interpretation:** what extends across the three published taxa is the retrospective predictive benefit of **present signed whole-group directional movement over older group movement**. The quantitative age of predictive decline appears context/model dependent. The specific '0.2-second half-retention' observation is **not a universal number** under the current available three-pipeline comparison. Distinguishing species biology from observation/sampling conditions remains for followup.

### Biological social interaction vs common-driver null

[Analytic no-social-interaction common-driver counterexample](V24_NON_SOCIAL_AUTOCORRELATED_COMMON_DRIVER_COUNTEREXAMPLE.md) shows that a rapidly or slowly autocorrelated common external driver can produce similarly slow or fast age-decay curves with **zero individual-to-individual causal following**. Thus this result does not prove memory, visual/lateral-line transmission, acoustic steering, predator detection, or contact-call feedback. No synchronized fish calls were measured in any of the three movement datasets.

**Exact source-safe reproducibility:** [original Actions run](https://github.com/zuizui0223/boids/actions/runs/45333770519), [Actions original aggregate artifact #14893016106](https://github.com/zuizui0223/boids/actions/runs/45333770519/artifacts/14893016106), ZIP SHA256 `1e57b9193c3eab5443f5a4a01a41d5dac63ce7b5410bc55997c5d376a831c514`. Original per-file primary contrasts and the numerical reaggregation check are stored at [verified JSON receipt](v26_verification/STICKLEBACK_THREE_RECORDING_ORIGINAL_AGE_FORECAST_RECEIPT.json).

## Next discriminating hypothesis

**Predictive-age decay may scale with the lifetime of collective heading/velocity fluctuations, not simply seconds or species identity.** To test this, the *same source cohort* must produce a direct school-wide velocity or heading autocorrelation curve, then compare whether normalizing predictor age by its estimated group-state correlation time collapses age-retention curves across fish sources. A common-driver alternative predicts the collapse may occur **without direct social causality**; a residual true-neighbor mapping effect after group-state control could justify a separate experimental test. Predeclare this before any new source outcomes, avoid fitting time constants using previous v24/v26 outcomes.

For a definitive third biological replication: obtain original author-verified mapping from numbered files to original 12 shoals/repeated sessions. Hold out **whole original shoals**, not merely three files. Only after this would a multi-source study-level meta-analysis become potentially defensible. The full 84 available files could support a larger source-level exercise but the school-ID unit is not yet identifiable.

Keep PR #248 Draft; main unchanged.
