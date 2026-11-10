# v102 2018 original UHSLC 8-band source rescue: transport-only sharding, no post-outcome selection

2026-11-10 JST. Original independent 2018 run \`42729101678\` was **CANCELLED** because the full N_00_15 (2019 22 eligible source IDs) original hourly retrieval did not finish within its 35-minute job budget. Seven other original fixed source bands finished and produced original QC artifacts, including genuinely non-positive source gates (S_00_15: 0 new 2018 valid original station data, 18 download failures; N_60_75: 0/4 downloaded). The lack of source never becomes a biological null or estimated tide×solar effect.

The original scientific source frame is **unchanged**:
- 2019 source quality-eligible all 160 UHSLC station IDs from original run 42616065580, with their exact 2019 original \`record_id\`.
- N_00_15 fixed original 2019 22 source IDs, **before opening any new N_00_15 2018 water-level source**, partition by \`uhslc_id % 3\` to three nonoverlapping immutable shards (0,1,2). No outcome or 2018 source quality controls which IDs enter a shard.
- Use frozen v97 code exactly on each source-only subset. 2018 year/month 80% QC, original datum record version, quality=4, no >72h gap, Astral true 2018 solar >3° are identical to v97; only acquisition workload is split.
- Strict union of all 3 original N_00_15 source shards, exactly covering all 22 2019 IDs once, with no duplicate or missing observations. If source times out, keep \`source_failures\` with explicit transport reason, never replace with zero window effect.
- Join original SHA/source 7 previous band outputs from run 42729101678, without re-running or cherry-picking existing outcomes. Exactly eight source artifacts and their source counts must be verified before the independent-year model v98 is reattempted.
- This is **engineering transport recovery**, not a newly registered confirmatory ecological hypothesis or a change in the scientific 2018-vs-2019 estimand. A second \`2018\` source outcome from resumed source must be separated from the older complete original 7 bands.
- An independent year 2018 is chronologically before 2019; any heldout result is a retrospective **hindcast**, not prospective future prediction.

The v100 physical harmonic surrogate already showed that the 2019 F→|M| rho 0.858 is compatible with bare astronomical frequency physics. Even successful v98 2018 source physical prediction is NOT evidence of a biotic temporal niche; the next ecological step requires independent tidal-flat map + actual organism behavior.
