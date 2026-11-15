# Pre-output lock: two published physical rules on common synthetic scenes (v1)

**Date 2026-11-02. Status: SOURCE-CONSTRAINED NEW PROXY SIMULATION, not numerical replay of either original paper. No new animal measurements.** Freeze this specification before inspecting this branch's common-scene outcomes. All 2020/2026 article conclusions and earlier bat and boids PRs remain unchanged.

## Source-derived exact pieces

**Hase et al. 2026, DOI 10.1098/rspb.2026.0921:** Within-group frequency state follows
`tau * dF_i/dt = F_i0 - F_i + sum_{j != i} C_ij * P_j(t) * max(0,1-abs(F_i-F_j)/3)`,
using `tau=0.200 seconds`, `C=20` if own terminal frequency exceeds another's and `C=-4` if own is lower, `F` measured kHz. Numeric method fourth-order Runge–Kutta, dt=0.001 s. The paper additionally simulated stochastic frequency drift, moving 2D flight trajectories, irregular emitted pulse intervals and measured angular/distance attenuation. THESE extra components are NOT reconstructed in this pilot. Same article: FM signals 3 ms duration, 40-kHz bandwidth, cross-correlation threshold 0.5, and 5–10s within a 15-second period for group acoustic coupling.

**Mazar & Yovel 2020, DOI 10.7554/eLife.55539, original 2020 MATLAB source SHA256 913dc06b606cecaeb33558de3ab97f8eca618eda302bd1cb720c2b11fc74baff:** `IsPreyDetected.m` contains source-native threshold comparison of echo dB power versus noise and pulse-detection threshold, plus a clutter masking comparison; `BatSonarDecision.m` triggers its JAR after a hunted prey has been marked masked. The complete correlation/filter-bank implementation and its prey/flight process are NOT ported here. The benchmark substitutes only a transparent source-inspired threshold; it MUST NOT be called 2020 MATLAB replication.

## Explicit additional assumptions, not observations

- Exactly **4 or 8** fixed synthetic 3D bat positions (not the original 2026 moving 2D geometry) and 15-second timeline. Baseline frequencies in an arithmetic progression symmetric about 48 kHz with step 0.4 kHz; deterministic, not originally sampled from the published Gaussian.
- Two geometries: "compact" scale 0.7 and "dispersed" scale 3, applied to predefined 3D points. Receiver normalized pulse strength = `min(1,(1 m / separation)^2)`, ignoring source airborne attenuation and angular directivity.
- Each synthetic bat emits a 3ms pulse every 70ms with a deterministic offset 17ms × bat index. Source empirical mean IPI was 70ms but actual original IPIs are gamma distributed. Pulse arrival propagation is omitted; this pulse schedule is ONLY the frequency drive and not a simulated 3D encounter history.
- Frequency drift noise is fixed zero. Base frequency control stays fixed but uses **identical** pulse schedule and geometry as the JAR forward dynamics; no tuning for expected effect direction.
- Linear downward 3ms FM chirps are sampled at **250k samples/s** with 40 kHz bandwidth. The published 2026 paper uses a species-informed pulse waveform (not necessarily a linear chirp); therefore this is a distinct receiver waveform hypothesis.
- Compute waveform normalized absolute correlation at (a) exactly zero lag and (b) maximum absolute correlation across ±0.35ms lags. The source used cross-correlations and threshold 0.5, but no claim is made that this synthetic lag acceptance or normalization exactly matches its source detector.
- A toy prey receiver compares synthetic prey echo margin in {3,6,9,12}dB with an illustrative noise-plus-interferer masking level derived from pairwise waveform correlations. Receiver multiplier=10 and threshold offset=3 dB are deliberately illustrative. Use the *same* receiver constants in JAR and no-JAR. No actual prey echo timing, capture trajectory, sonar ranging or verified false-alarm cost.
- Do not fit, optimize, or add sweeps after opening this result. A negative or non-monotone outcome is accepted.

## Endpoints

1. Difference in group-mean terminal-frequency pairwise absolute separation (within last 2s of source group-coupling window) between JAR and source-constant-frequency counterfactual.
2. Change in proportion of distinct ordered pairwise other-bat chirps whose correlation peak crosses 0.5, **zero lag vs ±0.35ms search** separately. These are **synthetic possible confusions**, not detector false alarms or prey attacks.
3. Change in synthetic threshold-correct target echo detection across fixed echo-margin grid, including both lag-treatment modes. The source-inspired threshold is a proxy, not the full 2020 detector or measured prey acquisition.
4. Cross-check exact identity `lag-optimized correlation >= zero-lag correlation`, correct units, direct path equality JAR/no JAR outside 5–10s, and finite outputs.
5. An independently coded pure waveform frequency-shift fixture at TF 48kHz and deltas `0,0.3,0.7,1,2,3,5,8`kHz, test whether allowing time lag can restore cross-correlation without changing true source spectral difference. **This tests waveform time/frequency ambiguity, not a novel bat neurophysiology fact.**

## Scientific stop

No comparable original 2020 vs 2026 numerical replication, species-specific behavior law, empirically calibrated capture advantage, population-scale mechanism or new field dataset can follow solely from this proxy. Report source-derived vs synthetic choices explicitly. Validation executes Python/Numpy on a separate GitHub Actions workflow and stores only aggregate summaries. Do not promote negative tests to an equivalent/zero effect.
