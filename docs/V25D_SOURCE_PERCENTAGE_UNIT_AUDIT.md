# v25-D original habitat covariate unit audit after the frozen v25-C source-domain stop

**2026-10-29 JST. This is a NEW source-format audit, registered after v25-C stopped on the `Corn` raw-value range but BEFORE any actual ecological regression or heldout predictor has been scored.** The v25-C STOP, source hash, source/model and all previous v13–v24 results are immutable.

Source: original USGS Overton & Casazza (2023), DOI [10.5066/P9ELSUHN](https://doi.org/10.5066/P9ELSUHN), frozen official CSV 27,997,528 bytes, MD5 `78eb6064eca992225d6907d6e46f5bef`, SHA256 `1a5c2342f9df4c70f170741c14b92b5146f0558f29fd593307768a228b82ca15`. File includes 380,578 source TRUE/FALSE paired habitat-profile rows.

Original paper [Overton & Casazza 2023, Frontiers](https://doi.org/10.3389/fevo.2023.1232704) describes each category as the **proportion** of 100 simulated movements' habitat outcomes. The deposited CSV's raw numeric scale is NOT assumed to be [0,1] because the immutable source-domain v25-C gate failed on `Corn`.

## Stage D0 source-only, before any habitat effect

- Read **ONLY** the seven numeric columns `Corn,Field,Other,Protected,Rice,Urban,Wetland` from original SHA-pinned CSV, ignoring all original `case` used/available labels, animal IDs, dates and outcomes. Calculate row counts, finite/missing counts, aggregate min/max, and percentages of entries in [0,1], (1,100], above 100 and below 0. Optional all-column sum bounds may diagnose whether Protected is an overlay rather than a disjoint composition. Never compare per-case distributions at this stage.
- Precommit unambiguous source-unit rule: If all seven raw columns have finite **nonnegative values ≤100**, and **at least one numeric entry >1**, classify raw values as a *published percentage-like scale* and convert **all seven** columns by exactly dividing by 100. If all raw values are ≤1, use identity scaling. Any field outside [0,100] yields a hard STOP, **not** a post-hoc cap/winsorization, alternative column selection, min-max scaling or response-informed transform.
- Source percentages may not sum to 100 across all seven columns because `Protected` is potentially a sanctuary overlay; percentage-scale detection is not evidence of disjoint ecological resources. The exact conversion is only a **unit correction**, not a novel source-specific statistical optimization.
- No original animal ID, exact habitat row, GPS coordinates, case-specific ecological predictor summaries, environmental association or model effect may be committed in D0.
- The earlier v25-C `NOT_ADMITTED_FROZEN_ORIGINAL_HABITAT_DOMAIN_OR_SOURCE` result is preserved. If D0 passes and the exact rule yields /100, only a **separate v25-D1 post-source-unit-conditioned exploratory analysis** with a fresh frozen contract may evaluate the SAME originally preregistered full 493 birdyear, 190,289 paired source dataset. Such a later effect can be exploratory, never described as original v25-C confirmed.
- The archived false case is an author-aggregated availability habitat profile, **not 100 distinct choice alternatives or an independently timed future choice set**. Only retrospective paired-profile habitat ranking is admissible.
