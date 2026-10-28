# v15 frozen observed 2D turning forecast — negative primary result

**Date:** 2026-10-28 JST. **Status:** Completed *exploratory observed-data benchmark*, not a demonstration of biological social force, niche partition, individual learning or 3D flight. The preregistered source eligibility gate **passed**. The preregistered *current partner versus same partner 10-second-stale* forecasting direction was **negative in all three held-out source trials**.

- [Pre-outcome frozen contract](OBSERVED_HORIZONTAL_TURN_FORECAST_CONTRACT_V15.md) was committed at SHA `144a142dc4482b32eb4eca408edd3219c4852490` (clarifying no-future partner measurement amendment at `83036e490b46a693cd911ce3e580394ef8837780`), before numerical turning results.
- [GitHub Actions completed run 40610956613](https://github.com/zuizui0223/boids/actions/runs/40610956613) and [independent full replay run 40610981484](https://github.com/zuizui0223/boids/actions/runs/40610981484) produced **numerically identical results**. Both passed 13/13 preregistered unit tests, source/member checksum gates, and full aggregate-receipt checks.
- Published workflow artifact (aggregate-only, no GPS tracks): `boids-v15-registered-observed-trial-results`, first run artifact ID `12782647670`, ZIP SHA256 `011fdfdb2f049d5efbc539c7f3aaf6697b870d25fb59bbb0804699716538bc22`. The digest refers to the **artifact ZIP**, not the inner JSON, and the artifact is currently retained through 2026-12-12 UTC.
- Original data: Huang, Li, Shang and Yang (2026), Zenodo [10.5281/zenodo.21092705](https://doi.org/10.5281/zenodo.21092705), CC BY 4.0, exact verified ZIP SHA256 `756eed718ad13c14233e60b19009ce0916f183eb540b1262ba030ebc25a0ab03` (126,588,691 bytes). **56/56** sensor members matched SHA256. No original raw data were redistributed.

## Observational eligibility

| Structural QC from original NMEA | Trial 1 | Trial 2 | Trial 3 | Total |
|---|---:|---:|---:|---:|
| Raw valid RMC fixes | 16,302 | 235,676 | 19,319 | 271,297 |
| Qualified uninterrupted airborne GPS segments | 7 | 12 | 10 | 29 |
| Original fixes in accepted airborne runs | 5,336 | 9,083 | 5,086 | 19,505 |
| Focal bird IDs with valid matched forecasts | 7 | 11 | 10 | 13 unique source IDs overall |
| Frozen **primary** target-matched 5-s anchors | **132** | **202** | **163** | **497** |
| Secondary 30-s lagged-surrogate matched anchors | 104 | 158 | 122 | 384 |

The source contained only **three independent flock-flight trials**. Multiple bird GPS records in the same trial are not independent field replications; four IDs appeared in all three trials. Even a unanimous 3/3 trial directional sign test would yield minimum one-sided p=0.125.

Flight gates enforced **6–35 m/s** ground speed, **≤0.5 s** raw GPS continuity, ≥12-s run and ≥60 fixes, and a 5-s UTC anchor grid. Current/stale other-bird fixes were recorded no later than focal-time raw GPS, ≤0.2 s old, with nearest-neighbor selection within 100 m. No interpolated/repaired time was used. Trial 2 originally contained many non-flying device fixes, but its retained airborne sample did **not** dominate the analysis: results are equal-trial averages and training was trial-balanced.

## Frozen held-out next-turn comparison

Target = wrapped change of *original GPS course over ground* at roughly 1 second. Values are mean squared angular forecast error **rad²**, lower is better. Whole source flock trial excluded for each fold. The exact same 497 event set is scored by every primary model.

| Held-out source trial | Matched events | Zero-turn | M0 own/history/route | M1 **current nearest partner** | M2 same partner **10 s stale** | MSE(M2) − MSE(M1) |
|---|---:|---:|---:|---:|---:|---:|
| Trial 1 | 132 | 0.030425795 | **0.019204842** | 0.020658690 | 0.019369587 | **−0.001289103** |
| Trial 2 | 202 | 0.015812873 | **0.009356749** | 0.010687565 | 0.009528832 | **−0.001158733** |
| Trial 3 | 163 | 0.019947505 | **0.017949340** | 0.019410676 | 0.018366039 | **−0.001044637** |
| Equal-trial mean | — | 0.022062058 | **0.015503644** | 0.016918977 | 0.015754820 | **−0.001164157** |

**Primary result:** mean stale-minus-current MSE = **−0.0011641574741605588 rad²**; **0 of 3** source trials favored the added current nearest-partner features over a 10-second-stale partner. On an equal-trial MSE comparison, M1 error is **7.39% higher than M2**. M1 also scored worse than the simple M0 own-motion baseline in all three trials (mean **−0.001415333302973371 rad²** M0-minus-M1; M1 error is **9.13% higher than M0**).

**Secondary surrogate:** on a separately matched 30-s-history subset (104,158,122 = **384** anchors), compare present partner with a **30-second-lagged version of the *same* partner**, not an independently observed ghost animal. All three heldout trials again had **negative** surrogate-minus-current error: −0.000100937, −0.001353731 and −0.000878189 rad²; equal-trial mean **−0.000777619 rad²**. This subset differs from the primary target set, so the two means are **not interchangeable**. Current partner vs stale 10 s also remained negative in all three restricted-subset folds.

## What is supported and what is not

**Directly supported by this independent real source:**
1. Raw GPS and pairwise synchrony are structurally observable in 2D; stringent speed/continuous-time gating leaves **497** matched prediction events across three trials.
2. The specified *own-history and route* model improved over a zero-turn reference in every heldout trial, at the tested horizon; this is a **descriptive prediction benchmark**, not causal ecology.
3. In the frozen linear ridge protocol, adding present nearest-partner geometry **did not add transferable predictive value** over either own-history or a 10-s-stale version of the same partner. The primary numerical direction was negative in **all three** trials, also corroborated by full deterministic rerun.

**Not supported or not identified:**
- The conclusion does **not** demonstrate that pigeons ignore neighbors, that social forces are absent, or that a neighbor is biologically detrimental; feature choice, GPS course error, common route/environment, narrow flight contexts, and unequal individual contributions remain alternatives.
- It does **not** recover Reynolds separation, alignment and cohesion coefficients, identify interspecific niche partition or verify v13's learning/network-rewiring mechanism.
- Only three independent trial episodes and repeated bird identities prevent strong statistical extrapolation. No iid-fix p-values, biological CIs, or multi-species transfer claims are appropriate.
- The 30-s shifted surrogate is **not a true different-animal ghost control** and should never be called one without qualification.
- Previous frozen v6 bat-pair and v8 pigeon-pair primary same-time social advantages were also **not supported**. Those independent observations and this v15 dataset have different sampling regimes and targets. Their agreement is a limitation on *these* simple transferable prediction models, **not** proof that wild animals lack social interactions.

## Next study must use independent observations, not post-hoc v15 rescue

The scientifically useful next task is to obtain multiple independent flocks, nights or sites with verified timestamps, actual overlapping individual observations and measured movement phase/habitat to test *context-gated* social information, with a new outcome-blind protocol. Do not change v15 cutoff, lag, ridge penalty, partner rule or event set to reverse this negative result. Separately, real v13 niche-hierarchy validation still requires repeated resource rewards, known social-network changes and enough multiday individual/3D sessions. There is no new 3D or ecological niche evidence in v15.
