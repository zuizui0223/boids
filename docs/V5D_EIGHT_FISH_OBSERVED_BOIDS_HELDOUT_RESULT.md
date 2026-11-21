# v5d: Original 2024 eight-fish movement data — whole-trial heldout Boids forecast

**Date:** 2026-11-20. **Outcome:** observed movement prediction, NOT observed fish vocalization or causal force. This report summarizes original [GitHub Actions run 44743721112](https://github.com/zuizui0223/boids/actions/runs/44743721112) and its [full original numeric artifact](https://github.com/zuizui0223/boids/actions/runs/44743721112/artifacts/14631573887).

## Authentic data and source scope
- Source: Puy et al. 2024, *Selective social interactions and speed-induced leadership in schooling fish*, PNAS DOI 10.1073/pnas.2309733121, original Zenodo DOI 10.5281/zenodo.10890112.
- Re-download all **six** independent recording FILES of 8 tracked fish, verify every author-published MD5 before numeric outcomes. Native CSV 17 fields: frame and 8 X/Y pairs. Native 50 fps; coordinates pixels converted to cm using published 100 cm tank / 2745 px scale.
- Actual source rows per recording (excluding header): 82998 / 89999 / 89999 / 89999 / 179999 / 114998, so source durations not uniformly 30 min. All source frame IDs monotonic, finite eligibility and exact native ±5/±10/±100-frame time supports verified by script.
- Two large **39-fish** recordings were NOT downloaded or evaluated (each >260 MB; outside registered 70 MB per-file cap).
- Native trajectories may have source smoothing/interpolation using later frames; therefore this is **retrospective heldout-trial prediction**, not prospective online forecasting.

## Precommitted comparison (protocol frozen before observed numbers)
One complete recording withheld and the other 5 used to train **fixed ridge alpha=10**, training-only standardized features; no random frame train/test split. Future target is average 2D velocity over **0.20 s = 10 native frames**, MSE both velocity components with unit (cm/s)^2.

- M0 `self`: focal fish current/past velocity, acceleration and tank-wall location.
- M1 `boids`: M0 plus neighbor separation (8 cm), alignment and cohesion (25 cm), neighbor count.
- M2 `speed_selective`: M1 plus velocity adjustment from **faster** neighbors and number of such neighbors.
- Ghost `stale_school`: M0 plus same-dimension **2s historical** neighbor features, available before the current time. Same response frames for all four models.

| Heldout 8-fish recording | Scored fish×frame targets | M0 own | M1 standard Boids | M2 faster-neighbor | 2s-old neighbor ghost |
|---:|---:|---:|---:|---:|---:|
| 0 | 66,304 | 15.271002 | 12.115604 | 12.014887 | 15.270500 |
| 1 | 71,904 | 13.191108 | 10.581969 | 10.518581 | 13.187860 |
| 2 | 71,904 | 12.427786 | 10.120567 | 10.062249 | 12.426420 |
| 3 | 71,904 | 13.063790 | 10.559745 | 10.513109 | 13.063150 |
| 4 | 143,904 | 13.705234 | 11.879668 | 11.882550 | 13.706510 |
| 5 | 91,904 | 15.759426 | 12.682023 | 12.567394 | 15.759170 |

Table displays rounded source-safe scores. Refer to the exact full-results artifact for exact per-trial MSE and SHA256 receipts rather than treating rounded table numbers as a bitwise artifact.

**Equal-recording mean MSE:** M0 **13.9030577584**, M1 **11.3232625068**, M2 **11.2597949695**, ghost **13.9022691375** (cm/s)^2.

- **PRIMARY M0→M1 Boids gain +2.5797952516 (cm/s)^2**, **18.5556%** relative reduction, **6/6** recording signs positive. Original trial bootstrap descriptive 95% [**+2.207558,+2.925282**]. Exact one-sided sign p=**0.015625** *assuming independent trial signs*.
- **Secondary M1→M2 speed-selective increment +0.0634675373 (cm/s)^2** (**0.5605%** reduction relative M1), **5/6** positive, exact one-sided sign p=**0.109375**; descriptive bootstrap [**+0.032077,+0.092911**]. **The predetermined six-trial sign consistency is NOT achieved**, notwithstanding the positive conditional bootstrap. Existing Puy et al. already reported selective faster-neighbor dynamics; no novel discovery here.
- Ghost→contemporaneous M1 +2.5790066307 (cm/s)^2, **6/6** positive; descriptive bootstrap [**+2.212034,+2.928898**], sign p=0.015625 under trial independence.

## Scientific interpretation boundary
The result establishes that **instantaneous neighbor spatial/motor information helps predict near-future motion on a withheld recording within this one species/study**, beyond focal past motion and wall position, under the fixed model. It does NOT identify individual separation/alignment/cohesion as distinct causal forces, nor infer fish communication, acoustic chorus formation, stable interspecific niches or global generality. Additional predictors can proxy shared position, acceleration, swimming context or experiment design. Six recordings may share fish or setting; not six independent fish populations. Correlated fish×frame targets are **not biological replication**. Nominal six-sign p requires record independence.

Next critical validation: repeat the **same frozen endpoint** in an independent fish population/recording dataset, with the same source morphology and units. Separately test sound-source localization in the XAV OSF audio/video data. Never conflate these distinct datasets as simultaneous fish-schooling and chorusing observations.

**Source published findings were already known**; novelty, if any, is strict heldout-trial transfer, not an entirely new biological school-force phenomenon. Keep Draft PR; do not merge on this single-source effect alone.

