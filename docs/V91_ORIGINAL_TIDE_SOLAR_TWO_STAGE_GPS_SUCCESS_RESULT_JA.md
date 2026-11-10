# v91 Real observed tidal×solar two-component decomposition (2026-11-10 JST)

**Original source SUCCESS:** [GitHub Actions #42604921696](https://github.com/zuizui0223/boids/actions/runs/42604921696), attempt 3. The first two source attempts were blocked by Rijkswaterstaat HTTP429; the third unchanged-source run succeeded. Genuine 2010 Zenodo oystercatcher GPS, RWS 10-min water levels, NIOZ monthly modeled tidal-exposure indicator, and WMR published historical mid/high intertidal ecotope map all authenticated. Tests (v91 8, v86 6, v82 7, v77 6) PASS. Original older v82/v86 whole-bird estimates and intervals exactly replayed **before** new decomposition.

## New original 2010 results

Same bird×month×2010 RWS measured 0.2-m water-height bin; all flood/ebb × day(>+3°)/night(<−3°) condition cells with ≥5 original GPS fixes each. Schier **18 real birds, 857 four-cell groups, 41,734 GPS fixes**; Ameland **10 real birds, 381 groups, 19,407 GPS fixes**. GPS fixes are repetitions of tagged animals, not independent birds.

- Define Y=1 when actual used GPS cell is in WMR mapped mid/high intertidal class 3/4 (Y=0 includes other genuinely usable low tidalflat classes, land/water/rest sites); p_c is used GPS fraction in category. Define R as the used GPS point's original NIOZ monthly model index *midrank* against all grid cells within 1km minus 0.5, with **unknown physical index units**, not observed dry time. The four-way effect is D(z)=(flood night − flood day) − (ebb night − ebb day).
- In each real four-condition stratum, pool original GPS locations across the four conditions with observed-location weighting to define mean R inside and outside (mu_in^0 and mu_out^0). The fixed descriptive composition contribution is D_comp=(mu_in^0−mu_out^0)×D(p). The remaining residual contribution is D_resid=D(R)−D_comp. Source interval: 10,000 whole-bird cluster bootstrap, per island.

| Fixed original field estimand | Schier | Original whole-bird 95% CI | Ameland | Original whole-bird 95% CI |
|---|---:|---|---:|---|
| Earlier v86 GPS mid/high intertidal class interaction D(p) | −0.0561557 | [−0.0769972,−0.0357502] | −0.0203798 | [−0.0933136,+0.0841505] |
| Earlier v82 GPS monthly modeled exposure rank interaction D(R) | +0.0499791 | [+0.0223793,+0.0831319] | +0.0052738 | [−0.0341010,+0.0546901] |
| **NEW composition contribution D_comp** | **+0.0072413** | **[+0.0039768,+0.0106367]** | −0.0020320 | [−0.0370462,+0.0483096] |
| **NEW conditional/composition covariance residual D_resid** | **+0.0427378** | **[+0.0152030,+0.0767202]** | +0.0073058 | [−0.0088928,+0.0226272] |

**Main falsification:** The previously frozen (but already post-v86) exploratory prediction *Schier D_comp negative / D_resid positive* is **NOT supported**, because D_comp is positive and excludes zero. Original positive whole-bird contribution counts are 14/18 for each new Schier D_comp and D_resid.

**Why opposing signs of two prior endpoints are not logically contradictory:** among the **676/857 Schier four-cell source groups with both habitat categories**, the **median of pooled inside-minus-outside R index = −0.1197688** (5–95 percentile [−0.3119680,+0.1046835]). Hence D(p)<0 can multiply a negative class rank contrast into D_comp>0. In Ameland among **362/381** groups with both categories, the corresponding median inside-minus-outside R rank = **+0.3314488** (5–95 [−0.0966501,+0.6504651]). That change of local class-index meaning matters; original group percentiles are descriptive and not independent field organisms.

**Two fixed sites, independent whole-bird cluster resampling:** Schier−Ameland D_comp +0.0092733, 95% [−0.0429590,+0.0440539] = **site difference not established**. D_resid difference +0.0354320, bird 95% [+0.0037705,+0.0715913] = **exploratory positive fixed-site difference**. These two adjacent Wadden islands do not estimate global coast random-effects variation. The original four-cell algebra identity error is < 1.4e−16.

## Critical limitations and next genuinely biological test

This is the SAME 2010 bird cohorts already analyzed in v82/v86; the split is an exact algebraic description, not an independent new biological experiment. NIOZ monthly index is not a momentary exposure time or measured prey, WMR Y=0 includes real lower tidal flats, GPS used locations need not be feeding/roosting, original receiver GPS-vs-UTC calibration remains unknown, 2010 June–July source raster latitude is explicitly inferred from a verified static model grid and official corrected WMR2021 map exact version identity is unverified. None establishes active within-flat choice or internal tidal clock.

A future causal/transferable model needs independently observed animal behavior and source-verified available habitat: local referenced bed elevation z(x), measured stage h(x,t), real tide-front propagation, light-dependent utilities, reachable alternative roost/foraging sites, and effort/detection controls. The model must compare behavior beyond that physical opportunity with independent bird/coast/taxon/tide-cycle holdouts. Existing negative v69/v70 extra tide×solar next heading prediction remains negative, and external other species WATLAS + Leizhou source support remains insufficient/access blocked.

**Original reproducibility:** v91 action artifact ID 13731407470, named v91-authentic-original-Wadden-two-stage-tide-solar-mix-decomposition; source anonymous numeric JSON, frozen source definitions in docs/V91_FROZEN_ORIGINAL_TWO_STAGE_TIDE_SOLAR_GPS_MIXTURE_DECOMPOSITION.md and verification code validation_v91.
