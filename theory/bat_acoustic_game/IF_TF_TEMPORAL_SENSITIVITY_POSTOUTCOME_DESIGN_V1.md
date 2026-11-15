# Fixed post-outcome temporal-sensitivity check on published IF/TF source

**2026-11-05. NOT a prospective new-animal analysis or independent preregistration.** We have already observed the full-window IF/TF model comparison (run 41922688245) and the source ON/OFF chronology audit (run 41923195416). The new purpose is **diagnostic only**: determine whether the source's full before/after spectral changes are stable when observations are restricted to local, symmetric original relative-time windows around the playback onset. This cannot deconfound stimulus ON from time since experiment start: all 105 source strata have OFF before ON.

Original source: Hase 2026 DOI 10.1098/rspb.2026.0921, Figshare 30937379, `Data_jamming.csv` SHA256 `2998ad0e57cc51cb4a98f48de6444d543f925994600cd5574f25e40babcfa367`.

## Freeze exactly three time policies

1. `near_one_second`: original OFF time `[-1,0)` versus ON `[0,1)` seconds.
2. `symmetric_two_seconds`: original OFF `[-2,0)` versus ON `[0,2)` seconds.
3. `exclude_near_switch`: OFF `[-2,-0.5)` versus ON `[0.5,2)` seconds, recognizing source TF controller's 200ms integration lag.

All three were selected after seeing full-window and chronology results but **before viewing any outcome for these windows**. Report all with source-qualified biological counts, not whichever gives favourable sign. Full-window result remains frozen as baseline.

For each window: require original bat-ID×experiment×condition×Var×jammingTF group ≥4 finite original rows in each original ON and OFF **within that window**, shared complete-case IF and TF, original IF>TF, and ≥3 distinct original condition levels per bat×experiment. Follow **unchanged** source model comparison definitions from `PUBLISHED_IF_TF_PHYSICAL_CONVENTION_PREOUTPUT_V1.md` and implementation in `published_IF_TF_convention_v1.py`:

- `M_start`: error = `|ΔIF|`.
- `M_band`: error = `|ΔIF−ΔTF|`.
- `D = E_band−E_start` (positive favours start fixed).
- Average Var/jammingTF contexts equally within bat×experiment×condition, then conditions equally within bat, then bats equally within each experiment.
- Report all experiment levels, biological bats and condition support, mean/median D, 5,000 whole-bat bootstrap from the previously pinned RNG seed, and ON/OFF mean-vs-median source sensitivity. Do not treat original calls or time windows as independent individuals.
- If an experiment-window has fewer than 5 bats, report `SOURCE_SUPPORT_STOP` for that cell and do not adjust the 4-row/3-level gates.
- No original bat IDs/time stamps, raw source rows or participant record-level outputs in committed artifacts. No measured prey capture, actual masked acoustic false alarm or species/colony generality.

**Interpretation bound:** A time-window sign change is evidence of source-time sensitivity of the *descriptive* comparison, not proof that playback has or lacks a causal effect. A robust sign would still be one source under a nonrandomized before/after sequence, not an independent biological confirmation. The source's original IF/TF Figure S2 is published prior art.
