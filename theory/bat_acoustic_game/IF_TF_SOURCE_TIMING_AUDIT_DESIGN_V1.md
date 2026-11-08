# Post-outcome source-timing and cohort audit — IF/TF interpretation

2026-11-05. Descriptive structural audit **after viewing the published IF/TF model-comparison outcomes**. Explicitly NOT independent preregistration or response-based confirmatory rescue. Source: Hase 2026 DOI 10.1098/rspb.2026.0921, original Figshare 30937379 `Data_jamming.csv`, SHA256 2998ad0e57cc51cb4a98f48de6444d543f925994600cd5574f25e40babcfa367.

Only read source experimental design fields (`ID`, `Experiment`, `Condition`, `Var`, `jammingTF`, `isON`, `Time`, `time`). **Never read TF, IF, DUR or recorded acoustic outcomes in this audit.**

Verify:
1. Total rows, unique physical source bat-ID labels across all arms, per-experiment distinct source bats, and pairwise biological-ID overlap across IPIlow/IPIhigh/SPLlow. No raw individual IDs, exact animal/source time stamps, original rows or trajectories to be uploaded/committed.
2. Per experiment × source ON/OFF, record original relative-stimulus `time` finite-n and percentiles 0, .25, .5, .75, 1, along with proportions of points before/during/after stimulus onset (0).
3. For each source experimental context `ID × Experiment × Condition × Var × jammingTF` with at least 4 original rows per ON and OFF, report only aggregate number of matched groups, how many ON/OFF `time` ranges overlap, and how many are chronologically nonoverlapping. A difference in original relative time supports chronology–stimulus confounding as a caution; it does not invalidate the original controlled protocol or identify a time trend.
4. No new cutoffs/windows or IF outcome filtering after seeing model-comparison errors; do not adjust the primary seven-bat IPIlow gate post hoc based on timing information. Report source coverage and unresolved interpretation.

A source input access error or SHA mismatch is STOP, not evidence of no confounding.
