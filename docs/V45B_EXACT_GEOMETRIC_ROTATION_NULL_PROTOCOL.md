# v45-B — Exact geometric rotational-inertia null for observed near/far heading divergence

**2026-10-31 JST; explicitly AFTER seeing v45 negative wild focal NEAR-versus-FAR convergence**, where C_NF = −0.097949 cosine-scale units (17 birds/4,660 orientation-eligible original GPS episodes, whole-bird CI [−0.135902,−0.057040]). This is a **post-outcome geometric nonidentifiability audit**, not newly independent animal evidence. It cannot rescue a desired positive or negative social-effect direction by retuning the original cohort.

## Why the null is mandatory

The v45 observed contrast C = (u_next − u_prev)·(n−f) is structurally sensitive to **initial near/far relative alignment**. If focal's original heading u_prev was more aligned with NEAR previous bird direction n than with FAR f, unbiased random turning (with persistence) tends to reduce the near-vs-far alignment. Hence even a robust negative C does **not** demonstrate social repulsion or active avoidance.

The exact 2D unit-heading identity for every original episode is:

\[
u_{next} = (\cos\delta)u_{prev}+(\sin\delta)u_{\perp},
\]

where cosδ = u_next·u_prev, sinδ = u_next·u_perp, u_perp=(-u_prev_n,u_prev_e). For fixed paired other-bird heading difference d=n−f,

\[
C_{\mathrm{obs}}=(\cos\delta-1)\underbrace{u_{prev}\cdot d}_{B}
  +\underbrace{\sin\delta(u_{\perp}\cdot d)}_{C_{\mathrm{excess}}}.
\]

The first term is **the exact conditional average of hypothetical turns with the same original absolute turn-angle magnitude but opposite left/right sign** (mirror original future direction about own prior heading). This is geometric regression to the mean and requires no social response. The signed second term is observed turn orientation beyond this symmetric angular-rotation null.

**SINGLE PRIMARY**, frozen before computation: whole-bird C_excess = C_obs − (cosδ−1)B; positive indicates selective relative turning toward near beyond symmetric geometry, negative selective relative turning away beyond geometry. Report 95% paired 10,000 whole-bird bootstrap, exact one-sided positive bird sign and all negative individuals, irrespective of outcome. Preset secondary: whole-bird original C_obs (must equal original v45), geometric-only C_expected=(cosδ−1)B, initial alignment B, cosδ, near-only and far-only excess. Per-episode exact algebraic identity must agree tolerance 1e−12.

## Exact original source and previous result numerical gates

Use exact original 2008–2014 seven-year SHA/MD5-pinned Zenodo 10053970 v4 O_SCHIERMONNIKOOG bird GPS and Rijkswaterstaat official Schiermonnikoog astronomical WATHTE in 10-minute UTC support, 7 years. Before any new excess score:
- Re-download and rerun complete original v41/v42/v33/v39/v40/v43/v44 source and all original anonymized numeric outcomes at absolute tolerance 1e−12 with v45 source gate.
- Recompute exact original v45 17 birds/4,660 episodes, the full C_NF, near/far components, bootstrap, annual/month and 100 within bird/month/UTC 6h block/tide phase shams. **Entire** frozen validation_v45/results/original_near_far_turning_convergence_v45.json must match recursively within abs1e−12, with identical other fields and keys, before computing new effects.
- Keep original prior/future focal displacement ≥50m, near ≤200m, far ≥1km, external mean resultant norm ≥0.25, original both-available 18-bird/68,232 source opportunities, the actual original 17-bird/4,660 effect cohort, and all source times/clock/season. No selection or refitting v43/v44 source models after viewing prior results.
- Counterfactual turns mirror ONLY the *sign* of each observed turn around its original previous heading, preserving angular magnitude, original previous and future motion speed/displacement, source tide, previous near/far headings, bird ID and target inclusion. This is an **analytic negative control**, not real randomized movement.

## Post-outcome source-scoped inference and reporting

For each original focal bird, average C_excess over all its original eligible episodes; then equal weight original birds. Bootstrap 10,000 original bird draws RNG 20261031, exact one-sided positive sign tail. Report all source years (2010 and 2011) and all 11 UTC calendar months with no positive-year selection.

Secondary **fixed initial-alignment strata**: B>0 initially near more aligned than far; B≤0 otherwise. Require ≥10 original birds with ≥10 original target episodes each and ≥1,000 episodes in each stratum to emit stratum-specific effect; otherwise STOP that stratum, with source support counts only. Report mean raw C_obs, geometric-only expectation and excess, with whole-bird CIs; do not redefine global primary.

Secondary near-only/far-only residuals: near_excess = (u_next−u_prev)·n − (cosδ−1)(u_prev·n) and far_excess analogue. Difference must equal main residual exactly to 1e−12.

## Interpretation limits

An apparent negative raw C can be explained by initial near/far alignment and symmetric turning alone. Even if C_excess is negative or positive, this is within one nonrandom Wadden Sea coastal animal tracking source. Original GPS has no prey capture, true behavioral state, fine bed topography, wind or actual social response. Focal prior/next movements share no GPS fixes but correlated device errors remain. No claim of social repulsion, attraction, cognition, Reynolds alignment/cohesion/separation coefficient, or true 3D ecological niche partition based on this audit.

Source-safe anonymized results only, no raw original bird IDs/GPS coords/animal timestamps/RWS tide arrays. Separate draft PR stacked on v45, earlier v29–v45 source/endpoint receipts unchanged; no eBird, TinyFish or main merge.
