# v10 — When uncertain Boids rules do and do not determine ecological niche patterns

**2026-10-27 · status: completed synthetic mathematical stress test; not wild-animal inference.**

## Current research question

A microscopic Boids rule may predict a trajectory without separately identifying its separation and cohesion coefficients. Can it still support a scientifically meaningful **macro-level prediction of 3D realized state use**, rather than merely predicting the distance between two flying individuals? Under what conditions are the dominant **between-species** niche axis and **within-species** state-use persistence robust to plausible steering rules?

This builds directly on [v9](MOVEMENT_TO_NICHE_IDENTIFIABILITY_V9.md), not on a refit or reinterpretation of the frozen v6 bat or v8 pigeon negative primary results.

## Generative and observation model

For a deliberately simple 3D paired-agent stress test, each agent follows:

\[
\dot x_i=v_i, \qquad
\dot v_i=-D v_i-K_E(x_i-c_{si})+\omega\,\mathrm{rotate}_{xy}(x_i-c_{si})+
\left(\gamma-\alpha / \|x_{j(i)}-x_i\|^3\right)(x_{j(i)}-x_i)+\epsilon_i.
\]

Here \(j(i)\) is the within-species partner, \(c_{si}\) is an explicitly imposed species/individual environmental target, and \(\epsilon\) is Gaussian acceleration noise (common random numbers across steering candidates). There are no modeled prey capture, resource depletion, interspecific social forces, collision physics, or flight aerodynamics. Thus any species partition is a **property of the stipulated environmental targets**, not empirical competition or an evolved niche.

At the single source-calibration distance \(d_0=10\) m, fix \(\kappa_0=-0.003\;\mathrm{s}^{-2}\) and vary \(\alpha\in\{0,0.5,1.0,1.5,2.0\}\) with \(\gamma=\kappa_0+\alpha/d_0^3\). All five candidates give **exactly the same instantaneous social force when d = 10 m**, yet can diverge as pair distances evolve. These five candidates are an **illustrative discrete subset** of an unbounded algebraic equivalence line; their min/max are not statistical confidence intervals or guaranteed bounds for every admissible rule.

Three worlds are simulated: (i) source pair distance 10 m, spatially overlapping species resource centres and vertically separated resource targets (−8/+8 m); (ii) 25-m source spacing, same resource centres; (iii) 25-m spacing, horizontal centres shifted to (−9/+9 m) and vertical targets compressed to (−4/+4 m). Two species × six agents/species × three paired dyads/species; 10 seeded stochastic worlds per candidate. Euler step 0.1 s, duration 110 s, 25-s burn-in and one recorded state every 0.5 s (170 per agent/seed). Noise/attraction strengths and bins are specified in `validation_v10/niche_identified_set.py`. **Parameters and scenarios were explored in a local pilot for demonstration before this v10 snapshot was fixed: this is not prospective confirmation.**

All recorded positions fall in predefined categorical 3D bins. In the main four-bin-per-axis grain, the x/y cutpoints are −18,0,18 and z cutpoints −12,0,12 m; a seven-bin-per-axis grain is a fixed resolution check. The outermost bin includes all positions beyond its cutpoint, so probability is conserved (rather than dropping tail observations). Equal numbers of records per individual and ten stochastic seeds are used. Random successive records are autocorrelated and **not independent biological replicates**.

## Ecological output definitions

The per-individual realized-use distribution is \(p_{si}(x,y,z)\), and species means are equal-weighted over six synthetic agents. The **between-species** metrics are:

\[
I(S;XY), \qquad I(S;Z\mid XY) = I(S;XYZ) - I(S;XY).
\]

Other outputs are the **within-species** average \(I(i;Z\mid XY,S)\), effective vertical states \(\exp H(Z\mid XY)\), horizontal species Bhattacharyya overlap and total variation of the combined \(p(S,X,Y,Z)\) between pairs of candidate rules. These are descriptions of generated **utilization distributions**, not measures of interspecific competition, habitat suitability or fundamental niches.

### Reproducible numeric result — 10 independent simulation seeds, 5 candidate rules

| World | Grid | I(S;XY), candidate min–max (nats) | I(S;Z\|XY), candidate min–max (nats) | max candidate-pair joint XYZ TV |
|---|---|---:|---:|---:|
| Same resources, initial 10 m | 4×4×4 | 0.00111–0.00142 | 0.57260–0.60517 | 0.02549 |
| Same resources, initial 25 m | 4×4×4 | 0.00064–0.00113 | 0.57168–0.60944 | 0.03917 |
| Reassembled resources, initial 25 m | 4×4×4 | 0.59567–0.65068 | 0.00609–0.01218 | 0.04299 |
| Same resources, initial 10 m | 7×7×7 | 0.00312–0.00500 | 0.52171–0.52650 | 0.02760 |
| Same resources, initial 25 m | 7×7×7 | 0.00334–0.00469 | 0.52898–0.53674 | 0.07686 |
| Reassembled resources, initial 25 m | 7×7×7 | 0.51070–0.52852 | 0.04697–0.05177 | 0.07912 |

In **both grains and all five candidate rules**, the dominant between-species information axis changes from *vertical* to *horizontal* when the artificial resource centres are relocated. The **exact magnitude of information and distribution shape is grain-sensitive**, however. This is a robust conclusion *conditional on this constructed finite simulator*; it does not demonstrate that nature switches niche axes in response to the same perturbation. The six independent stochastic trajectories **per species in each simulation are simulated identities, not independent biological units**.

## Does individual state-use structure predict held-out episodes?

To connect to the question posed by `batter` and `ODSP` without relabeling their evidence, a separate **leave-one-simulation-seed-out** analysis fits \(P_i(z\mid xy)\) from the other seeds and predicts the withheld seed's conditional height state. It compares a self-history model to a pooled conspecific model on **the same target records and same supported x-y cells**, using a fixed pseudocount of 0.5 per z category and requiring five training fixes per x-y cell. Each artificial individual and stochastic seed has equal score weight; no GPS record is used.

| Same θ=α1.0, 4×4×4 grain | Stable z-target assigned to same simulated agent | Reassign z-target between agents independently each seed |
|---|---:|---:|
| Shared resource, initial distance 10 m | **+0.15787** | **−0.06470** |
| Reassembled resource, initial distance 25 m | **+0.15379** | **−0.13083** |

Values are self-minus-pooled **held-out log-score gains in nats/fix**. The observed x-y test-support fractions were ~0.99. In the 7×7×7 grain, the stable and reassigned contrasts likewise had opposite signs. The negative control holds the within-species distribution of z preferences constant while changing which agent label carries each preference from one simulated bout to the next. Thus the experiment demonstrates a **sufficient toy mechanism for repeatable within-species utilization profiles without exclusive spatial partition**, not memory/learning, individual personality, or the exact `batter` *median-centered-height shape* result. Its assigned z targets repeat as two role-based classes per species; the toy does **not** impose six unique continuous individual physiological parameters.

## Three boundaries: model uncertainty, process uncertainty, biological inference

1. **Structural ambiguity:** five distinct \((\alpha,\gamma)\) pairs are source-instantaneously indistinguishable. Taking the min/max of five outcomes measures *finite candidate disagreement*, not full uncertainty in a causal biological parameter or a complete identified set.
2. **Stochastic uncertainty:** stochastic variation among seed replicates is reported separately for each coefficient. Do not describe the candidate min/max as a 95% confidence/prediction interval; there is no empirical sampling model or calibrated coverage statement.
3. **Ecological transport:** this simulation uses short pair episodes and imposed resource centres. It cannot reproduce the ecological data structure in `mina`, the environmentally matched hydrological contrasts in `louis`, the detailed centered vertical-shape estimator in `batter`, or the independent wildlife state-prediction transfers in `ODSP`. Nor can it predict unobserved wild bird or bat niches.

## Relation to the four source repositories

- [batter](https://github.com/zuizui0223/batter): shows repeated individual vertical use despite no obligatory extra spatial segregation in its evaluated fruit bat panels. Here fixed individual/role-level target preferences are **one mathematical sufficient condition** for held-out profile persistence; the cause in batter is unresolved.
- [ODSP](https://github.com/zuizui0223/odsp): distinguishes niche thickness, conditional state organization and independent transfer. v10 reproduces **the definitions and a simulation-seed-heldout scoring architecture**, but not the actual ODSP data, independent site transfers or its frozen inferential endpoints.
- [louis](https://github.com/zuizui0223/louis): highlights environmental-state tracking versus local availability. v10 imposes changed resource centres, **without** simulating matched local availability or claiming buffering results.
- [mina](https://github.com/zuizui0223/mina): uses annual relative breeding-site composition and a fixed-count error null. v10 contains **no nesting counts or demographic time scales**, so breeding contraction must remain a separate module.

## Reproduce this frozen v10 snapshot

```bash
python -m pip install 'numpy>=1.26,<3' 'matplotlib>=3.7,<4'
PYTHONPATH=validation_v10 python -m unittest discover -s validation_v10 -p 'test_*.py' -v
python validation_v10/niche_identified_set.py --seeds 10 --out validation_v10/results/niche_identified_set_v10.json
python validation_v10/profile_transfer.py --seeds 10 --out validation_v10/results/profile_seed_transfer_v10.json
python validation_v10/plot_v10.py
```

Additional GitHub Actions numerical replay separately reproduces each JSON and checks every numeric field against its pinned result with tolerance 1e−9; all code tests are deterministic on synthetic fixtures. See `.github/workflows/niche-identified-set-v10.yml`.

## Scientific decision and next independently testable frontier

**Positive model-theoretic claim:** a partly unidentified local movement rule can generate reproducibly classifiable *dominant dimensions* of multidimensional synthetic utilization, even when its precise spatial probability field varies. A stable, known-in-the-model individual policy can predict a separate stochastic realization; label-reshuffling removes the advantage in this test.

**What remains unestablished:** a physically identified wild Boids law, empirical 3D niche forecast, interspecific competition causing axis switches, behaviorally inferred memory, or cross-taxon universality. The next meaningful external validation needs **multiday/seasonal 3D trajectories, independently characterized measurement errors, measured accessible resources and truly independent held-out individuals/sites**. The v6 and v8 observed neighbor-forecast primary failures stay frozen, not rescued by v10.
