# Common receiver v1: JAR expands spectral spacing without necessarily resolving acoustic identity

**2026-11-02 — source-constrained SYNTHETIC result.** The experimental or 2020/2026 paper results are not being rerun or overturned. No new animal observations or original protected data were accessed. A pre-output protocol is frozen at [COMMON_PHYSICS_PREOUTPUT_CONTRACT_V1.md](COMMON_PHYSICS_PREOUTPUT_CONTRACT_V1.md).

## The falsifiable bat-only question

> Does greater separation in emitted terminal frequencies necessarily prevent another bat's FM pulse from being mistaken for one's own echo when a receiver is free to search over echo arrival time, and does any acoustic benefit translate to target detection?

Published Hase et al. 2026 (`10.1098/rspb.2026.0921`) supports a leaky vocal frequency response, and reports fewer **potential** misdetections under JAR in its own species-informed waveform / 2-D flight / correlation model. Published Mazar & Yovel 2020 (`10.7554/eLife.55539`) reports JAR does not improve its own simulated sensorimotor insect captures. These claims concern different bat species, acoustic systems and outcomes and are **not contradictory measurements of one experimental estimand**.

## Provenance

**Source-derived pieces**: `tau=200ms`, asymmetric acoustic susceptibility multipliers (`C=-4` when own TF is below a competitor, `C=+20` when above), ±3 kHz triangular influence, 1ms RK4 numerical time step, 5–10s group-acoustic interval inside 15s, 3ms/40kHz FM waveform *duration and bandwidth*, and normalized cross-correlation threshold of 0.5 (Hase 2026).

**IMPORTANT imposed pieces**: deterministic initial frequency spacing 0.4kHz; fixed 3-D positions for 4 and 8 bats; invented distance-dependent normalized received pulse power and deterministic IPI70ms phase offsets; frequency noise absent; **linear** FM chirps rather than the published M. fuliginosus spectro-temporal waveform; 250kHz waveform sampling; 0ms versus ±0.35ms receiver lag search; synthesized noise/interference multiplier and threshold; four synthetic prey-echo SNR margins. No prey flight, actual bat navigation, range-response decision or capture-rate model is recreated here. The 2020 true detector is only a threshold **inspiration**, not a source-equivalent implementation.

GitHub Actions [run 41407501554](https://github.com/zuizui0223/boids/actions/runs/41407501554) passed **18/18** physical/software tests and generated the complete aggregate output artifact. Independent baseline source-reanalysis and its protected animal/source rights remain unchanged.

## Actual v1 outputs (source-constrained synthetic, not species predictions)

| Synthetic group | Space scale | Change in mean pairwise emitted TF gap | Zero-lag confusable pairs before→after | Receiver lag-window confusable pairs before→after | Target detection proxy across echo-power grid |
|---|---:|---:|---:|---:|---|
| 4 bats | compact | **+0.772 kHz** | 0/6→0/6 | **6/6→6/6** | zero-lag 0.750→0.750; lag-search 0→0 |
| 4 bats | dispersed | **+0.127 kHz** | 0/6→0/6 | **6/6→6/6** | zero-lag 0.750→0.750; lag-search 0.4375→0.4375 |
| 8 bats | compact | **+0.767 kHz** | 0/28→0/28 | **28/28→28/28** | zero-lag 0.750→0.750; lag-search 0→0 |
| 8 bats | dispersed | **+0.129 kHz** | 0/28→0/28 | **28/28→28/28** | zero-lag 0.750→0.750; lag-search 0.21875→0.25000 |

**Interpretation:** JAR increased emitted frequency separation in all four predeclared synthetic situations, but **did not lower the count of possible other-bat matches at the selected peak correlation cutoff, in any of the four**. Only one target-sensitivity cell changed, in the 8-bat dispersed case. These values are conditional on *one* specified linear-FM waveform, lag acceptance and toy receiver threshold; there is **no source-independent effect size or confidence interval**, and different waveform shapes and receiver rules may change the conclusion.

The remarkable opposite zero- versus lag-search sensitivity is **not** evidence that real bats ignore relative arrival time; it is a mathematical feature of the simplified sound signal.

## Exact time–frequency ambiguity in this waveform family

For a linear downward FM waveform with duration `T`, frequency sweep bandwidth `B`, and two otherwise identical pulses whose terminal frequencies differ by `Delta f`, a time translation `Delta t = Delta f*T/B` can approximately align the instantaneous frequencies over overlapping waveform support. For `T=3ms` and `B=40kHz`:

- `Delta f=1kHz` → `Delta t=0.075ms` → two-way range equivalent `1.29cm` (sound speed 343 m/s).
- `Delta f=3kHz` → `Delta t=0.225ms` → two-way range equivalent `3.86cm`.

The actual synthetic normalized source-pair FM correlation (48 versus 51 kHz):
- **zero lag ≈0.000001**;
- **peak within ±0.35ms ≈0.840** (>0.5 decision threshold).

This is the standard broadband chirp range–Doppler/time–frequency ambiguity in a simple constructed waveform. It is **NOT** a bat ranging error observed or computed by either original paper.

### Why original 2020 cannot automatically validate this specific ranging-error mechanism

Mazar & Yovel's paper explicitly states that, in their correlation-receiver model, range errors are a function of signal-to-noise ratio and a Gaussian timing error, **assumed independent of call spectral parameters** for FM chirps. The filter-bank model, by contrast, calculates errors from detected peak arrival times. Thus a theoretical range bias arising directly from `Delta f` cannot be validated merely from the original correlation receiver's stored range-error column. The 2020 paper already showed no reliable JAR improvement in range accuracy; it is prior art, not a new independent confirmation here. See official 2020 [eLife article and Figure 2 source description](https://elifesciences.org/articles/55539).

The 2026 paper constructed a **species-specific waveform** from published sound shapes, not our linear chirp, and used a cross-correlation threshold and actual pulse timing windows. Thus we do **not** claim its own reduction in potential misdetections has been disproved by our alternative waveform.

## What is actually novel enough to pursue without new measurements?

Not yet an ecological law. The possible new source-bounded computational question is whether **true/prey echo timing discrimination versus false arrival-time matches** changes the JAR sign *within the same source-constrained waveform and moving 3-D scene*, when the receiver code and physics are held fixed.

Progress requires:
1. Retrieve the species-informed 2026 source FM waveform equation and publicly justified sound arrival-time gates **before** running a replacement model. Lock the source before any results. If unavailable, retain this v1 as a conditional counterexample, not an alleged source replication.
2. Reconstruct exact original-source Hase signal synthesis or formally fail source equivalence; differentiate range/Doppler ambiguity from spectral overlap and from sensor processing.
3. With an independently source-authorized comparator (ideally original 2020 range/receiver implementation), score identical virtual emitted pulse/echo opportunities under JAR/no-JAR and explicitly separate potential false templates, actual false detections, true prey detection and capture. Modelled captures remain wholly synthetic unless the original predator-prey simulator is faithfully ported.
4. Do **not** reopen v1 lag width, distances, thresholds or pulse shape after viewing its output to rescue a favourable sign.

**Publication ceiling:** Code, 18 source-aware tests and the no-necessity counterexample are validated. A real-bat law, a source-to-source numeric reproduction and an adaptive fitness claim are **not**.
