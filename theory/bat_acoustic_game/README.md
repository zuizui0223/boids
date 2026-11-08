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


## Phase 7 — bat unknown-individual IF prediction and matched single-donor test (2026-11-05)

**No new animal observations. Original Hase 2026 IF/TF published source, one 11-bat cohort.** In a source-bat×stimulus double holdout, original 2026 low-TF/interval start-frequency ΔIF (NOT the published article's terminal TF target) did **not** transfer: on each unknown bat × original withheld stimulus level, a linear stimulus model had **MAE 3.677 kHz**, versus **MAE 3.291 kHz** for a constant learned only from the other bats. Original 7/7 biological source bats worsen; **18 of 24** heavily reused window/median/experiment result cells show stimulus-linear worse. **These 24 are not independent experimental replicates**. [Frozen result and no-novelty decision](NO_NEW_MEASUREMENT_BAT_PREDICTIVE_CEILING_AND_DECISION_2026_11_05.md) · [24-group, 120-model pinned evidence](BAT_DOUBLE_HOLDOUT_IF_SOURCE_RESULTS_LEDGER_V1.json) · [fresh-source SHA/ledger check](https://github.com/zuizui0223/boids/actions/runs/41958144552).

An **equal-training-information test** uses the focal bat's four OTHER experimental stimulus levels vs each of six donor bats' four OTHER levels; these are *not earlier historical days or source time-series history*. In original low-TF/interval full source, own-bat constant MAE **3.408** vs mean single-donor error **4.016** (5/7 bats better, source bootstrap difference CI includes 0). In the other two stimulus experiments the sign reverses. Fitting a personal linear dose-response instead of a personal constant increases mean error in **24/24 reused analysis cells**, not 24 independent studies. [Matched-four pre-response plan](SELF_VS_DONOR_EQUAL_FOUR_CONDITIONS_PREOUTPUT_V1.md), [source results](BAT_SELF_VS_DONOR_SOURCE_EQUAL_TRAINING_LEDGER_V1.json), [24-group/96-model original source numeric replay CI](https://github.com/zuizui0223/boids/actions/runs/41959659455).

**External archive source gates also tested:** [2015 Pipistrellus original Dryad CC0](https://github.com/zuizui0223/boids/actions/runs/41958348509) lists `Dryad.xlsx` 1,810,012B with verifiable provider MD5, but original file download returned HTTP401; [2025 Rhinopoma original Mendeley CC BY4.0](https://github.com/zuizui0223/boids/actions/runs/41958645979) lists movement+audio and original code, but the public metadata APIs returned HTTP401/404. No original alternative species/3D acoustic data was read in this environment.

**Scientific decision:** This specific 2026 source cannot establish a bat-wide learned sonar strategy, functional prey-capture advantage, or a 3D acoustic-niche mechanism. The 2026 original terminal-frequency control result remains established. Further refitting of its initial-frequency source should STOP without independent, source-admitted biological animals and a true receiver/foraging endpoint. Keep PR #36 Draft and frozen `batter` JAE/BE unchanged.

---

## Phase 8 — within-bat capture-success decline at high call density (2026-11-07)

**Existing original PNAS 2024 source only; new animal observations 0.** The source 2024 authors already showed lower prey-capture success under high conspecific-call density using bat random effects. The narrow follow-on question was whether our source-heldout model's high-density **22.6 predicted versus 10 observed successes given 36 real attempts** might be entirely a between-bat composition artifact. We froze a direct within-bat contrast and original-flight thirds before opening bat-specific source outcomes.

- Original 10 bats × **4299 observed 5-second rows**, public original XLSX SHA256 `92acbc36cce42028bfd5a07ad1ec8aa8062121575d6d665dc7392b47222f562d`, 112 high-source-call windows (≥76 calls/5s) from eight original bats. **Six** bats made source high-density attacks and source 26–75-call moderate attacks.
- In those same six biological source bats, high-density **10/36 (27.8%)** vs moderate **119/173 (68.8%)** attacks succeeded. Equal-bat difference high-minus-moderate **−40.2 percentage points**, descriptive bat-bootstrap 95% [−54.4, −21.2], 5 bats lower, one tied. Source bat-stratified success odds ratio **0.159**. Original probability calculated conditional on within-bat attack/success totals **8.8×10⁻⁶** under an exchangeability model; this is **not a randomized causal p-value** and may be influenced by original source serial dependence.
- Pre-fixed **within-bat × flight-third** grouping retained six source bats, nine source strata and **all 36 high-call attacks**; conditional lower-tail allocation benchmark **0.00498**. Coarse flight-time control does NOT remove insect/prey density, animal state, source selection into attack or sonar-receiver uncertainty.
- Excluding original source bat with 7 gaps in `sec_group` leaves exactly the same six attack-eligible bats (not a separate replication). The first V1 inflated `numel_5swindows` exposure remains INVALID; all analyses retain E=one actual source 5-second group row.
- This result **does not rescue** original bat-leaveout model prediction (M1/M2 worse than a source density-blind model on source bat-equal primary Poisson deviance), and it overlaps the source authors' prior GLMM. It is a reproducible small-n within-bat and within-flight support check, **not** a new general bat sonic interference mechanism.

Evidence: [frozen observational plan](MOLOSSUS_WITHIN_BAT_HIGH_DENSITY_PREOUTPUT_2026_11_07.md), [full source result](MOLOSSUS_WITHIN_BAT_HIGH_DENSITY_SOURCE_RESULT_2026_11_07.md), [original source aggregate ledger](MOLOSSUS_WITHIN_BAT_HIGH_DENSITY_SOURCE_LEDGER_V1.json), [source test run](https://github.com/zuizui0223/boids/actions/runs/42333699222), [fresh-source SHA and whole-ledger replay CI](https://github.com/zuizui0223/boids/actions/runs/42334035042). PR remains Draft; `batter` frozen manuscripts unchanged.

---


## Phase 9 — independently published bat source and task-conditioned echo memory (2026-11-07)

**No new bat measurements. All actual independent-source and original-code checks verified; no causal acoustic-prey mechanism claimed.** Rather than optimize increasingly complex source-reused *Molossus* models, an independent original bat audio/movement source admission was executed: 2025 *Goldshtein* PNAS `10.1073/pnas.2407810122` Europe PMC appendix includes PDF+video+figures but **no original machine-readable synchronized acoustic/flight dataset**, and the 2021 *Gilmour* JEB `10.1242/jeb.242715` supplemental package likewise includes only PDF/images. Original Mendeley data bytes remain unadmitted due earlier API 401/404. [Original-public-source admission CI](https://github.com/zuizui0223/boids/actions/runs/42338871309) (6 tests).

New independently published **Mazar & Yovel 2026 eLife** `10.7554/eLife.105571` authentic open MIT MATLAB code was found. All seven original source files, two species-specific parameter workbooks, cave exit decisions and a simulation MAT struct were verified with GitHub original commit `a74fb61a8efb57ca37693893c3bd7b35fa94fa89`. The authors ALREADY demonstrated multi-echo memory and rapid obstacle steering under dense bat masking; source scripts have hard-coded Windows paths / MATLAB GUI, so **the original figures and source solver have NOT been rerun**. [Upstream original-code architecture and seven blob verification CI](https://github.com/zuizui0223/boids/actions/runs/42339355443).

**Source-motivated exact filtering model (generic mathematics, not bat data):** with target drift per call `q`, measurement error `r`, K accepted echoes averaged to estimate current target position,
`MSE(K)=r/K + q*(K-1)*(2K-1)/(6*K)`. For K=5 vs K=1, more memory improves *conditional* localization accuracy only if `q/r<2/3` assuming all original echoes available. Seven q/r conditions × ten source-independent K settings, **70** analytical cells plus 40,000 synthetic histories per q/r, all 12 test cases passed, maximum Monte Carlo relative disagreement 2.01%. [Source-motivated 70-cell original CI](https://github.com/zuizui0223/boids/actions/runs/42339580008).

Under independent lost-echo availability `p`, exact enumeration of every usable echo subset for four p values × six q/r values × ten K yields **240** analytic conditions. No-echo probability `(1-p)^K` is kept separate from error **conditional on at least one echo**. For K=5, break-even `q/r` where memory still improves conditional accuracy declines from 0.667 (p=1) to 0.547 (p=.75), 0.354 (p=.5) and 0.153 (p=.25). This conditional threshold is a post-output algebraic consequence of the fixed model, **not an estimated or new empirical bat threshold**. At p=.25, K=5 lowers probability all echoes are missing to 23.73% versus 75% with K=1, but old target location samples can worsen conditional accuracy on fast-moving prey. [240-cell exact ensemble CI](https://github.com/zuizui0223/boids/actions/runs/42339782477). [Combined 310-cell full source/contract SHA and numeric CI](https://github.com/zuizui0223/boids/actions/runs/42340082179).

**Scientific decision / stop:** [complete task-dependent sensory-memory evidence and publication memo](BAT_SENSORY_MEMORY_TASK_DEPENDENCE_EVIDENCE_DECISION_2026_11_07.md), [permanent 310-cell ledger](BAT_ECHO_MEMORY_TASK_CONDITIONED_THEORY_LEDGER_V1.json), [source frozen source audit](MAZAR_2026_SOURCE_AUTHENTICITY_AND_BOIDS_BRIDGE_V1.md). No natural bat q/r or usable-echo probability p recovered, no moving prey echo-target synchronized raw data admitted, and the original *Molossus* 2024 high-density observed attack success decline is PRIOR ART not explained causally by these uncalibrated equations. Consequently do NOT claim a newly demonstrated individual ecological strategy or submit a third bat paper. Keep PR #36 Draft and original `batter` JAE/BE frozen.

---


## Phase 10 — original 2026 source completeness & available-helper semantics (2026-11-08)

**New observations 0.** Previous Phase 9 Gaussian echo-memory 310-cell theory remains independently verified but **NOT** the actual published Mazar & Yovel 2026 source model. We investigated whether the originally published code could support a complete source-authentic cross-species cave-exit replay.

- **Original source reproduction hard blocker confirmed in BOTH author archives:** pinned original GitHub MIT `omermazar/Colony-Exit-Bat-Simulation` commit `a74fb61a8efb57ca37693893c3bd7b35fa94fa89` and original source Zenodo DOI `10.5281/zenodo.16992617` 6,853,824B archive (all 268 archive members). Original `BatFlightForGui.m` requires **`BatManueverDecision_FullConfusion_ver08Aug24`** when clustering flag is TRUE; the function is **absent in both source archives**. The corresponding confusion-workbook `ObsClusterFlag=1`; the source Confusion experiment script separately sets `ObsMemorySize=10`, while the README default was 5, and sets `ObsRepeationsFlag=0`. Distinct existing non-cluster fallback is not the original clustered treatment. [Official source/Zenodo original SHA and parameter audit, 6 tests](https://github.com/zuizui0223/boids/actions/runs/42436920370).
- **Author's AVAILABLE helper is order-dependent (source microbenchmark, not published simulation):** source `distanceTHClustering.m` greedily associates only direct neighbors with first unused seed; identical ten synthetic echo points and 6 orders yield source-cluster acceptance **2/6**, while an explicitly non-source transitive graph comparator accepts **6/6**. [Fixed test CI 10/10](https://github.com/zuizui0223/boids/actions/runs/42437209144).
- **Original available helper counts echo points vs independent contributing calls:** source `findRepeatedClusters.m` threshold `10 relevant calls × 0.22=2.2`, but accepts cluster by spatial POINT count. Two synthetic datasets with same 10 emitted calls and same 12 2D echo points, but three close returns in 1 call vs spread over 3 calls, are **both accepted by the source helper**. Different *not-source* call-recurrence test accepts only the 3-call case. [Fixed test CI 7/7](https://github.com/zuizui0223/boids/actions/runs/42437369087).
- **Source experimental lineage caveat:** separate existing `BatManueverDecisionXXX.m` references the repeated-cluster helper only when `ObsRepeationsFlag=1`, but the real original Confusion experiment sets it to zero; it cannot be silently renamed and presented as the absent published main cluster code.
- [Scientific prior-art/reproducibility decision note](MAZAR_2026_ORIGINAL_CLUSTERING_SOURCE_AUDIT_RESULT_2026_11_08.md) · [permanent source/code-SHA and exact result ledger](MAZAR_2026_CLUSTERING_SOURCE_AUTHORITY_LEDGER_2026_11_08.json) · [full frozen-source and two microbenchmark numerical verification CI](https://github.com/zuizui0223/boids/actions/runs/42437558093).

**Scientific STOP:** Original Mazar/Yovel 2026 already demonstrated cave-exit benefit of multi-call integration and spatial clustering. The actual published clustered-branch source is unavailable in both official archives; available-helper synthetic failure modes do NOT prove original reported figures wrong or any bat biological behavior. Further source-equivalent ecological simulation requires an authentic missing function (or author-confirmed equivalent), a runnable MATLAB environment and novel untouched obstacle/target tasks. Keep this PR Draft, no original `batter` paper changes, no reproduction or submission claim.

---

## Phase 11 — original 2026 bat3d code and 28 saved results verified (2026-11-08)

**No new animal experiments or measurements.** Original Steckel 2026 self-supervised virtual 3D echolocation study, preprint `10.64898/2026.10.22.760884`, original Zenodo `10.5281/zenodo.23537553`, was accessed via original **HTTP206 byte ranges** instead of downloading its entire 988,293,611-byte ZIP. Original author `code.zip` (11,212,647B, SHA256 `a5b951abf5cda1ebe2e783c06d193fd9a09cb3fc36c02a265dcc7ac72bab7ae8`), `experiments.json` and `source_data/run_table.json` (original SHA256 `42148acb514b7bb89ab77bc7815951582b32551e54da61885c81803982d30681`) were verified without uploading original code/raw virtual samples or any external HRTF MAT.

**28/28 original published virtual-agent source runs matched** by normalizing original Windows path metadata to archived run directory names. Every author `az`, `el`, `gc`, source evaluation `n`, training `step` and available source correctness/correlation metrics was preserved. [Full permanent 28-run source metric ledger](STECKEL_2026_ORIGINAL_28_RUN_SOURCE_NUMERIC_LEDGER_V1.json) · [independent publisher SHA and author 28-run values replay CI](https://github.com/zuizui0223/boids/actions/runs/42446672218). This is **author prior-art result reproduction, not trained-model execution**.

The published source model exhibits **axis-specific** 3D observability of bat-like sensor movement: main E1 `az=2.510, el=2.788`, shuffled own motion C1 `az=12.445, el=23.245`, two-call time shift C3 `az=9.497, el=15.264`; E7 pan-only `az=2.367, el=14.718` versus pan+tilt `az=2.494, el=2.479` (~5.94x vertical error). Source n is ~3972-3999 simulated evaluation examples, NOT distinct real bats. Original published memory controls also exhibit nonmonotonic saved error: `el_N64=2.788`, `el_N256=2.943`, `el_N512=2.564` (and n/training steps may differ). **The authors already studied these motions and ablations.** [Original source and inference report](STECKEL_2026_ORIGINAL_3D_AXIS_OBSERVABILITY_RESULTS_2026_11_08.md).

**Actual original author's source Python code RUNNABILITY now verified:** source pyproject requires torch>=2.1, numpy, scipy, matplotlib and tensorboard; all **29** original bat3d/ and tests/ Python source files compiled. On a CPU-only Python3.11 runner with torch2.6.0+cpu, numpy2.2.6/scipy1.15.3/matplotlib3.10.7/pytest8.4.2, three original untouched author geometry/motion/warp/head-axis test modules yielded **15 passed / 4 skipped / 0 failed (19 collected cases; 16 test functions)**. All four skips are original tests explicitly marked **needs CUDA**, not scientific failures. This runs authentic original spatial-transformation/kinematics source functions but **does not retrain the original model, regenerate source figures or admit any real bat behavior**. [CPU source tests + skip reasons CI](https://github.com/zuizui0223/boids/actions/runs/42447087638) · [permanent full authority/result/test ledger](STECKEL_2026_ORIGINAL_GEOMETRY_CPU_TEST_AND_28RUN_SOURCE_LEDGER_V1.json).

**Next actual distinct science goal (not yet tested)**: with original code now executable, prospectively define an *unseen* geometry × sensor-excitation intervention beyond author E1–E9/C1–C5, comparing an az/el-specific holdout predictor to author source controls at common training/checkpoint/evaluation scenes. Need original code's simulator/evaluator and source-authorized compatible HRTF and weights before claiming a source-authentic new model result. The source 2026 Teshima `10.1098/rspb.2026.1463` already studied flight policy transfer across two real bat species and seven arenas; merely learning a 3D movement rule is prior art.

**Decision**: original evaluation and source-code CPU infrastructure complete. No original or new biological bat ecological law, prey capture, or species-general inference from this simulated material. Keep PR #36 Draft, no merge or changes to frozen `batter` JAE/BE manuscripts.

---
