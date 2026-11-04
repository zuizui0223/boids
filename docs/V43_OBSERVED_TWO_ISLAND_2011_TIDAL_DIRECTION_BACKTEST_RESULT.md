# v43 OBSERVED: original 2011 horizontal movement direction contains extra tide-phase information at both Wadden islands

**2026-11-05 JST. Completed original source-backed retrospective two-island backtest.** Predefined after seeing the v41 2012 directional result; this is **post-v41 exploratory** same-species/same-source temporal sensitivity, not another independently preregistered study or population.

## Fixed hypothesis and source/model identity

The source was exactly the verified original Zenodo UvA-BiTS 2010–2011 Eurasian oystercatcher GPS for Schiermonnikoog and Ameland and physical RWS `schiermonnikoog.waddenzee` / `ameland.nes` **measured WATHTE** 10-minute water heights (original cm NAP, fixed UTC+01), 52,561 source gauge values per calendar year/site. Original GPS annual gzip provider MD5 verified afresh, independent source SHA256 recorded in temporary receipts. No raw bird tokens or original fixes committed.

**Imported unchanged v41 code** `original_three_fix_heading_episodes`, `forecast`, `directional_half_mse`. One first visible genuine GPS fix per hour; both previous A→B and next B→C 0.5–2h and geodesic speed 0.4–120km/h. At B, the bird's own previous 2D unit direction and previous speed, location, cyclic day/year time and actual tide height/h² are M0 predictors. M1 adds true ebb/flood phase based on preceding 20min source gauge slope ±0.012m/h and phase×height. Heldout target is the actual **next 2D unit displacement direction** B→C, scored at `0.5 × ((east−predEast)^2+(north−predNorth)^2)` with frozen train-only standardized weighted ridge L2 10.

**Train 2010 ONLY, test 2011 ONLY**, source GPS clock interpreted native as UTC first; −15s is sensitivity. All original field observations eligible by frozen gates, both sites, no searching for time or lag ranges. This test year was part of previous v41 2012 training and v41 2012 directional outcomes had already been opened before this backtest was designed.

## Original primary v43 heldout outcomes (native original clock assumed UTC)

| Original site | Train 2010 triple-fix episodes | Test 2011 episodes | 2011 birds | 2011 ISO weeks | M0 equal-bird half-MSE | M1 equal-bird half-MSE | Δ=M0−M1 | % MSE reduction |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **Schiermonnikoog** | **7,911** | **4,948** | **13** | **53** | 0.4491437063 | 0.4137069386 | **+0.0354367677** | **+7.8899%** |
| **Ameland** | **3,753** | **4,678** | **5** | **53** | 0.5107931837 | 0.4346461838 | **+0.0761469998** | **+14.9076%** |

### Correctly paired uncertainty (different estimands remain separate)

| Island | Positive heldout birds | **Bird-pooled** improvement 95% whole-bird bootstrap | Positive source test weeks | **Separate equal-week-then-bird mean improvement** | Matched whole-week bootstrap 95% |
|---|---|---|---|---:|---|
| Schiermonnikoog | **12/13** | **[+0.006111666,+0.055111021]** | **49/53** | +0.042710020 | **[+0.035310238,+0.049971658]** |
| Ameland | **5/5** | **[+0.051601453,+0.100713895]** | **48/53** | +0.077246860 | **[+0.058280878,+0.101731895]** |

These tests estimate **predictive MSE information about the next source GPS displacement heading**, not true instantaneous biological steering force or prey-site choice. Bird and week resampling reflect different estimands, and 53 weeks are not 53 independent coastal populations.

### Frozen source-clock −15 seconds sensitivity

- Schiermonnikoog 2010 training 7,923 original heading episodes, test 2011 4,949 episodes, **12/13 birds**, **49/53 weeks** improve. Direction phase relative error reduction **+7.9308%**, bird-pooled gain +0.035626079, whole-bird interval [+0.006288352,+0.055362464]; separate week mean +0.043036549, matching interval [+0.035732431,+0.050197611].
- Ameland 2010 training 3,727 source episodes, test 2011 4,671, **5/5 birds**, **48/53 weeks** improve. Relative reduction **+14.8645%**, pooled gain +0.076299227, bird interval [+0.051708907,+0.101204068]; separate week mean +0.083820250, week interval [+0.061389263,+0.111345452].

These clock choices are highly dependent analyses on the same source, **not independent replications**. Native GPS original clock UTC versus GPS time remains uncertain and telemetry error is not independently calibrated.

## Interpretation alongside frozen v32–v41 field findings

1. **Observed, predictive tidal organization of horizontal movement:** on same original 2011 source, the ebb/flood state improves the next movement direction beyond **the focal bird's own prior heading**, location, current water level, diel/year time and previous speed. The positive increment is recorded at **both** Wadden islands, not just Schiermonnikoog.
2. Schiermonnikoog's phase speed effect was previously confirmed on calendar-2011 and separately untouched-2012 years using different speed endpoints and samples (v32/v39/v40). Ameland had an inconsistent or tiny pooled all-motion **speed** MSE gain (v34/v39/v40), but now has directional information in the **moving three-fix subset**. Different inclusion criteria and response units **prevent concluding a quantified speed–direction tradeoff**.
3. v41's truly new directional 2012 Ameland endpoint showed +6.57% pooled reduction on 1,186 episodes, 2/3 birds and **whole-bird interval crossing zero**, despite a positive week interval. This study-year result is preserved exactly. v41's Schier 2012 **869** source headings failed the frozen 1,000-episode admission threshold; v43 2011 cannot be used to retroactively re-label the 2012 source STOP as a positive 2012 finding.
4. **Mechanism unproved:** these GPS segments cannot identify actual prey availability, feeding/commuting state, exposed intertidal cells, waterline propagation, physical alignment/social Reynolds steering or dynamic realized niche partition between species. The source-clock and gauge-location uncertainties remain. Matched source-shuffle evidence from earlier separate Boids v47 (near-field turn excess largely explained by locally matched control) remains relevant; do not infer genuine social information transfer from an environment-only model's positive prediction.

## Reproducibility and publication boundary

- [Original 2-island field run 41924916567](https://github.com/zuizui0223/boids/actions/runs/41924916567): two source original GPS/RWS and model QA jobs **SUCCESS**, pure known-truth tests pass, both site receipts/source MD5 and original number of eligible episodes included.
- Frozen document before v43 outcome: [V43_FROZEN_2011_TIDAL_DIRECTION_BACKTEST.md](V43_FROZEN_2011_TIDAL_DIRECTION_BACKTEST.md), itself committed **after** 2012 v41 outcomes had been opened.
- Exact source-code unit implementation: `validation_v43/backtest_2011_heading_phase.py`, tests `validation_v43/test_backtest_2011_heading_phase.py`; base v41 model imported unchanged.
- Scientifically defensible phrasing: *at these two Wadden Sea tracking sites, observed water-level phase predicts next horizontal displacement direction conditional on individual motion history and spatiotemporal controls; its mechanism, universality and behavioral state dependence are unresolved.* Keep as a **draft exploratory analysis**, not a fully independent confirmatory multi-species result.
