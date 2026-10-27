# Boids-to-niche mathematical chain: prediction is not inverse-law identification

## Explicit three-layer model

Consider an individual `i` in species `s`. A falsifiable *candidate*, not a discovered universal law, is

\[
\dot{\mathbf x}_{si}=\mathbf v_{si},\qquad
\dot{\mathbf v}_{si}=\mathbf f_{\mathrm{base}}(\mathbf v, E, H)
+\alpha_{si}\mathbf S_{si}+\beta_{si}\mathbf A_{si}
+\gamma_{si}\mathbf C_{si}+\delta_{si}\nabla R_s+\boldsymbol\varepsilon_{si}(t).
\]

`S` represents avoidance/separation, `A` neighbor heading alignment, `C` cohesion, `R` available resources, `H` individual experience or route/history, and `E` environment and wind. Each candidate term must have fixed units, scale and an observation model before fitting. Instantaneous relative positions cannot on their own identify learned memory, competition or actual force production. GPS captures `y_t = H_obs x_t + e_t`, not noise-free `x_t`; the v5 known-truth audit found that altitude-position error can create a useful yet biologically spurious *velocity-class* predictor.

Repeated simulated trajectories induce a distribution of **realized state use**

\[
U_{si}(x,y,z,t)=\mathbb E_{\theta,R,E}\left[\frac{1}{T}\int_0^T\delta((x,y,z)-\mathbf x_{si}(u))\,du\right],
\]

where the expectation, time window and environment ensemble must be declared. A short homing route does not automatically represent an animal's niche, daily utilization distribution, or fundamental niche. From comparable observation models one can measure:

- `I(individual; z | x,y,species)` — **within-species** repeated individual vertical organization;
- `I(species; z | x,y)` — **between-species** vertical organization in shared horizontal context;
- `I(species; x,y)` and `I(species; t | x,y)` — geographic and time-axis organization;
- use-versus-available environmental-state retention against a matched pseudo-use null;
- 1/sum(p_j^2) — effective use of breeding/colony components **only with annual count and observation-error models**.

Information metrics describe organizations in observed or simulated distributions. They are **not tests of causal competition or optimal specialization**, and must be compared under identical sampling effort and declared grid/smoothing choices.

## Independent validation ladder

1. **Structural observation gate:** are different individuals co-observed, and what time/3D-accuracy/sensory scale is observed rather than spline-created? The v4 original bat GPS failed a 5-s/100-m social-pair gate. The v6 bat-pair 3D and v8 pigeon matched GPS sources passed structural gates.
2. **Short-step predictive transfer:** on unseen birds/pairs/nights, compare equal-target own/route, own+real-neighbor and own+time-lagged/ghost-neighbor predictors. In v6 bats and v8 pigeons, the **strong contemporaneous control did not pass**; do not invent positive social-causation claims.
3. **Inverse steering-law rank/measurement diagnostics:** full force design SVD (not just two columns), near/far neighbor configurations, observational localization/velocity errors, external environment, and candidate alternate representations. If multiple steering parameter sets give near-identical trajectories, report an *identified set*, not a unique Reynolds coefficient.
4. **Longer-horizon ecological forecast:** train the force/policy model **without opening target niches**, simulate full 3D utilization and independently score entire held-out nights/individuals, with ODSP-style probability scoring and predeclared spatial/temporal grains.
5. **Cross-taxon transfer:** repeat in independently held-out bird and bat taxa with comparable sensor semantics, then test whether common rule families generalize; only then discuss between-species niches and whether resource competition changes the axes of partition.

## Status at this snapshot

**Completed:** 3D synthetic known-truth model, prediction within synthetic simulator family, v4 short vertical-state bat prediction, v5 GPS error alternative, v6 independently archived bat-pair directional forecast (primary not supported), v7 geometry rank known truth, v8 independently archived pigeon data: 197 two-tracker episodes with 10 independent bird-connected holdout groups (primary contemporaneous partner contrast not supported).

**Not established:** a unique biological separation/alignment/cohesion law, true 3D bat/bird niche predicted from a fitted social policy, individual strategy maintenance mechanism, resource competition as a cause, or transfer across species. The next gain must come from independent observation/error calibration or new source contexts, *not a new fit on the already tested v8 outcome*.

## v9 exact source-geometry equivalence and out-of-context uncertainty

For the illustrative pair displacement \(\mathbf r=\mathbf x_j-\mathbf x_i\), define

\[
\mathbf F(\mathbf r;\alpha,\gamma)=\Big(\gamma-\frac{\alpha}{\|\mathbf r\|^3}\Big)\mathbf r.
\]

At a single observed inter-individual distance \(d_0\), only the *effective* steering coefficient \(\kappa_0=\gamma-\alpha/d_0^3\) is determined. Every point on the line \(\gamma=\kappa_0+\alpha/d_0^3\) generates the same one-step acceleration for this geometry, regardless of prediction precision. For a different distance \(d\), the identified set generates

\[
\kappa(d)=\kappa_0+\alpha(d_0^{-3}-d^{-3}).
\]

This term depends on the unidentified \(\alpha\). In an explicit small-acceleration deterministic 3D pair-world stress test (`validation_v9/identified_set_forecast.py`), the calibrated source distance is 10 m, \(\kappa_0=-0.003\,\mathrm{s}^{-2}\), candidates \(\alpha=0,0.5,1,1.5,2\,\mathrm{m}^3\mathrm{s}^{-2}\), 30 seconds at `dt=0.02 s` and velocity damping `0.5 s^-1`. All candidates exactly match the source instantaneous acceleration. Their *30-second final inter-bird distances*, however, span **28.28–34.75 m** when initialized 25 m apart (a 6.47 m spread); at 10 m initially, the spread is 0.86 m. This is an invented known-truth stress test with no parameter estimation from wild GPS and **does not itself describe a species niche**.

The resulting mathematical rule is more useful than treating every fitted Boids parameter as recoverable: **report the ecological prediction envelope over the identified set, and only claim reliable context transfer when that envelope remains narrow under genuinely independent environments.**
