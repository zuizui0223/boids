# Bat-only sonar strategy selection — without new measurements

**2026-10-31 / SYNTHETIC TESTBED, NOT A NEW EMPIRICAL BAT RESULT.**

This branch contains a self-contained, **Python standard-library only** model. Nothing here was fitted to raw bat calls, 3D flight tracks, prey captures or source species; no new measurements or animal experiments are required or authorized. Do not merge claims into frozen `batter` JAE v0.4.0, integrated bat PR #99 or existing `boids` observational endpoints.

## The question that could be new

> Under what **resource contestability × acoustic interference × value of conspecific information × 3D movement opportunity** conditions should an echolocating bat use another bat's calls, time-shift its own calls, move to another 3D route, or acoustically interfere with a rival?

Do **not** claim to discover these actions individually. Prior art already established public acoustic information and mobile sensory networks, non-monotone effects of conspecific density, active competitive jamming, spatial spreading during dense emergence, and self-organized spectral frequency differentiation.

## Explicit source-independent toy assumptions

Two bats each choose:
- EMIT: standard active sensing;
- STAGGER: altered pulse timing, less masking with a loss of own temporal sensing;
- LISTEN: reduced emission, stronger response to publicly available signals;
- JAM: antagonistic emission that decreases the rival's signal detection;
- DETOUR: use an alternate 3D path at resource/cost penalty, only when routes>=2.

Detection probability for bat i is:

```
p_i = logistic(base - self_cost_i +
    1[colocated] * (B * receptivity_i * public_signal_j
                  - M * vulnerability_i * emission_j
                  - J * 1[j=JAM]))
```

The **assumed** reward at a shared prey patch is

```
U_i = (1-C)*p_i + C*2*p_i^2/(p_i+p_j) - acoustic_cost_i.
```

When detouring, own payoff is `detour_quality*p_i - detour_cost`, with all pair terms suppressed. These functional forms are illustrative; `C` is a dimensionless prey-contestability **assumption**, not a measured bat social condition. A finite strategic game has mixed equilibria even if pure equilibria are absent. We report pure equilibria and a damped **logit-response heuristic**, not biological strategy proportions or a proof of evolutionary equilibrium. This toy model has no acoustic wave propagation, 3D trajectories, frequency physics or actual bat prey dynamics.

## Reproducible toy output

Using the arbitrary constants declared in the source and `beta=8`:

| Synthetic setting | Pure equilibrium combinations | Logit response |
|---|---|---|
| Strong masking; no public information; 1 route | STAGGER / STAGGER | alternative route unavailable |
| Strong masking; no public information; 4 routes | EMIT / DETOUR (or reverse) | p(DETOUR)=0.300 |
| Strong masking; useful public information; 4 routes | EMIT / LISTEN (or reverse) | p(DETOUR)=0.185 |
| Low masking, little resource contestability | EMIT / EMIT | p(JAM)=0.141 |
| Low masking, strongly contested patch, stronger jammer | **no pure equilibrium** in this toy | p(JAM)=0.362 |

**Pairwise analytic boundary:** against an ordinary emitter, for `B=.2,M=.2,J=3`, the illustrative `JAM` versus `EMIT` payoff equality is `C*=0.2589663969`. This does not make jam optimal against all five actions or biologically predict a bat species' behavior.

**Sensitivity:** in 27/27 modest toy parameter sets varying route quality/cost and logit beta, increasing `B:0→1` reduced simulated detour propensity under strong masking (changes -0.1774 to -0.0458). In 27/27 sets varying jammer strength, route quality and beta, increasing `C:0→.9` increased simulated jamming propensity (+0.0819 to +0.3190). All those signs depend on the **same core utility specification**; they do not constitute empirical evidence or broad model-structure robustness.

## Run (no third-party package or original movement files)

```bash
cd theory/bat_acoustic_game
python -m unittest discover -p "test_model_v1.py" -v
python bat_acoustic_game.py > results.json
python sweep_v1.py > sweep_results.json
```

The model itself labels its outputs `SYNTHETIC_ONLY_NOT_FITTED` / `SYNTHETIC_ONLY_NOT_EMPIRICAL`. The test suite checks explicit utility properties, equilibrium best responses, analytic indifference, convergence from multiple initial states and the bounded parameter sweep. The independent Actions workflow is `.github/workflows/bat-acoustic-game-v1.yml`.

## The actual zero-new-measurements science opportunity

**Most important literature tension:** Mazar & Yovel's 2020 *eLife* sensorimotor simulation found that additional *spectral jamming-avoidance shifts* did not improve foraging prey capture, whereas the 2026 *Proceedings B* model reports reduced **potential acoustic misdetections** from self-organized spectral differences. Those are **different biological endpoints** (capture versus detection) and different biological tasks/assumptions; do not declare a contradiction without source-code audit.

- Mazar & Yovel (2020), eLife, DOI https://doi.org/10.7554/eLife.55539 — published MATLAB model and numeric supplements exist on article page.
- *Self-organized spectral adjustment in echolocation sounds within group-flying bats* (2026), PMID https://pubmed.ncbi.nlm.nih.gov/42869478 — code/raw numerical availability must be checked before claiming reproducibility.
- Krivoruchko et al. (2024), PNAS, https://doi.org/10.1073/pnas.2321724121 — real field bat social information gives advantage at some densities and disadvantage at high densities; that non-monotonicity is not original here.
- Roeleke et al. (2022), https://pmc.ncbi.nlm.nih.gov/articles/PMC9388074/ — mobile echolocation sensory networks modeled previously.
- Corcoran & Conner (2014), Science, https://doi.org/10.1126/science.1259512 — active competitive sonar jamming already measured.
- Goldshtein et al. (2025), https://pmc.ncbi.nlm.nih.gov/articles/PMC12002023/ — dense emerging bats experience masking and spatial spreading, combining tracking and onboard acoustic measures.

**Next reproducible study requiring no original fieldwork:**
1. Reproduce the original 2020 acoustic physics + predator-prey model from source code and source numeric outputs; audit source model licensing and MATLAB dependencies.
2. Establish whether 2026 model/code support re-running without new sound recordings; separately code target detection, misdetection, and eventual prey capture as distinct endpoints.
3. Freeze a **common counterfactual**: the same simulated bat population and fixed signal physics, with/without adjustment, at fixed resource contestability, route availability and receiver error. Test which source-model assumptions flip the predicted advantage. Do **not** tune against both papers' response signs and call it external confirmation.
4. Only when model assumptions are independently bounded, evaluate whether a unified bat-specific regime boundary is defensible; otherwise report non-identifiability and retain this as a model demonstration.

No existing `batter` lab-to-wild causal bridge is rescued by this toy. Its frozen field bridge previously failed the prespecified overall rule. The appropriate scientific conclusion today is **model constructed, computationally tested, ecological mechanism not validated**.


## Phase 2: existing published data and endpoint bridge (2026-10-31)

The original 2020 MATLAB archive and 2026 Figshare original source inventory are now **verified accessible** through a non-executing GitHub Actions source gate. The native **2020 predator-prey model has not been numerically rerun** and the 2026 full group-flight misdetection model has not been independently reconstructed.

Using **only** Hase et al. 2026 already-published lab data, a locked secondary reanalysis from `Data_jamming.csv` (12,308 rows, 11 source animal-ID labels across original experiments) found:
- IPIlow: **7/7 individual slopes negative**, equal-bat mean -1.0060 native TF/log10(ms), 95% whole-bat bootstrap [-1.4669,-0.7013], descriptive source sign p=0.0078125. ON/OFF mean instead of median retains 7/7 negative.
- IPIhigh: 7 bats, 4 negative/3 positive, whole-bat CI overlaps zero; changing ON/OFF median to mean produces 2 negative/5 positive. **No stable signed claim.**
- SPLlow: 7/7 positive, equal-bat mean +0.04756 native TF/dB, mean sensitivity retains 7/7.
- Only **4** original bat IDs have both high- and low-IPI slope support; do not treat 7+7 as 14 independent same-system bats.

A separate analytical renewal-reward model derives when reducing **potential** acoustic misdetections translates into extra captures, and shows **opposite group-size threshold orderings** under fixed workload versus fixed per-event false-alarm cost. Neither the false-event cost nor task detection penalty is observed.

**Evidence and decision note:** [SOURCE_HARMONIZATION_AND_ENDPOINT_BOUNDARY_V2.md](SOURCE_HARMONIZATION_AND_ENDPOINT_BOUNDARY_V2.md) · [source-result aggregate](SOURCE_BOUND_RESULTS_LEDGER_V1.json) · [source reanalysis code](published_jamming_response_v1.py) · [endpoint bridge](endpoint_bridge_v2.py).

**Execution receipts:** [2020+2026 published archive structural audit](https://github.com/zuizui0223/boids/actions/runs/41190038624), [outcome-blind source-availability gate](https://github.com/zuizui0223/boids/actions/runs/41190147131), [2026 original source reanalysis](https://github.com/zuizui0223/boids/actions/runs/41190407233), and [31-test synthetic/analytical validation](https://github.com/zuizui0223/boids/actions/runs/41190502673).

These are **source-consistent reanalyses and conditional mathematics**, not original ecological bat experiments, no source 2020/2026 full-model replication, and no new universal bat sensory strategy.
