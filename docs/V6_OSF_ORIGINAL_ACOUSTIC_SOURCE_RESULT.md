# v6 authentic XAV original acoustic source: event-level 3D localizations, no fish tracks

Observed 2026-11-20 original-source gate, fully reproducible GitHub Actions [#44750614686](https://github.com/zuizui0223/boids/actions/runs/44750614686), source data frozen by OSF file IDs, SHA256 hashes, and column-only schema in saved artifact.

Original 2023 Mouy et al. MEE XAV dataset: [OSF q8dz4](https://osf.io/q8dz4), six distinct published `localization_results.csv` files. All **6/6 official original files** downloaded successfully; no source STOP. The source SHA256 is recorded in the Actions receipt. No individual coordinate or original timestamp is redistributed.

| Published array | Localization rows (not individual fish) | Explicit fish track ID? |
|---|---:|---|
| Large OGD | 17 | No |
| Mini | 2 | No |
| Mobile A | 6 | No |
| Mobile B | 6 | No |
| Mobile C | 23 | No |
| Large HI | 12 | No |
| **All original files** | **66** | **No** |

Original source fields include `uuid`, detection label/class/subclass, `time_min_date`, `time_max_date`, `x,y,z`, spatial coordinate uncertainty spans, recorder metadata and TDOA error diagnostics. They do **not** include an individual fish ID or a continuous per-fish movement track. OSF also offers video clips and audio WAV, but this schema result has not tracked individual fish from them.

**Key consequence:** These 66 reported sound-source localizations can support technical validation of localized *sound sources*, but not estimation of Reynolds separation, alignment, cohesion from individuals, nor fish-call facilitation, nor time-ordered movement of one fish. Repeated events of the same label are not evidence of the same fish. Puy et al. 2024 8-fish tank tracks were collected in a different field/source and must not be paired as if synchronized.

The v6 original fish motor-ablation is a separate predeclared all-six-recording heldout test on the true Puy data, **not a paired acoustic field analysis**. Keep this caveat in the central article narrative. No raw OSF time or location values are retained in the repository.

