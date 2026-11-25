# v48 completed: polarization × prediction horizon is heterogeneous across three source studies

2026-11-25 JST. Original fixed v48 run [45572378950](https://github.com/zuizui0223/boids/actions/runs/45572378950) completed all three jobs SUCCESS. All original source and six-model replay gates passed, all speed×polarization cells admitted (minimum group times: tetra 1196, ayu 256, zebrafish 2953). No state-dependent refitting. v47 dispersion and v46 independent hierarchy nonreplication retained. Zebrafish is a same-source replay, tetra and ayu are new endpoints in previously studied source datasets.

Define F=100*(MSE_NEAR_TRUE−MSE_FAR_TRUE)/MSE_GLOBAL for each original heldout evaluation unit, state and prediction horizon. K=(F_highP−F_lowP)_delayed−(F_highP−F_lowP)_short. Positive K indicates that increased polarization relates to relative far advantage more at the longer prediction horizon. Speeds are within-recording rank halves, not equal physical speed thresholds between species.

| Study | All states K, pp (positive) | Low speed K (positive) | High speed K (positive) | Equal speed-stratum K (positive) | High minus low speed K |
|---|---:|---:|---:|---:|---:|
| Tetra 6 files | −.063889 (2/6) | +.040632 (4/6) | −.103310 (1/6) | −.031339 (4/6) | −.143942 |
| Ayu 7 files | +.348050 (5/7) | +.450239 (6/7) | +.041536 (3/7) | +.245887 (5/7) | −.408703 |
| Zebrafish 8 trials | +.079205 (7/8) | +.004744 (6/8) | +.107857 (7/8) | +.056301 (7/8) | +.103114 |

Frozen v48 transfer: tetra NOT_SUPPORTED, ayu NOT_SUPPORTED (5/7 <6/7 prespecified). Zebrafish SAME_SOURCE_REPLAY. No new independent confirmation of universal positive K. Descriptive paired 95% intervals (state GLOBAL normalization): tetra overall [−.156282,.015345], high speed [−.200274,−.014590]; ayu overall [.080734,.596099], low speed [.126330,.741886]; zebrafish equal-speed-stratum [.025375,.083689], high speed [.042464,.157520]. Speed moderation (high−low) intervals tetra [−.294327,.011234], ayu [−.719559,−.084801], zebra [.027216,.160188].

## Denominator sensitivity and independent numeric check

Downloaded original three artifacts and verified each ZIP digest. Independently recomputed all 5 signed K arrays for each of 4 normalizations (60 combinations total) from saved source-safe state MSE matrices, using NumPy and same fixed 10000 paired bootstrap draws. All per-unit K and interval quantiles agreed to 1e−10 absolute/relative tolerance. No refitting in this audit. All three speed-moderation point-estimate signs are preserved across four normalizations; intervals vary, so no denominator-robust claim of significance. Equal-speed-stratum K on full-recording GLOBAL changes zebrafish positive count 7/8 to 5/8 and CI crosses zero. Thus speed conditioning reduces confidence; do not say speed has been fully controlled or causal modulation established. Within-speed rank bins are not matching. Raw MSE not comparable between studies.

| Scale | Tetra K high−low | Ayu K high−low | Zebrafish K high−low |
|---|---:|---:|---:|
| State GLOBAL (pp) | −.143942 | −.408703 | +.103114 |
| Full GLOBAL (pp) | −.225244 | −.464278 | +.044956 |
| State G_geometry (pp) | −.095295 | −.390434 | +.082571 |
| Native MSE | −.028588 | −44.147122 | +1.0276684e−5 |

Artifact IDs and original ZIP/JSON SHA256:
- Tetra 15002482854 / 7ac770a4c2425e7569f265fd690c783cb3d500056d2b13859de215f792afff2e / 74afe2917dc7924728330fb8022cb04d7b198bd454729b9416447a23a360e786.
- Ayu 15003545097 / 5c23516a6b807974bbc3694f48ce0902dedf25783d07e6cbbe3fb46f2de9994f / 69952920a5ae2bccddac617dfd09a157a492ad2d99ce697bbf35f16d0ca8b465.
- Zebrafish 15002602208 / 96755c92ab081b969af770f727e5a92c05abeb1f2aa43c26f0ff8fdd81e28617 / 2e365b6975c4d0b37d34b7044aff996e417a935bc4fd1ab267945598375a1943.

Maximum absolute replay error 1.44595e−12 tetra, 8.51287e−10 ayu, 0 zebra. Partition recombination 1.72662e−12, 1.04046e−9, 1.45647e−14 respectively. The model predicts heldout focal 2D velocity, not communication or causal perception. Study species, habitat geometry, group size, tracking and behavior differ. Tetra/ayu file independence unverified. No pooled species estimate. Next use all 84 stickleback trials in actual 12 author shoals, no independent trial inflation. Main unchanged.
