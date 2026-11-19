# v40 completed: post-outcome Finnish regional climate-support descriptive result

**Executed 2026-11-19 JST.** The original provider-MD5-verified Finnish bat Data.xlsx (Zenodo 18298435) was re-read on precisely the **4,208** original v39 eligible detector nights. No acoustic response model was refitted, no new inferential p-value or selection criterion introduced. Three synthetic source-logic tests PASS in [Actions run 44464407566](https://github.com/zuizui0223/boids/actions/runs/44464407566). v39 primary positive gate remains **FAIL**: +0.017943 nats/night mean 6/7 positive years but one-sided sign p=.0625. v39 out-of-region mean remains **−0.038835** nats/night, 1/3 positive.

## Climate-support diagnostic, all withheld regions

Train for each test region includes only the OTHER original regions. An observation is "out of support" if its predictor lies outside the training 5th–95th percentile. This definition was **descriptive**, not a physiological weather threshold or a model selection gate.

| Heldout region anonymized | Valid nights | M0−M1 v39 loss gain | Outside train 5–95% temperature | Outside night length | Outside either |
|---|---:|---:|---:|---:|---:|
| region_group_1 | 1,556 | +0.032840 | 10.35% | 28.47% | **34.58%** |
| region_group_2 | 334 | **−0.117115** | 11.68% | 29.64% | **38.92%** |
| region_group_3 | 2,318 | **−0.032231** | 10.70% | 1.81% | **12.51%** |

Region2 has the largest combined climate-range extrapolation and the worst v39 prediction; however region1 has substantial extrapolation and a **positive** v39 gain. Region3 has much less temperature/night-length extrapolation but remains **negative**. Therefore a single explanation based **only on out-of-envelope climate support cannot account for the region-wise sign pattern**; this is not an identified multivariate causal contribution and must not be promoted as a statistical rejection of climate extrapolation.

Additional descriptive original medians:
- region_group_1 heldout temp 12.7°C vs training 13.64°C; heldout night length 6.626h vs training 6.398h.
- region_group_2 heldout temp 11.57°C vs training 13.43°C; heldout night length 7.083h vs training 6.451h.
- region_group_3 heldout temp 13.93°C vs training 12.49°C; heldout night length 6.347h vs training 6.680h.

All original three regions have 7 year labels in test and train under the leave-region-out diagnostic and no heldout period category absent from other regions. Source precipitation's 5–95% envelope misses only 3.8%–6.9% of test nights, while mean wind has region-dependent extrapolation 0.6%–24.0%. No direct prey, canopy, instrument calibration or detection-effort differences were measured by this specific audit.

## Causal and inference boundary

These are **post-outcome environmental covariate summaries only**. They do not demonstrate regional evolution, memory, optimum, behavioral mechanism, or new predictive transfer. The original study's thermal/night-length activity relationship is prior art and v39 did **not** pass its preregistered sign criterion. No refitting or group selection was performed after viewing v39 outputs.

Meaningful next test: verify which independent Italy and Belgium recordings include explicit **measurement-effort / zero-detection** windows and matched time and resource support before cross-country analysis. Do not stitch together presence-only Italian acoustic calls with Finnish active-night proportions or Belgian separate pitfall/transect collections as one common response.
