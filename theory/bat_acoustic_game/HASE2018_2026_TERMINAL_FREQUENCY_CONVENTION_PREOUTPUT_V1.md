# Pre-output source-crosswalk: what is held fixed when a bat changes TF?

**2026-11-02, SOURCE-CONSTRAINED SYNTHETIC benchmark, NOT empirical replication.**

## Prior data, no new measurements

Hase et al. (2018), *Communications Biology* DOI 10.1038/s42003-018-0045-3, Figure 4c–e, reported a peak cross-correlation half-maximum when synthetic bat-like 3-ms frequency-modulated calls' terminal frequency changed by about **2%, approximately 1 kHz** near 45–48 kHz. Its example source waveform sweeps ~90→45kHz in 3ms. This is an already published finding, not a newly held-out source. No raw 2018 audio obtained: official Dryad DOI 10.5061/dryad.4f99c46 metadata CC0, source file 614,454,096-byte SoundFile.zip MD5 `c6651cc04aefbdaf0cce77b184b8a8c9`, authenticated file GET returns HTTP401 (Actions run 41411436841). Do not attempt unauthorized bypass.

2026 paper DOI 10.1098/rspb.2026.0921 constructs a 3-ms 40kHz bandwidth pulse with TF changes. Full author signal formula remains unavailable in its 15 public data-model files and two supplementary DOCX manuscripts. The `source_timing_waveform_v2.py` computed shape sensitivity with **fixed bandwidth**.

## BEFORE inspecting this new output, freeze 2 source-formula conventions

For precisely the same pre-existing three SYNTHETIC waveform curvatures `p=1,0.6,2` and a 3-ms signal at 250kHz, compare normalized full-lag absolute correlation of **two** 3ms synthetic pulses for original TF and modified TF. No additional shape parameters may be fitted after opening.

- **2018-like fixed start frequency**: baseline Fs=90kHz TF=45kHz; change TF by `+Δ` but keep Fs=90kHz, so sweep bandwidth changes from 45kHz to (45−Δ)kHz. *This is one possible operationalization of changing TF while holding initial frequency fixed; original author waveform formula is not reproduced*.
- **2026-like fixed bandwidth**: baseline TF=48kHz, bandwidth=40kHz; add `+Δ` to TF while B stays40kHz, causing starting frequency to change by Δ too, as assumed by v2. Note that original group calls need not hold B exactly fixed.

Predeclared Δ grid in kHz `(0,.25,.5,.75,1,1.25,1.5,2,3,4,5,6)`; same source figure half-height 0.5 threshold, three shapes, both fixed conditions. Calculate exact normalized amplitude cross-correlation peaks over all finite waveform-relative time lags (not zero-lag only). Report full 2×3×12 results and linearly interpolated first crossing under 0.5, or NOT_ESTIMABLE.

Additional output with **no TF shift** is trivial identity. Distinct baseline Fs and B mean the two protocols are not direct numerical comparisons of one common chirp: the scientific target is relative sensitivity to **which other sound property is held constant**, not a pooled source effect.

Do not tune exponents to achieve 2018's ~1kHz threshold. Report whether each prespecified waveform/protocol reproduces that order of magnitude; no p-values or prey-payoff claims. The 2018 source cannot serve as genuinely independent support for 2026 behavioral mechanisms, because source lab/species/method lineage overlaps.

## Failure of transfer criterion

If a putative "waveform curvature causes JAR benefit" result vanishes after distinguishing fixed-B versus fixed-Fs manipulations, the appropriate conclusion is **manipulation definition and waveform jointly govern predicted matched-filter discrimination**, not "curvature is a universal bat strategy." No 3D bat encounters or original prey capture are modeled by this crosswalk.
