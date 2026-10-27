# v14 outcome-blind public source admission — completed structural result

**Date:** 2026-10-28 JST. **Result type:** observed-source quality, not a movement model or ecological effect. The previous v6/v8 observational primary outcomes and v13 synthetic outcomes are unchanged.

**Executable original-source audit:** [v14 source code](../validation_v14/) · [successful GitHub Actions run 40541344970](https://github.com/zuizui0223/boids/actions/runs/40541344970) · 16/16 offline source/parser/no-leakage tests passed. The run publishes a temporary aggregate-only JSON source receipt; raw animal tracks were discarded, not committed or redistributed.

## 1. Independent 2026 pigeon data: physical acquisition and integrity

Original authors: Huang, Li, Shang & Yang (2026), *Raw GPS and Attitude/IMU Data from Three Homing-Flight Trials of Pigeon Flocks*, Zenodo **DOI 10.5281/zenodo.21092705**, version **1.0.0**, released 2026-07-01, **CC BY 4.0**.

| Property | Original verified value |
|---|---|
| Download archive | `pigeon_homing_public_trials_v1.0.0.zip` |
| Exact bytes | **126,588,691** |
| Source MD5 and observed MD5 | `5c1e9b386bff5794e177b122b1fcb244` (match) |
| Locally computed ZIP SHA256 | `756eed718ad13c14233e60b19009ce0916f183eb540b1262ba030ebc25a0ab03` |
| Internal ZIP | 62 members; 489,034,466 total reported uncompressed bytes |
| Source SHA256 manifest | 61 entries |
| Sensor-file checksum verification | **56 / 56 match** (28 raw NMEA GPS and 28 attitude/IMU files) |
| Independent raw flock-flight episodes | **3** |
| Bird-trial records | 7, 11, 10 |
| Distinct `SB` identity tags | **13** |
| Identifiers present in ≥2 episodes | **11** |
| Identifiers present in all 3 episodes | **4** |

**Independence caution:** the 28 GPS files are *bird-trial observations*, not 28 independent full flock trials, and the 121 bird pairs share trials and individual identities. Even a unanimous 3/3 trial-level gain in a sign test yields minimum one-sided `p=0.125`.

## 2. Raw GPS, time support and structural co-observation

Source `DATA_DESCRIPTION.md` describes headerless NMEA device logs; valid `$GNRMC` records provide UTC, latitude, longitude, GPS ground speed and track heading. GPS nominal rate ~10 Hz; IMU nominal ~100 Hz. Source preprocessing explicitly repairs repeated/missing GPS timestamps. **This audit reads only the original RMC UTC and positions, performs no timestamp interpolation, and uses no inferred height.**

| Observability property | Trial 1 | Trial 2 | Trial 3 | Combined |
|---|---:|---:|---:|---:|
| GPS files | 7 | 11 | 10 | 28 |
| Original NMEA text lines | 16,302 | 255,551 | 19,319 | 291,172 |
| Valid and distinct UTC fixes | 16,302 | 235,676 | 19,319 | **271,297** |
| Invalid-positioning status | 0 | 19,833 | 0 | 19,833 |
| Other malformed/non-RMC lines | 0 | 42 | 0 | 42 |
| Within-trial bird-pairs with ≥50 valid fixes each | 21 | 55 | 45 | 121 |

- Median of each GPS file's observed positive UTC spacing medians: **0.1 seconds**.
- Trial 2 contributed **86.9% of all valid GPS fixes**. Treating fixes or dyads as independent biological replicates would heavily overstate effective sample size.
- Original pairwise co-observation audit across all 121 dyads found **1,168,985** directional nearest-UTC correspondences within **≤0.2 s** and **1,161,053** within **≤0.2 s AND ≤100 m**. Of these, **910,064** were also ≤10 m.
- These are **algorithmic observation opportunities**, each an A-fix paired to the nearest measured B-fix; they are **not independent synchronized social events, not fitted social force and not confirmed in-flight**. The source logs may include takeoff/landing/stationary segments. Trial-specific speed-based flight gating and acquisition-error checks are mandatory before any behavioral forecast.
- The source NMEA `$GNRMC` provides **no measured altitude**. IMU attitude is not a substitute for absolute 3D positioning. Any claim of measured `I(S;Z|XY)` would be unsupported here.

### Explicit source gate results

| Proposed endpoint | Admission decision | Rationale |
|---|---|---|
| Raw source integrity and 2D time/proximity observability | **PASS, source-level** | 56/56 individual files match declared SHA256; plentiful true raw UTC records |
| Confirmatory flock-level social-force prediction | **NOT ADMITTED** | Only 3 independent flight episodes, no observation-error calibration, unfiltered pre/post-flight GPS; no defensible cluster-level significance |
| Exploratory short-step horizontal social predictor comparison | **Potentially feasible, no predictions yet** | Requires fixed in-flight/speed/clock support and matched own/current/stale/ghost predictors with held-out whole trials |
| Stable individual preference or socially inherited memory | **NOT ADMITTED** | Only three episodes and no independently observed individual reward history |
| 3D niche / altitude partition | **NOT ADMITTED** | No calibrated GPS altitude |
| Rewiring-mediated population/individual niche shift (v13) | **NOT ADMITTED** | Different observed flock compositions do not constitute independently manipulated partner networks |

## 3. Independent 2025 repeated-flock habitat GPS Dryad candidate

Mehlhausen-Franks (2025), Dryad `10.5061/dryad.4tmpg4fp6`, original processed dataset version `406157`, file `4448091`, reported CSV size **35,505,714** bytes, declared SHA256 `c5d5ce1d43e72e9ceb79f3f1d4c509bb2e99026c78f3ce0c207987b1cf2497f3`, **CC0**.

The API, browser file_stream and legacy stash routes were tried without credentials. **No data file was returned**. The API file download responded **HTTP 401**; no row-level QC, timestamp disambiguation, or horizontal individual-history predictions have been completed. Do not claim raw-data reproduction or use the reported file SHA256 as independently matched; it is metadata-only.

## 4. What this changes for the Boids programme

Previously the archived Tadarida source supplied zero close 5-s/100-m cross-bat pairs, rendering short-range social forces unobservable. The **independent NMEA pigeon source now shows substantial 2D pairwise observation opportunities using non-interpolated clocks**, though only in 3 flock-flight trials. Therefore **structural observability, not demonstrated predictive social force**, is the newly improved aspect.

This source can motivate a carefully labeled exploratory leave-one-trial-out **horizontal turning** study with matched negatives. A meaningful v13 ecological-niche hierarchy validation still requires genuinely repeated multiday animal identities, measured network change, resource/habitat context, and enough independent groups/sites. Do not mistake successful timing QC for support of an animal-learning mechanism.

## 5. Next independent analysis requirements (no effect sizes pre-viewed)

1. Freeze source ZIP SHA256, member digests and exact trial IDs. Audit speed-filtered airborne segments and flight-only contemporaneous co-observation at predeclared ≤0.2/1/5-s and ≤10/25/100-m windows. Report changed denominator by trial.
2. Freeze whole-trial exploratory next-turn forecast contract: matched own-only / actual-current-neighbor / 10-second-stale-same-neighbor / ghost-neighbor designs, feature definitions, clock uncertainty, training-only standardization, ridge penalty, and identical held-out targets across competitors.
3. Explicitly restrict result claim to *within-source short-horizon horizontal kinematics*. Do not derive Boids law recovery, competitive niche segregation, 3D height niches, or transferability across bat and bird taxa from this small sample.
4. Expand independent source replication before upgrading to confirmatory wild-animal inference.

Original prior outcomes: v6 3D bat-pair and v8 pigeon real-current versus strong negative-control forecasts were **not supported**; those results remain frozen.
