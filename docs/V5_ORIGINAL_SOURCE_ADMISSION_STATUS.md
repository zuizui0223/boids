# v5 original data admission & motor-transfer status (2026-11-20)

## Real original source verified, not an inferred ecological effect

Original 2024 Puy et al. PNAS fish-school trajectories, DOI 10.5281/zenodo.10890112: all **6** original 8-fish CSVs downloaded directly from the publishing repository into temporary GitHub Actions storage, provider MD5 **6/6 passed**. Source native header (17 columns): `Time [frame]`, paired `X_0 [px]`, `Y_0 [px]` through `X_7 [px]`, `Y_7 [px]`. CSV source line counts including header by recording ID 0–5: **82999, 90000, 90000, 90000, 180000, 114999**, respectively. Exact original source structural run **#44742814342** passed.

Two 39-fish author files exist in the same Zenodo repository, original source sizes **261,243,818** and **260,959,984** bytes; neither included in the precommitted <=70MB per-file six-trial source gate. No cross-school-size result can yet be reported.

## Independent wild acoustic source

Mouy et al. 2023 XAV audio/video source, OSF https://osf.io/q8dz4, live OSF API **71 original files in 12 pages**: 16 WAV, 11 MP4, 18 CSV, 6 NetCDF and other documentation. See source catalog Actions run **#44743169531**. These acoustic/visual records are **not the 2024 fish track subjects**. They cannot be joined by ID, date or acoustic scene. Many localization CSVs contain already modeled acoustic-source estimates, NOT individually tracked trajectories of silent and calling fish.

## Precommitted out-of-trial test

Frozen before any numeric 2024 tracks were read, [protocol](V5_FISH_MOTION_TRANSFER_PROTOCOL.md) compares:
- M0: own velocity history + wall location.
- M1: M0 + classic separation, alignment and cohesion computed from the 8 actual nearest fish positions.
- M2: M1 + alignment limited to faster neighbors.
- Ghost: M0 + 2 s old neighbor vectors.

Target is observed future 0.2s displacement / 0.2s on exact same heldout source frames. Train on 5 entire trials; test the 6th; report six trial-level MSEs, equal-trial gains, exact sign test, and trial-level descriptive bootstrap. The 2024 paper already found speed-selective social interactions, so an in-sample replication of that mechanism is not novelty. Test is *transfer* to a completely heldout recording rather than force or cognitive causality.

**Strict caveats**: source trajectories may have past+future smoothing, so benchmark is retrospective and not a prospective online prediction. Recording-level holdouts do not prove distinct animal populations (reused fish unknown). No synchronized fish sound response in these data; do not infer fish acoustic chorus or Reynolds steering from forecast coefficients.

The real numeric forecast evaluation has a separate Actions run; a pass on data admission alone must never be reported as a positive forecast.

