# v10c: complete original wild sound-source positional uncertainty audit

**Source:** Mouy et al 2023 *Methods in Ecology and Evolution* DOI 10.1111/2041-210X.14095, six genuine [OSF](https://osf.io/q8dz4) original localization_result.csv arrays. All six SHA256 reauthenticated as previously locked in v6 source-only receipt. Earlier [v10b original event-time ordering Actions #44769141245](https://github.com/zuizui0223/boids/actions/runs/44769141245) yielded one array-level source-location time-neighbor result (large HI 12 localized events, 11 adjacent ≤120s pairs, observed 0.07903m vs 1999 shuffle expectation 0.27667m, O/E=0.2856, one-sided conditional p=.0005). Four of six arrays had enough observations; two source support STOP. All 66 original CSV row count but 50 with finite xyz and timestamp; labels `label_class` empty for all analyzable events; no repeated identified fish tracks.

## Why spatial localization uncertainty matters
Large HI original reported xyz uncertainty-span combined 3D median **0.70712m**, nearly 9× its nominal 0.07903m successive event distance. Therefore nominal acoustic point estimates cannot show that *individual* fish move or school, even if a time/order label-shuffle null is unexpectedly small.

## Exploratory source-fixed sensitivity (post-v10b)

[Uncertainty scenario original Actions #44770473705](https://github.com/zuizui0223/boids/actions/runs/44770473705): Source original six files successfully re-acquired after transient HTTP timeouts. This run printed `PARTIAL_SOURCE_TIMEOUT_STOP` **solely because of a report-status key mismatch** (`source_valid` versus actual `source_n_valid`), not missing source files; per-array full original records show all 6 source arrays admitted. Status-only fix committed afterward without changing original calculations. [Final original run #44770995567](https://github.com/zuizui0223/boids/actions/runs/44770995567) reauthenticated all six original OSF files, reported `ALL_SIX_SOURCE_REPLAY_AND_JITTER_SENSITIVITY` with n_source_admitted=6, and reproduced the fixed sensitivity numbers unchanged. Five fixture tests passed. The preceding reporting-only key mismatch and transient original source read timeouts remain documented in the Actions history.

For each original 3D localization event, sample its coordinates *independently*, each axis uniformly from centered intervals with half-width half the supplied `x_err_span,y_err_span,z_err_span`. This is a hypothetical positional noise sensitivity scenario, **not a draw from an actual posterior of the acoustic localization algorithm**. Each of 500 draws is compared with 299 within-array original event time/position permutations. Fixed RNG and thresholds before new sensitivity readout. The outcome is a distribution across imposed noise scenarios, **not a conventional confidence interval**, and not 500 independent fish experiments.

| Original array | complete source 3D events | original time-adjacent pairs | Median error-span norm (m) | 5/50/95% ratio observed consecutive distance / time-shuffle expected | fraction ratio <1 | fraction per-scenario p<=.05 |
|---|---:|---:|---:|---|---:|---:|
| large OGD | 5 | 4 | -- | SOURCE_SUPPORT_STOP | -- | -- |
| mini | 2 | 1 | -- | SOURCE_SUPPORT_STOP | -- | -- |
| mobile A | 6 | 5 | 0.5954 | 0.691 / **1.077** / 1.395 | 38.0% | 0.6% |
| mobile B | 6 | 5 | 0.3086 | 0.730 / **1.100** / 1.452 | 32.6% | 1.8% |
| mobile C | 19 | 18 | 4.5162 | 0.672 / **0.847** / 0.986 | 96.4% | 21.6% |
| large HI | 12 | 11 | 0.7071 | 0.460 / **0.646** / 0.832 | **99.6%** | **63.4%** |

**Interpretation ceiling:** At large HI, shorter temporal-adjacent sound-location separation survives many independent coordinate error-span perturbations relative to the shuffled null, but the source localization uncertainty dwarfs absolute nominal distances and 36.6% of scenarios do **not** give p≤.05. Individual fish identities and acoustic source propagation conditions are unobserved. Mobile C shows qualitatively shorter relative distances in 96.4% of hypothetical scenarios but its conditional p threshold is reached in just 21.6%, and original unperturbed p=.167. These data are too small, single-scene and audio-specific for general biological schooling or vocal coordination claims.

The source arrays are not interchangeable ecological populations: 6 source configurations, sound counts of 2–23, mix of animal scenes, no calibrated uniform recording effort. It is not valid to pool 500 simulated uncertainty scenarios as samples or to claim independent meta-analysis.

## Important separate access gate for genuine school-acoustic proxy dataset

Kim et al 2026 public Dryad 10.5061/dryad.qz612jmx0 has South_T UF440 20-min chorus and 70kHz active acoustic biological backscatter within the *same survey system*, but author paper already modeled nightly SPL versus backscatter (existing prior art). Our source gateway verified **nine public file metadata records**, while file payload access returned **HTTP 401**, as the Dryad API requires OAuth bearer authorization for download. Thus a new properly heldout backscatter→future-chorus prediction was **not performed**, and no actual scatter signal was used. [v10 source admission Actions #44768532962](https://github.com/zuizui0223/boids/actions/runs/44768532962). Do not invent source bytes or use alternative data as if simultaneous.

## Research integration decision

The strong original fish motor prediction v5–v9 in 2 tracked species and the wild acoustic localization-time pattern exist in **different organisms and sampling studies**. A coherent paper cannot claim that Boids-generated fish schools produce collective acoustic choruses from these unpaired observations.

At most two rigorously scoped sub-studies:
1. Two-species fish motion: shared school-wide velocity supports recording-holdout next-fish velocity prediction; locally unique alignment weaker/horizon-dependent.
2. A sound-source observability/failure-mode study: one array's repeated sound-localized positions exhibit temporal locality, with a larger localization uncertainty than the apparent separation; robust 3D social trajectories not identified.

The **full hypothesis** requires synchronous fish individual locations, detection-calibrated sonic call attribution, acoustic propagation and independent site/night holdouts. Position+sound without unique fish ID does not define causal social Boids force.

**Keep PR #248 Draft. main unchanged.**

