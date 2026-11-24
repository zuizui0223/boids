# v4: Fish schooling and acoustic observability — exact known-truth versus original wild source

Date: 2026-11-20. **Scientific status: NO NEW FIELD BOIDS EFFECT.**

## What v4 resolves

Previous synthetic v3 showed a five-hydrophone acoustic history model could improve next-intensity prediction over a same-hydrophone persistence model. That relied on imposed homogeneous emission and a known Gaussian attenuation law.

This v4 contains two independently testable **mathematical counterexamples**, under a positive Gaussian expected-energy observation operator, with 5 microphones and 12 fish:

1. Even with all 12 fish positions known, two distinct per-fish emission strength vectors in [0,1] have the **same expected microphone signals** to 1e-10 numerical precision (5 × 12 matrix, rank 5, null space dimension 7); total source emission differs.
2. Shift the entire 12-fish source configuration **1.2 arbitrary spatial units**, then change each fish's admissible emission rate in [0,1]. The alternative arrangement gives exactly the same expected power at all five receivers to 1e-10 numerical precision. Therefore even centroid position is not identifiable from aggregate intensity without additional emission/propagation constraints.

These are *structural* counterexamples: no fish was filmed/tracked and source amplitudes are expected acoustic intensities, not actual individual-call occurrence data. They do not disprove the original Ota state-space estimates, which are **conditional on model assumptions**. They do not establish anything about real fish schooling rules or coral reef bioacoustics.

## Real source alternative with no raw data redistribution

Pinned external GitHub: https://github.com/xaviermouy/XAV-arrays at commit `5258350fe78f107a7f3e03ca50ff08bc0e8d0362`. Six independent public wild-example WAVs and their 3D hydrophone geometry originate from a fish-sound localization example (2019-09-20, Hornby Island). Git SHA and WAV sampling/synchronization are audited in an independent GitHub Actions job. Small example recordings **cannot show enduring fish-school movement** or long-run chorusing, and published audio-video fish-behavior study underlying the technology does not supply accessible synchronized individual fish trajectories for this exact original example. No source waveforms or raw samples should be committed to the user's repo.

Ota original Kashima Dryad DOI 10.5061/dryad.zkh1893qn has previously been independently checked on Actions: 40 metadata items across 2 pages but required original file download HTTP 401; not admitted. Keep this scientific stop and avoid inventing fish effects.

## Reproduction

`python -m unittest discover -s validation_fish_school_v4 -p 'test_*.py' -v`; `python validation_fish_school_v4/inverse_identifiability.py`. For the external source gate, clone pinned XAV in GitHub Actions and run `xav_source_gate.py --root ...`. Numeric results under `validation_fish_school_v4/results/` (source status artifact only; no original WAV or per-fish recordings).

## Next field test needed

**Primary**: verify source availability and raw receiver effort; predict heldout future 10-min acoustic intensity by the next day conditional on observed chorus, using prior-only filtering. Compare day/season, audio persistence, group-centroid/velocity state and wrong receiver positions with identical target observations. **Mechanism** requires independent fish location/density and measured individual sound source, or an identified-set analysis that remains valid across heterogeneous emissions and propagation error. Prevent smoothing with later audio, sampled-on-chorus zeros, false negatives, and pseudo-independent frames. No merging without further review.
