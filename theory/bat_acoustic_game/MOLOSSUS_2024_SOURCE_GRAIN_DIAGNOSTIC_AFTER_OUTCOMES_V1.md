# Post-outcome correction: original PNAS Molossus source group grain audit (2026-11-05)

**MANDATORY before any ecological interpretation of previous model run.** The original source 2024 original XLSX was opened and the predefined M0/M1/M2 bat-holdout run was completed, but its initial assumption `E = numel_5swindows` may be **incorrect**: 4299 source rows across 10 original bats contain a total of 197566 `numel_5swindows` entries, corresponding to ~274h if naively counted as distinct 5-second flight windows; the 2024 published flight sessions are around 17–50min each. **Previous initial model scores are quarantined and are NOT accepted as ecological results.** Do not silently overwrite or hide that analysis.

The original published source data is byte-pinned: DOI 10.1073/pnas.2321724121, Europe PMC original `pnas.2321724121.sd01.xlsx` SHA256 `92acbc36cce42028bfd5a07ad1ec8aa8062121575d6d665dc7392b47222f562d`, one worksheet `A1:H4300`. Fields `bat,sec_group,numel_5swindows,sum_attacks,sum_success,sum_cons,sum_commute,sum_disrupt`.

**SOURCE-GRAIN AUDIT, after outcomes known but response-agnostic admission**:
- Identify original source row count and original individual-ID unique count (do not release bat original labels).
- Per bat: quantify unique `sec_group`, numeric source group min/max and spacing (do they form consecutive 5-second window IDs?) and whether source rows equal each bat's group coverage. Report only min/median/max of *bat-level summaries*, not original IDs.
- Calculate per-original-row min/median/max of `numel_5swindows`, pooled sum and ratios to original source row count; include range in `sum_attacks` and `sum_cons` as **source-structure validity diagnostics** (already-published outcomes, do not search significance).
- Compare `number original rows ×5sec` and `sum(numel_5swindows)×5sec` with original published approximate per-bat flight duration range. Do not claim 5s row exposure until sec_group is independently supported as source 5s group.
- If bat-specific sec_group is a contiguous count sequence with 1 row per step and group length matches published flight durations, label `E=1 original 5-second window per worksheet row` as **provisionally source-compatible**. Still check whether source `numel_5swindows` is a different field such as sample/count with author documentation, and avoid asserting its meaning without evidence.
- If sec_group does not support a five-second row, then source group grain remains ambiguous: stop original prey-capture model until clarified.

Any corrected model MUST have a **new versioned post-outcome correction contract**, rerun all 10 bats with same frozen models/predictors/penalty and publish both old invalid and new corrected outputs, no positive sign tuning.
