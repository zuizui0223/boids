# King Rail v5 — original real-data time-alignment experiment (exploratory): fixed primary **FAIL**

**Source and audit:** 2026-11-15. Original Brewer et al. (2023), [paper DOI](https://doi.org/10.1002/ece3.10043), [Zenodo data](https://doi.org/10.5281/zenodo.6604660), `CARTdataset_12.31.21_All_D.csv`. Exact original published-file MD5 verified against source: `2ce75a621fa7a755688f6a542c76c7ca`; downloaded actual SHA-256 `de9e845da63bcb7451ebe8f8b9bd1b877bdbc997d9150db65161150fb7b82bda`; 92,166 original bytes. GitHub Actions original-data one-shot: https://github.com/zuizui0223/boids/actions/runs/43694499003; artifact ID `14153831679` (sha256 `5eb7bb642d326771f1a99fffaaf14444b355ceb5845f97692c7785ced2e4331f`). Machine-readable full model and individual outcomes: [`comparative_state/results/king_rail_temporal_grain_v5_receipt.json`](../comparative_state/results/king_rail_temporal_grain_v5_receipt.json).

## Question, identical response and non-leaky holdout

Can original **same-event** local random-plot mean depth better predict the **same heldout used water depth**, compared with the average available depth over the previous three observation dates, after controlling focal bird-year historical used depth and a slope learned on other bird-years' training dates? All models score **exactly the same original bird's future observed depth**. Only chronological earlier dates (60%) train personal baselines; final 40% unseen dates are test. Fixed primary decision rule was set before new outcome scoring. Same-event random depth was measured retrospectively within 72 h and would not be known before a real movement decision.

### Data and independence

- 607 source rows; 17 publisher `Missing=Yes` rows and 2 malformed-ID rows excluded without repair; no additional malformed environmental/date values.
- 190 matched homing-plus-local-random events, 173 with two random plots; 10 full bird-year identifiers, 9 distinct un-suffixed codes.
- 79 future-date heldout events across **all 10** complete bird-year series; no bird-year failed eligibility.
- Original authors reported **no recaptured or observed banded individual between years**, so equal un-suffixed numeric codes in different years alone do NOT prove an identical physical animal. The v5 uncertainty check additionally collapses identical prefix strings conservatively, but 10 different birds remain the published original field cohort.

## Fixed outcome: **FAIL** for event-vs-recent-history predictor

Primary `G=MSE(Mlag) − MSE(Mevent)` (positive = same-event environment better), equal-bird-year weighted:

| Estimand | Mean (cm²) | 95% bird-year bootstrap interval | Positive series | Frozen decision |
|---|---:|---:|---:|---|
| Same-event depth vs prior-3-date mean depth | **+9.8664** | **[−1.9004, +31.3281]** | **5/10** | **FAIL** |
| Same-event depth vs personal-historical constant | +25.9201 | [+0.2885, +67.6844] | 6/10 | Secondary, not primary-confirmed |
| Own historical intercept vs other-birds' intercept, same event covariate | −14.9408 | [−104.2296, +47.8902] | 5/10 | Identity generalization unsupported |

Mean heldout MSE (cm²) equal across bird-year series: history-only 245.9364; 3-date lag 229.8827; same-event 220.0163; other-bird current 205.0755. Lower MSE is better. The one-sided within-heldout time-series circular-shift diagnostic had observed same-event MSE 220.0163, shifted-null median MSE 227.7379, Monte Carlo p=0.0475, but **this secondary control does not override the failed fixed across-individual gate**; short series and shared data limit calibration.

### Individual heterogeneity — descriptive sensitivity, not new inferential gate

| Bird-year | N train | N test | `MSE(lag) − MSE(event)` (cm²) |
|---|---:|---:|---:|
| 020_21 | 20 | 14 | −1.550 |
| 332_20 | 15 | 10 | −1.560 |
| 332_21 | 9 | 6 | +1.008 |
| 361_21 | 10 | 8 | +1.387 |
| 368_21 | 8 | 6 | +3.064 |
| 390_21 | 9 | 7 | −4.235 |
| 506_20 | 13 | 10 | +3.893 |
| 856_20 | 9 | 6 | −1.165 |
| 871_21 | 9 | 6 | −5.312 |
| 881_20 | 9 | 6 | +103.134 |

The positive pooled difference is **driven by a single high-squared-error bird-year**: the median across series is −0.0788 cm², and the purely descriptive mean after omitting `881_20` is **−0.4967 cm²**. This omission is **not a valid basis for changing the precommitted primary cohort or claiming a negative population effect**. Prefix-collapsed sensitivity: 9 prefix groups, mean +10.9933 cm², 95% [−1.9916, +34.6017], 4/9 positive (still fails).

## What can and cannot be learned

1. **Positive spatially matched buffering is not the same as positive predictive improvement for absolute used depth.** The previously observed ~84% attenuation of King Rail experienced-depth response to its sampled nearby environment can coexist with a weakly predictive event-conditioned environment model. A bird maintaining a fairly stable experienced state can be predicted from its own past even if external conditions change.
2. This is a new, original-source, *same-response* reanalysis, but not an **independent ecological replication**: the original `louis` studies already used the 190 matched King Rail events. Pseudoreplication is not repaired by generating 79 time-heldout rows; the independent biological units remain only the original birds.
3. The comparison is **current event vs previous-3-date lagged availability**; timeliness and temporal smoothing are confounded. Thus this negative result does **not** falsify the clean hypothesis that spatial/temporal *aggregation alone* reduces predictive power. That requires future independent same-time fine-versus-aggregated predictors with equal information latency.
4. Original 75-m random-plot depths are only sparse reference samples conditional on homing locations; they do **not** enumerate all geographically reachable alternatives. There is no independently verified transition-to-step-origin join, no state portfolio exhaustion estimate, no causal competition/learning/fitness, and no evidence of universal resilience thresholds.
5. New external precedent: Rowcliffe et al. (2026), *Methods in Ecology and Evolution*, DOI 10.1111/2041-210x.70295, already separated activity from spatiotemporal use across 7 mammal populations and emphasized observation-effort/detection confounds. Its example Zenodo data 10.5281/zenodo.18991825 were listed as **embargoed** at source check; this is not a replication dataset currently used here.

## Next falsifiable scientific step

Find a **new** source with independently identified individual or site, observed resource state at each choice, contemporaneously measured availability/reachability, observation effort and an exact time index. Freeze (before opening outcomes) both `A_event` and **same-date aggregated `A_smooth`** models on the *same* heldout animals and response; separately compare a `A_prior` lag model for timeliness. Use whole-independent-organism/site holdout and a measurement-error sensitivity. Only after true choice sets and geographic movement join can a conservation claim be made about environmental option exhaustion or scale expansion of movement.

**Current cross-taxon verdict remains empirical synthesis + methodological falsification, not a universal mechanistic original-research demonstration.**
