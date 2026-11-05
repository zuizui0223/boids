# Frozen double-holdout bat source vocal prediction contract — 2026-11-05

**Question:** Can a response rule inferred from *other bats under different original playback stimulus levels* predict a new bat's initial-frequency (IF) change, or are the previous IF/fixed-bandwidth model differences non-transferable?

**Prior-art and source dependence:** Hase et al. 2026 Proc. R. Soc. B DOI 10.1098/rspb.2026.0921 published a leaky-integrator **TF** response and source IF acoustic characteristics. Original Figshare DOI 10.6084/m9.figshare.30937379, single `Data_jamming.csv` SHA256 `2998ad0e57cc51cb4a98f48de6444d543f925994600cd5574f25e40babcfa367`. This new experiment is a **post-publication, post-existing-source-results exploratory predictive holdout**. It is NOT independent animal validation or a new biological experiment.

## Before reading new prediction scores: fixed 5 source models and evaluation

One source participant = one biological bat ID. Existing IF-TF code `clean_source_rows`, `contrast_contexts` and `stimulus_coordinate` are reused unchanged. Eligible complete-case original source calls must have finite IF, TF and IF>TF, original binary source isON, >=4 rows per original ON/OFF within exact ID×Experiment×Condition×Var×jammingTF; source IF and TF contrast is median(ON)-median(OFF), with mean rather than median as one fixed sensitivity. Aggregate source Var/jammingTF *equally* to individual×experiment×condition; only bats with >=3 distinct admitted source levels. Primary experiment `IPIlow`, secondary `IPIhigh` and `SPLlow`. No leak of original IDs into outputs.

For each original experiment e, each eligible bat i, and each of its admitted condition levels s, **train only on other bats j ≠ i AND other condition levels t ≠ s within SAME experiment e**. Require >=5 training bats and >=3 training stimulus levels. If not, record STOP without threshold relaxation. Target is one held-out biological bat×condition ΔIF. The held-out ΔTF is available only for **conditional secondary models**, not forward stimulus-only predictions. The source stimulus coordinate x is log10(IPI in ms) for two IPI experiments or SPL in dB for SPLlow. The source design already knew all 5 levels, so "unseen stimulus level" means absent from the TRAINING FOLD, not independent out-of-range experimental generality. No stimulus response from target bat is admitted to training.

Fixed **forward models** using only original stimulus coordinate (no held-out ΔTF):
1. `zero`: predict ΔIF=0.
2. `constant_training_mean`: predict the mean ΔIF among equally weighted training bat-condition cells.
3. `stimulus_linear`: unregularized OLS ΔIF = a + b*x on training bat-condition cells with in-fold centering. Two coefficients, no hyperparameter tuning.

Fixed **conditional transfer models** using target-bat measured ΔTF (CANNOT forecast IF before observing emitted TF):
4. `fixed_bandwidth`: predict ΔIF=ΔTF.
5. `trained_IF_TF_affine`: OLS ΔIF = a + b*ΔTF fitted only on eligible other bats×other levels, with no regression regularization.

For each model calculate held-out absolute errors (kHz) at the 5 within-bat held-out condition cells; compute a **per-bat equal-condition mean MAE** then an **equal-bat mean MAE**, median MAE, bat-count, source test-pair count, and simple descriptive 5000-draw seed 20261105 whole-bat bootstrap interval for model error *differences*. No fold-level p-values. Report per-experiment mean paired error difference `stimulus_linear − constant_training_mean` (negative = cross-level stimulus information helps) as **primary**; secondary `stimulus_linear − zero`, `trained_IF_TF_affine − fixed_bandwidth` and `trained_IF_TF_affine − constant_training_mean`. Report 7 source-bat win signs and leave-one-bat-out means; **do not optimize model structures, wins, windows or filters after opening results**.

Evaluate the exact four existing original-source time policies, with no selection of a best outcome:
- `full`: all source calls after original QC (source 12,308 rows);
- `near_one_second`: original OFF time [-1,0), ON [0,1);
- `symmetric_two_seconds`: OFF [-2,0), ON [0,2);
- `exclude_near_switch`: OFF [-2,-0.5), ON [0.5,2).
All are *post-prior-result* sensitivities, not new independent held-out seasons. In each cell record original source row count, biological bats, pair coverage and which models are permitted. The complete expected grid is **4 windows × 2 contrast summaries × 3 experiments × 5 models = 120 model-level source aggregates**, but individual conditions are dependent and not independent n=120. Report all 24 window×summary×experiment group cases.

**Interpretation restrictions:** The source study already fitted an original TF integrator response; OLS stimulus and IF–TF crossfit here may rediscover original-source protocol statistics. Crucially all 105 previous source contexts have OFF entirely before ON, so **source-time drift is perfectly confounded with stimulus exposure**; even unseen-bat/condition forecasting inside this source is not independent causal proof of sensory JAR or field prey capture. No exact 2026 group sonar source code, original bat field niche results, biological response generality, fitness payoff or peer-reviewed original novelty is claimed. Every 2018 real waveform source access stopped HTTP401. Never rehost source audio or individual original pulse rows.

**Decision rule:** if forward `stimulus_linear` does not consistently outperform `constant_training_mean` across biological bats in the full source and temporal windows, close the stimulus-only predictable rule as unsupported. If it outperforms, describe conditional within-source extrapolation only, and do not turn it into an ecological mechanism without independent source validation. No source-answer-driven model refits.
