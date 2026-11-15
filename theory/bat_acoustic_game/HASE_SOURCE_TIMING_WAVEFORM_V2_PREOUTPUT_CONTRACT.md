# Frozen prospective v2 source timing / waveform sensitivity contract — 2026-11-02

**Before outcomes.** This is a source-informed INDEPENDENT synthetic sensitivity analysis, not original 2026 group flight replication and not new animal observations. Prior v1 results/parameters are immutable. Do not select a more favourable waveform post-outcome.

## Source-original checks performed first

Published Hase et al. 2026 *Proceedings B*, DOI 10.1098/rspb.2026.0921 (article public HTML), and Figshare supplementary collection 10.6084/m9.figshare.c.8694625. Source DOCX `rspb20260921_si_002.docx` SHA256 `08757770509ae9dd678a6ec5e064c5a16f03496b271afb7435f61ec491645376` and `rspb20260921_si_001.docx` SHA256 `66bcf2de38b9f17068252b838fff0e4209dad37dc04cb9f26b75b94d93d7275b`, verified public publisher metadata and read-only structural inspection.

Source-formula parameters: ODE time constant 200ms; triangular frequency-overlap window 3kHz, multipliers -4/+20 for higher/lower own TF, RK4 at 1ms. Original acoustic INTEGRATOR input rectangle lasts **5ms**; emitted FM sound duration **3ms** with 40kHz bandwidth; source individual IPI gamma mean **70ms**, s.d. **18.7ms**; original group coupling 5–10s inside 15s. Original 2D 5×5m chamber bats move by self-propulsion/repulsion/wall/random force; original figures use a waveform mimicking *Miniopterus* pulse spectrotemporal shape, but the complete waveform formula/code and moving model were NOT found in the disclosed Figshare data/source methods. **Do not call v2 waveform source-exact.**

## Locked assumptions and four synthetic worlds

Use the SAME four preexisting synthetic sets from v1: 4/8 fixed bats × 0.7/3.0 scaling of v1 fixed 3D points. They are not real 2026 2D tracks or physical bat capture sites. Original B=40kHz, T=3ms, TF initial 48kHz +/- deterministic 0.4kHz spacing (not the original random Gaussian). Same 250kHz sampled waveform, pulse-level 3ms emission, 5ms acoustic input to ODE; distinct input versus emitted audio clocks.

For each group, use a fixed local RNG PCG64 seed **20261102** plus (group size, scale index) deterministically, and 17ms×bat start offsets; sample independent renewal intervals `Gamma(k=(70/18.7)^2,theta=18.7^2/70)` in milliseconds, rounded to nearest millisecond with **minimum 10ms**. This is one frozen synthetic realization, NOT confidence intervals. All JAR and no-JAR runs for a world share EXACT emitted pulse timestamps and positions. Source original gamma tail and motion are not fully reproduced.

Received stimulus onset is shifted by 3D distance/343m/s; stimulus rectangle 5ms. Received power proxy is `min(1,(1m/d)^2)`, no atmospheric absorption/directional calls, and is fixed for the corresponding same world. Retain exact v1 asymmetry constants and 1ms RK4; source gaussian drift omitted, no new attraction/competition law introduced.

## Waveform families, fixed BEFORE output

- `linear`: instantaneous frequency `f(t)=TF+40000*(1-t/T)^1` Hz, source-NONEXACT v1 comparator;
- `power_0p6`: same duration/end frequency/bandwidth with exponent **0.6** (curved chirp);
- `power_2p0`: exponent **2.0** (opposite curvature).

In all variants phase is the numerical integral of instantaneous frequency, and each signal normalized by Euclidean norm. The curvature values are independent invented waveform alternatives (not an estimate of *M. fuliginosus* spectra). Distinct original pulse shapes remain unidentified from the published release. Do not tune values after opening results.

## Main endpoints and units

For each focal synthetic pulse emitted within 5–10s, identify the NEXT focal emission from its gamma schedule and construct that one source-motivated reception window. For every other bat j, include an interfering emitted pulse only if its distance-delayed ONSET lies strictly within that reception window. Conditional on this source-constrained **opportunity**, compute:
- 0-lag normalized absolute waveform correlation;
- maximum normalized absolute waveform cross-correlation over all physically possible waveform partial overlaps (lag <=3ms), with same 0.5 source cutoff;
- number of *opportunity-eligible cross-bat pulses above threshold*, divided by focal emission count (= possible-other-bat matches per own emitted pulse, an invented pairwise proxy, NOT same as published fully summed 2026 spectrogram counts).
- fraction of eligible emissions with one or more such matched other-bat pulses.
- late 8–10s mean pairwise terminal frequency separation change (kHz) under JAR versus no-JAR.

Report ALL 4 worlds×3 waveforms×2 correlation modes, with denominators and no zero substituted for missing. No capture/mortality/fitness, no true-echo threshold, no 2020 model p-values, no biological replication. Source original normalizes sounds before cross-correlating entire summed receiving spectrogram and tests other pulses in current-to-next interval. Our pairwise waveform separation is only a constrained alternative due to missing original full group-simulation code.

## Exact technical tests / hard stops

1. Check no new biological data, no original 2020/2026 full simulation claimed, original DOCX authors credited.
2. Verify original IPI mean/sd intended gamma parameters, shared schedule JAR/noJAR, 5ms integrator vs 3ms emitted pulse, source active 5–10s, received flight delay positive.
3. Verify source law C/FD/tau and 1ms integration; no numerical overflow, binned/cached waveform correlation only if lookup-error maximum <=0.025, with exact full correlation fallback at failures.
4. Check zero-lag <= peak-lag, positive counts <= eligible opportunities, and stable TF baseline outside group.
5. A result changing with the waveform curve is a **failure of unqualified universality** of v1, not something to delete/rescue; preserve all effect signs.
6. CI shall print aggregate results and store compact JSON on branch/Action; never redistribute original DOCX or original bat IDs.

If original author source waveform remains unavailable, the permitted result is only cross-waveform sensitivity of this model family, never Hase Figure 5 re-execution.
