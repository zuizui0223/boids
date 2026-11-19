# v30 Carollia original absolute-beam heldout forecast — FROZEN PRIMARY NOT SUPPORTED

**Finished:** 2026-11-19 JST  
**Workflow:** [44444921438](https://github.com/zuizui0223/boids/actions/runs/44444921438) — successful end-to-end source hash, 5 leakage/known-truth unit tests, one frozen primary fit, full result JSON stored as artifact \`boids-v30-frozen-carollia-absolute-beam-heldout\` (original source raw arrays excluded).  
**Exact source:** \`00keveland/Tunnel_2026@59928a71887d521fec143080b0b187736c046a0e\` with 30/30 original Git-blob hashes verified.  
**Pre-outcome contract:** \`docs/BAT_ACTIVE_SENSING_CAROLLIA_HELDOUT_CONTRACT_V30.md\`, committed before the numeric heading-change outcome was opened. **No after-outcome retuning or subset rescue.**

## Frozen primary

The structural gate passed **8 bat labels** and **1,207 eligible next-original-call events** from all 30 source trials. Exclusions were 434 invalid pre-event quality/kinematic candidate events and 113 invalid next raw-displacement target events. The original eight bat labels were C1–C8, not eight species or eight independent field sites.

Primary prediction: leave-one-bat-label-out signed next-call heading-change regression (wrapped squared radian error). M0 used only prior raw-call kinematics and coordinates. M1 added absolute fitted sonar beam azimuth from the target call (not future-contaminated \`beam.rel_deg\`). Both were identical fixed train-only standardized Ridge(alpha=1.0) models and scored on identical test rows.

| Endpoint | Equal-bat result |
| --- | ---: |
| M0 (prior motor only) MSE | **1.483968 rad²** |
| M1 (motor + absolute acoustic beam) MSE | **1.493075 rad²** |
| Primary MSE(M0)−MSE(M1) | **−0.0091074 rad²** |
| Whole-label bootstrap 95% interval | **[−0.020811, +0.003412]** |
| Labels with positive M1 gain | **3/8** |
| One-sided exact positive-label sign p | **0.855469** |
| Predeclared positive primary criterion | **FAIL** |

Per-label primary gains (MSE saved, positive = acoustic model better):

- C1 −0.036235 (35 eligible events)
- C2 −0.013096 (72)
- C3 −0.027043 (133)
- C4 +0.002230 (202)
- C5 +0.004610 (240)
- C6 −0.009927 (216)
- C7 −0.016906 (107)
- C8 +0.023508 (202)

This is a direct **failure to support incremental out-of-bat predictive information from this specific absolute-azimuth feature**, beyond a prior-movement predictor on this processed source. It is **not evidence that sensory orientation is absent** or an independent falsification of the published ~70% Carollia future-turn-direction association: the targets, baselines, and sample units differ. Note also that shared ultrasound-array measurement errors and author-designed corridor effects remain potential limitations.

## Fixed secondary diagnostics — not rescue

- Three-calls-old beam replacing current beam on the matched 1,207 events: +0.003414 mean gain versus motor-only, while current beam was −0.009107. This **does not** make older beam a confirmed advantage; secondary direction was not null-calibrated as a new primary and is open to history/measurement confounding. No lag scan was opened.
- Whole-source-date transfer: withholding all 2023-12-16 trials (442 events) gave gain −0.014649 rad²; withholding 2023-12-22 (765 events) gave −0.002528 rad². Both are negative for the acoustic addition under this predictor. Only two source dates exist, so do not claim population-level portability or universal absence.

## Biological and statistical boundaries

- Both M0 and M1 forecast the same next **call-to-call angular change**, not experimentally manipulated sonar sensing or confirmed feeding effort.
- The saved \`beam.rel_deg\` embeds future-smoothed-track heading and was excluded entirely, as fixed before this run.
- \`XYZ_raw\` and fitted \`az_rad\` are both obtained through the published acoustic localization pipeline; model comparison does not identify causal sensory control, real-world calibrated motor latency or the physically complete q ratio.
- Reported uncertainty resamples whole bat labels, not thousands of non-independent call pairs; the source contains only eight labels on two dates.
- Negative M1 result is retained and **must not be turned positive** through post-hoc thresholds, alternative endpoints, lag windows, feature transformations, one-sided sign reversals, subsets or species-unsafe pooling.
- A bat-wide sensory-motor law needs a *new independent source* with original simultaneous audio, independent 3-D trajectory and externally calibrated sensory availability/geometry, not additional re-exploration of this source.

## Next action

Advance a source-only independent bat sonic interference / motor-history archive admission gate (PNAS 2025 \`Rhinopoma microphyllum\` Mendeley DOI \`10.17632/k7pt2j84f7.1\`). Before choosing a comparable model, verify independent acoustic+GPS timestamps, original bat IDs, repeated bouts, sensor quality and exposed echo-observability fields. If missing, record structural STOP, do not rescue Carollia's negative primary.

**Frozen scientific state:** original Carollia source schema verified; in-sample published gaze anticipation remains prior art; new bat-label-heldout incremental acoustic gain **not supported**; original \`batter\`/other \`boids\` conclusions unchanged.
