# v124 independently verified 36-cell geographic validation: rho +0.960 is real arithmetic but NOT unique to observed map alignment

Date 2026-11-11 JST. [GitHub Actions #42969127219](https://github.com/zuizui0223/boids/actions/runs/42969127219) SUCCESS, four source/source-identity/no-pseudorep known-truth tests PASS; source is exact TRUE v123 [#42968384405](https://github.com/zuizui0223/boids/actions/runs/42968384405) 36 original 2021 native20m RWS dry-index cells. Original 2019/Oct2020 historical terrain and 2016/2021 published M2 dry-duration TIFF source SHA/CRS QC previously passed before v124. v124 reads only the already published and source authenticated 36-cell true native-2021 coarse table; it does NOT refit original bathymetry, cherry-pick sites, interpolate missing pixels, infer native dry-index units, claim 36 organism replicates or recompute any original bird effects.

### Independent arithmetic and projection metadata checks

Independent **scipy.stats.spearmanr** (not the v123 custom rank helper) EXACTLY reproduces the previous original 36-cell Spearman results:
- Primary, retaining the original genuine 2016 source WKT PROJ stere versus native 2021 EPSG28992 PROJ sterea: rho(original 2019→Oct2020 ground z change, original 2016→2021 drying-index native numeric change) **+0.9604240395**; 36-cell unadjusted native drying raw-index mean change **+2.77777778**. Coarse cells with positive model code change: **23/36**; zero **1/36**; negative **12/36**. Thus a positive mean and high rho do NOT mean every source cell has increased dry duration.
- Sensitivity, overriding original 2016 TIFF's contradictory terminal EPSG authority (which differs by 3.82m from its actual Stereographic native projection): rho **+0.9618771869**, 36-cell raw native index mean change **+2.91666667**, positive **23/36**, zero **4/36**, negative **9/36**. This is a projection assumption only, not an independent map.
- Real Oct2020 original height versus published 2021 modelled dry-index raw score rho **+0.9875818036** for BOTH 2016 CRS assumptions. This extraordinarily strong association is expected because height is an input to hydrodynamic dry-duration models.

### Spatial-dependence diagnosis, POST-outcome and NOT a statistical test

The 36 true coarse source cells form one geographically contiguous **6×6 original 20m plot**, NOT 36 independent study units or 36 random coasts. v124 performed diagnostic no-refit map shifts determined on that fixed grid, without assigning a p-value:
- TRUE original aligned primary rho=**+0.9604240**.
- The **35 other toroidal cyclic map offsets** preserve much of the 2016→2021 drying-index map's internal spatial texture but physically wrap boundaries, which is an unrealistic geography. One WRONG map shift (0 rows, 5 columns) achieved **rho=+0.9630069**, slightly **HIGHER** than true original aligned primary. Thus even this very strong source rho is NOT unique to the exact geographic correspondence.
- Sensitivity CRS override: true rho+0.9618772, maximum wrong toroidal shift +0.9551281. There are 0 of 35 wrong offsets as high in this alternative; that apparent difference by source projection is another reason not to promote a single coordinate interpretation as proof.
- Leave one complete 20m source ROW out, six cases: primary rho **+0.9330 to +0.9679**; leave one COLUMN out (six cases): **+0.9567 to +0.9648**. These are observational source stability checks, NOT spatially independent confidence intervals.
- As an explicitly post-hoc geographic diagnostic, remove a linear spatial row/column trend from both mapped variables: Spearman of residual values remains **+0.8772** primary, **+0.8412** CRS-override. This does NOT correct all spatial autocorrelation, physical model endogeneity or temporal mismatch.

None of the 35 toroidal shifts are valid field experiments or official randomization nulls, because a 6×6 torus creates artificial edge seam pairs and the source is one single shoal. We must NEVER report shift-count/36 as a formal p-value, or leave-row ranges as independent 95% intervals.

### Consequence for time-niche paper

**Accurate narrow claim:** authenticated original 2016/2021 published modelled dry-duration native scores and observed historical terrain-height changes of the Roggenplaat plot are strongly co-varying, robust in *sign* to interpreting source 2016 raster projection two ways. That source pattern is substantially explained by model construction/physics and spatial trends. It does NOT establish bird behavior, measured substrate dry hours at 2020 GPS locations, prey, active feeding, adaptive habitat choice, hydrological propagation to bird locations, independent cross-species/coast transfer, or novel ecological time-niche law.

Observed 2020 two-gull GPS tide×sun movement v111 and observed static source wetland used-location v112 taxon contrasts were NOT ESTABLISHED. Later v113–v115 found exploratory static spatial use differences, NOT a unique true-tide time signature. Original v118 2019 ground DTM source 8-point valid only 41.7%/57.8% of 2020 gull step alternatives, below pre-frozen 90% true local dry-habitat support gate. Original 2020 Oct DTM and 2021 modelled dry duration postdate May–July gull fixes. The right next field test requires real independently georeferenced/dated local z(x), h(x,t), reachable alternative substrates and actual foraging/activity labels. No new bird-time niche effect was estimated in v123/v124.

Source code: validation_v124/independent_SciPy_2021_native20m_spatial_shift.py, four unit tests and frozen explicit POST-v123 protocol docs/V124_POSTOUTCOME_INDEPENDENT_20M_SPATIAL_SHIFT_VALIDATION.md; source v123 publicly usable 36-cell original ecological-model/environmental aggregate, no individual bird GPS/raw tide series.
