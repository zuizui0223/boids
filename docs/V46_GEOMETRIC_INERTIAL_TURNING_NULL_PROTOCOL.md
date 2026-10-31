# v46 — Geometric inertial null for original wild focal NEAR-vs-FAR turning

**2026-10-31 JST; explicitly post-v45 observed outcomes.** Known v45 source result: 17/18 eligible wild oystercatchers, 4,660 original next GPS step episodes where focal *past and future* movements each ≥50m and mean other-bird near and far prior headings each have norm≥0.25; observed C_NF = −0.0979493 (bootstrap95 [−0.135902,−0.057040], 15/17 negative). The 100-replicate original v45 clock+tide source shuffle was more weakly negative than observed, but did not hold the focal's initial alignment and true turn angle fixed. **Negative C_NF is not evidence of wild bird avoidance until a stronger purely geometric null is excluded.** This is a NEW synthetic geometric-null comparison of the ALREADY OBSERVED original wild records, not independent validation or causal evidence.

## Fixed physical null and signed estimand

Let two unit headings of the same original focal bird be \(u_b\) before its forecast and \(u_a\) at the future recorded next-step displacement (the source segments are independent four-GPS-fix and each ≥0.05km). Let \(n,f\) be the **unit-normalized** means of other birds' source near≤200m and far≥1km previous headings; those other bird observations ended in the 5min before the focal forecast start. All four headings and the exact original 17-bird / 4660-step admitted v45 cohort must be reproduced **without any threshold changes**.

Define \(d=n-f\), \(c=\mathrm{clip}(u_a\cdot u_b,-1,1)=\cos\theta\) and \(B=u_b\cdot d\). The observed focal direction-change difference is the original
\[
C_{\rm observed}=(u_a-u_b)\cdot d.
\]
If the **absolute focal turning angle** \(|\theta|\) and initial heading \(u_b\) are fixed but turning handedness (clockwise/anticlockwise) is equiprobable and independent of the other bird's direction, the geometric expectation is
\[
C_{\rm geom}=(c-1) B.
\]
The **single fixed primary** signed excess contrast, positive if greater near-directed turning than an equiprobable-handedness inertial null:
\[
C_{\rm excess}=C_{\rm observed}-C_{\rm geom}
=(u_a-cu_b)\cdot(n-f).
\]
**Primary is equal-original-bird mean C_excess**, estimated by first averaging ALL previously admitted v45 source episodes within each bird then equal-weighting the 17 birds. A negative robust value is still not causal repulsion because local route curvature, wind, bathymetry and observer duty can yield turn handedness; a null/positive value means original negative C_observed cannot be described as robust evidence for avoidance.

**Preset SECONDARIES** are residual near-only \(C_{N,\rm excess}=(u_a-cu_b)\cdot n\), residual far-only \(C_{F,\rm excess}=(u_a-cu_b)\cdot f\), and the geometric expectation \((c-1)B\) itself. Report **all** and the accounting identity \(C_{N,\rm excess}-C_{F,\rm excess}=C_{\rm excess}\) for every episode and per-bird mean. No sorting sign or after-result threshold tuning.

## Strict old-source/old-outcome replay

Download the exact same original Zenodo 10053970 v4 GPS seven years and official RWS astronomical WATHTE 2008–2014 as v45, all original provider MD5/SHA and source QC. **Before opening the NEW per-episode geometric residual**, run the ENTIRE v45 source replay: old v41 ID/UTC, v42 source spatial opportunity, v33-D tidal-speed, v39 private speed, v40 private heading, v43 near/far predictive 2D and v44 balanced 18/68,232 source future episodes, and then old v45 **17 birds / 4,660 direction episodes, all original per-bird, annual, monthly and shuffle values**. Compare saved \`validation_v45/results/original_near_far_turning_convergence_v45.json\` at **absolute numeric tolerance 1e−12** including source gates, labels, all values, and exact cohort counts. If any mismatch, **STOP with no new v46 score**.

Important: the same v45 \`direction_ready\` uses source-fixed values H, current dH, private past disjoint heading, u_after, near/far norm gates; no source direction/fix replaced. To obtain \(u_b\), use v45 original X40 private-heading columns (unit and source-fix disjoint). Obtain \(u_a=u_b + \mathrm{turn}_{v45}\), checked unit norm within 1e−10. Use **original v45 eligible_birds** with exactly 17 birds/4,660 whole-source episodes; NOT all candidate 4,667 episodes or a reselected post-hoc subset.

## Fixed uncertainty, annual/month controls and handedness sham

- 10,000 paired whole-original-bird bootstrap (seed 20261031), same C_excess orientation; one-sided positive exact bird sign tail plus two-sided percentile CI, all 17 signed per-bird effects; no individual GPS point or timestamp in report.
- Yearwise descriptive equal bird effects, counting 2010 AND 2011 including negative signs; equal UTC calendar-month means and naive 10k bootstrap labeled as **correlated, different estimand**.
- **Fixed 1,000 handedness sham draws** (RNG 20261031) on the exact same original admitted cohort. Preserve each real focal initial heading, exact |turn angle|, same corresponding n and f, and actual episode count/participation. For each episode independently choose clockwise vs counterclockwise with probability 1/2 and reconstruct \(C_{\rm sham}=(c-1)B+s\sqrt{1-c^2}(u_b^\perp\cdot d)\), where \(u_b^\perp=(-u_{b,N},u_{b,E})\) and \(s\in\{-1,+1\}\). Report equal-bird mean of sham C_observed and excess, 5–95% sham range, and observed minus sham mean. **Monte Carlo permutations are synthetic** and are not 1,000 independent animal replications; inference remains bird-clustered.
- **Fixed source support** 17 whole birds / 4,660 previously observed source episodes (original v45 gate). If ANY fail, stop. No changing to ≥20m move, alternate spatial radius, or relative orientation threshold.
- **Initial geometric alignment** B: source descriptive mean, number B>0/B<0 for all matched episodes and per-bird, and report fraction of original negative C_observed attributable to \(C_{\rm geom}\) *only when algebraically stable*. Do **not** divide by tiny observed C to claim a % explained: report additive mean decomposition instead.

## Interpretation

The previous v45 negative observation alone may arise automatically via regression to the mean. **A C_excess near zero** would show equal-handedness turning is sufficient for its negative sign, under the chosen null; neither true social avoidance nor true social alignment can be inferred. **A nonzero C_excess** indicates a turning-direction asymmetry conditional on current initial orientation and observed magnitude, but may be caused by geographic path geometry, wind, tide-state history or focal private route and does not identify social motor forces.

No original animal GPS, IDs, coordinates, individual UTC dates, per-step movements or original tidal heights should be committed. All v29–v45 original output receipts must remain untouched; create a separate draft PR stacked on v45, no merge or release without authorization. Use only read-only GitHub Actions original source. No eBird or TinyFish.
