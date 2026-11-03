# v34 — External island test: Ameland does not reproduce large Schiermonnikoog tide-phase predictive gain

**2026-11-02 JST.** Original observed field GPS, original RWS NAP water, new island. This independent *site* validation was frozen before opening the Ameland outcomes in [V34_FROZEN_AMELAND_EXTERNAL_SITE.md](V34_FROZEN_AMELAND_EXTERNAL_SITE.md). **Outcome: original-source audit PASS, predictive association near zero on Ameland.** Earlier positive Schiermonnikoog results remain unchanged.

## Independent source coverage

- [Zenodo O_AMELAND v6, record 10053853](https://zenodo.org/records/10053853): original UvA-BiTS GPS 2010 119,507 source fixes (compressed 5,972,361 bytes, SHA256 `c92f1a21ee95c41f59e0c3ef4567a0d953b86b134bb895186cab40bb2e6cb61c`) and 2011 81,568 source fixes (compressed 4,115,807 bytes, SHA256 `f1fe4bc16eb8081ab0073326e3494af0ed4798a6044db3327b3fd0dcf9559875`). **Both published MD5 hashes matched**.
- Independent RWS measured `ameland.nes`, `WATHTE`, `meting`, cm above NAP, fixed UTC+01. **52,561 separate source gauge readings** in each 2010 and 2011, ten-minute intervals with no >30-min gap.
- 2010: 15 birds with admissible island GPS movement; 30,860 original-hourly derived 0.5–2h displacement steps. 2011: **5 birds** and **31,216 steps** across 53 source test ISO weeks. Source GPS timestamp GPS vs UTC not independently resolved; fixed -15sec sensitivity reported below.
- Original out-of-island movements excluded by frozen lat/lon envelope. No original bird IDs, fixes or gauge timeseries committed to GitHub.

## Frozen primary: 2010 train → 2011 test, same v33 Mphase model

| Site and test design | M0 equal-bird MSE | Mphase equal-bird MSE | M0−Mphase error reduction | Test birds positive | Test weeks positive | Whole-test-week bootstrap 95% |
|---|---:|---:|---:|---:|---:|---|
| **Ameland 2010→2011** (new island) | 0.173722022 | 0.173718313 | **+0.000003709 = +0.0021%** | 3/5 | 25/53 | **[−0.000397,+0.000132]** |
| Previously frozen **Schiermonnikoog 2010→2011** | 0.163169228 | 0.158776139 | **+0.004393089 = +2.6924%** | 12/13 | 49/53 | **[+0.001180,+0.003449]** |

Both sites use same original-hourly first GPS fix, source RWS 10-min water, height/square + spatial/clock baseline, addition of phase + phase×height, train-only standardized ridge λ10 and equal-bird test MSE. Models are **separately trained by island**, not pretrained weights transferred from Schiermonnikoog. Contrasting effect magnitude across only two sites is *descriptive*; cannot estimate a universal island-level variance or causal vegetation/foraging effect.

Other prespecified observed Ameland models: rate-only M0−Mrate **−0.000017949**, phase+rate M0−Mboth **−0.000079084** (negative predictive increments). All whole-week intervals cross zero. Prespecified GPS source clock -15 seconds gives **+0.000021258** phase-only, 3/5 birds and 26/53 weeks positive, with week interval [−0.000342,+0.000145] crossing zero. Thus **no robust Ameland predictive increment** under either interpretation.

## Same-height matched descriptive contrast: weaker/different at Ameland

Within bird, month, 0.15m measured height bin and 6-hour original clock bin, each stratum requires 3 ebb and 3 flood original observations.

| Site, year | Matched bird counts with ebb faster | Matched strata | Equal-bird mean ebb−flood log1p(km/h) |
|---|---|---:|---:|
| Schiermonnikoog 2009 | 7/7 | 787 | +0.06676 |
| Schiermonnikoog 2010 | 21/21 | 4493 | +0.09844 |
| Schiermonnikoog 2011 | 11/11 | 2994 | +0.11408 |
| **Ameland 2010** | **8/13** | 1960 | **+0.00453** |
| **Ameland 2011** | **2/5** | 1958 | **+0.00555** |

The different site contrast is compatible with **environment-dependent tidal movement organization**, but a specific explanation based on mudflat proximity, habitat, breeding-versus-wintering behavior or device clock is not demonstrated. This study tracks Ameland birds that breed on polder meadows while Schiermonnikoog birds were tagged on saltmarshes; this ecological contrast is source-described context, not proof of a selection mechanism.

## Interpretation and next required evidence

- Do **not** overwrite Schiermonnikoog positive v32/v33: new original independent site results are conditional and may differ because animals use different landscapes or GPS capture contexts.
- In Ameland the test population is 5 birds; the near-zero mean, mixed signs and week CI overlapping zero justify **not established**, not statistical proof of zero effect.
- Local tidal propagation between gauge station and each GPS fix, activity state (resting/foraging/commuting), and source clock remain uncertain. Without georeferenced habitat and prey/mudflat DEM, the **moving resource-front mechanism** remains a *hypothesis*.
- Social Boids M3 has not been estimated; coincidence/nearby tracking alone is not motor-force identification.
- The **next mechanism-discriminating test** is externally measured habitat availability/intertidal use across both islands, controlling for tidal height/phase and season. Test before assuming tide coupling depends on which island.

## Reproducibility

- [Original v34 source-backed CI 41411371339](https://github.com/zuizui0223/boids/actions/runs/41411371339), all tests PASS, original Ameland GPS MD5 verified, RWS NAP original values verified and fixed model reported.
- Code: `validation_v34/ameland_external_site.py`, pure tests `validation_v34/test_ameland_external_site.py`.
- Frozen before opening Ameland outcomes: [V34_FROZEN_AMELAND_EXTERNAL_SITE.md](V34_FROZEN_AMELAND_EXTERNAL_SITE.md).
