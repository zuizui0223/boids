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

## Phase 3: publisher-source JAR-to-capture decoupling (2026-10-31)

The 2020 *eLife* original Figure 2 outputs have now been re-computed, both receiver models (`n=240` source-output rows each), with 20 model rows per JAR arm × six group sizes. Independent source-sha ledger verification passed; this **is not a MATLAB forward rerun or bat field measurement**.

In the **filter-bank** source:
- JAR decreases published total interference ratio in **6/6** group-size cells.
- Yet it increases original model false-alarm rate in **4/6** cells.
- Mean modeled prey-capture changes have **mixed directions**, average JAR−no-JAR **+0.100** captures per output row across equal group sizes, compared with **−0.058** for the independent correlation receiver family.
- Conditional finite-point-estimate capture×false-alarm Pareto classes are **2 JAR-favourable / 2 no-JAR-favourable / 2 tradeoff**. These have **no source-level statistical support for stable ecological regime boundaries**.
- Under a row-variability audit, the largest absolute capture difference is **less than 0.4 pooled source-output SD**. Do not treat row-level variation as uncertainty across wild bats.

See [complete evidence and publication boundary](SOURCE_JAR_CAPTURE_DECOUPLING_V3.md), [source aggregate ledger](ELIFE_2020_SOURCE_PAYOFF_LEDGER_V1.json) and [exact original-file versus committed-values check](verify_elife_2020_ledger_v1.py). [Original 2020 numerical rerun and exact ledger validation CI](https://github.com/zuizui0223/boids/actions/runs/41191999849), [Pareto descriptive audit](https://github.com/zuizui0223/boids/actions/runs/41191677355), [variation check](https://github.com/zuizui0223/boids/actions/runs/41191875666).

The research question is now **how detector-specific reduction of acoustic overlap translates — or fails to translate — into reliable target detection and capture**, not simply whether spectral JAR exists. Full source-authoritative common-physics comparison with Hase 2026 has **NOT** been achieved. Neither the original 2020 MATLAB simulation nor the full 2026 group simulator has been independently executed.

---



## Phase 4: source-derived vocal control versus receiver time-lag ambiguity (2026-11-02)

**NEW source-constrained SYNTHETIC counterexample — NOT a true 2020/2026 original simulator rerun.**
The 2026 published vocal frequency ODE (tau 200ms, asymmetric C=−4/+20, triangular 3kHz spectral response) is now executable as a deterministic RK4 module in four fixed, invented 3D group contexts (4/8 bats × compact/dispersed). Synthetic 3ms 40kHz **linear** FM sound and a threshold-based receiver proxy evaluate a fixed 0.5 cross-correlation criterion. The simulated JAR raises emitted group mean pairwise frequency gaps **+0.127 to +0.772 kHz**, but source-conditioned max-lag confusable-pair counts remain unchanged in all four test worlds, as do target-proxy outcomes in three of four.

**Mathematical counterexample:** for a simple linear chirp, TF shift `Delta f` can correspond to an echo time lag `Delta t=Delta f*T/B`. With 3ms/40kHz, 3kHz of frequency differentiation gives about 0.225ms time shift (3.86cm of two-way range equivalent). In the actual synthetic calculation, same pair's instantaneous waveform correlation approaches zero, while its best ±0.35ms lagged correlation is **0.840**, above the 2026 paper's 0.5 detection threshold. This is NOT an observed bat location error and NOT a disproof of the actual species-informed 2026 waveform or group-flight results.

**Executable, auditable outputs:** [source-frozen design](COMMON_PHYSICS_PREOUTPUT_CONTRACT_V1.md), [18-test implementation](common_physics_v1.py), [scientific source/boundary memo](COMMON_RECEIVER_SOURCE_BOUNDED_RESULT_V1.md), [permanent aggregate ledger](COMMON_RECEIVER_SYNTHETIC_LEDGER_V1.json) and [independent numeric SHA guard](verify_common_receiver_ledger_v1.py). The entire phase passed [GitHub Actions run 41408077261](https://github.com/zuizui0223/boids/actions/runs/41408077261), including **source Git-blob identity and result ledger match**. Previous 31 standard-library tests run separately without numpy.

**Outstanding blocker:** neither original 2020 MATLAB nor complete 2026 moving-group receiver waveform programme has been independently executed under identical physics. The original 2020 correlation receiver explicitly postulated a ranging-error formula independent of chirp spectral parameters; consequently it cannot validate the new linear-FM frequency-to-lag proxy. A real common-source generality claim requires the exact 2026 species-specific wave shape / receive-window reconstruction, with all endpoints predeclared and no sign-selected sensitivity search.

---


## Phase 5 — source-correct timing, authentic waveform gate, TF-invariant counterexample (2026-11-02)

**Original published supplemental DOCX source identified**, including 2D motion equations, source 5ms integrator pulse input distinct from 3ms actual FM call, gamma IPI mean70ms/SD18.7ms. Corrected v2 fixed 4/8-bat × compact/dispersed × three pre-frozen waveform shapes and source-like reception opportunities. **17/17 code tests passed**. All 12/12 scenarios were independently rerun with **exact, unbinned cross correlations**, preserving the candidate-match JAR effect despite an earlier invalid grid-aligned cache-error fixture (off-grid peak correlation error 0.0643 in 16/63 test cases). [Source-bounded v2 explanation](HASE_WAVEFORM_CURVATURE_SOURCE_BOUNDED_RESULT_V2.md) · [12-scenario exact ledger](HASE_2026_SOURCE_TIMING_WAVEFORM_EXACT_LEDGER_V2.json) · [exact verification CI](https://github.com/zuizui0223/boids/actions/runs/41410719843).

**Published same-species source admission:** Hase et al. 2018 `10.1038/s42003-018-0045-3` reports an approx 1kHz terminal-frequency shift giving half the original bat-like call waveform correlation. Dryad `10.5061/dryad.4f99c46` has catalogued CC0 `SoundFile.zip` **614,454,096 B**, provider MD5 `c6651cc04aefbdaf0cce77b184b8a8c9`; actual original-audio GET is **HTTP401**, so *no source audio/real FM waveform was recovered*. [Original provider admission log](https://github.com/zuizui0223/boids/actions/runs/41411436841).

**6 pre-frozen benchmark conditions** crossed three synthetic curvatures `p=1,.6,2` with **fixed initial frequency** vs **fixed 40kHz bandwidth** during a terminal-frequency change. The approximate max-lag normalized cross-correlation halfwidths (kHz) are:
- Fixed initial 90kHz: `p=1:2.03`, `p=.6:5.95`, `p=2:.72`.
- Fixed bandwidth 40kHz: `p=1: no halfwidth within 6kHz`, `p=.6:2.84`, `p=2:.94`.
- Eight pure code tests and **6/6 exact input/source SHA and output-ledger verification passed**: [CI run](https://github.com/zuizui0223/boids/actions/runs/41412310099). The p=2 approximate similarity to published 2018 ~1kHz is NOT evidence of true pulse `p=2` or independent validation.

**Science/novelty gate:** A terminal-frequency shift is an *incomplete intervention definition* unless the starting frequency, sweep bandwidth and receiver timing rule are fixed. That is an important model-identifiability counterexample, but **acoustic discrimination and TF adjustments in bats are established prior art**, and authentic 2018 sounds/full 2026 simulator were not admitted. No new bat ecology law, prey captures, or fitness benefit is established. See [complete source and claim-decision note](TF_INVARIANT_SOURCE_GATE_AND_NOVELTY_DECISION_V1.md). Keep PR Draft and all `batter` frozen manuscripts unchanged.

---


## Phase 6 — original IF/TF response constrains the acoustic intervention (2026-11-05)

**New animal measurements: 0. Secondary published source, original Hase 2026 Figshare acoustic call records.** The previously unresolved question `when TF changes, is initial emitted frequency or chirp bandwidth fixed?` has now been analysed using original published *paired-source-field* IF and TF on the same source calls, and then stress-tested with three predeclared (but post-full-outcome) source-relative time windows.

- Original CSV: **12,308 rows**, original source SHA256 pinned; **11 unique bat ID labels** across all three source experiments, **seven** bats per experiment and **35** eligible bat×condition means per experiment. Original cohort pairwise overlaps 4/5/5.
- Model comparison (fixed-IF `ΔIF=0` vs fixed-bandwidth `ΔIF=ΔTF`, equal-bat mean absolute error): low-TF IPI 3.170 vs 2.941 kHz, 5/7 bats prefer fixed-B but 95% bat bootstrap includes zero; high-TF IPI 2.774 vs 2.901, 7/7 prefer fixed-IF but TF's mean change is only **−0.056kHz** and model-score gain is tiny compared with error; low-TF SPL 3.985 vs 3.415, 7/7 prefer fixed-B in the full source.
- **Critical source confounding:** **all 105 source ON/OFF subcontexts are chronologically disjoint with OFF entirely before ON**. In the strict ±1-second comparison, SPLlow fixed-B preference drops from 7/7 to 5/7 and its D interval crosses zero. Thus there is **no justified universal bat spectral-coupling policy**. All time policies, mean/median sensitivities and source biological support are shown; they are NOT independent replications.
- **Fresh publisher-source replay verification:** re-downloaded original authenticated Figshare data, reanalysed main + three time windows with both summary rules, and matched **all 24** stored scientific ledger cells exactly, 11 source bat IDs, 105 chronological source contexts and original script/contract Git blob hashes. [Ledger CI](https://github.com/zuizui0223/boids/actions/runs/41924313188).
- [Main scientific conclusion, alternative explanations and source limits](PUBLISHED_BAT_IF_TF_PHYSICAL_MODEL_RESULT_2026_11_05.md) · [original-source aggregate ledger](IF_TF_SOURCE_TIME_PHYSICAL_CONVENTION_LEDGER_V1.json) · [verifier](verify_IF_TF_source_time_ledger_v1.py).
- [Original IF/TF source reanalysis 14 tests](https://github.com/zuizui0223/boids/actions/runs/41922688245) · [source chronology and cohort audit](https://github.com/zuizui0223/boids/actions/runs/41923195416) · [three time-window diagnostic 7 tests](https://github.com/zuizui0223/boids/actions/runs/41923633026).

**Editorial decision:** This settles the source-admissible secondary physical-convention test, but it does NOT explain JAR prey capture, identify neural motor control, or validate the entire 2026 2D group sonar simulator. Real recordings/spectrotemporal source waveforms and independently tested receiver/capture outcomes are still missing for mechanistic generality. Keep PR #36 Draft, do not relabel prior published TF/IF effects as a new bat ecological discovery, and do not alter `batter` frozen manuscripts.

---
