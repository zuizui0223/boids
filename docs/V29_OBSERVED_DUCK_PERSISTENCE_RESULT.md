# v29: Yesterday's measured duck spread is a strong forecast; a multi-day advantage is not established

**Completed 2026-10-30 JST. Same-source exploratory extension of v23, not independent replication.** The positive v23 outcomes were already known when the new comparator was specified. The [protocol](V29_HISTORY_VERSUS_PERSISTENCE_PROTOCOL.md) was committed locally as `744ae65` before the new persistence errors were calculated; implementation `a4dc841` was independently reviewed before the original-source run. No claim of public preregistration is made.

## Main result

On the exact original **49 birds and 2,664 future bird-days**, predicting the next day's horizontal GPS spread with **the exact previous day's observed value (MP)** gave the lowest mean error among the five declared predictors. The fixed primary hypothesis that the original multi-day combined-history predictor (MEI) improves over MP was **not supported**: `MSE(MP) − MSE(MEI) = −0.0270185`, whole-bird bootstrap 95% **[−0.0787546,+0.0213542]**, only **18/49 birds** favoring MEI.

The observed point ranking does not demonstrate that MP is statistically superior to MI or MEI, and the interval crossing zero is not an equivalence test. It does show that the original positive history increment over the external-bird reference does not by itself establish added predictive value beyond a simple last-day state rule.

## Exact original source and cohort reproduction

- Original GPS: Van Toor & Waldenström (2025), [Zenodo 16940654](https://zenodo.org/records/16940654), `250823_LNU_dabbling_ducks_hourly.csv`, **46,324,165 bytes**. MD5 `1972d0ef08b83c2b88a169ba07bb48b3`; SHA256 `001ec8ffe1e9be5258129dfb931b0abd6551785080e2c755cbd4c72cd79ec52e`. The original file was newly downloaded and verified, then its exact bytes were verified again before the new parser run.
- Both original ERA5 sources were retrieved again through unchanged v23 code. Canonical SHA256 matched `b6c1fc7323cb6cb7275e9f5d31ea8ad1f9f4bea4b479eb93e9a13058057d9b54` (Baikka Beel) and `c856bc0b884b5d13c1529003fc2a1d1d335c856559ae4d4ae7c097837eb54307` (Tanguar Haor). Each contains 1,826 UTC days and zero missing declared daily weather variables.
- The source's **294,683 rows** yielded the original Bangladesh support: 94,248 rows, 360 duplicate rows fully excluded, four invalid QA rows, and 6,154 qualifying complete individual-days. Existing source selection then produced exactly **2,664 targets from 49 birds**.
- All four original per-bird model mean errors, every bird's daily count and source metadata, cohort sizes, and the four equal-bird errors matched the frozen v23 receipt with absolute tolerance **1e-12**. The receipt SHA256 is `4d3dcb0dc6017027e2ae5c3b824f327f359f67759a40a2c92e1ae7d45c1b9247`.
- The old v23 source code, gates, result and protocols were not edited. MP was added to copies of the original target records after receipt verification.

## Five absolute errors on identical future days

The target is `log(1+R)`, with R the within-day horizontal radius of gyration of observed GPS positions, in km. Squared errors are first averaged within each bird, then given equal weight across 49 birds. These are errors of a transformed daily-spread statistic, not errors in home-range area or 3D resource use.

| Predictor | Information available before the target day | Equal-bird MSE |
|---|---|---:|
| M0 | Earlier observations of other birds from the same fixed wetland region | 0.518970723315 |
| ME | M0's source histories matched to the fixed previous-day temperature/rain class | 0.520228597466 |
| MI | Same bird's last 3–14 eligible same-site observations | 0.348175806507 |
| MEI | Original fixed combination of ME and MI, `w=n/(n+2)` | 0.347094827809 |
| **MP** | **Exact complete calendar day t−1 for the same bird** | **0.320076305548** |

MP's MSE is **38.32% lower than M0** and **38.47% lower than ME**. It is **7.78% lower than MEI as a point estimate**, but the paired uncertainty does not establish the superiority of either MP or MEI.

## Every declared comparison, in its original signed direction

Positive values below mean the named history comparator improves over MP. The same paired whole-bird resamples were used for every contrast: **10,000 draws**, seed **20261030**. The one-sided sign probability tests positive history-over-MP gains; its near-one value must not be interpreted as a probability that the opposite hypothesis is true.

| Comparison | Equal-bird MSE(MP) − MSE(comparator) | Whole-bird 95% interval | Birds favoring history comparator | One-sided sign p |
|---|---:|---|---:|---:|
| **Primary: MP−MEI** | **−0.027018522261** | **[−0.078754571236,+0.021354221156]** | **18/49** | 0.977808 |
| Secondary: MP−MI | −0.028099500959 | [−0.082152902795,+0.020964275821] | 19/49 | 0.957283 |
| Descriptive: MP−ME | −0.200152291918 | [−0.282605327872,−0.124103502636] | 8/49 | 1.000000 (rounded) |
| Descriptive: MP−M0 | −0.198894417767 | [−0.279525306872,−0.122387808539] | 11/49 | 0.999981 |

Equivalently, for the **declared descriptive** comparison to the weather-matched external reference, MP saves **+0.2001523** MSE, with the sign-reversed interval **[+0.1241035,+0.2826053]** and **41/49 birds** favoring MP. This reverses the presentation sign of the already declared contrast; it is not a new selected model or a replacement primary endpoint.

## What the chronology audit found

- The original MI predictor included the exact previous calendar day for **2,645/2,664 targets (99.29%)**.
- Eight targets had a complete raw previous day but no previous-day eligible event; another eleven had a previous-day eligible event at a different site. These nineteen targets were retained, and MP still used the exact raw preceding day. No earlier event was silently substituted for yesterday.
- MI's number of prior eligible observations had minimum 3 and median 14. The median oldest-observation age was 14 calendar days and the median newest age was 1 day.
- The maximum oldest-observation age was **274 days**, and maximum newest age **261 days**. Thus v23's window is the last fourteen **eligible observations**, not necessarily the last fourteen consecutive calendar days. This is a descriptive audit; no new elapsed-time cutoff or favorable subset was fitted after inspecting the result.
- Every date's targets were scored/audited before that date's source records entered any history. No current or future outcome was used as a predictor.

## Scientific interpretation and next model decision

The most defensible positive statement from v23 plus v29 is: **an observed bird's recent movement state contains useful information for forecasting its next day's GPS spatial spread beyond an external-bird historical reference.** A one-day persistence rule already captures a strong predictive gain. The evidence presently does not require a multi-day memory term to beat that rule.

This remains compatible with several processes: state persistence, stable differences among individuals or taxa, repeated local environments, measurement/coverage characteristics, and behavioral learning. The comparator does not separate their causal contributions. A positive multi-day score against an external population mean is insufficient to identify cognitive memory or stable individuality; lack of an increment against MP is likewise not evidence that those processes are absent.

For future movement-to-space models, **MP should be retained as an explicit baseline before attributing incremental value to longer history, environment or social terms**. A sustained individual-profile mechanism would need added predictive information after controlling for immediate state on a separately specified future or independent-source evaluation. No new fitted model, window search, species subset or post-result parameter adjustment was added here.

The study is a forecast of later days for previously observed birds in one original Bangladesh study and two broad wetland reference regions. Whole-bird bootstrap does not create independent climate, species, site-year or population replications. This result is not an unseen-animal forecast, future-climate forecast, habitat-choice likelihood, 3D niche or identified Reynolds force.

## Artifacts and verification

- [Executable comparator](../validation_v29/persistence_benchmark.py), [known-truth tests](../validation_v29/test_persistence_benchmark.py), [aggregate result](../validation_v29/results/duck_persistence_v29.json).
- Numerical result SHA256: `2055a07f9cda4963789f84d43558dec66ae64f454139ddb00fec6d07ce4bbf95`.
- Original-source execution code commit: `a4dc841369b80ad0994435fe17ffe2aef197fd2a`.
- Fresh local verification: **12 v29 tests and 17 unchanged v23 tests passed**. Independent scoped review found no critical or important issues before source scoring. Original-source CLI then completed with `V23_FROZEN_RECEIPT_MATCH`.
- The separate v13 computation was regenerated from unchanged code with 30 seeds and 14 original passing tests. [Full regenerated receipt](../validation_v29/results/v13_replay_2026-10-30.json) is preserved; this is computational reproduction, not independent biological evidence.
- The new [read-only source replay workflow](../.github/workflows/duck-persistence-v29.yml) is supplied for future GitHub execution. **No v29 GitHub Actions run has occurred in this session.** Remote push was blocked by automatic approval review; all new work is currently on the local research branch, awaiting explicit publication approval.

Reproduce from the repository root:

```bash
PYTHONPATH=validation_v23:validation_v29 python -m unittest discover -s validation_v29 -p 'test_*.py' -v
PYTHONPATH=validation_v23 python -m unittest discover -s validation_v23 -p 'test_*.py' -v
python validation_v29/persistence_benchmark.py --out /tmp/duck_persistence_v29.json
```

Alternatively supply `--gps-file /path/to/250823_LNU_dabbling_ducks_hourly.csv`; the local file must pass the same exact original byte count, MD5 and SHA256. Only aggregate anonymous errors and source hashes are exported; raw animal data remain outside this repository.
