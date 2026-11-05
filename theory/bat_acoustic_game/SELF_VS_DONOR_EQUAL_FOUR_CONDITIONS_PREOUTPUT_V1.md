# Frozen equal-record bat-own versus other-bat vocal response test — 2026-11-05

**Post-publication, post-previous-negative-results EXPLORATORY reanalysis. Not new bat recordings, not a new independent dataset, not a bat-learning or long-term memory test.**

Published 2026 source: Hase et al. 2026 DOI `10.1098/rspb.2026.0921`, Figshare `10.6084/m9.figshare.30937379`, original source SHA256 `2998ad0e57cc51cb4a98f48de6444d543f925994600cd5574f25e40babcfa367`. Earlier double-heldout source analysis (GitHub CI 41957632263; 120 numeric result CI 41958144552) showed the condition-only ΔIF model was worse than a 24-cell other-bat constant baseline in the primary IPIlow full source and 18/24 reused time-method-experiment group summaries.

## Falsifiable bat-only question

**Is there information about a held-out bat's source playback IF shift in that bat's responses to four OTHER source stimulus conditions that is not transferable from a different original bat with equal training opportunities?**

This tests **within-experiment individual-context predictability**. It does *not* show individual learning, persistent memory, true sonar receiver discrimination, competition, prey capture, cross-species transfer or a causal individuality mechanism. The same source individuals have already been studied and original paper IF acoustic characteristics published.

## Frozen model/training/test design — no outcome-based changes

For each of the three source experiments `IPIlow` (primary), `IPIhigh`, `SPLlow`, and each original eligible bat i (>=5 source stimulus levels), hold out one original condition s. Train one model on bat i's **four OTHER** conditions and, separately, train one model on each of the **six OTHER bats' four OTHER conditions**. ALL candidate individual models receive exactly four source bat×condition summary rows. Compare:
1. `self_constant`: mean(source ΔIF) across the target bat's four other levels.
2. `other_constant`: mean(abs prediction error) across six donor bats, **each donor trained only on its own four other levels**, not on their pooled 24 levels.
3. `self_linear`: plain OLS ΔIF = a+b*x fitted on the target bat's four source levels and tested on s, where x=log10(IPI) or SPL.
4. `other_linear`: mean(abs prediction error) across six independent donor-bat OLS fits with exactly the same four original stimulus levels. Do not select the best donor or average donors' predictions before absolute error (the latter would effectively exploit six times the information).
5. `self_linear_vs_self_constant` included to test whether personal dose shape adds predictive value beyond a personal intercept.

The **primary** estimand is `D_constant = MAE(self_constant) − MAE(mean_donor_constant)` for IPIlow full original source medians; **secondary** `D_linear = MAE(self_linear) − MAE(mean_donor_linear)` and `self_linear − self_constant`. Negative values mean same-bat training is more informative. Report number of bats favouring self versus donor, equal-bat mean absolute errors, per-bat average across five original heldout conditions (35 tests/experiment), whole-bat seeded 5,000-draw bootstrap intervals for mean D (seed 20261105), and leave-one-bat-out mean D. No test-fold p-values. The six donor models are correlated through the original experimental design; only seven recipient bats are biological replication within an experiment.

IF and TF must be same-record finite values with IF>TF, original source ON and OFF at least four calls each in ID×experiment×condition×Var×jammingTF group, source ON−OFF ΔIF median; average accepted Var/jammingTF subcontexts equally per bat×experiment×condition. The mean ON−OFF contrast is the only predeclared summary sensitivity. Use unmodified preprocessing `published_IF_TF_convention_v1.py` and original source `IF_TF_temporal_window_sensitivity_v1.py` (all 4 original time policies). **All prior temporal windows and methods are included unchanged**: full original source; before/after 1s; before/after 2s; OFF[-2,-0.5) vs ON[0.5,2). No selection of favourable window or degree of fitting.

Eligibility hard stop: source experiment has fewer than **seven** bats each with **five** common original conditions; if missing in any experiment/window, STOP that cell and report source support, do not loosen thresholds. All eligible donor pairs must hold out exact same condition s; no source original bat IDs, source call-level IF/TF, timestamps or donor labels in GitHub artifacts. Source original participant count across source experiments is 11 (7 per experiment, 4/5/5 ID overlap).

## Possible results and exact scientific ceiling

- `self_constant` consistently beats each single donor model in the same test source: source response offsets could be individualized within original experimental sessions, **not** necessarily socially learned or stable across months; original ON before OFF chronology confound remains.
- `self_linear` wins but `self_constant` does not: condition-dependent personal dose-response curve may be descriptive; only four in-source training levels, risk of endpoint overfitting.
- Neither self rule wins: individual response sensitivity not transferable even between original 5 conditions in this source. Do not upgrade model complexity or record threshold.
- Source all 105 original ON/OFF contexts have original OFF earlier than ON; within-bat time/fatigue/order affects interpretation and is NOT controlled here.
- Even a strong source result cannot be called causal acoustic JAR adaptation, 3D niche partitioning, original model prey-capture payoff or across-bat-species generality. External original source candidates Pipistrellus 2015 and Goldshtein 2025 currently STOP HTTP401; source admissions are not experiments.

**No animal source records are rehosted. Source-level aggregate and all windows, including negative results, must be saved with code and original source SHA after running.** The frozen bat JAE/BE papers are left unchanged; this boids PR remains Draft.

## Pre-response arithmetic correction (after synthetic unit-test failure; before original source outcome evaluation)

A source eligibility check allowing six eligible bats contradicted the frozen comparison requiring **six other donor bats** per recipient. The invented-only fixture exposed this: dropping one source bat would leave five donor models and break the equal donor count. To keep the predefined six-donor estimand, the gate is STRICTLY seven biological bats with all five matching source stimuli in each experiment-window, or STOP. No original-source outcome for this self-vs-donor test was opened before this repair. This is a guardrail correction, not a source-response-tuned modification.
