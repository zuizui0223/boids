# Why a frequency adjustment succeeds or fails under receiver delay search

**2 Nov 2026 — SOURCE-INFORMED SYNTHETIC MECHANISM RESULT, not an independent bat finding or full original simulation replication.** This note documents all pre-output scenarios and the post-output numerical correction, including earlier failures. No new bat field/lab data or raw third-party files are committed.

## Prior art and actual research gap

- Hase et al. (2018), *Communications Biology* 1:39, DOI 10.1038/s42003-018-0045-3, ALREADY showed that group-flying *Miniopterus fuliginosus* shift terminal-frequency differences and their published waveform-correlation index is reduced. Their frequency manipulation simulation over 3-ms 90-to-45kHz FM sounds predates this work. **Do not claim a novel discovery that TF differences can discriminate acoustic calls.**
- Hase et al. (2026), *Proceedings B*, DOI 10.1098/rspb.2026.0921, used a source-informed nonlinear pulse sound and leaky-integrator JAR, then reported fewer *potential* misdetections under their 2D moving-colony simulator.
- Mazar & Yovel (2020), *eLife* DOI 10.7554/eLife.55539, modeled insect detection/capture in a DIFFERENT sonar/predator–prey source. Its source Figure 2 JAR/noJAR capture differences are mixed and small (secondary reanalysis in this branch), so neither original experiment implies the other is wrong.

**Narrow next question:** Under the same *source-described acoustic frequency dynamics*, does FM waveform curvature determine whether individual spectral differentiation survives a receiver's freedom to shift the echo arrival time? This is a source-bounded **alternative physics** demonstration, not a claim that waveform-curvature dependence has never been described in acoustic literature.

## Source reproducibility and model choices

Original Hase 2026 source metadata and supplements verified:
- Figshare DOI 10.6084/m9.figshare.c.8694625, exact `rspb20260921_si_002.docx` SHA256 `08757770509ae9dd678a6ec5e064c5a16f03496b271afb7435f61ec491645376`.
- Public supplementary figure document `rspb20260921_si_001.docx` SHA256 `66bcf2de38b9f17068252b838fff0e4209dad37dc04cb9f26b75b94d93d7275b`.
- Supplemented source describes 2D moving flight by self-propulsion, group repulsion, wall force and random force; it does not supply the entire original simulated group-flight executable. No source-exact digital species-specific FM waveform file or exact synthesis formula was found in the inspected Figshare data/Methods files.

**v2 source corrections:** the 5-ms acoustic input rectangle is different from the emitted 3-ms / 40-kHz FM pulse; original frequency-response ODE `tau=200ms, C=-4/+20, triangular |FD|<3kHz` and 1ms RK4; gamma-distributed source IPI mean70ms, sd18.7ms; 5–10s group-acoustic interval; received pulse onset after physical time of flight; receiver opportunity = source-described *current own pulse to next own pulse*.

**Still invented/not source equivalent:** fixed 3D bat positions (0.7/3 scale) instead of 2D moving animals, 17ms per-bat initial offset, deterministic TF spacing 0.4kHz rather than normal-distributed frequencies, inverse-square power with no directionality/atmospheric attenuation, three hypothetical 3ms FM frequency curves:
`f(t)=TF + 40kHz*(1-t/T)^p` with `p=1,0.6,2`. 2026 original uses source-specific spectrotemporal pulses, not these exact polynomial curves. Absolute-normalized **pairwise** full chirp cross correlation at threshold 0.5 is NOT its fully mixed receive-window cross-correlation algorithm.

All 12 conditions (4/8 bats × compact/dispersed × three shapes) were **frozen before looking at outcomes**: [original v2 contract](HASE_SOURCE_TIMING_WAVEFORM_V2_PREOUTPUT_CONTRACT.md).

## Validated source-constrained synthetic output

**Number of other-bat template matches above 0.5 per own emitted pulse**, JAR before → after, based on strict current-to-next emission reception and source-corrected gamma stimulus timing:

| Synthetic world | Linear FM (`p=1`) | Curved FM (`p=0.6`) | Curved FM (`p=2.0`) |
|---|---|---|---|
| 4 bats, compact | **856/291 → 856/291** (=2.942→2.942) | **856/291 → 720/291** (=2.942→2.474) | **573/291 → 131/291** (=1.969→0.450) |
| 4 bats, dispersed | 855/288 → 855/288 (=2.969→2.969) | 855/288 → 855/288 (=2.969→2.969) | 569/288 → 434/288 (=1.976→1.507) |
| 8 bats, compact | 4060/590 → 4060/590 (=6.881→6.881) | 3914/590 → 2551/590 (=6.634→4.324) | 1592/590 → 635/590 (=2.698→1.076) |
| 8 bats, dispersed | 3920/568 → 3920/568 (=6.901→6.901) | 3782/568 → 3508/568 (=6.658→6.176) | 1536/568 → 1111/568 (=2.704→1.956) |

At the same synthetic source-described JAR control rule and timing, JAR raises mean terminal-frequency gaps in all four geographic environments (approximately **+0.198 to +1.080 kHz**), but **the linear waveform gives zero change in pairwise delay-optimized template matches in 4/4 worlds; curved forms give decreases in 7/8 comparisons and one zero**. This is a conditional model-structure sensitivity, not four independent replications, population statistics, empirical jamming avoidance success, or an observed predator–prey payoff.

## The mathematical reason

Consider downward FM pulses with instantaneous frequency
`f(t)=F_T+B(1-t/T)^p` for `0<=t<=T`, `B=40kHz`, `T=3ms`.

Its local chirp rate is
`|df/dt|=Bp/T*(1-t/T)^(p-1)`.

For two versions that differ in terminal frequency `Delta F`, a locally equivalent time displacement is approximately

`Delta t(t) ≈ |Delta F| / |df/dt| = |Delta F| T / [B p (1-t/T)^(p-1)]`.

- **Linear FM (`p=1`):** one constant time shift can align instantaneous frequencies for much of both finite-duration pulses. In the v1 fixture, 3kHz TF separation corresponds to a hypothetical 0.225ms shift (3.86cm two-way range equivalence at 343m/s). That is not an actual bat localization error.
- **Curved FM (`p ≠ 1`):** different pulse segments require different local time shifts. A receiver using a *single* lag for its whole pulse cannot perfectly realign all portions. This can make spectral differentiation more informative in our specific chirp family.

This is ordinary signal-processing ambiguity theory, not evidence of a newly evolved bat strategy or of any species' actual nervous system. Actual bat emitted signals, beam direction, Doppler processing, multi-echo ranging, noise and physically calibrated receiver time windows can change the quantitative response.

## Numerical audit failure and repair (both retained)

The initial v2 output had an **invalid precision check**: all 63 synthetic audit frequencies were multiples of the 0.02kHz lookup grid; thus the originally reported `5.5e-14` numerical error was artificially reassuring. We did NOT change the original source-frequency law, conditions, waveforms or outcomes.

An independent post-output recheck used **63 off-grid** frequency comparisons:
- maximum binned-lookup absolute correlation error **0.064256**, exceeding the preset 0.025 error threshold in **16/63** tests;
- none of those 63 tests changed the binary 0.5 threshold decision;
- all source-conditional emitter-pulse comparisons were then recomputed using **unbinned, exact normalized cross-correlation** in each of the 12 worlds;
- **12/12 JAR effect contrasts and candidate classifications matched the original cached outputs exactly**.

This rescues numeric reproducibility of the **synthetic scenario grid**, not biological validity of the waveform choice. [Full exact rerun](https://github.com/zuizui0223/boids/actions/runs/41410278182) and [failing-cache-acceptance off-grid receipt](hase_waveform_postoutput_numeric_audit_v1.py) are retained.

## Evidence/replay trace

- [Source DOCX availability audit](https://github.com/zuizui0223/boids/actions/runs/41408961845)
- [Source supplementary methods source inspection](https://github.com/zuizui0223/boids/actions/runs/41409310375)
- [v2 source-corrected simulations, 17 tests](https://github.com/zuizui0223/boids/actions/runs/41410042618)
- [Exact all-event numerical audit and non-grid fixtures](https://github.com/zuizui0223/boids/actions/runs/41410278182)
- [SOURCE-derived-result JSON with whole-git-blob+12-cell replay](HASE_2026_SOURCE_TIMING_WAVEFORM_EXACT_LEDGER_V2.json)
- [Fresh exact ledger verification](https://github.com/zuizui0223/boids/actions/runs/41410719843)

## Decision for further work without new measurements

**Source-original waveform is the unresolved identity variable.** Modelled exponents p=1/0.6/2 are merely physically distinct spectrotemporal assumptions; without empirical bat pulse-shape constraints the model cannot support a claim that JAR truly benefits from spectral nonlinearity in wild *Miniopterus* or bats generally.

The **2018 independent published dataset DOI 10.5061/dryad.4f99c46** contains original 10-sec, 500kHz/16-bit bat-mounted-microphone flight audio for the same taxon, with bat/flight-condition filenames (published in Hase et al. 2018). This is an existing ~614MB archive, NOT new collection. Its initial file/rights/source-access preflight is a legitimate zero-new-measurements next step, but the original study already found lower cross-bat signal similarity when frequencies diverged; any new pulse-shape test must distinguish itself by **predicting a source-blind change in cross-correlation under explicitly varying received echo delay windows**, not simply rediscovering the 2018 cocktail-party finding.

**No biological manuscript claim or journal submission follows from this v2 alone.**
