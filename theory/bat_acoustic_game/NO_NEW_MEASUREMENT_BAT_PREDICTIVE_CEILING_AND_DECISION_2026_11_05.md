# Bat vocal policies: what remains after unknown-bat and equal-data tests?

**5 Nov 2026 — EVIDENCE-BOUNDED DECISION, no new bat measurement and no journal submission.** This is a combined, audit-ready response to the same Hase 2026 source experiment. All reported 2026 source results are SECONDARY. No original acoustic pulse files, animal IDs or individual original data are redistributed.

## One defensible question, not five parameterized stories

**Can individual bats' responses to acoustic masking be predicted from shared playback rules, or is there source-internal information specific to each bat?**

This is potentially relevant to bat sensory individualization, but **not** an original discovery of bat echolocation JAR. Hase et al. 2026 (*Proceedings of the Royal Society B*, DOI [10.1098/rspb.2026.0921](https://doi.org/10.1098/rspb.2026.0921)) already developed and tested the **terminal-frequency** leaky-integrator model and reported original vocal acoustic characteristics (IF, TF and others). Our newer comparison predicts **initial frequency IF**, an importantly different response variable. It does not refute the published TF model.

Original archive Figshare DOI [10.6084/m9.figshare.30937379](https://doi.org/10.6084/m9.figshare.30937379) / `Data_jamming.csv`, SHA256 `2998ad0e57cc51cb4a98f48de6444d543f925994600cd5574f25e40babcfa367`; 12,308 original pulse rows, **11 distinct biological bat IDs** across three original experiments, each experiment **7 bats** with 5 measured stimulus conditions (the source cohorts overlap across experiments). All 105 source stimulus-level ON/OFF contexts have OFF entirely before ON, so playback activation and stimulus-relative chronology are entangled. New sound recordings: **zero**.

## 1. Stimulus-only policy fails to transfer robustly to unseen source bats/levels

Source test: for every bat i and original stimulus condition s, fit on other six bats under other four original conditions; predict source ΔIF at i,s. No original data from the test bat or held-out stimulus level enters training. This is **source-internal double holdout**, not external validation in another study or a new stimulus range. Each original experiment has 7×5=35 test cells; 7 bats remain biological source n.

Full original source ON−OFF median ΔIF, equal-bat mean MAE (kHz):

| Experiment | Zero IF shift | Other-bat constant response | Stimulus-only linear response | TF-informed constant-bandwidth diagnostic | TF-informed affine diagnostic |
|---|---:|---:|---:|---:|---:|
| **Low-TF IPI** (predeclared primary) | 3.170 | **3.291** | 3.677 | 2.941 | 3.244 |
| High-TF IPI | 2.774 | 2.552 | **2.493** | 2.901 | 2.653 |
| Low-TF SPL | 3.985 | **3.714** | 3.853 | 3.415 | 3.623 |

For primary low-TF IPI, the **stimulus-linear rule is worse than the other-bat constant baseline in 7/7 source bats**, increasing error by +0.386kHz, source whole-bat bootstrap 95% descriptive interval [+0.263,+0.508]. Replacing medians with means preserves the adverse direction. Across **4 time policies × 2 summary policies × 3 original experiments**, the stimulus-only linear model is worse than the constant baseline in **18/24** model-group comparisons; these are heavily repeated source samples, **not 24 independent studies**. The original authors' TF stimulus-dependent effect can still be valid.

The `fixed_bandwidth` and `trained_IF_TF_affine` models use the **held-out individual's actually recorded ΔTF**. They are *conditional acoustic-field reconstruction*, **not forecast from playback exposure** and must not be compared as a prospective ecological predictor against stimulus-only algorithms without acknowledging that target-outcome side channel.

Evidence: [frozen double-holdout contract](DOUBLE_HOLDOUT_IF_PREDICTION_PREOUTPUT_V1.md), [source code](double_holdout_IF_source_v1.py), [24 source-cell/120 model numeric ledger](BAT_DOUBLE_HOLDOUT_IF_SOURCE_RESULTS_LEDGER_V1.json), [fresh original-data and Git blob verification](https://github.com/zuizui0223/boids/actions/runs/41958144552), [invented 13-fixture tests + original data run](https://github.com/zuizui0223/boids/actions/runs/41957632263).

## 2. A limited own-bat mean advantage survives in one source context, but not a transferable personal dose curve

**Separate post-result hypothesis, recorded before the own-vs-donor source outcome:** For each source bat and target stimulus, train on its **four other source stimulus conditions**, and compare separately to **each of six other bats trained on four matched source conditions**. Average *errors* from six equally trained donor models AFTER predicting; do not average other-bat predictions before computing errors. No donor ever receives 24 training cells in this equal-training test. These are four **alternative stimulus conditions**, **not four earlier chronological occasions**: do not call this long-term history, memory, or learning.

Full original ON−OFF median source ΔIF, equal-bat MAE (kHz):

| Source experiment | Own 4-level mean | Equal-data other-bat donor mean | Own four-level OLS | Equal-data other-bat donor OLS |
|---|---:|---:|---:|---:|
| **Low-TF IPI** | **3.408** | 4.016 | 4.033 | 4.373 |
| High-TF IPI | 2.955 | **2.683** | 3.376 | **3.003** |
| Low-TF SPL | 4.179 | **3.837** | 5.050 | **4.353** |

For original low-TF IPI, own-bat average is 0.608kHz better than a single equally trained other-bat model, with **5/7 original bats in that direction**. But source 95% bat bootstrap of own minus donor errors [−1.493,+0.364] overlaps zero. The original mean-based IF contrast yields own minus donor −0.435, 6/7 bats, descriptive interval [−0.886,−0.060]; **other time windows do not consistently support it**. In the other two original stimulus experiments, personal baseline prediction is worse on the full-source median. This does **not** establish a general individual bat auditory policy.

**Informative negative:** a source OLS line fitted to each bat's own four condition responses is less accurate than that bat's simple personal mean in **24/24 source-reused window×summary×experiment comparison groups**. That does not imply real bats do not have nonlinear response rules; it means no justified predictive advantage is recovered for this particular four-point *linear* personal-dose model. With only four source levels per fit, added flexibility may amplify measurement noise or non-transferable context-specific slopes.

Evidence: [source pre-output matched-four contract and noted seven-bat support correction](SELF_VS_DONOR_EQUAL_FOUR_CONDITIONS_PREOUTPUT_V1.md), [source code](self_vs_donor_bat_source_v1.py), [24 source group/96 model aggregate ledger](BAT_SELF_VS_DONOR_SOURCE_EQUAL_TRAINING_LEDGER_V1.json), [fresh original-data/whole-ledger CI](https://github.com/zuizui0223/boids/actions/runs/41959659455), and [12 invented-only tests + source run](https://github.com/zuizui0223/boids/actions/runs/41959317431).

## 3. Why this still is not the bat ecological mechanism the user wanted

- **Source 2026 already established TF masking response.** Here IF covariance/predictability is a secondary measurement. Do not confuse a negative IF predictor with absent TF regulation.
- **All source OFF samples precede ON.** The within-record source timing audit and the three window analyses (full, ±1s, ±2s, pre/post excluding ±0.5s) cannot remove this confound.
- **Personal response calibration within one experimental session is not long-term individuality.** The original source's time windows and five levels do not test behavior over independent days, cohorts or colonies.
- **No true acoustic receiver outcome, prey failure or jamming benefit was recorded in this source.** The *Mazar & Yovel 2020* simulation original output showed that acoustic masking and false alarms or insect capture are not equivalent; the original 2026 Hase simulator tested *potential* misdetections, not actual prey capture. The model-to-functional-payoff link remains open.
- **Cross-study data admission is not yet possible here:** 2015 *Pipistrellus kuhlii* original Dryad DOI `10.5061/dryad.8f0v4` catalogues `Dryad.xlsx` (1,810,012 bytes, CC0, provider MD5 `38fe393092ac0e9936f88f3bf450eac7`) but official file HEAD/Range returned HTTP401. 2025 *Rhinopoma microphyllum* movement/audio Mendeley DOI `10.17632/k7pt2j84f7.1` publicly lists CC BY4.0 `Code.zip` and `Data.zip`, but the public Mendeley API returned HTTP401/404 in this environment. Files were not admitted or processed; source public pages do NOT grant executable access here. [Dryad source-only gate](https://github.com/zuizui0223/boids/actions/runs/41958348509) and [Mendeley source-only gate](https://github.com/zuizui0223/boids/actions/runs/41958645979).

## One science decision

**Keep source-confirmed positive and negative parts separate:**

- Source-confirmed previously published positive: Hase bats show spectral TF shifts linked to playback; the original 2020/2026 published work already establishes the physics/behavior direction within its task.
- New transparent secondary result: **No robust transferable stimulus-only linear IF rule across unknown original bats and stimulus levels.** Some source contexts show within-session same-bat baseline response information, but it is not a general or long-term individual strategy, and personal linear dose-response overfits under this evaluation.
- New mathematically validated synthetic boundary from earlier v1/v2: frequency shift, FM shape, time-delay search and fixed IF/bandwidth conventions jointly determine cross-correlation; the exact real 2026 waveform and group receiver are not reproduced. This is a conditional model example, not biological validation.

**Stop fitting more response rules to the same Hase 2026 archive.** The decisive next requirement is a genuinely independent accessible bat study with biologically identifiable individuals, simultaneous acoustic stimulus and true ecological receiver/foraging performance (if such source exists), with source rights and leave-one-bat/source-out holdout locked BEFORE target outcomes. If access fails, close this as a source-limited audit and theoretical demonstration; do not submit it as an original bat ecology paper. No new animal measurements are needed for this *strategy*, but the source required for a publishable outcome has not yet been admitted.

PR #36 remains Draft; original frozen `batter` JAE/BE results untouched, and no original source files rehosted.
