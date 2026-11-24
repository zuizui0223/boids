# v21 — Two independent fish schooling data sets + auditory observability: ecological result hierarchy and falsifiable next study

2026-11-22 JST. **This is an evidence synthesis, NOT a new observed acoustic-to-school feedback result.** Original v5–v9c movement tests and v15–v20 synthetic hearing results remain frozen. PR #248 stays Draft, no main merge.

## 1. The empirically supported piece is movement information transfer, not chorus

| Original source and source-verified heldout design | Added collective information | Heldout result | Scope |
| --- | --- | --- | --- |
| Puy et al. 2024, *PNAS* 8 black neon tetra × six recording files, whole-file holdout, future 0.20s velocity | own+wall versus own+wall+Boids neighborhood state | MSE 13.90306 → 11.32326 **18.56% reduction**, 6/6 files positive | Same original experiment; local-versus-global confounded by 25cm radius covering all other 7 fish in 93.67% of rows; original tracking may include smoothing/interpolation |
| Same Puy source, fixed geometry baseline | whole-school other-seven mean relative velocity | MSE 13.735379 → 11.352981 **17.34% reduction**, 6/6 files positive | Adding genuinely local alignment *after* global provides only 0.03213 MSE in source (6/6 short-term), not a unique causal force |
| Niizato et al. 2024 *Scientific Reports*, seven 10-ayu recordings, original TXT native ~30fps, whole-file holdout | geometry + relative other-nine school velocity | Short 0–0.2s MSE 7343.446 → 6604.327 **10.065% reduction** (7/7); delayed 0.5–0.7s 31090.917 → 26311.946 **15.37% reduction** (7/7) | Original coordinate/s units **not** comparable with tetra cm/s; recording IDs may reuse animals; no fish calls |
| Same ayu source, after global velocity | nearest-3 relative velocity | Short gain ~0.955% vs global baseline (6/7); delayed increment −0.1277 original squared units (4/7), interval spans zero | Local unique velocity information is weak and not robust at delayed horizon |

Original result files: [v5](V5D_EIGHT_FISH_OBSERVED_BOIDS_HELDOUT_RESULT.md), [v7](V7_OBSERVED_FISH_GLOBAL_VS_LOCAL_RESULT.md), [v8](V8_OBSERVED_FISH_ASSIGNMENT_AND_DELAY_RESULT.md), [v9c](V9C_INDEPENDENT_AYU_OBSERVED_GLOBAL_LOCAL_RESULT.md).

**Defensible synthesis:** *The current collective motion state provides short-horizon predictive information beyond own motion in two different fish taxa, while unique nearest-neighbor motion transfer is much smaller, especially at longer horizons.* This is cross-source **prediction**, not proof of an emergent global information processing force, not an independent-species meta-analysis, and not an observed acoustic or vocal effect.

## 2. Auditory motor response is already established independently of our model

- Veith et al. (2024), *Nature*, DOI [10.1038/s41586-024-07507-9](https://doi.org/10.1038/s41586-024-07507-9), experimentally showed phase-dependent directional startle in **individual** *Danionella cerebrum*.
- Veith, Svanidze & Judkewitz (2026), *Current Biology* DOI [10.1016/j.cub.2026.02.019](https://doi.org/10.1016/j.cub.2026.02.019) already fit a frequency-/phase-dependent sensory-to-motor model. **Do not claim this individual fish auditory algorithm as original to Boids.**
- Our v21 offline [constructed exact counterexample](V21_FISH_VECTOR_ACOUSTIC_OBSERVABILITY.md) shows the **limited** proposition that matched pressure and particle-motion *magnitudes alone* cannot resolve opposite constructed phase-cross-term signs. It does not test real fish labels and does not refute other acoustic localisation approaches.

## 3. Actual new question and two rival mechanistic predictions

### Hypothesis H1: social acoustic–motor–vocal feedback

An acoustically triggered local motor response changes spatial neighborhood/connectivity, which changes conspecific audibility and subsequent self-generated calling after an external cue has ended. This predicts, **in the same experimentally tracked school**, that a randomized calibrated cue has a persistent impact on calling *conditional on pre-cue geometry*, that movement/connectivity changes precede later caller escalation, and that effect size changes when spatial hearing opportunities are selectively weakened.

### Rival H0: independent individual excitation plus common school movement

A playback cue both excites calls and causes whole-school displacement, without an acoustic-to-motion-to-acoustic loop. H0 can generate a positive correlation between compactness and calls; even strong short-term persistence can arise from individual response decay and recording threshold. On same-school histories, H0 predicts no extra future-call predictive value from **time-ordered acoustic connectivity after controlling individual excitation, cue, initial calling and common school heading**.

These are **proposed discriminating predictions**, not results. The v20 artificial path interactions (compact, vocal-long motor-long vs motor-short +24.69 calling-rate points across 22 selected artificial seeds) show a model possibility and heterogeneity but cannot establish H1 in real fish.

## 4. Minimum real-world input and frozen prospective evaluation

At least several independent real schools (not thousands of within-school frames as independent units), with:
- synchronized tracked unique-fish XY(t) and direct audio recording;
- source-attributed fish calls or calibrated source probability with uncertainty, including **non-calling** spans;
- measured local sound pressure and particle motion with sensor geometry/phase calibration;
- randomized cue on/off, fixed stimulation times and independent cohort blocks;
- explicit response time ordering: pre-cue covariates → motor/neighbor geometry → later call rates.

Hold out entire schools and observation sessions. Compare four fixed next-call models on identical windows:
- N0: past calls, cue, elapsed time, social cohesion, current global school motion.
- N1: N0 + local audibility from independently calibrated acoustics but no motor history.
- N2: N1 + prior motor/neighbor geometry transitions not derived from future calls.
- N3: a structured state model with hypothesized reciprocal paths, fitted only on training schools.

Primary endpoint: heldout **out-of-sample conditional log-loss difference N2−N3**, and a randomized-cue conditional effect. Null control: clock-shift or misassigned callers preserving whole-school intensity and call counts, within independent sessions. Counter-mechanism: individual slow response/undriven shared heading. Causal mediation requires an actual design identifying it, not model feature importance.

**Scientific success gate:** even if v21's phase operator improves an individual startle prediction, still no school-to-chorus feedback claim without same-school raw synchronized calls and movement. Cross-species evidence for global heading is a useful movement-layer prior, not a surrogate for vocal data.

## 5. 2026-11-22 original GIN source admission status

- [v21b metadata-only source run #45031604373](https://github.com/zuizui0223/boids/actions/runs/45031604373) correct publisher-lowercase GIN endpoint `/contents/behavior?ref=master` returned HTTP **404**; no raw trajectories.
- [v21c multi-route run #45031703768](https://github.com/zuizui0223/boids/actions/runs/45031703768) repository API reported **public, nonempty, default branch master**, canonical full name `danionella/Veith_et_al_2024`. Root file listing and both `behavior?ref=master` and `behavior?ref=main` returned **404**. The difference in canonical case might matter; service behavior has not been resolved.
- [v21d source-only Git API run #45031828840](https://github.com/zuizui0223/boids/actions/runs/45031828840) `/branches/master`, `/git/trees/master`, `/git/commits/master`, and recursive tree: all HTTP **403**.
- All three workflows returned technical **SUCCESS** because their expected failure states were captured; this is **not a source admission PASS**. No original Veith fish trajectories, playback labels or any field fish scores were downloaded, examined or fitted.

**STOP scientific source gate**, no invented fish auditory prediction. Do not call this evidence that the published data are absent, only that the tested unauthenticated API routes did not expose them in these runs. A manual publisher/G-Node/author-provided checksum-verified access path remains required for raw behavioral data fitting. PR #248 stays Draft and `main` unchanged.
