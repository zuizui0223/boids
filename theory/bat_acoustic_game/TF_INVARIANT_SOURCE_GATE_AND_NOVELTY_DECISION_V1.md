# Terminal-frequency manipulation is not a unique acoustic intervention

**2026-11-02 · Phase 5 scientific decision · zero new animal measurements.** This synthesis is based on source-authenticated, *secondary* published-model results and a set of prospectively fixed synthetic comparisons. Neither original Hase 2018 pulse waveform nor Hase 2026 full moving-group simulator was reconstructed; do not claim original-model replication, a new measured effect in live bats or learned/fitness consequences.

## What was decided from the original source

**Hase et al. 2018** *Communications Biology* DOI [10.1038/s42003-018-0045-3](https://doi.org/10.1038/s42003-018-0045-3) already reported acoustic differences/spectrally separated terminal frequency in group-flying bats, and a synthetic-pulse correlation halfwidth on the order of 1 kHz. Thus a claim that "frequencies distinguish bats" is pre-existing knowledge.

The original 2018 Dryad DOI [10.5061/dryad.4f99c46](https://doi.org/10.5061/dryad.4f99c46) does provide publicly catalogued `SoundFile.zip`, 614,454,096 bytes and official MD5 `c6651cc04aefbdaf0cce77b184b8a8c9`, license CC0. Dataset version 376 / file ID 1962 were retrieved via the official API. The actual file endpoint returned **HTTP401 Unauthorized**. **No sound or bat vocal waveform bytes were opened.** Metadata access and public licensing alone are not data-access admission; no alternate privileged download or redistribution has been attempted.

**Hase et al. 2026** *Proceedings B* DOI [10.1098/rspb.2026.0921](https://doi.org/10.1098/rspb.2026.0921) describes a source-driven leaky terminal-frequency controller and time-window comparison. Its published audio-synthesis exact equation, full 2D group simulation source code and original stochastic trajectory seeds have not been identified in the inspected publicly accessible 15-file Figshare model/experimental archive or two source-verified DOCX supplements. No claim of source-exact Hase 2026 figure reproducibility is possible.

## Completed new analytic benchmark (not an experiment)

Two pre-output-frozen interventions for the exact same source-inspired **3ms power-curve synthetic FM family**:

- **Hold start frequency fixed (2018-like, 90→45 kHz)** while shifting terminal frequency upwards by `ΔTF`. The bandwidth necessarily changes.
- **Hold sweep bandwidth fixed at 40 kHz (2026-like, 88→48 kHz)** while shifting terminal frequency upwards by `ΔTF`. The starting frequency changes.

Each is tested under three independently imposed exponents `p ∈ {0.6,1.0,2.0}`. Cross-correlations are normalized and optimized over **all waveform relative time shifts**; an absolute peak threshold of 0.5 defines the synthetic first-crossing condition. No waveform shape was fit after opening the crosswalk output.

| Synthetic shape | Fs held fixed: ΔTF first crosses under 0.5 | B held fixed: ΔTF first crosses under 0.5 |
|---|---:|---:|
| Linear p=1.0 | 2.03 kHz | **no crossing ≤6 kHz** |
| Curved p=0.6 | 5.95 kHz | 2.84 kHz |
| Curved p=2.0 | 0.72 kHz | 0.94 kHz |

**Scientific contribution demonstrated, bounded:** a prediction about signal dissimilarity is not defined by `ΔTF` alone. It is dependent on what is **held invariant when changing the call** and on the spectrotemporal curvature. This sharpens the previous v2 result where linear-chirp TF differentiation never reduced candidate matched pulses over four 3D source-constrained scenarios, while curved synthetic pulses did reduce it in seven of eight waveform×space combinations. The two models share synthetic source assumptions and **are not independent biological replicates**.

Although the p=2.0 shape has a threshold close to the published 2018 approximate ~1kHz result, this is **NOT an estimate of a real bat pulse curvature**: the two source baseline ranges are different; unpublished original waveforms are inaccessible; multiple waveform functions and experimental reference conventions can match a single threshold. Inverse-identification from one correlation halfwidth is inherently underdetermined.

## Exact independent numerical and provenance verification

- [Pre-output contract, source conventions](HASE2018_2026_TERMINAL_FREQUENCY_CONVENTION_PREOUTPUT_V1.md).
- [Independent reproducible synthetic calculation](hase_TF_convention_crosswalk_v1.py), [8 regression tests](test_hase_TF_convention_crosswalk_v1.py).
- [Full six-curve numerical ledger](HASE2018_2026_TF_MANIPULATION_EXACT_LEDGER_V1.json).
- [Fail-closed replay and Git-blob verification](verify_hase_TF_crosswalk_ledger_v1.py).
- [Original sample/schedule/waveform v2 source note](HASE_WAVEFORM_CURVATURE_SOURCE_BOUNDED_RESULT_V2.md), [12 exact scenario ledger](HASE_2026_SOURCE_TIMING_WAVEFORM_EXACT_LEDGER_V2.json).
- [Hase 2018 source data rights and HTTP401 gate](https://github.com/zuizui0223/boids/actions/runs/41411436841).
- [Six scenarios original source-convention test](https://github.com/zuizui0223/boids/actions/runs/41411818238).
- [All twelve exact group-waveform scenes verifier](https://github.com/zuizui0223/boids/actions/runs/41410719843).

## Editorial conclusion and stop/go

The current *bat-only* project is **a source-constrained auditory/physical hypothesis with reproducible counterexamples, not a confirmed ecological law about JAR or foraging payoff**. Both previous documents [Mazar & Yovel 2020 source output vs catch](SOURCE_JAR_CAPTURE_DECOUPLING_V3.md) and [Hase 2026 pulse curves](HASE_WAVEFORM_CURVATURE_SOURCE_BOUNDED_RESULT_V2.md) remain available without overwriting scientific records.

One possible publication-grade next comparative inference is to **predeclare a receiver-identity estimand independent of the detection threshold used to select pulse models** and check its generalization to *independent authentic source waveforms*. That final generalization is currently **SOURCE STOP** because:
1. true original waveforms were not accessible (2018 Dryad 401);
2. 2026 exact group pulse-synthesis physics and model source were not released in inspected archives;
3. no verified emitted vs receiver echo–prey payoff crosswalk is available.

Do not silently substitute the curved `p=2` proxy as the real *Miniopterus* sound, do not use the source 2018 ~1kHz target to optimize exponents retrospectively, and do not submit an original empirical bat paper based on this source-limited synthetic agreement. Keep PR #36 Draft and frozen `batter` field/JAE/BE endpoints untouched.
