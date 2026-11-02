# v36 — POST-RESULT local tide propagation/clock lag sensitivity across TWO islands

**2026-11-02 JST. EXPLORATORY after opening v34 Ameland outcome and v33 Schiermonnikoog outcome.** Do not call this an independent confirmatory test. No freely optimized lag or winning-site subset.

## Question
Could the difference between Schiermonnikoog's positive external-year tide-phase association and Ameland's near-zero association depend on gauge-to-bird tidal phase offset rather than different ecological use of intertidal resources? Gauge observations at a fixed station are not the actual local water-line crossing at the bird's GPS fix; tide propagates along channels, and tag clocks may have offsets.

## Identical sources and fixed year transfer
- Reuse both source-authenticated original 2010/2011 GPS studies `O_SCHIERMONNIKOOG` (Zenodo 22296922) and `O_AMELAND` (Zenodo 10053853) and their original 2010/11 RWS historical WATHTE NAP series (`schiermonnikoog.waddenzee` and `ameland.nes`).
- Reuse frozen ORIGINAL HOURLY first-fix sampling, source visible/within study region, 0.5–2h next-fix horizontal displacement, GPS source clock interpreted UTC with -15 sec source-clock sensitivity.
- Both models fit 2010 and evaluate untouched full calendar 2011, independently per island. Baseline features are fixed: M0 = height at the true GPS time (quadratic), source lat/lon, diel/seasonal clocks. Mphase = M0 + shifted *phase only* and phase×**unshifted** height; no continuous water-rate or extra sources.
- Original ridge penalty λ=10, training-only normalization, equal bird weighting and no bird-ID fixed effects. Output M0 vs Mphase original equal-bird MSE differences.

## FROZEN exploratory lag grid (must report ALL)
`[-120,-60,0,+60,+120]` **minutes** applied to original gauge phase time `t+lag` only, while contemporaneous observed height remains `h(t)`. No change of source GPS fixes, outcomes, site envelopes or bird selection by best lag. For each site+clock interpretation, take the **common support** of source rows at all five lags (including trailing 20-min phase measurement and tide sample max-gap gate) before any fitting, so all lag variants are evaluated on EXACTLY the same bird/time rows. Slack phase (0) at displaced time is allowed as a distinct phase feature instead of screening rows by placebo phase.

Compare M0 baseline to all five Mphase alternatives under original 2010 train/2011 test. Save per-lag both equal-bird signed gain and complete test-week paired resampling 95% with fixed seed 20261102 and 4000 replicates. Also report 2011 held-out bird count, week count, records and all phase frequencies. Report both sites even if one has negative associations. The -15-sec GPS offset is a sensitivity check and **not an additional independent site**.

## Interpretation guard
- A shifted phase signal can remain predictive because tidal patterns are periodic, not because bird reacts to a future water level. Thus phase lag scans cannot identify true hydrodynamic propagation or prove a behavioral mechanism without local elevations, current flow, habitat maps and actual sensor clock verification.
- If a different lag improves Ameland, it is a **post-result apparent improvement** and needs independent locality-level timing before being called a causal lag correction.
- If Schier vs Ameland difference persists across all lags, this is compatibility with spatial heterogeneity, not identified habitat mechanism.
- No motion-only synchronization equates to a Boids alignment force, and M2 front and M3 social mechanisms remain unidentifiable from these sources.
- Never commit original animal IDs, coordinates, or original water time series, only source checks and aggregate scores.
