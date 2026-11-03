# v38 — Original repeated-tide WATLAS red-knot source is not sufficient for social Boids forecast

**2026-11-02 JST.** Independent public file from [Figshare supplementary Additional file 14, DOI 10.6084/m9.figshare.26553446.v1](https://doi.org/10.6084/m9.figshare.26553446.v1) fully downloaded and provider source MD5 matched. Source-quality result only, **not a test of social or tide-related behavior**.

## Verified original source
- Original provider file: `40317_2022_307_MOESM14_ESM.csv`
- Size **1,246,403 bytes**, provider MD5 verified, new SHA256: `f8ef4f488a1f7f77182da59a0350b761c1b3aaa935fc5f99c3caa7ef4d15afff`.
- **7,595 original localization rows**, all passed NBS/variance/UTM numeric quality requirements; **5 unique tags**, **9 original tideID values**, **1,093 TAG×30-second non-interpolated location bins**.
- **Zero different-tag near pairs** within 50 metres in the same 30-second bin. Therefore **zero** directed samples with both animals' prior headings and next focal outcome, **zero** dyads and **zero** tide cycles qualifying with two dyads and ten directed samples.
- Pre-frozen admission requires 200 qualifying directed samples, five birds, five dyads and four independent tideID cycles with ≥10 directed pairs and ≥2 dyads in each cycle: **NOT_ADMITTED_MULTITIDE_SOCIAL**.
- Publication has multiple tide identifiers, but repeated tide identifiers are not equivalent to repeated observed **social dyads**. This original home-range subset does not answer the social Boids prediction question. This is a dataset/source limitation, not evidence that birds do not interact.
- Source `waterlevel` is reported for West-Terschelling; do not assume its vertical datum or local mudflat elevation or use it to infer causal resource-front pursuit. No raw tag identities, geographic coordinates or original time series were redistributed.

## Both original WATLAS source gates
| Original published source | Original fixes | Birds | Tide cycles | Near different-tag pairs | Qualified directed pair headings | Admission |
|---|---:|---:|---:|---:|---:|---|
| [Additional file 12, Figshare 26553440](https://doi.org/10.6084/m9.figshare.26553440.v1) | 56,366 | 7 | one nonrandom selected tide | 266 | 90 | NOT_ADMITTED |
| **[Additional file 14, Figshare 26553446](https://doi.org/10.6084/m9.figshare.26553446.v1)** | **7,595** | **5** | **9 tideID values** | **0** | **0** | **NOT_ADMITTED** |

Do not merge the two supplemental datasets as if they are independent individuals or independent repeated social-group experiments. Neither reached the originally frozen social admission gate.

## Reproduce
- [GitHub Actions original v38 complete run 41413911327](https://github.com/zuizui0223/boids/actions/runs/41413911327)
- Original source code `validation_v38/watlas_multitide_original_source.py`; tests `validation_v38/test_watlas_multitide_original_source.py`; frozen before observed outcomes `docs/V38_WATLAS_MULTITIDE_RED_KNOT_SOURCE_GATE.md`.
- This only certifies source observation support. **No social-force, predation, competition or resource-niche parameter estimated.**
