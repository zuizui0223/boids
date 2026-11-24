# v21 — Acoustic-direction observability gate: amplitude-only Boids is not a fish auditory mechanism

**2026-11-22 JST — source-grounded methodological audit + analytic constructed counterexample. NOT a new field-fish result.** The existing v20 synthetic outcomes and PR #248 Draft status are unchanged.

## 1. The specific mismatch in the current v20 operator

The current fish simulator `validation_fish_boids_v20/two_pathway_simulation.py` computes a vocal audibility scalar `perceived=(hearing_call @ calling)/(n/4)` from exponentially attenuated **known true caller positions**. It independently steers `toward_callers` using the true agent-to-agent displacement vector `diff` and known true binary caller states. This is a valid **oracle-equipped ABM**, but it does **not** reconstruct directional hearing from actual pressure/particle-motion measurements or from receiver intensities.

The model's sound-guided steering is therefore not yet a field-calibrated fish auditory policy. Its v20 acoustic-motor and vocal-hearing parameter interactions remain valid *for the defined artificial model* and should not be revised retrospectively. An observer with only scalar acoustic energy cannot assume the `toward_callers` direction vector is observable.

## 2. Independent published biological boundary

Veith et al. (2024), *The mechanism for directional hearing in fish*, Nature 631:118–124, DOI [10.1038/s41586-024-07507-9](https://doi.org/10.1038/s41586-024-07507-9), experimentally decoupled sound pressure and particle motion in **single** *Danionella cerebrum* during triggered sound playback. Original paper: 65 intact fish, 3,798 playbacks, including 1,415 startles; ~80% directional escapes away from a single-speaker condition (pooled 240 startles from 63 fish), while the manipulated pressure/particle-motion relationship could reverse the response direction (~67% approaches, 331 startles from 61 fish in the paper's trick condition). Pressure-only and particle-motion-only stimuli did not show the same significant directional bias in the reported experimental contrast. These are **authors' previously published results**, not effect sizes re-estimated in Boids. Repeated startles are not independent fish.

The authors deposited fish trajectories at [GIN/G-Node](https://gin.g-node.org/danionella/Veith_et_al_2024) and behavioral reproduction code at [danionella/veith_et_al_2024](https://github.com/danionella/veith_et_al_2024), including `figure_1_2`. The original GIN bytes and field-level schema have **not** been admitted or read by this v21 audit; no original fish heldout model has been fitted.

**Crucial non-equivalence:** experimentally evoked escape by isolated *D. cerebrum* is neither a social contact-call response nor a school chorus. It establishes the plausibility and context-dependence of an auditory motor **component**, not school-level acoustic feedback.

## 3. Exact observability counterexample, not a biological fit

For complex harmonic sound-pressure `P` and axial particle-velocity `U`, an illustrative phase-blind representation is

`S(P,U) = (|P|², |U|²)`.

A phase-sensitive axial cross term, **a physical proxy rather than a fitted sensory rule**, is `C(P,U) = Re(P * conj(U))`. Consider two matched stimuli `(P,U)` and `(P,-U)`:

- `S(P,U) = S(P,-U)` exactly, so any policy depending only on **these two amplitude values** must give identical predictions to both.
- `C(P,-U) = -C(P,U)` exactly. In a constructed balanced classification with target `sign(C)`, the two stimuli have opposite labels.
- Therefore, for equally weighted matched cases, **any amplitude-only classifier has maximum accuracy 1/2**, while a phase-aware classifier achieves 1 in this deliberately constructed target. This is a logical prediction limit for the constructed labels, **not** a 50% observed fish accuracy, not a new causal result, and not an assertion that fish compute this exact cross term.

In actual acoustics, `Re(P conj(U))` is related to **active axial acoustic intensity**, which is directional; do not call it invariant scalar intensity. Only amplitude/power-like phase-blind summaries are invariant in this contrast. Also, an acoustic propagation model or multi-receiver localization may recover direction by other means; this counterexample does not rule out all scalar-plus-geometry estimators.

## 4. Executed known-truth fixture (no biological observations)

The dependency-free `validation_fish_boids_v21/phase_counterexample.py` generated 1,000 paired synthetic harmonic fields (2,000 constructed cases), with pressure and velocity magnitudes equal within each polarity pair and the relative phase inverted. All 1,000 pairs had identical amplitude signatures and reversed signed cross terms. Balanced amplitude-only accuracy bound **0.500**, constructed phase-aware target accuracy **1.000**. Local `python -m unittest discover -s validation_fish_boids_v21 -p 'test_*.py' -v` passed **6/6** offline tests. These are mathematical/implementation checks, not real fish movement measurements.

## 5. New analysis admission hierarchy (freeze before obtaining source numeric outcomes)

1. **A — audio→individual motor response**: from the original Veith GIN files, require exact original checksum, source version/license, fish identity, track timestamp, playback clock, sound condition (including relative pressure/particle-motion polarity), and a nonfuture-dependent pre/post turn definition. If inaccessible or key mappings unknown: `SOURCE_NOT_ADMITTED` and no scores. Verify trial inclusion before opening response values.
2. **B — independent whole-fish prediction**: only after A passes, freeze complete-fish heldout folds. Compare M0 prior velocity/heading, M1 M0 + scalar pressure/particle-motion amplitudes, M2 M1 + relative phase/known calibrated stimulus orientation. Score future turn vector or sign on identical events; cluster uncertainty by fish, not startle events. Include non-startle trials and habituation, sound-condition balance, and pre-stimulus response/placebo control. No tuning on test fish.
3. **C — school sound→movement→calls feedback**: requires *within the same school and episode* time-registered individual XY(T), fish-origin call events or attributed sources, calibrated sound field, cue/quiet interventions and absent-call intervals. Neither Veith (single-fish stimulus), original Puy locomotion-only recordings, nor the Mouy short edited audio-video examples independently satisfy C. Separate cohorts cannot be stitched into a synchronized school.
4. **Cross-species synthesis**: van Oosterom et al. (2016) bigeye playback/cohesion evidence is an established social response (24 fish × 4 shoals, seven on/off cycles) but no analysis-ready individual synchronized trajectories have been admitted; it does not replace a level-C dataset. Distinguish literature-confirmed sound→behavior from a newly estimated feedback effect.

**Decision:** keep PR #248 Draft, no main merge and no new claims about fish social-feedback mechanism. The immediate defensible result is a **model observation gap**, not another positive v20 seed experiment. Next empirical step is to source-admit individual sound-triggered tracks (A), then seek multi-fish simultaneous call attribution (C).


## 6. v21b addendum: original publisher repository path and 2026 prior mechanism

**Publisher-path correction:** The exact 2024 Nature data-availability link uses **lowercase**
[gin.g-node.org/danionella/veith_et_al_2024](https://gin.g-node.org/danionella/veith_et_al_2024). Our initial v21 source-metadata attempt accidentally used uppercase `Veith_et_al_2024` in a GIN repository path, yielding HTTP 404 in [run #45031438955](https://github.com/zuizui0223/boids/actions/runs/45031438955). That run's 11 offline tests passed but no GIN source records or model outcomes were accessed. It must **not** be characterized as evidence the dataset is absent. The original publisher-case spelling has now been restored in the source script and requires a new metadata-only run before an access-status statement.

**Newly confirmed published analytical prior art:** Veith, Svanidze & Judkewitz (2026), *An algorithm underlying directional hearing in fish*, Current Biology 36:1435–1443.e3, DOI [10.1016/j.cub.2026.02.019](https://doi.org/10.1016/j.cub.2026.02.019), published March 2026 (PubMed 41819098), already varies sound pressure–particle-motion relative phase and frequency and provides a quantitative directional startle sensorimotor model in *Danionella*. We must not present 2024 paper + our constructed phase counterexample as **first** derivation of the sensory transformation. A meaningful new endpoint needs **the coupling of identified fish sensorimotor rules with actually tracked conspecific encounters, school geometry, and source-attributed calling**, not merely a better synthetic acoustic direction classifier.

The analytic paired amplitude counterexample remains valid for its precisely defined phase-blind observation model regardless of previous literature. It is only an observability audit; it is not an effect from Veith trajectories, not a new universal fish auditory law, and not a school-level acoustics result.
