# v48 — Original wild GPS destination AHN2 elevation NOT robustly predicted by true tide phase in two Wadden islands

**2026-11-05 JST, original field results frozen.** Original outcome-blind source contract: [V48_FROZEN_NEXT_DESTINATION_ELEVATION_TIDE.md](V48_FROZEN_NEXT_DESTINATION_ELEVATION_TIDE.md), before this v48 altitude prediction was first evaluated. *But prior v32–v44 source speed+direction results were already known*, so v48 remains a post-result exploratory mechanistic probe, not independent confirmation.

## C-only terrain because B+C source data did not pass v47

v46 original 2011 C GPS destination AHN2 candidate elevation was valid in Schier **1,018** / Ameland **1,243** source three-fix trajectories. v47 added B original start height and found B+C valid only Schier **112**, Ameland **373** (both under precommitted 500), so **DO NOT fit genuine B→C height change, exposure age or moving wet–dry boundary pursuit**. For v48, target is the original AHN2 terrain elevation **z(C)** at the actually observed next GPS fix only; the source terrain measurement is **not constructed from the tide height**, unlike a `z>η` response.

Same source-only 2010 GPS bird-day ranked **eight predeclared 2km RD EPSG:28992 cells** per island, historical AHN2 2007–2012 original WCS DTM 256px/2km (~7.8125m sampled), original source Float32 first candidate height band and a 0–1 auxiliary (formal quality/mask semantics not verified) with conservative eligibility ≥0.999. 2011 test destinations never influenced tile selection. No water mask fill; missing seabed cells remain inaccessible. Original GPS source SHA256 and provider MD5 verified. AHN2 exact site flight/year and actual seabed/exposed habitat unknown.

At original middle B fix, M0 uses source absolute RWS NAP water height h(B), h², source B lat/lon, diel+seasonal cycles, original own previous A→B unit horizontal direction and `log1p(prior km/h)`. Mreal = M0 plus original measured RWS ebb/flood and phase×true h(B); Mghost = M0 plus **the same station's original observed water phase exactly one calendar year earlier** and phase×**true h(B)**. Source WATHTE meting original cm/NAP fixed UTC+01: **52,561 original measured values each calendar year 2009, 2010 and 2011, both stations**. Clock native GPS UTC or GPS time ambiguous, tested fixed primary 0s and −15s sensitivity. True RWS slack excluded from all models; ghost slack retained. Train source **2010**; test source **2011** entire year, individual-equal ridge λ10 / train-only scaling; test MSE in **square metres** and paired bird/week bootstrap with matching distinct estimands.

## Verified original support and 2011 test scores (native original GPS clock assumed UTC)

| Site | Original 2010 train C-only z outcomes after gauge join | Original 2011 test C-only z outcomes | Test birds/weeks/source cells | M0 MSE m² | Mreal MSE m² | Mghost MSE m² |
|---|---:|---:|---|---:|---:|---:|
| **Schiermonnikoog** | **1,627** | **1,009** | **13 / 51 / 4** | **0.070288161** | **0.069735259** | **0.068435002** |
| **Ameland** | **1,136** | **1,238** | **5 / 53 / 7** | **1.791095055** | **1.806179673** | **1.793130819** |

Both original source+sample gates pass (minimum train 400, test 500, test 3 birds, 4 weeks, 2 source cells). These are two site-specific different response distributions: **absolute between-site MSE is not comparable as an effect size**.

### Prespecified primary M0−Mreal source phase added prediction

| Original site | Equal-bird MSE gain m² (positive is improved) | Paired whole-bird 95% CI m² | Birds positive | Separate equal-week-then-bird gain m² | Whole-week 95% CI for that distinct mean m² |
|---|---:|---|---:|---:|---|
| Schiermonnikoog | **+0.000552902** (~**+0.787%** relative M0) | **[−0.000182672,+0.001469682]** | **5/13** | **−0.000045889** | **[−0.000612086,+0.000563591]** |
| **Ameland** | **−0.015084618** (~**−0.842%**, error worsened) | **[−0.017973871,−0.011885498]** | **0/5** | **−0.007939117** | **[−0.024053330,+0.008262526]** |

Schier current phase tiny bird-pooled positive but *both* bird and week CIs include zero. Ameland current phase **worsens** altitude forecast on pooled equal-bird target, all 5 birds worse with matching whole-bird CI negative, while different equal-week target CI spans zero. Both are **NOT independently robust positive altitude prediction**.

### Real tide vs year-ago historical tide negative control

- Schier Mghost−Mreal **−0.001300257 m²**, 5/13 birds positive, bird 95% **[−0.003505895,+0.000643290]**, week mean −0.000346397 with week CI [−0.003128351,+0.002285782]. Real phase does **not** establish superiority over previous-year phase.
- Ameland Mghost−Mreal **−0.013048855 m²**, 0/5 birds positive, bird CI **[−0.018229772,−0.007096379]**, week mean −0.007788252 with week CI [−0.021713011,+0.006782019]. Real phase is actually worse in the pooled equal-bird metric; previous-year phase does not itself beat M0 (M0−Mghost−0.002035764 m², bird CI crosses zero).
- Pre-fixed -15s source clock interpretation preserves direction: Schier M0−Mreal +0.000547397, bird CI crosses zero; Ameland M0−Mreal −0.015150684, 0/5 birds positive and bird CI negative.

### Scientific interpretation

**Positive results preserved:** The v43 field GPS next-direction prediction can improve with tide phase (Schier +7.89%, Ameland +14.91% on 2011 original full moving triples), and the v44 same-triple speed-vs-direction contrasts showed a directional information axis, not universally faster travel. **v48 does not erase this positive result.** It tests a *new destination DTM-height target on a restricted AHN2-valid C subset*: Schier 1,009 and Ameland 1,238 instead of the full direction sample Schier 4,948 and Ameland 4,678. Hence it **cannot rigorously demonstrate that direction effects do not depend on height within identical source episodes**; that requires a matched C-height-qualified direction analysis with same GPS cohort.

What is NOT supported: tide phase uniquely predicts next **static terrain altitude** beyond own movement and time/position/height controls, or birds select a newly exposed band of the Wadden intertidal landscape. A tidal state can change travel route directions without changing destination elevation, but such *isohypse movements* are a **new hypothesis**, not established from this restricted source.

Interpretation risks: historical AHN2 single static height is not a time-resolved wet/dry front, second WCS normalized band meaning undocumented, LiDAR largely masks water, 2010 bird-day hotspot tiles select high-occupancy habitats, surveyed years may differ from 2011 tracking, lack of direct prey/foraging state, gauge station hydrograph at site differs from locally experienced tidal water, source GPS device clock UTC/GPS time unresolved, regional correlation and only 5 Ameland birds.

## Original reproduction

- [Full original AHN2+GPS+RWS two-island successful run 41958169153](https://github.com/zuizui0223/boids/actions/runs/41958169153) (test suite, original GPS MD5, AHN2 raster SHA, RWS three-year original NAP measurements, test scores and source counts).
- [Spec fixed before opening new v48 elevation scores](V48_FROZEN_NEXT_DESTINATION_ELEVATION_TIDE.md).
- `validation_v48/ahn2_destination_z_tide_prediction.py` and `test_ahn2_destination_z_tide_prediction.py`. Raw GPS identities, positions, accurate timestamps, AHN2 raw pixels and tide series are never committed; only aggregated data and source manifests.
- Follow-up scientific test should use **exact C-height-valid same episodes to test v43 tide-conditioned next heading**, thereby excluding sample-selection differences before proposing route direction is not related to destination elevation. A physically calibrated local front and prey availability still remain unmeasured.
