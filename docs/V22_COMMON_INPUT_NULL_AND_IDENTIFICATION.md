# v22 interpretation safeguard — non-social common-driver null makes collective velocity predictive

**2026-11-24 JST; analytic known-truth derivation, before opening v22 empirical outcomes.** This is an independent mechanism counterexample to the *interpretation* of v22's pre-registered score, not an alteration of its frozen prediction protocol or an observed fish-field result.

## 1. One exact counterexample (no neighbor response anywhere)

For each coordinate at one time \(t\), let an unobserved externally generated shared movement driver be \(U_t\sim \mathcal N(0,\tau^2)\), with independent fish-specific measurement/motor variation \(\epsilon_{i,t}\sim\mathcal N(0,\sigma^2)\) across fish. Observed velocity is \(v_{i,t}=U_t+\epsilon_{i,t}\). The focal's future velocity in the constructed no-social-coupling model is \(y_{i,t+\Delta}=aU_t+\eta_{i,t+\Delta}\), where \(\eta\) is independent. **There is no arrow \(v_{j,t}\to v_{i,t+\Delta}\) from any other fish.** Other fish are sensors of the same unobserved external driver, not social causes of the focal's motion.

The own current velocity \(v_i\) alone estimates \(U\) with posterior variance
\[
V_{\mathrm{own}}=\big(\tau^{-2}+\sigma^{-2}\big)^{-1}
=\frac{\tau^2\sigma^2}{\tau^2+\sigma^2}.
\]

The mean current velocity of the other \(N-1\) fish provides conditionally independent additional information with variance \(\sigma^2/(N-1)\), so
\[
V_{\mathrm{own+group}}
=\big(\tau^{-2}+\sigma^{-2}+(N-1)\sigma^{-2}\big)^{-1}
=\frac{\tau^2\sigma^2}{\sigma^2+N\tau^2}.
\]

The exact expected squared-error improvement of optimal Gaussian prediction is therefore
\[
\Delta \mathrm{MSE}
=a^2(V_{\mathrm{own}}-V_{\mathrm{own+group}})>0
\]
for \(a\ne0\), \(\tau,\sigma>0\), \(N>1\), despite **zero biological neighbor-to-neighbor interaction**.

At \(\tau^2=\sigma^2=1,\ a=0.8\), this purely constructed model yields 0.248889 squared velocity units with \(N=8\), and 0.261818 with \(N=10\). These are theoretical toy-model numbers and **are not** the Puy/Niizato field MSE improvements, nor comparable to either source's physical units.

### A stale-state null can also fail even with no social effect

Let the shared source \(U_t\) be independent of \(U_{t-2s}\). Then two-second-old other-fish velocities contain no additional signal about current \(U_t\) beyond own current state. The current global predictor beats the stale global predictor under the same constructed, *entirely non-interacting* animal model. With an autocorrelated \(U_t\), stale information may recover some predictive value but need not match contemporaneous velocities.

**Consequently, even if all four preregistered v22 empirical contrasts are positive, this supports time-specific shared-state information, NOT uniquely social alignment, a moving causal Reynolds force, learning, contact calls, or feedback.** Common unmeasured motion (water, wall/corridor constraints, vibration, other hidden common cues), or shared tracking filters, can generate the same signed effect. The original tank experiments do not directly measure these latent drivers for this proof.

## 2. Related prior work and distinction from a new discovery

- Herbert-Read et al. (2011), *Inferring the structure and dynamics of interactions in schooling fish*, PNAS, DOI [10.1073/pnas.1107583108](https://doi.org/10.1073/pnas.1107583108) explicitly derives interaction forces from dedicated fish pair/triad data, including three-body effects. Predicting movement with group features alone is not a first mechanistic discovery.
- A 2025 study in *Movement Ecology* on landscape heterogeneity and interactions, DOI [10.1186/s40462-025-00567-0](https://doi.org/10.1186/s40462-025-00567-0), shows that environmental covariates can generate false inferred animal-interaction effects in movement analyses. The v22 toy construction is a precise illustration of this confounding possibility, not a replication of that study.
- Veith et al. 2026, *Current Biology*, DOI [10.1016/j.cub.2026.02.019](https://doi.org/10.1016/j.cub.2026.02.019) has already established a quantitative auditory phase/frequency-to-individual motor transformation in fish. It does not provide group call–motion feedback attributions in Puy or Niizato trajectories.

## 3. What an actual discriminating school experiment would require

A genuinely novel and identifiable school↔chorus test must separately measure (or experimentally manipulate) the common field and local acoustic-motor couplings. Minimum design: pre-cue individual trajectories and source-attributed calls with calibrated local pressure/particle-motion, cue/no-cue randomization at the **school** level, a time-specified interval where local motion/connectivity is measured before future calls, and matched acoustic/stimulus controls to estimate both paths.

Without such data, a negative or positive current-vs-stale benchmark describes **predictive sufficiency and temporal information**, not social causality. Maintain scientific hierarchy: original field-movement model → source-conditional collective forecast; synthetic auditory ABM → mechanism possibility; individual auditory literature → established individual physiology; joint empirical fish school→calls effect → NOT YET MEASURED.

**Do not tune v22 after results; retain all original per-recording signs and both species. Keep PR #248 Draft and main unchanged.**
