# v4c genuine XAV wild audio: fixed-window acoustic coherence, NOT fish group motion

Date: 2026-11-20. Source project: [Mouy et al. (2023)](https://doi.org/10.1111/2041-210X.14095) / [XAV-arrays](https://github.com/xaviermouy/XAV-arrays), MIT **not assumed**; source repository is BSD-3-Clause. Public source pinned at `5258350fe78f107a7f3e03ca50ff08bc0e8d0362`.

## Source verification (actual wild field recordings)
- Six original 2019-09-20 Hornby Island example WAV file Git blob SHA values all matched exactly.
- Six 3D receiver positions have spatial rank 3.
- All six streams are original mono, 24-bit PCM, 32 kHz.
- Native receiver #1: 544230 frames = 17.0071875 s; #2–#6 each 544000 frames = 17 s. Mismatch is precisely **230 samples/7.1875 ms**.
- **Strict original `SOURCE_FRAME_SYNC_STOP` is preserved.** This difference is file length, **not proved initial time offset**.

## Frozen diagnostic, independent of any fish-response model
- Analyze only the first common **17.0 seconds** (no resampling, no alignment correction).
- Four clock-fixed 0.5 s windows starting at 1, 5, 9, 13 seconds.
- 200–2500 Hz digital bandpass and raw waveform cross-correlation of reference receiver 0 against receivers 1–5, finding largest absolute normalized peak within ±10 ms.
- Negative diagnostic: circularly shift each non-reference half-second waveform by **0.25 seconds**, then recompute same correlation. This is not an exchangeable ecological null.
- Same 2019 original source and at most 4 source time windows, not multiple independent biological populations.

## Actual result (completed Actions)
- **20 channel×window contrasts**.
- Median actual absolute normalized peak correlation = **0.6980967202363797**.
- Median 0.25 s rotation control correlation = **0.06305951113736409**.
- [Strict original field-source and numeric code run #44735776053](https://github.com/zuizui0223/boids/actions/runs/44735776053) completed successfully and **11 source-independent known-truth tests passed** (5 structural inverse +3 XAV source fixtures+3 audio-lag known-truth).
- A passing workflow is a reproducibility check, NOT a positive biological interaction test. The original XAV source **sync gate remains stopped**, and per-window lags are diagnostic not physically calibrated localization.

## Scientific boundary and next gate

This demonstrates observable shared acoustic waveform structure in a real field array compared with a deliberately shifted source surrogate. It **does NOT show** individual fish, fish schooling, local acoustic calling, vocal facilitation, social influence, fish group movement, or identification of any Reynolds separation/alignment/cohesion force. Technical alternatives: acoustic propagation and reflection, shared ambient/correlated equipment signal and inter-board clock effects. There is no legitimate multi-night or between-population biological replication here.

Next: prior to any claim of localized fish movement, verify channel start alignment independently with calibration/synchronization beeps and original source acquisition logs; then process separate natural sound events with TDOA uncertainty and independent video association. Only after matched individual positions and observed calls can movement-law and call-response models be tested. The original Ota Dryad acoustics remain HTTP 401 source STOP; do not silently switch this field source into the Ota endpoint.

**Keep Draft; never merge into main on acoustic correlation alone.**
