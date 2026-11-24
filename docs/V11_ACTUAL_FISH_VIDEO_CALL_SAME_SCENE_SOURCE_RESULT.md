# v11 genuine original audio–video fish scene matched (source admission, not new fish motion)

**2026-11-21 JST** — Source Mouy et al. (2023), *Methods in Ecology and Evolution*, DOI https://doi.org/10.1111/2041-210X.14095, original OSF https://osf.io/q8dz4 (supplemental videos CC BY-SA 4.0). Original video plus source CSV gates and fixed annotated stills [GitHub Actions #44837116865](https://github.com/zuizui0223/boids/actions/runs/44837116865) **SUCCESS**, 4 fixture tests passed. [Original source manifest and six-frame contact sheets](https://github.com/zuizui0223/boids/actions/runs/44837116865/artifacts/14678144519). The source integrity and timestamp window match are additional to earlier v6/v10 source SHA checks.

| Original same field scene | OSF original supplemental MP4 | Video technical | Original recorded audio window | Source annotations with UTC timestamp within the window | 3D source localization eligibility |
|---|---|---|---|---:|---|
| Fig 9, lingcod | SuppInfo_Video_Figure9.mp4 (OSF file 640113ebf014b90ad1eb4471) | 1366×680, 20fps, 199 frames/9.95 s | 2019-06-17 15:13:07 UTC, 10s | **17/17** | Earlier v10: **5/17** finite xyz |
| Fig 10, lingcod + 3 quillback rockfish | SuppInfo_Video_Figure10.mp4 (OSF file 640113f940cecd0b3d76e56f) | 860×672, 20fps, 339 frames/16.95 s | 2019-09-20 16:38:58 UTC, 17s | **12/12** (times 1.33–13.70s) | Earlier v10: **12/12** finite xyz |

The two source CSV original SHA-256 values are 095f1f3dbe9b45c480c1987a83a3a2459d38baa3f2ccfccf4824e2f308d7143b (Fig9) and a2270a82dae5435ba992cdeef002e7cdca1aa054edf3e336f80f986f2d9c841b (Fig10), rechecked byte-for-byte before source event clock reads. The video original SHA-256, total byte count and provider checksum check if present are in the retained manifest. Only selected published edited-frame stills and source aggregate are retained in the Actions artifact; no original fish raw video or event xyz files are committed.

### What the video actually is
The original MP4s are **publisher-prepared composite demonstration videos**, with an underwater view occupying approximately one half of the frame and a static+updated acoustic spectrogram/source-localization plot occupying the other half. These are **not** original unannotated 20fps multi-object tracking positions for all 4 fish. The paper explicitly describes the Fig10 behavioral episode: lingcod changes position, rockfish move or avoid, and acoustic localization confirms quillback rockfish as the sound producers. This acoustic/video attribution was already a result in 2023, **not new positive evidence of a causal Boids steering rule**.

The source event UTC timestamps fit the matching 10s/17s WAV clip intervals. This does NOT demonstrate frame-perfect synchronization between the **edited supplemental MP4 playback clock** and original WAV sample time. The original paper aligned field video to acoustic recorders with camera synchronization beeps; those original full-resolution video/clock calibration records are not supplied as per-frame fish trajectories in the currently admitted source.

### New decision
The same-scene source problem is resolved at publication-case level (Figure10 is an actual audio-video linked fish interaction); the missing *analysis-ready* part is continuous per-fish identity/position and individually attributed calls with uncertainty. No entirely new effective sample of independent fish schools has been obtained from Fig10, and 12 vocal events do not create 12 independent fish-level cases.

Strong next data strategy: use the **2016 randomized conspecific call playback experiment** (van Oosterom et al., DOI 10.1038/srep19098) as the already-established audio→cohesion causal evidence, then test the feedback hypothesis separately with raw individual school tracking and randomized acoustic stimulation. Their experimental publication reported shoal area **−4.3%** and spontaneous calls **+229/shoal/10 min**, source-level findings rather than an effect re-estimated here. Collect post-playback persistence and behavior history for the novel hypothesized hysteresis.

**All synthetic feedback numerical results in v12 are model output, not a quantitative reproduction of the 2016 experiment**. Keep PR #248 Draft; main unchanged.

