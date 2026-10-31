# v33-E — after-outcome duty-cycle and tidal phase-alignment audit

**2026-10-31 JST. Explicitly POST-OUTCOME diagnostic**, written after seeing v33-D high-minus-low tidal movement result (-0.215357; 36/36 birds lower at high water), and after knowing v33-C non-improvement of daily tidal-range forecast. This is NOT new confirmatory validation of v33-D and may not be used to select a more favorable cohort/model. The exact original v33-D outcome, thresholds and full bird-receipt remain unchanged.

## Artifacts and admission

Reuse exclusively the checksum-pinned original seven annual Schiermonnikoog GPS gzip files from v32 (2008–2014), the same official RWS source `schiermonnikoog.waddenzee` astronomical heights, original bird visibility/outlier flags, original 25km two-fix local filter, consecutive original fix pairs lasting **5 to 180 minutes inclusive**, midpoint RWS 10minute nearest lookup, original fixed-source low≤Q25 and high≥Q75 thresholds, and within **bird × year × month × UTC hour** strata with ≥2 high and ≥2 low pairs. ≥8 matched strata/bird, ≥20 birds, ≥200 strata, bird-balanced comparison. Require an exact replay of D's **full saved anonymous bird and effect JSON** (tolerance 1e−12) before emitting additional diagnostic scores. Do not silently reselect the sample or move the tide station.

## Fixed diagnostic questions and direction

1. **Observational-duty diagnostic, primary audit:** Compare pair elapsed minutes HIGH−LOW within the *original matched D clock-month strata*, first equal-stratum within bird, then equal bird. Report 10k whole-bird bootstrap and counts. A systematic interval difference is possible measurement artefact affecting speed; its absence reduces but does not remove bias. Also report durations and speed-sign diagnostic for all 36 original D birds, without exporting any individual original UTC.
2. **Duration-bin robustness** with exactly three *nonoverlapping* bins in minutes:
   * SHORT `5 ≤ Δt < 30`
   * MEDIUM `30 ≤ Δt < 90`
   * LONG `90 ≤ Δt ≤ 180`
   Each bin separately requires its **own** ≥2 high and ≥2 low GPS steps in *each* original bird×year-month×UTC-hour stratum and the same cohort support gate (≥8 strata/bird, ≥20 birds, ≥200 strata). STOP without effect for a failed bin. **Do not reassign the main endpoint to the strongest bin.** Report sign, 95% whole-bird bootstrap, per bird counts for every admitted bin.
3. **Tide-phase offset sensitivity:** Shift *only the astronomical tide classification time* by exactly **+3h** and **+6h** at the same actual original GPS pair and its same UTC clock hour/year-month. Keep all other filters, Q25/Q75 source cutoffs, and admission gates. Apply the same fixed within-bird-hour-month pairing. Both shifts may alter which steps are included; report exact matched support counts and NO causal or confirmatory evidence based on these post-outcome comparisons. +6h is approximately a half semidiurnal cycle, so a sign reversal can be a mathematical consequence of tidal periodicity, not independent proof of biological entrainment.
4. **Yearly descriptive stability:** Reuse original D matched strata and calculate equal-bird mean high-minus-low log speed separately for each of **all seven years 2008–2014**. Report n birds/strata per year. Do not drop years with weak or positive directions. No repeated-year independence claims (birds can recur).

No other offsets, temporal bins, distance buffers, GPS quality cutoffs, or tidal outcome variables may be searched. Fail explicitly if original source changes. A positive robustness direction in all bins strengthens the claim that one GPS interval regime alone did not drive D, but GPS interval matching, the original GPS observability process and site choice remain uncontrolled mechanisms. No claim about feeding, exposure or Boids forces. No original animal GPS, real IDs, exact timestamps or per-day movement data in repository.
