# v34-B post-outcome composition and one-minute GPS-duty audits

**2026-10-31 JST, EXPLICITLY AFTER OPENING v34 EBB−FLOOD RESULTS.** This is NOT independent biological confirmation. The original primary v34 gain (+0.022694 log1p[km/h], 27/39 positive, 25,855 matched strata) and its descriptive low-water positive / high-water negative pattern are now known. The following frozen post-outcome diagnostics ask whether the apparent water-height sign reversal is simply different bird composition, and whether an original GPS step-duration difference of +0.143 minutes biases the main v34 association. It does **not** authorize fitting new thresholds to claim a universal tide-height transition.

## Original fixed data and admission

- Exact original Zenodo 10053970 v4 GPS (all seven 2008–2014 years, original MD5/SHA) and RWS official `schiermonnikoog.waddenzee` astronomical WATHTE, all seven exact complete years, NAP/cm, correct timezone.
- Exact prior 25 km local station geofence, consecutive original GPS fix pairs with 5–180 minutes UTC interval, original visible / manual outlier flags and all original duplicate timestamp exclusion. No GPS interpolation, altitude, disturbance or tide station changing.
- **STOP before new effects** unless the complete original published v34 anonymized 39 bird effects, 25,855 matched strata, all height-bin/interval/year descriptive statistics, original source counts and full v33-D 36-bird 5,422-strata receipt replay agree to **absolute 1e-12**. Any error in original source data, tide or code => no new effect.
- Ebb/flood remains based on RWS astronomical height ±30min at the GPS pair midpoint. Water height bands are *exactly* 0.5m NAP `floor(h/0.5)`. Original response is `log(1 + Haversine displacement km / elapsed hours)` and each stratum uses ≥2 ebb and ≥2 flood GPS pairs; all per-bird and per-stratum weights are unchanged unless explicitly part of the robustness audit below.
- This is still **one nonrandom island/site**, not independent year/species replication. Both diagnostics are *post-selection* to evaluate failure modes and must not modify the original positive v34 inference.

## Audit A: within the SAME bird, low vs high absolute water-height bands

The original descriptive height bins changed phase contrast sign between `[0,+0.5)m NAP` and `[+0.5,+1.0)m NAP`. Acknowledge that this cut was **selected after inspecting original v34 height-bin results**. It is not a pre-ecological fixed biological breakpoint.

- Define **LOW** as all original v34 already-admitted height bin codes `≤0` (H less than +0.5m NAP) and **HIGH** as bin codes `≥1` (H at least +0.5m NAP).
- For each source bird, require ≥8 original height/duty/hour/month matched ebb-flood strata in BOTH low and high regimes; never include a bird supported in only one. Require ≥20 paired birds and ≥200 original strata in each of low and high. If fail, **NOT_ADMITTED** with support only (no mean difference or inferential statistic).
- Calculate each bird's mean ebb−flood log-speed from original matched strata separately in LOW and HIGH, and difference `(ebb−flood)_LOW − (ebb−flood)_HIGH`. Report all 3 signed equal-bird means, **same-bird** 10k paired bootstrap percentile 95% (RNG seed 20261031), positive/negative bird counts and exact one-sided positive sign tail for the difference. Also count birds with `LOW>0 AND HIGH<0` and birds with the reverse. Same birds eliminate between-bird **composition** bias, not within-bird differences in season, movement behavior or observation process.
- Regime comparison depends on different tide heights by design; it tests whether the phase effect is height-dependent, **not** the effect of height alone or a causal shoreline threshold.

## Audit B: exact-source step interval matching within ONE minute

The original v34 used 3 registered GPS duration bins (5–30, 30–90, 90–180 minutes). Diagnose whether the small +0.143 minute ebb−flood elapsed difference creates the phase-speed contrast. Use **original strict same source-pair eligibility** and matching keys `bird × UTC year-month × UTC hour × exact original 0.5m water-height bin × rounded original elapsed GPS step duration in whole minutes`. Round to **nearest whole minute**, with the half-minute tie to the earlier/lower bin. This approximation is precommitted for the new audit and retains any original duration differences within ±0.5 minute; report actual residual elapsed difference.

Again ≥2 original ebb and ≥2 original flood GPS steps within each **one-minute** stratum, ≥8 such matched strata/bird, ≥20 whole birds, ≥200 paired strata; otherwise **NOT_ADMITTED** no rescue with 2/5/10-minute bins. Summarize equal matched-stratum bird means of ebb−flood log-speed, ebb−flood mean GPS elapsed minutes and residual water-level height; 10k whole-bird bootstrap CI and exact sign probabilities. Compare qualitatively to the original v34 effect but note cohorts/strata can differ.

## Science boundaries and outputs

The original v34 comparison is observational and GPS source has no feeding, tidal-flat polygon, prey accessibility, tide-specific actual surface elevation at each bird, or direct social interaction. An association after matched level/time/duty does not establish causal ebb/flood or Reynolds steering. A negative B audit may indicate observation-process bias; a positive B audit supports robustness within available duty regimes **without making this post-outcome diagnostic independent**.

Reproduce and retain frozen v34 and v33 output files; create a separate draft PR stacked on v34, no merges, no raw animal GPS identities, coordinates or per-fix UTC records published.
