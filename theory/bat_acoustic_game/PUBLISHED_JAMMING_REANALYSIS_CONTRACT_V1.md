# Pre-response contract: archival 2026 bat masking reaction curves (2026-10-31)

**SOURCE-REUSE, NOT NEW BAT MEASUREMENT.** This analysis is secondary, performed after the 2026 source paper already disclosed relevant directional outcomes. It is NOT a preregistered independent validation, and it cannot measure actual prey capture or prove a wild colony strategy. Frozen field JAE and earlier boids results unchanged.

## Original source and fixed structural feasibility

- Source: Hase et al. 2026, Proceedings B DOI 10.1098/rspb.2026.0921; Figshare 10.6084/m9.figshare.30937379, one public file `Data_jamming.csv`.
- Independent read-only pre-response source gate: Actions run 41190147131, PASS, 12,308 source rows, 11 distinct bat ID labels, 15 source experiment-condition combinations.
- ON/OFF code: `isON` 0 (5,467 source rows) vs 1 (6,841); all 11 bat labels contain ≥2 matched condition groups with ≥4 rows/state. 105 ID×condition×experiment×Var×jammingTF contexts passed the source-only count rule (without reading TF).
- Source groups: IPIlow (50,100,200,800,1600ms), IPIhigh (5,10,20,50,100ms), SPLlow (-40,-30,-20,-10,0 dB). These fixed levels have already been defined by source design, not selected for significant results.

## Primary estimand and frozen procedures

**Primary:** for each bat under low-frequency interference (IPIlow), does median TF_ON−median TF_OFF **decrease as log10 of the source stimulus inter-pulse interval increases**?

1. Parse native `TF` as finite float; no filling, no conversion guessed from numeric magnitude.
2. Group original rows by biological `ID × Experiment × Condition × Var × jammingTF × isON`. Require at least 4 finite TF rows in each ON and OFF. Use median(TF_ON) − median(TF_OFF) per qualified context.
3. Average qualifying Var×jammingTF context shifts **equally** within `ID × Experiment × Condition`; do not weight by number of calls. Do not pool raw call rows as independent biological individuals.
4. For IPIlow and IPIhigh separately, fit the transparent OLS slope of condition shift versus log10(source IPI in ms) **within each bat**, if ≥3 distinct eligible IPI levels.
5. Primary bat-level sign direction for IPIlow is NEGATIVE (more positive TF response with denser low-frequency masking), with an exact one-sided sign test if ≥5 bats have within-bat slope support. Also report equal-bat mean/median slope, seeded whole-bat 95% percentile bootstrap CI.
6. IP I high (IPIhigh) and SPLlow are **SECONDARY DESCRIPTIVE**: slope against log10(IPI) for high TF; slope against dB stimulus SPL for low TF. Do not re-sign outcomes after results. A shared-bat IPIlow-vs-IPIhigh slope contrast is descriptive unless ≥5 true overlapping bat IDs.
7. Sensitivity: replicate with ON–OFF **means** instead of medians, using exactly the same source groups and eligibility. No threshold relaxation if source numerical eligibility differs from source-only preflight.
8. A result is NOT evidence of acute causal effect if ON/OFF phases correlate with unmeasured time, stimulus order or bat drift; do not call it independent species replication because every entry derives from one published source.
9. No original bat IDs or numeric pulse-by-pulse records are published in repository or workflow artifacts; publish only bat-aggregate summaries and original source-file SHA.

**Source STOP:** if native finite TF or sufficient paired exposure across ≥5 bats is unavailable, do not open alternate endpoints. Report exact structural reason. No optimization of time windows/condition filters after inspecting TF.

## Connection to endpoint-bridge v2

The 2026 data constrain *emitted frequency shifts* in experimentally controlled masking. The separate 2026 published group model quantifies potential acoustic misdetections. Neither dataset by itself estimates **conversion from a potential false detection into actual lost foraging time**, true prey detection or capture. Thus no new source result can automatically resolve the 2020-vs-2026 capture vs signal question.

## Source attribution

Hase et al. (2026), *Self-organized spectral adjustment in echolocation sounds within group-flying bats*, DOI 10.1098/rspb.2026.0921. Figshare dataset DOI 10.6084/m9.figshare.30937379. Reanalysis design committed before this branch's new source numerical TF scan; the ORIGINAL PAPER had already described its direction and thus this is not a blind independent discovery.
