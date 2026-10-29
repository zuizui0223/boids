# boids — 3D movement rules → ecological patterns → prediction

**Status (2026-10-27): exploratory research repository.** This repository centralizes the 3D Boids simulations, ecological niche partition analyses, cross-repository synthesis, synthetic forecasting benchmarks, and observed bat movement-transition feasibility test from the research sessions of 2026-10-25–26.

**日本語要約：** 3D Boidsの分離・整列・凝集と、資源消費・環境追跡・個体履歴を結合し、種内／種間ニッチ分化の数理指標と予測を検証する研究リポジトリ。*合成モデルによる予測成功と、実測データで検証された運動法則を混同しない。*

## Current evidence, in order of strength

1. **Synthetic mechanism / known-truth (v1–v3).** Agent-based trajectories produce persistent individual vertical-profile differences, spatial versus vertical partition contrasts, local environmental-state buffering, and breeding-component concentration under specified parameters. A surrogate predictor performs better than simple baselines at unseen combinations drawn from the same synthetic model. These are **not wild-species forecasts**.
2. **Observed Tadarida benchmark (v4).** Archived bat GPS summaries support a small positive held-out next-climb-class gain from prior climb class (M1−M0 ≈ **+0.01383 nats/transition**, equal-individual mean, 7/8 positive). Adding annotated wind gives **−0.00113**; adding other-night individual history does **not** pass label-permutation calibration (**p=0.32**). These outcomes do not establish or refute the biological causes of individuality.
3. **Known-truth GPS-error identifiability (v5).** An independent *synthetic negative control* demonstrates that previous-climb-class forecast gains can arise solely from shared altitude measurement error even when true successive climb velocities are independent. This does not establish the error magnitude for actual tagged bats or refute a true movement policy. See [`docs/GPS_ALTITUDE_ERROR_IDENTIFIABILITY_V5.md`](docs/GPS_ALTITUDE_ERROR_IDENTIFIABILITY_V5.md).
4. **Independent public bat-pair 3D forecast (v6, exploratory).** A separately published, checksum-verified 30-flight-pair archive supplied 28 eligible paired 3D trajectories under a frozen structural gate. Whole-pair held-out actual-partner versus mismatched-ghost mean MSE gain was +0.000555 (pair-bootstrap 95% CI [-0.000092,+0.001276]); 16/28 pairs favored the actual partner. **The planned forecast advantage was not supported**, and these brief spline-resampled flight episodes do not identify social-force coefficients or persistent 3D niches. See [v6 result](docs/OBSERVED_BAT_PAIR_RESULT_V6.md).
5. **Full Boids social-force estimation remains unidentifiable from the original Tadarida source.** Approximate archived GPS observations provided no cross-individual fix pairs both within five seconds and within 100 metres; the sampling cadence and localization error are not suitable for estimating short-range separation/alignment/cohesion coefficients. The original raw-data checksum was **not independently reverified in the local run**; no raw GPS tracks are redistributed here.

## Repository contents

- [`boids3d_empirical_v4/`](boids3d_empirical_v4/) — **canonical executable snapshot** (70 source, result and figure files, preserving their original relative paths and v4 manifest).
- [`boids3d_empirical_v4/boids3d_research/`](boids3d_empirical_v4/boids3d_research/) — 3D Boids rules, ecological ABM, niche/partition metrics, resource depletion, prediction scripts, synthetic JSON outputs, figures, and 24 regression tests.
- [`boids3d_empirical_v4/EMPIRICAL_RESULT_V4.json`](boids3d_empirical_v4/EMPIRICAL_RESULT_V4.json) — observed bat next-state prediction and neighbor-observability results.
- [`boids3d_empirical_v4/PROTOCOL.md`](boids3d_empirical_v4/PROTOCOL.md) — definition of observed transition tasks, cohorts, controls, and limitations.
- [`archives/`](archives/) — unmodified original v2, v3 and v4 release ZIPs so prior snapshots are not silently rewritten.
- [`validation_v5/`](validation_v5/) — independent synthetic GPS-altitude error counterexample, 30-seed receipt, and 6 new unit tests. **The original v4 tree and archive stay unchanged.**
- [`validation_v6/`](validation_v6/) — checksum-pinned independent 30-bat-pair 3D source, held-out real-partner versus ghost forecast, strict eligibility gate, and saved original-scale numerical result (not raw trajectories).
- [`docs/OBSERVED_BAT_PAIR_RESULT_V6.md`](docs/OBSERVED_BAT_PAIR_RESULT_V6.md) — completed observed-data analysis, negative primary gate, caveats and reproduction.
- [`docs/EVIDENCE_AND_PREDICTION.md`](docs/EVIDENCE_AND_PREDICTION.md) — mapping to batter, ODSP, mina, and louis and the precise scientific claim boundaries.
- [`docs/MIGRATION_MANIFEST.json`](docs/MIGRATION_MANIFEST.json) — per-file SHA-256 and Git blob SHA-1 audit of the staged transfer.

## Reproduce without raw animal records

```bash
python -m pip install -r requirements.txt
cd boids3d_empirical_v4
python -m unittest discover -s boids3d_research -p 'test_*.py' -v  # 24 tests
python -m unittest discover -p 'test_*.py' -v                 # 4 tests
cd boids3d_research
python predict_niche.py --help
cd ../..
PYTHONPATH=boids3d_empirical_v4:validation_v5 python -m unittest discover -s validation_v5 -p 'test_*.py' -v  # 6 tests
python validation_v5/altitude_error_audit.py --seeds 30 --out validation_v5/results/gps_altitude_error_known_truth_v5.json
```

The observed-data numerical benchmark requires the original Movebank source. Follow [`boids3d_empirical_v4/README.md`](boids3d_empirical_v4/README.md) and its explicit MD5 gate. Avoid claiming raw-data re-execution from the bundled aggregates alone.

## Independent 3D paired-flight forecast (v6)

The [predeclared experiment and source eligibility](docs/INDEPENDENT_3D_SOURCE_AND_FORECAST_V6.md) is completed. [GitHub Actions run 40277563862](https://github.com/zuizui0223/boids/actions/runs/40277563862) passed all checks; the result and the figure are committed in `validation_v6/results/`. Reproduce source validation and held-out prediction by running the predeclared workflow; the downloaded original bat recordings remain separate from this repository.

```bash
PYTHONPATH=validation_v6 python -m unittest discover -s validation_v6 -p 'test_*.py' -v
python validation_v6/paired_trajectory_gate.py --out validation_v6/results/paired_eligibility.json
python validation_v6/social_forecast.py --out validation_v6/results/bat_pair_directional_forecast.json
```

**Claim limit:** non-significant directional forecasting improvement is not evidence of no acoustic influence, and spline-derived 30-Hz computational spacing is not independently observed 30-Hz localization. No same-source model or threshold rescue is authorized after opening outcomes.

## Observed pigeon forecast v8 and inverse-law caution v9

The **197 matched pigeon flights** from [Zenodo 5010830](https://zenodo.org/records/5010830) were evaluated under a frozen **10 bird-connected group** holdout. The *prespecified primary* current-partner vs 10-second-stale-partner gain was **+0.00008669 rad² MSE** (95% bird-group bootstrap interval **[-0.00003237,+0.00021788]**, **6/10** groups positive, one-sided exact sign p=**0.377**). **Not supported**. Present-partner vs own-only was a secondary positive contrast: **+0.00031012 rad²** and 9/10 positive groups, but that does not identify unique social forces. This is **horizontal next-turn prediction**, not a fitted 3D niche or a cross-species forecast.

- [Frozen v8 result and source provenance](docs/OBSERVED_PIGEON_V8_FROZEN_RESULT.md) · [exact original numerical receipt](validation_v8/results/pigeon_social_forecast_v8.json) · [original workflow](https://github.com/zuizui0223/boids/actions/runs/40323282974)
- [v9 audit and movement-to-niche theory](docs/MOVEMENT_TO_NICHE_IDENTIFIABILITY_V9.md): exact replay of group-weighted original result, plus a **synthetic identified-set counterexample**. At a fixed calibration distance, distinct separation/cohesion coefficients predict the same instantaneous force. At new spacing, they produce different long-horizon motion. This is mathematical *known truth*, not a wild-animal ecological observation.
- `validation_v9/` contains **12 new regression tests**, offline replay, known-truth equations, result JSON and plots. The [CI workflow](.github/workflows/receipt-consistency-v9.yml) does not redownload raw GPS.

**No post-hoc rescue of v6 or v8 primary predictive failures is authorized.** The next ecological validation needs independent multiday 3D trajectories, calibrated observation errors and source-blind distribution-level forecasts.

## v10: from ambiguous Boids coefficients to 3D niche and individual-profile predictions

**Synthetic mathematics, not field validation.** [v10 ecological report](docs/NICHE_IDENTIFIED_SET_V10.md) and [20 regression tests](validation_v10/) propagate five source-equivalent separation/cohesion candidate pairs through two-species, twelve-agent stochastic 3D use simulations. Each parameter candidate has identical instantaneous social force at the stipulated 10-m source spacing.

- In shared synthetic resources, the coarse-grid vertical information is **0.573–0.605 nats** and horizontal species information is **0.0011–0.0014 nats** across candidates; after imposed spatial resource reassembly the respective ranges are **0.006–0.012** and **0.596–0.651**. The dominant niche axis switches under all tested rules and remains consistent on a finer grain. This is **by construction of toy environmental selection targets**, not observed competition.
- Across ten stochastic simulation holdouts, a stable per-agent vertical target produces an individual self-versus-species conditional-height log-score gain of **+0.158 nats/fix**; reassigning these targets between agent labels across seeds gives **−0.065** at the representative alpha=1.0. This illustrates a sufficient mechanism for profile persistence and does not prove bat memory.
- Precise categorical probability maps are **not identical** across candidate rules. The 4×4×4 shared-resource source-world candidate-pair joint TV reaches **0.0255**, increasing to **0.0430** for the reassembled resource world (7×7×7 grain up to **0.0791**). These are finite candidate-set spreads, **not statistical confidence intervals or complete identified-set bounds**.

The known-truth simulations contain no measured habitat, competitive resource depletion, calibrated GPS error, or wild-animal individual identities. Frozen v6/v8 wild movement primary failures remain unchanged.

```bash
PYTHONPATH=validation_v10 python -m unittest discover -s validation_v10 -p 'test_*.py' -v
python validation_v10/niche_identified_set.py --seeds 10 --out validation_v10/results/niche_identified_set_v10.json
python validation_v10/profile_transfer.py --seeds 10 --out validation_v10/results/profile_seed_transfer_v10.json
python validation_v10/plot_v10.py
```

See [Figure: niche axes](validation_v10/figures/fig_v10_species_niche_axes.png) and [Figure: held-out individual-profile contrast](validation_v10/figures/fig_v10_individual_profile_transfer.png), or the [full reproducibility workflow](.github/workflows/niche-identified-set-v10.yml).

## v11: Separating imposed resource targets from Boids-generated niche-axis organization

The [v11 driver-ablation report](docs/RESOURCE_AND_SOCIAL_DRIVER_ABLATION_V11.md) compares **social on versus off under common simulation noise**, with no pseudo-species environmental target contrast, vertical targets, horizontal targets, and both. Same-target species information is nearly zero; strong horizontal/vertical partitions persist with social interactions removed. Thus the previously reported species-axis switch is mostly **by imposed habitat target design**, not spontaneous niche partition produced by Boids alone.

Boids itself modifies the *distribution of an existing habitat-driven difference*: in the two-contrast synthetic world, the coarse-grid alpha=1.0 social intervention changes I(S;XY) by **−0.1055 nats** and I(S;Z|XY) by **+0.0743 nats**, with matching signs at fine grain but different magnitudes. Individual z-profile identity falls from **0.2721** to **0.0353 nats** when the prescribed role-specific z-target is eliminated with social on; this is not evidence of naturally arising bat individuality.

The independent-seed forward comparison favors the **correct known target environmental world** over an environment-blind baseline; it is a synthetic Monte Carlo oracle, **not a new observed habitat or cross-species prediction**. All 3D state-use results are categorical occupancy of invented coordinates, not realized feeding-niche proof or field competition inference. Original negative v6 and v8 tests remain frozen.

- [Complete reproducible code and receipt](validation_v11/)
- [Driver/partition figure](validation_v11/figures/fig_v11_driver_by_niche_axis.png)
- [Individual target-control figure](validation_v11/figures/fig_v11_individual_target_ablation.png)
- [GitHub Actions reproducibility test](.github/workflows/ecological-driver-ablation-v11.yml)

## v12: Endogenous individual and guild niches (synthetic, no field mechanism claim)

The [v12 research note](docs/EMERGENT_NICHE_HIERARCHIES_V12.md) and [source/results/tests](validation_v12/) replace pre-imposed individual resource targets with identical initial patch preferences and specified **private reinforcement + social choice sharing**. Initial network topology defines two artificial social guilds of 6 agents each; these are **not evolved biological species**. The short-term Boids motion force is distinguished from the separate social-choice imitation term.

- With private reward reinforcement alone, held-out days 5–8 showed **+0.428 nats/choice** individual patch prediction and **+0.242 nats/fix** individual vertical-profile prediction.
- With assortative in-guild choice imitation, **+0.592 nats/choice** guild patch and **+0.183 nats/fix** guild vertical-profile prediction were generated, while individual held-out gain disappeared. Mixing social connections across guilds, resetting reward memory, or adding resource depletion removed most of this guild-level effect in the specified simulation.
- The exploratory individual-vs-guild prediction-score crossover was **social choice strength ≈0.443**, with a 30-seed computational bootstrap range **[0.349, 0.535]**. **This is neither a biological threshold nor a sharp phase transition.** Which guild settles on the left versus right patch changed among seeds.
- Pairwise Boids separation/cohesion force on/off made almost no difference to the guild patch gain under fixed social choice. Thus **the main emergent effect is social policy imitation and private memory, NOT proof that Reynolds steering causes interspecific niche partition**.
- All seven saved JSON outputs were replayed, **40 regression tests** passed locally, and [CI](.github/workflows/emergent-ecological-hierarchy-v12.yml) uses fixed random seeds with an exact receipt check.

No source wild bats/birds, calibrated 3D error, cross-species interactions, animal learning, real resource competition or demographic site-use data were fitted here. Frozen v6/v8 observed social forecast primary failures remain unchanged.

```bash
python -m pip install 'numpy>=1.26,<3' 'matplotlib>=3.7,<4'
PYTHONPATH=validation_v12 python -m unittest discover -s validation_v12 -p 'test_*.py' -v
PYTHONPATH=validation_v12 python validation_v12/check_replay_v12.py --help
```

## v13: Learned niche hierarchy after social-network rewiring (synthetic)

A [predeclared eight-condition experiment](docs/NETWORK_REWIRING_FORECAST_PROTOCOL_V13.md) retained symmetric innate patch choice but exchanged half the original artificial guild members at day 5. Fixed training days 5–6 predicted days 7–8 with a two-guild model conditioned on the *current* network versus an ex-ante orthogonal grouping. All observations are generated by the original v12 simulator and a new fixed intervention (30 stochastic seed worlds; 14/14 new regression tests).

- **Registered primary synthetic gate passed:** rewired current-guild held-out patch log-score advantage **+0.1935 nats/choice** (seed bootstrap 95% **[+0.1020,+0.2870]**); initial stable guild +0.5178 [+0.4069,+0.6109].
- Without private reinforcement the rewired advantage was **−0.0453**; learned vs no-learning paired difference **+0.2388** [+0.1465,+0.3336]. Fixed-grid conditional height advantage was +0.1218 nats/fix after rewire.
- Erasing Q memory *at* the rewire increased the new-group signal by +0.3399 [+0.2021,+0.4742] versus inherited Q, illustrating inertia versus reorganizability **within the stipulated model**. Restoring original dyad Boids motor forces had near-zero incremental effect.
- Resource reward-gradient attenuation was **not supported by the paired uncertainty interval**. These are 30 simulator-seed bootstrap intervals, NOT wild-species confidence limits or evidence of social forcing in bats/birds.

[Full v13 results](docs/NETWORK_REWIRING_RESULT_V13.md) · [passing GitHub Actions run](https://github.com/zuizui0223/boids/actions/runs/40535430474) · [next independent observed-data preflight](https://github.com/zuizui0223/boids/issues/2).

## v14: Independent public GPS/IMU source and 2D social-observation gate (observed source quality, not mechanism)

[Predeclared v14 admission](docs/INDEPENDENT_OBSERVATIONAL_ADMISSION_V14.md) and [completed structural result](docs/INDEPENDENT_OBSERVATIONAL_RESULT_V14.md): independently published Zenodo DOI [10.5281/zenodo.21092705](https://doi.org/10.5281/zenodo.21092705), 126,588,691-byte archive, verified MD5 and derived SHA256. Every one of its 56 raw sensor files passed an individual published SHA256 check; **16 no-leakage/data-quality tests passed** in [the recorded run](https://github.com/zuizui0223/boids/actions/runs/40541344970). There are **three** pigeon flock-flight trials (7/11/10 birds; 13 unique identities), not 28 independent flights.

The 28 raw GPS files contain **271,297 valid distinct NMEA UTC fixes**, median positive timestamp spacing **0.1 s** across files, and raw short-lag proximity observation opportunities across 121 within-trial bird pairs. These counts include all device records and are **not speed-gated airborne effects**, predictions or independent behavioral replications. Trial 2 supplied ~87% of the valid fixes. There is **no NMEA altitude for 3D niches**; source GPS preprocessing repairs timestamps, so original-device time and interpolated time must remain separate.

**Claim boundary:** the external source is technically observable for exploratory 2D movement comparison, but contains only three independent flight groups (best possible trial-level sign-test p=0.125), and does **not** validate Reynolds forces, stable learned niches or v13 rewiring ecology. The independent repeated-horizontal-flight Dryad candidate is metadata verified but its data download was unavailable (HTTP 401); no CSV rows or forecasts were fitted. v6/v8 observed negative primary results remain frozen. See [next source/forecast gating issue #2](https://github.com/zuizui0223/boids/issues/2).

## v15: An independent raw-GPS short-step partner forecast **did not support** the social-information primary (observed field data)

The [preregistered v15 experiment](docs/OBSERVED_HORIZONTAL_TURN_FORECAST_CONTRACT_V15.md) used the **different**, checksum-verified 2026 Zenodo flock-flight source (3 flights, 7/11/10 birds), retaining 497 matched airborne 1-second horizontal GPS turn prediction anchors after fixed raw-time and speed gates. Three leave-one-source-flight-out ridge models compared own/route, present nearest partner and **the same partner 10 seconds earlier** on identical test records; 30-second history offered an independent restricted-subset *time-shift surrogate* comparison.

- **Primary negative:** mean MSE(stale) − MSE(present) **−0.001164 rad²** across the three equally weighted held-out source trials; **0/3** favorable to current neighbor features. Current-partner MSE was 7.39% above the stale-partner model.
- **Own-only stronger:** mean MSE(own) − MSE(present) **−0.001415 rad²**, **0/3** current-partner favorable; the 30-second surrogate likewise outperformed present partner on its separate matched subset.
- 13 pre-outcome unit tests passed and two complete independent GitHub Actions source reruns returned exactly the same per-trial numerical results: [first run](https://github.com/zuizui0223/boids/actions/runs/40610956613), [replay](https://github.com/zuizui0223/boids/actions/runs/40610981484).
- A negative result for a fixed **linear GPS predictor** does not mean birds lack interactions or show that biological Boids steering is false. With only **three** independent flight trials (minimum one-sided sign p=0.125), no new field causal force, memory or niche claim is supported. No post-hoc rescue on this same source.

[Complete frozen observed result and per-trial scores](docs/OBSERVED_HORIZONTAL_TURN_RESULT_V15.md) · [executable source](validation_v15/). Prior v6/v8 observed primary negatives and v13 learned-policy **synthetic** positives remain unchanged.

## v16: Independent eight-flock source yields **positive short-step social predictive information** but **non-robust repeated-route memory** (observed data, exploratory)

The original Watts et al. 2016 GPS source [Zenodo 4943714](https://zenodo.org/records/4943714) is independent of v8 and v15. The 272,270,105-byte ZIP (SHA256 `7380feccd8c2e4e1675679411d1ee8075cd29ccbd2dada98e317ca88053ffbfa`) has 559 original GPS CSVs from **eight pigeon flocks**, 13–15 repeated releases per flock; 178 `._` macOS sidecars excluded. Structural/source tests identified exact UTC+MS, original 2D coordinates, headings and uncalibrated GPS altitude. Original labels for clock-shift treatments were *not* used as causal predictors. Study is CC0.

- **Fast 1-second GPS heading prediction:** fixed linear ridge current nearest-partner vs the same partner 10 seconds earlier, with training on releases 5–8 in the **other seven flocks**, tested on releases 9–15 in each heldout flock. **9,279 matched future anchors**, **7/8** flocks with improvement: equal-flock MSE(stale) − MSE(present) **+0.001509 rad²** (whole-flock bootstrap 95% **[+0.000680,+0.002110]**), ~**4.64%** reduction in equal-flock mean MSE. Present partner also beat own-only in **7/8**. [Frozen fast result](docs/OBSERVED_EIGHT_FLOCK_FAST_RESULT_V16.md) · [full CI execution](https://github.com/zuizui0223/boids/actions/runs/40615273961).
- **Slow future-release route-history prediction:** at nine fixed 500–4500m radial shell crossings, compare other-flock population history with this flock's history and this individual's history from releases 5–8. The same source showed **only 4/8** flocks benefiting from a static flock route template (mean +0.003543 rad², whole-flock bootstrap [−0.01817,+0.02696]); personal-history addition **5/8** positive (mean +0.002932, CI [−0.00284,+0.01219]). **Neither slow contrast demonstrated a generalizable benefit.** [Frozen slow result](docs/OBSERVED_EIGHT_FLOCK_ROUTE_RESULT_V16.md) · [full CI execution](https://github.com/zuizui0223/boids/actions/runs/40614826472).
- **Scientific boundary:** The two endpoints are distinct. Current-neighbor features can predict short-step turns in this source but may represent shared route/stimulus rather than causal social steering. A lack of stable route-template transfer is not proof of absent animal memory. This is no observed **3D** resource niche, no identified Boids coefficients or network-rewiring mechanism. The negative v15 2026 pigeon source and v6/v8 observed endpoints remain frozen. **The opposite v15 direction cannot be attributed solely to ecology because sensor/model regimes differ.**

[Pre-outcome dual-timescale contract](docs/DUAL_TIMESCALE_ROUTE_PREDICTION_CONTRACT_V16.md) · [source data-quality gate](docs/EIGHT_FLOCK_INDEPENDENT_SOURCE_CONTRACT_V16.md) · [reproducible code and aggregate-only frozen outputs](validation_v16/).

## v17: Independent 2019 pigeon GPS + wind source admitted, **but wind-gated social prediction is not yet identifiable**

[Original source-level result](docs/V17_ORIGINAL_WIND_SOCIAL_SOURCE_RESULT.md): an independent study of **20 homing pigeons** (Taylor et al. 2019, [Zenodo 5026107](https://zenodo.org/records/5026107), CC0), consisting of **458 original 5-Hz GPS CSV files** across four solo/paired phases (120/120/113/105), plus **152,227** one-minute weather records. The exact original GPS ZIP (240,056,153 bytes, SHA256 `030e70082b107a353dd4f0afb0cd54868438273a416efac135120a6bdf9c2b29`) and weather CSV (11,529,364 bytes, SHA256 `45885ce19954fd99397b92847421d3e11a6ea2c8d22d1a1d6220ea4940fa2917`) were independently downloaded and provider MD5-verified. **Nineteen of twenty identities** have source files in all four phases.

- The raw weather CSV has three unnamed numeric columns; its timestamp converts plausibly as MATLAB serial-day values to **2015** with ~60-second median interval. But the **absolute weather time-zone is still unknown**. In 2,748 sampled raw GPS timestamps, weather coverage was **100%** at shift 0, **97.93%** at −1h, **99.67%** at +1h. The nearly continuous weather record makes all offsets plausible; do not choose a model-favorable clock.
- The **original PLOS S3 supplementary pairing ledger is now source-verified**: 20 individuals, 10 reciprocal paired dyads in each experimental phase; switching pair partners forms **exactly five disconnected four-bird C₄ networks**, NOT eight or twenty independent groups. The registered v17 confirmation gate (≥8 components) therefore **fails before behavioral model fitting**. [Exact experiment graph and original checksum](docs/V17_PUBLISHED_PAIR_GRAPH_RESULT.md).
- [Source admission protocol](docs/V17_INDEPENDENT_WIND_SOCIAL_ADMISSION.md), [GPS/weather schema addendum](docs/V17_ORIGINAL_SCHEMA_OBSERVABILITY_ADDENDUM.md), [weather clock contract](docs/V17_ORIGINAL_WEATHER_CLOCK_ADMISSION.md), and [aggregate source receipt](validation_v17/results/source_observability_v17.json) are committed. [source CI](https://github.com/zuizui0223/boids/actions/runs/40617588626), [schema CI](https://github.com/zuizui0223/boids/actions/runs/40618193722), [clock CI](https://github.com/zuizui0223/boids/actions/runs/40618700050) passed. [Eight pure NOAA solar / wind-component tests](https://github.com/zuizui0223/boids/actions/runs/40618948563) also passed; they are mathematical known-truth tests, **not wild behavioral evidence**.

**Claim boundary:** **No new v17 GPS turning or wind × social effect has been fitted**, and no v17 biological conclusion is claimed. The 2019 experiment sampled visible-sun days and does not identify sun visibility variation. The original pair ledger is now verified, but supplies **only five** independent connected social groups. The absolute weather clock is unresolved and the predeclared ≥8-component confirmatory gate is not met. Do not fit the planned confirmatory wind × partner forecast on this same source; seek independent experiments with sufficient connected social groups. The separate v16 positive fast result, v15 negative fast result and v13 synthetic results remain frozen and distinct.

## v17-B: Original published pairing-network topology and exact train/test leakage

[PLOS Biology 2019 S3 Table](https://doi.org/10.1371/journal.pbio.3000299.s008), original 12,200-byte XLSX, independently downloaded and SHA256-pinned at `f06a89cdb0bb4df338337c1d2f459d7eee545289ede06904bc76114653981e84`. The two published pairing phases are each **ten reciprocal, non-overlapping dyads**. Their union is **five disconnected four-bird cycle graphs (C₄)**, each bird with two assigned direct partners (one per phase). This is original source network design, **not observed GPS steering**.

A naive random **4-of-20 bird-level test split** keeps entire experimental networks isolated in only **5 of C(20,4)=4,845** possible splits; **99.897%** cut a real assigned social network across train/test. A random 10-of-20 split is *always* network-leaky because all components are size four. These are **exploratory mathematical graph consequences**, not animal causal-effect sizes.

**Pre-registered confirmatory gate failed: 5 < 8 required independent components.** No v17 wind-gated social movement forecast was fitted; station weather clock remains unidentified. [Full original pairing graph](docs/V17_PUBLISHED_PAIR_GRAPH_RESULT.md) · [machine-readable original graph](validation_v17/results/original_s3_pair_graph_v17.json) · [passing S3 graph CI](https://github.com/zuizui0223/boids/actions/runs/40624331811).

## v17-C: Ten published transmission chains identified, original 1.23-GB source exceeds current admission cap

The independent [Valentini et al. 2021 eLife paper](https://doi.org/10.7554/eLife.68653) reports **ten** repeated social transmission chains across five paired generations; the [official Figshare article 14043362](https://doi.org/10.6084/m9.figshare.14043362) lists a **1,231,215,640-byte** `figshare.zip` (published MD5 `4f4a3cbe268562b14b19b04eaa325470`; CC BY 4.0). The original archive **was not downloaded** because it exceeded the precommitted bounded 160-MB source cap. Therefore the paper's ten-chain design, original raw GPS IDs/timestamps and environmental support remain **unverified in our source pipeline**, and no new behavioral endpoint can be reported. [Full source-only result](docs/V17C_TEN_CHAIN_SOURCE_RESULT.md) · [API receipt](validation_v17/results/ten_chain_original_metadata_v17.json) · [source metadata CI](https://github.com/zuizui0223/boids/actions/runs/40624919419).

An independently published **2026 alternative with 14 pigeon pairs** and a roughly 21-MB public GPS ZIP is recorded as a prospect in the same report; its actual independent pair/flight structure and weather conditions are not yet verified. Do not use these source-discovery facts to reverse the 2019 v17-B five-component stop or already opened v15/v16 field results.

## v17-D: Another independent 2026 pigeon dataset has 14 original disconnected pair groups (raw data source gate passed)

[Morford et al. 2026](https://doi.org/10.1038/s41598-026-39898-2) tested collective route memory using pigeon partners. Its original author [GitHub dataset and code](https://github.com/Morfordjoe/Collective-route-memories-in-homing-pigeons), pinned commit `8e4f7e48abfa57212c5207c28580003f0ef14210`, was **downloaded and hash-verified** by [original-source CI](https://github.com/zuizui0223/boids/actions/runs/40625385833). The pair ledger `CM info.csv` (348 bytes, SHA256 `8796f115d80f13b455704a2ad4c8710e23b18103ab0ba6d913c553fbd7342279`) identifies **14 nonoverlapping partner pairs = 28 unique individuals**, split 7:7 between assigned additional-training sites. The GPS ZIP `CM_trimmed.zip` (21,425,810 bytes, SHA256 `8e3f588ae927ab196f8c9dc9eebc9146bf656b344e68db8ba5f3c20d49edc3dc`) contains **426 actual GPS CSV trajectories** with a common original 18-column schema including `DT`, `Latitude`, `Longitude`, `Course`, `Speed.km.h.`, `DistRS` and `DistHome`. No raw track rows were read or redistributed for this source-quality audit.

**Important distinction:** The source's **14 disjoint pair components pass** the previously selected ≥8 social-group structural requirement, unlike 2019 Taylor's five connected C₄ components. But **no new observed memory prediction score has been fitted**, raw GPS time/observation quality needs another gate, its source telemetry reuse license is still unverified, and no wind-context data are established. This is a prospective **slow route-memory** independent field validation, not a rescue of the already failed 2019 confirmatory wind × neighbor study or a result about wild 3D resource niches. [Full source result](docs/V17D_INDEPENDENT_14_PAIR_MEMORY_SOURCE_RESULT.md) · [frozen source/eligibility contract](docs/V17D_INDEPENDENT_14_PAIR_MEMORY_SOURCE_CONTRACT.md) · [machine-readable original dataset receipt](validation_v17/results/2026_fourteen_pair_source_audit.json).

## v18: All-14-pair future GPS route-memory benchmark stops on original missing target (no behavioral scores)

The [v18 outcome-blind contract](docs/V18_FROZEN_14PAIR_MEMORY_FORECAST_CONTRACT.md) prespecified training-only `TR` route templates and held-out `CM` future-memory route bearings at fixed 250–2000m distance shells, comparing same-release-site other-pair, own-pair and own-individual histories on **all 14** independent original 2026 Morford pigeon pairs. [Source-only audit](https://github.com/zuizui0223/boids/actions/runs/40626226608) checked all 426 original filenames, including 19 author-native `Checked`/`pair*` labels; no GPS movement target was examined while repairing source grammar.

The [source/eligibility-verified run](https://github.com/zuizui0223/boids/actions/runs/40626313864) passed 10 known-truth tests but the precommitted source gate **NOT ADMITTED**: original pair **O19** has historical TR at both LH and SH (10/14 files respectively) but **no later CM file at either site**. No 14-pair memory gain or prediction errors were computed. [Complete frozen stop](docs/V18_FROZEN_FOURTEEN_PAIR_ROUTE_STOP_RESULT.md) · [machine-readable all pair/site file counts](validation_v18/results/frozen_14pair_source_stop_v18.json).

A **separate 13-pair complete-case exploratory** test may be preregistered based solely on this pre-behavior source availability audit. Do not quietly relax or rewrite the original v18 all-14 rule after the fact.

## v19: Observed original 2026 pigeon memory-test GPS — individual history beats own-pair average, not the population baseline (exploratory)

The [original v18 all-14-pair protocol](docs/V18_FROZEN_FOURTEEN_PAIR_ROUTE_STOP_RESULT.md) remains **NOT ADMITTED**, because one original pair O19 lacked any CM future memory-test GPS tracks. A separate [v19 post-source-availability exploratory protocol](docs/V19_EXPLORATORY_COMPLETECASE_13PAIR_MEMORY_CONTRACT.md), frozen before GPS movement outcomes, evaluated the **other 13 original independent pairs**; O19's TR history remained in population reference training. The same original author-pinned `CM_trimmed.zip` (21,425,810 bytes, SHA256 `8e3f588ae927ab196f8c9dc9eebc9146bf656b344e68db8ba5f3c20d49edc3dc`) and 426 source CSV tracks were retained; 72 eligible future CM files gave **576 measured radial-shell route bearing targets**, without synthesized GPS fixes.

- **Group historical route versus other-pair/site population:** MSE(M0) − MSE(M1) **−0.055778 rad²**, 6/13 pairs positive, whole-pair 95% [−0.325982,+0.179685]; no general group-history benefit.
- **Personal history versus pair history:** MSE(M1) − MSE(M2) **+0.045130 rad²**, 9/13 pairs positive, whole-pair bootstrap 95% **[+0.007902,+0.099253]**; positive *exploratory conditional* individual-history increment. This does **not** establish neural memory/social causation or a cross-species niche law.
- **Important hierarchy guard:** absolute equal-pair MSEs were **M0 population 0.860210 (best)**, M1 own pair 0.915988, M2 own individual 0.870859 rad². So individual history beat the weaker pair historical template **but did not beat the population baseline on average**. A 9/13 one-sided exact sign test is ≈0.133; bootstrap gain interval positivity should not be overstated as uniform replication.
- [Full original source, per-pair results, and limits](docs/V19_OBSERVED_COMPLETECASE_13PAIR_MEMORY_RESULT.md) · [aggregate-only source-backed JSON](validation_v19/results/frozen_thirteen_pair_aggregate_v19.json) · [passing no-leakage/real-source CI](https://github.com/zuizui0223/boids/actions/runs/40626721143).

This study is about route-navigation prediction from authored, previously processed GPS data. It does **not** measure 3D food niches, GPS-altitude measurement error, ecological competition, actual learned Boids forces, or wind/solar visibility. All earlier v15/v16 observed endpoints and v17-B five-network stop remain unchanged.

## v20: Wild guineafowl historical group space-use predicts next-season spatial fidelity (original published-derived ecological data)

[Papageorgiou & Farine (2020)](https://doi.org/10.7554/eLife.59902), original freely accessible derived group-season file, author commit `15ea08ed10555beba227792f4ef106d87d52b6a4`, original Rdata SHA256 `c6a534993e99f2cb324e9691ff7ec58095bf7cd7e82d7a38721f3575097cbb55`. **45 group×season observations from 21 original social groups in five seasons**, 15 groups with repeat observations in ≥2 seasons. This is a separate wild species and source from all pigeon v15–v19 data. Raw Movebank GPS is **not accessible without study permission**, and no raw GPS was downloaded.

In a [pre-outcome frozen next-season prediction](docs/V20_FROZEN_GROUP_SEASON_FIDELITY_FORECAST.md), M0 uses **prior seasons of OTHER groups**, M1 same-group prior seasons, and M2 combines them with fixed historical shrinkage weight `w=n/(n+2)`. Exactly **15 group IDs / 24 future group-season cells** met the source-only eligibility gate.

- **Primary group spatial-fidelity forecast:** equal-group MSE M0 external **0.0105669**, M1 own **0.0072165**, M2 fixed shrink **0.0079186**. The preregistered M0−M2 gain was **+0.0026483 fidelity²**, **11/15** positive groups, whole-group bootstrap 95% **[+0.000618,+0.004493]**, ~**25.1%** lower MSE. This is an **exploratory numerical prediction result on published group-season summary data**, not a cognitive-memory proof; 11/15 exact one-sided sign `p=0.0592`, and fixed shrinkage was not shown to beat the numerically best unpooled own-group history.
- **Other registered indicators:** log(core home-range area) +0.1312 (10/15 positive), log(group movement speed) +0.00211 (7/15), but their group-bootstrap intervals overlap zero. No cross-trait universal predictive improvement identified.
- An explicitly **post-outcome** all-season/leave-one-group-out audit reproduced the original primary. All four eligible source seasons D–G showed positive point estimates but some have only 2–6 group-season targets; these diagnostic observations are not confirmatory and the 15 groups experience shared environmental seasons.
- [Full new observed result and scientific boundaries](docs/V20_OBSERVED_WILD_GROUP_FIDELITY_RESULT.md) · [source+model+audit reproduction](validation_v20/) · [aggregate-only exact results](validation_v20/results/forward_group_fidelity_v20.json) · [main original CI 40628278255](https://github.com/zuizui0223/boids/actions/runs/40628278255).

**No climate or habitat-availability predictors were actually used**: the comparator is prior OTHER-group spatial-state history. Individual learning, true competition, resource patches, actual environmental forcing, 3D movement and identified Reynolds/Boids forces all remain untested. The v19 pigeon finding of personal-vs-pair route information and v20 wild group fidelity are **different endpoints with different units**, not a single universal social-memory law.

## v21: Original individual-redstart foray × NDVI source is source-access **NOT ADMITTED**

Independent Jamaican American redstart dataset, Dossman et al. 2024 [Dryad 10.5061/dryad.gb5mkkwx1](https://doi.org/10.5061/dryad.gb5mkkwx1), published version **5**, license **CC0**. The **official original Dryad metadata and complete file manifest** were verified: original `forays.rds` **971 bytes**, published SHA256 `a1457fe03d6a454210e019c96724e60b8aa6ba30f124128714e035d20052b3b9`; `ndvi.rds` **2,245 bytes**, published SHA256 `0ee6605fe491b2be2917f5c3c1c1123c2ff180ca36921c101f069282683069c1`. **The RDS bytes themselves were NOT obtained:** official anonymous download paths returned HTTP 401/403. Later metadata retrieval also returned 403. No individual-week grain, original numeric NDVI, future foray target or model result has been inspected or invented. [Complete no-source-access result](docs/V21_ORIGINAL_REDSTART_NDVI_SOURCE_RESULT.md) · [source receipt](validation_v21/results/source_gate_v21.json) · [source API CI](https://github.com/zuizui0223/boids/actions/runs/40635763390).

The new independent data would allow **individual history versus measured vegetation** validation if authenticated official access becomes possible; source `pred` (smoothed NDVI) must not be used prospectively due to potential future-information leakage. An additional 2021 wild guineafowl seasonality source has public environment categories, but it **shares original group/season cohorts with v20** and cannot be called independent biological confirmation; exact overlap must be audited separately.

## v22: Explicit wet/dry environment context can prevent overtrusting historical group states (same wild population, exploratory)

[2021 author-derived guineafowl seasonality dataset](https://github.com/DanPapageorgiou/ranging_seasonality) at pinned Git commit `2a3aec308bb4a8449d1eeb16beed4aff8f387116` (same **Avulturinum_Farine** Movebank population as v20, so **NOT independent biological replication**). Three public Rdata files have been source-hash verified; day-to-day fidelity source `df_dhor.Rdata`, SHA256 `d08864e91a543403cb1e8abf1bf9ea84247543181b8d4f4464ceb03929c0fa83`, contains **143 original source group×season rows, 26 group IDs, 11 seasons, 4 missing fidelity responses**, and season-wide **dry/intermediate/wet/wet_breeding** categories. No raw GPS, numerical rainfall, individual memory, prey-use or actual social contacts were measured by the v22 workflow.

The [predeclared v22 predictor comparison](docs/V22_FROZEN_WET_DRY_CONTEXT_GROUP_PREDICTION.md) scored **113 heldout original group×season fidelity targets from 23 groups**, comparing M0 historical OTHER groups; ME prior OTHER groups with matching observed target-season regime; MG own group past; and MEG shrinkage `w=n/(n+2)` of own history toward ME. **29/113** ME cases needed fixed support-driven fallback M0; all four models score the same future response values. The original target-season environment label is a **known conditional scenario**, not a weather forecast available before the season.

- Absolute equal-group MSE: M0 **0.003818**, ME **0.003615**, MG **0.005485**, **MEG 0.003292 (lowest)**.
- **Primary, MG added to ME:** gain +0.000322, only **11/23** groups positive, whole-group CI **[−0.000592,+0.001246]** — not robustly established. Pure regime ME versus M0 gain +0.000203, **12/23**, CI includes zero.
- **Registered secondary, fixed shrink over unpooled own group MG:** gain **+0.002192**, **18/23** positive, group-bootstrap 95% **[+0.000544,+0.004153]**. This is exploratory evidence that historical group state can be overtrusted, not evidence for an optimal biological learning coefficient or a universal law. The wet_breeding category also couples the wet season with breeding state.

[Full numerical result, all group/season effects and limits](docs/V22_OBSERVED_GUINEAFOWL_ENVIRONMENT_HISTORY_RESULT.md) · [reproducible code](validation_v22/) · [group/season source and model JSON](validation_v22/results/regime_group_history_forecast_v22.json) · [successful actual-data CI 40636440228](https://github.com/zuizui0223/boids/actions/runs/40636440228). Distinct v20 fidelity result and v21 Dryad source block remain unchanged. Future independent validation needs genuinely **different wild groups and measured resource/climate variables**, not recasting two analyses of the same population as replication.

## v23: First independent original wild duck GPS + preceding-day ERA5 context demonstrates repeatable individual-level predictive information

A new original source entirely independent of the previous pigeon and guineafowl experiments: [van Toor and Waldenström 2025 original Zenodo 16940654](https://zenodo.org/records/16940654), source GPS CSV 46,324,165 bytes (exact original SHA256 001ec8ffe1e9be5258129dfb931b0abd6551785080e2c755cbd4c72cd79ec52e). Source-only inspection verified 294,683 raw GPS rows, 181 original study×individual IDs, seven taxon labels, five study groups, and 154 birds with at least 14 separately recorded UTC days. The separately pinned [ERA5 historical weather source](docs/V23_ERA5_SOURCE_CANONICAL_PIN.md) supplies 1,826 prior-weather days at **two independently selected Bangladesh wetland grids**, UTC aligned and with no meteorological gaps. ERA5 is gridded weather reanalysis, **not observed prey/resources**.

The [pre-outcome model contract](docs/V23_FROZEN_DUCK_DAILY_GPS_ERA5_FORECAST.md) predicted future-day original-GPS **log daily radius of gyration** (within-day horizontal spatial spread), only for original Bangladesh ducks whose **previous GPS fix** lay within 120 km of the original preselected wetland reference points. Strict fixed GPS quality, prior-day weather and past history gates yielded **49 independent bird IDs / 2,664 future daily targets**. Four models scored identical target days: M0 previous other birds, ME previous other birds of same preceding-day rain/temperature class, MI own history of previous 3–14 days, MEI fixed shrink into ME with w=n/(n+2).

- **Primary positive predictive information:** equal-bird MSE **ME 0.520229 vs MEI 0.347095**, difference **+0.173134** in squared transformed log-km errors, 44/49 birds positive, whole-bird 95% bootstrap **[+0.111878,+0.240944]**, **33.28%** lower relative MSE. [Full independent observed result](docs/V23_OBSERVED_INDEPENDENT_DUCK_ERA5_RESULT.md).
- **Important nonrobust effects:** gridded prior-day weather class alone M0−ME **−0.001258** (21/49 positive; interval overlaps zero); shrinkage on top of unpooled individual history MI−MEI **+0.001081** (34/49 positive; interval overlaps zero). Absolute mean MSE M0 **0.518971**, ME **0.520229**, MI **0.348176**, MEI **0.347095**.
- The source's 49 birds span seven taxon labels **very unevenly**, with 29 garganey. Species/sex/age/habitat differences, study-year climate dependence and original GPS observation processes were not fully controlled. This is **repeatable individual history forecasting**, not proof of cognitive memory, climate causality, social contacts, individual niche partition, or recovered Boids/Reynolds motor forces. Weather was ERA5 reanalysis not original local field gauges, and no resource availability baseline was independently measured.
- [Reproducible original GPS/weather source and forecast code](validation_v23/) · [full 49-bird aggregate numerical receipt](validation_v23/results/independent_duck_daily_ERA5_forecast_v23.json) · [original passing actual-data CI 40804057488](https://github.com/zuizui0223/boids/actions/runs/40804057488). Old v13–v22 results remain frozen.

**Information hierarchy implication:** the utility of private movement history can transfer to an entirely new wild telemetry source, but neither coarse gridded climate bins nor the previously frozen shrinkage rule is demonstrated to add robust predictive value. These endpoints do not yet identify a common social-motor mechanism. The next independent field study should measure prior environmental resource availability, taxon/demographic information and actual contact networks before attempting a combined Boids force/niche theory.

## v24: Original USGS wetland-use predictor transfers to heldout broods, but private wetland history is NOT observable

Independent 2026 [USGS Peterson & Ackerman Suisun Marsh duckling release](https://doi.org/10.5066/P13NYGAI), original CC0 sources, 2016–2019. Both original CSVs and FGDC were checksum-verified. Source wetland-selection data include **185 original radio brood IDs**, **2,069 used locations** and **74,000 computer-generated availability points (400 per brood, nest radius 2.4km)**, plus wetland type, dominant vegetation, vegetation cover, salinity and flooded area. The original separate movement source has **2,039 radio brood-age/nest-distance rows** (188 brood IDs, 185 overlapping selection), but **NO original Wetland ID**. Habitat selection has **NO original visit dates/ages**, and all generated available points have Wetland ID unavailable, so **a matched time-ordered private wetland-revisit prediction cannot be computed**. [Frozen original v24 temporal STOP and data-quality audit](docs/V24_OBSERVED_USGS_DUCKLING_HABITAT_RESULT.md).

A DISTINCT static environmental habitat used-versus-generated-available model was registered before opening source numeric habitat predictor values. Independent **brood-blocked five-fold** evaluation kept each of the 185 radio brood IDs entirely out of training, comparing used points against that brood's original 400 generated available points:
- Uniform baseline within-brood ranking AUC **0.5000**; environmental 5-covariate M1 AUC **0.61265**, improvement **+0.11265** in **126/185** broods, 10k original brood bootstrap 95% **[+0.08054,+0.14413]**.
- Original sampled pseudo-choice log loss **5.99396 uniform vs 5.91135 environmental** (gain +0.08261 nats, 95% [+0.03143,+0.13277]); **this is not a genuine choice of 1 of 401 separately recorded wetlands**, since original available source points are generated spatial samples.
- Source species-by-environment interaction model did **not** robustly improve over plain ecology (ΔAUC −0.01241; 95% [−0.02593,+0.00168]).
- Entire-year heldout environmental AUC **2016 .58285**, **2017 .60925**, **2018 .54817**, **2019 .60958**; in **2018**, sample pseudo-choice log loss **6.01049** was **worse** than the null **5.99396**. Year/site transfer is limited.

[Full source-backed 185-brood results, source checksums, scientific limits](docs/V24_OBSERVED_USGS_DUCKLING_HABITAT_RESULT.md) · [reproduction code/source and synthetic tests](validation_v24/) · [anonymized full brood/year numeric receipt](validation_v24/results/static_brood_habitat_preference_v24.json) · [successful real source/model CI 40808140284](https://github.com/zuizui0223/boids/actions/runs/40808140284). **This supports transferable environmental ranking in one landscape, NOT chronological individual memory, resource intake/fitness, social interactions or Boids/Reynolds forces.** Previous v23 wild duck movement-spread predictive result is a different field source/metric, and v13–v23 endpoints remain unchanged.

## v25: Original four-waterfowl habitat-profile source exposed a **spurious 100% classifier**; corrected private-history increment **not supported**

Independent 2023 USGS Overton & Casazza original [DOI 10.5066/P9ELSUHN](https://doi.org/10.5066/P9ELSUHN), original source `Data Release P9ELSUHN.csv` **27,997,528 bytes**, MD5 `78eb6064eca992225d6907d6e46f5bef` and independently verified SHA256 `1a5c2342f9df4c70f170741c14b92b5146f0558f29fd593307768a228b82ca15`. The original data have **380,578 rows = 190,289 `birdyear × timestamp` pairs**, one TRUE (observed used habitat) and one FALSE (**aggregate** frequencies for 100 author-simulated alternative steps) per pair, **493** original birdyear tokens across four waterfowl taxa. There are **NO** original 100 destination positions or original step-start GPS coordinates in this published CSV, so the test is **retrospective paired habitat-profile ranking, not true prospective location/choice forecasting**. The full-source movement kernel may already include heldout animal trajectories.

- A separate Tennessee original Mallard Dryad [10.5061/dryad.cjsxksnd5](https://doi.org/10.5061/dryad.cjsxksnd5) source was metadata/hash-inventory verified (v4, CC0) but original RDS/README download returned HTTP401/403, so **NO Tennessee Mallard habitat model was fitted**.
- **Critical source-unit artifact:** Original TRUE has precisely one nonzero habitat category raw count **1 or 2**, whereas FALSE contains aggregated **100 candidate habitat counts** raw 0–100. The v25-C raw [0,1] source gate stopped; the separately tested v25-D incorrectly divided BOTH cases by 100 and generated **mathematically spurious 100% case separation**, falsely apparent positive private history. The explicitly post-outcome v25-E audit showed every FALSE row had a larger seven-field sum, norm and maximum than its paired TRUE. **v25-D is INVALID FOR ECOLOGICAL INTERPRETATION and retained only as a reproducible bias-failure mode**, not cited as independent evidence of memory.
- A distinct, clearly **post-source-outcome-conditioned exploratory** v25-F corrected source meaning, preserving all original 190,289 pairs: TRUE single used category becomes one-hot **1**, FALSE original generated count becomes proportion **count/100**. All original v25-C modeling/whole-birdyear folds and history rules were reused unchanged. **492** eligible birdyear tokens, **188,812** later paired profiles. M0 null pseudo log loss **0.693147**, M1 pooled habitat **0.602916**, M2 habitat + taxon interactions **0.595042** (best), M3 pooled environment + earlier same-birdyear profile history **0.611741**. Rank fractions M1 **0.8145**, M2 **0.8161**, M3 **0.7476** (not 100% after correction).
- **Corrected PRIMARY source-habitat-history contrast M1−M3 = −0.008825**, positive only **196/492**, 10,000 whole-birdyear bootstrap 95% **[−0.018191,+0.000810]**: personal past-habitat-profile gain **not supported**, not proof that birds lack cognition. Common ecological-profile M0−M1 +**0.090231** (420/492, 95% [+0.079754,+0.100476]) and source taxon-specific slopes M1−M2 +**0.007875** (310/492, CI [+0.004963,+0.010909]); these are **source-designed paired-proxy predictability**, not causal resource preferences/Boids laws.
- [Full original-source result and artifact correction](docs/V25_OBSERVED_SOURCE_CORRECTION_AND_HABITAT_PROFILE_RESULT.md) · [all original 492-birdyear corrected data-only scores](validation_v25/results/case_corrected_paired_habitat_v25F.json) · [SOURCE construction audit proving v25-D invalid](validation_v25/results/postresult_source_artifact_v25E.json) · [reproducible A–F source/model tests](validation_v25/) · [original corrected model successful CI 40842443398](https://github.com/zuizui0223/boids/actions/runs/40842443398).

**Biogeographical implication:** independent previous v23 duck GPS showed a private movement *spread* history increment, whereas v25 corrected same-birdyear previous *habitat-profile* association does not add reliably beyond common environment slopes. Different targets/source generations make these non-comparable as one biological learning law. **Source observation construction matters as much as Boids motion rules**; no robust learned-foraging niche or social force has yet been recovered across these studies. Frozen v13–v24 observed results remain untouched.

## v26: Verified independent original sea turtle steps and global mammal sources; source identifiability prevents new choice claims

The independently original USGS [2020 marine turtle step-selection source](https://doi.org/10.5066/P9UZU4GG) was **actually downloaded**, exact published MD5 matched and independent original SHA256 computed (`eef4d2dd16c97cd0d8722ed1cac8a031cf3dd336404b2e8e4c085cb2fadd4ec0`). Its **420,365 original CSV rows** have 11 fields including PIT, step ID, start/end time, protection status, water depth and chlorophyll. Verified metadata-only inspection found **23 PIT identity tokens**, all spanning ≥3 calendar days, **26,997 PIT×step-ID keys**, usually 16 source rows per key, with **382,560 rows concentrated in one PIT token**. Source has **NO explicit used/available case column**. The separately published FGDC file's downloaded MD5 did not match its provider MD5. Thus **actual habitat choice is NOT ADMITTED**: no chosen-versus-random step can be reliably labeled, and no sea turtle habitat model effect was fitted. [Complete original-source audit, results and caveats](docs/V26_INDEPENDENT_ORIGINAL_SOURCE_ADMISSION_RESULT.md) · [source-backed scripts/receipts](validation_v26/).

The [2026 48-species terrestrial mammal](https://doi.org/10.5281/zenodo.15756163) original Zenodo source declares **1,788,505,978-byte** data ZIP; the [bank vole concurrent movement study](https://doi.org/10.5281/zenodo.10101651) original data ZIP is **662,165,095 bytes**. Both exceed the pre-frozen 250MB per-file source cap and were **not** downloaded. The mammal original **3,580-byte README was independently MD5-verified** and describes nested individual iSSA step tables with explicit `case_` TRUE used / FALSE available and NDVI, road distance, population density and terrain features. These descriptions are *not* newly measured cross-species habitat effects. All five v26 source provenance/format workflows passed; all v13–v25 results remain unchanged.

**Research lesson:** Original source design and an actual observed choice label are prerequisites for any genuine use-versus-availability inference. Repeated GPS steps, attractive habitat variables or an article's description of candidate generation do not supply missing case labels or independent PIT/network units. Avoid retrospective surrogates masquerading as prospective ecological niche forecasts.

## v27: Original long-tailed tit pair + sampled-tree source license/files verified but source bytes unavailable

Independent published 2026 long-tailed tit study [Dryad DOI 10.5061/dryad.kprr4xhm0](https://doi.org/10.5061/dryad.kprr4xhm0), [paper](https://doi.org/10.1111/2041-210x.70316), describes 18 jointly moving breeding pairs and independently sampled tree availability. Official Dryad source metadata verified **version 4, CC0, five source files** (`GPS_LOCATIONS.csv` 136,016 bytes, `NestLocations.csv` 7,742, `Tree_Availability_Data.csv` 128,484, `TREE_SAMPLING_LOCATIONS.csv` 8,431, `README.md` 2,123), each with provider-published SHA256. However **all 5 original file GETs failed** (Dryad API HTTP 401, provider file stream HTTP 403), so NO original pair IDs/times/locations, tree cover or new prediction were inspected or fitted. [Full original source-access receipt and limits](docs/V27_ORIGINAL_TIT_TREE_SOURCE_RESULT.md) · [CI source audit](https://github.com/zuizui0223/boids/actions/runs/40850950358). Prior v13–v26 findings remain unchanged.

## Cross-project positioning

- [batter](https://github.com/zuizui0223/batter): persistent bat-specific vertical strategies without obligatory additional spatial segregation.
- [ODSP](https://github.com/zuizui0223/odsp): niche thickness versus transferable vertical/temporal state organization.
- [mina](https://github.com/zuizui0223/mina): concentration of penguin breeding components as abundance declines.
- [louis](https://github.com/zuizui0223/louis): within-home-range hydrological state buffering in King Rails.

The four repositories provide separate empirical results. **boids is a mechanistic bridge and an independent prediction-validation programme, not a replacement for their frozen analyses.**

## Licence and release boundary

No licence is assigned by this migration. Research source attribution and original upstream dataset licences must be verified before republishing or redistributing any raw biological records. No raw animal GPS records are included in this repository snapshot.
