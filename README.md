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

## Cross-project positioning

- [batter](https://github.com/zuizui0223/batter): persistent bat-specific vertical strategies without obligatory additional spatial segregation.
- [ODSP](https://github.com/zuizui0223/odsp): niche thickness versus transferable vertical/temporal state organization.
- [mina](https://github.com/zuizui0223/mina): concentration of penguin breeding components as abundance declines.
- [louis](https://github.com/zuizui0223/louis): within-home-range hydrological state buffering in King Rails.

The four repositories provide separate empirical results. **boids is a mechanistic bridge and an independent prediction-validation programme, not a replacement for their frozen analyses.**

## Licence and release boundary

No licence is assigned by this migration. Research source attribution and original upstream dataset licences must be verified before republishing or redistributing any raw biological records. No raw animal GPS records are included in this repository snapshot.
