# Tunnel_2026 Carollia original-source v29: completed schema and leakage audit

**Date:** 2026-11-19 JST  
**Status:** verified original-file metadata; no numerical animal behaviour/outcome fitted.  
**Code/receipt:** [v29 source workflow #44444045498](https://github.com/zuizui0223/boids/actions/runs/44444045498), [original author repository](https://github.com/00keveland/Tunnel_2026/tree/59928a71887d521fec143080b0b187736c046a0e).

## Original source integrity and actual support

The full author repository was checked out at commit \`59928a71887d521fec143080b0b187736c046a0e\`. All 30 archived \`Trial_Data_Carolia/*RESULTS.mat\` files passed independent size and Git-blob-SHA1 verification and HDF5 source-metadata inspection. Four known-truth tests passed. The complete original metadata receipt is archived by the source workflow, not fabricated from published aggregate results.

| Structural target | Verified |
| --- | ---: |
| Trial .mat source bytes, hash and key fields | 30/30 |
| Bat-like labels in filename (C1–C8) | 8 (not 30 unique biological replicates) |
| Author-saved call timestamp slots | 1,904 total; 16–132 per trial |
| Matching beam azimuth/relative heading/fit quality array lengths | 30/30 |
| Author-saved **interpolated** trajectory samples | 31,031 total; 241–1,598 per trial |
| Track XYZ shape consistent with time field | 30/30 |
| Raw per-call positions \`RESULTS/calls/XYZ_raw\` field | 30/30 |
| Absolute sonar azimuth \`RESULTS/beam/az_rad\` field | 30/30 |
| Target-independent obstacle clearance distance \`d_free\` | NOT VERIFIED |
| Target-independent echo reliability \`p_usable\` | NOT VERIFIED |
| Public companion \`Rousettus\` per-trial data | NOT FOUND in the checked non-truncated 80-path tree |

Labels C1–C4 occur in 2023-12-16 files and C5–C8 in 2023-12-22 files. There are only **two source dates**, and no label crosses the two days. The observed 1,904 slots are **not 1,904 independent bats or verified high-quality pulses**. The 31,031 interpolated trajectory points are **not independently observed GPS/video measurements**.

The original saved \`RESULTS/env\` group has temperature, RH, ambient pressure and sound-speed model. It does not contain a verified position-wise obstacle clearance field or a source-calibrated usable-echo probability. The full dimensionless sensing-margin \`q=v*IPI/(d_free*p_usable)\` is **NOT_ADMITTED** from these files.

## A decisive source-code leakage finding

The upstream MATLAB live script (\`Pipleline_V7.asv\`, \`matlab/document.xml\`) shows that the stored **relative beam angle is not a sensor-only exposure**:

- Global beam azimuth is fitted to the microphone array as \`BEAM.az_rad\`.
- Travel direction is reconstructed from the smoothed bat path at the corresponding call index.
- Relative beam direction is formed by subtracting that reconstructed travel direction from global beam azimuth.
- The upstream \`heading_from_track.m\` uses symmetric \`idx-1\` and \`idx+1\` coordinates.
- \`carollia_build_track_from_calls.m\` interpolates and smooths the track from per-call localized positions.

**Consequence:** using \`beam.rel_deg(t)\` to predict the next heading change risks feeding a future-dependent track estimate into a purportedly prospective predictor. This is a preprocessing/identifiability risk, **not evidence of no acoustic anticipation**. It also means the published 70% directional anticipation for Carollia is not a newly discovered effect of this programme.

For any narrower new prediction test, use independently fitted *absolute* \`beam.az_rad\` only; construct the pre-event travel direction using strictly earlier raw call positions; use nonoverlapping later coordinates for the future target; and require negative controls for jointly estimated microphone-array position and beam errors. **Do not promote the author-saved relative beam or interpolated 200-Hz track to a causal predictor.** Global azimuth vs XY chamber coordinate registration remains to be validated before fitting.

## Separately predeclared limited next test (not a universal law)

Only after fixed coordinate-system and valid event-preflight gates:

- **M0**: prior-only raw-call displacement/heading/speed/kinematic history; optional known static corridor geometry only if independently documented.
- **M1**: M0 plus global sonar beam azimuth and previous call interval, both dated before future movement. Fit quality filtered at the pre-specified author's \`fitR>=0.30\`, with the full number excluded reported.
- **Target:** direction of the next *raw call-to-call* horizontal displacement (not author-defined turn windows, not interpolated track). Same response and covariates for M0 and M1.
- **Validation:** full original bat-label leave-one-out folds, equal-bat scoring; also fixed whole-day transfer analysis (two dates, descriptive only). Pre-register one metric such as mean held-out log-loss improvement \`loss(M0)-loss(M1)\` and a whole-label interval before numerical outcome opening.
- **Censor/stop:** if pre-only positions and beam cannot be aligned in a common physical coordinate system, or if too few independent bat labels and valid events survive, STOP before fitting. Never replace with a post-hoc beam sign chosen using target outcomes.
- **Interpretation:** a positive holdout advantage would establish *predictive information from acoustics in one processed Carollia archive*; it would not establish sensorimotor causation or a bat-wide policy. A negative outcome is retained unchanged.

The independent cross-species law additionally requires another source, different sensing regime and matching pre-event variables; both original bat species are **not** jointly reproducible from the checked public repository alone.

## Scientific outcome boundary

- **Completed:** exact original file verification; HDF5 structural consistency; bat/trial/days unit audit; identification of non-independent interpolated track and future-dependent relative beam angle.
- **Not completed:** independent sound-to-video clock verification, original beam/XYZ coordinate registration, geometry and echo-probability calibration, clean pre-only behavioral forecast, any cross-species transfer.
- **Decision:** keep [PR #213](https://github.com/zuizui0223/boids/pull/213) in draft; do not modify frozen \`batter\` results or claim a universal movement law.
