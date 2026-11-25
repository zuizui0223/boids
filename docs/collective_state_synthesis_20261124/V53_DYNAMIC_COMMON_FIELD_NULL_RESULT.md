# v53 dynamic common-environment null — exact calculation, source candidates

2026-11-25 JST. Frozen protocol commit 2590e68a5500e36bcb50bdf1045dd0bc96589b87. No empirical v53 prediction outcome admitted. Prior v52 empirical four-study result and all failed prior gates remain unchanged.

## Actual executed synthetic population calculation

See validation_fish_school_v53/dynamic_common_driver.py. Executed locally with NumPy on the 81 predeclared parameter combinations. Script Git blob b66584b54328ad544b2d34d43103d402b6fb9065 matches executed file, SHA256 dd470e01d4552652942ef3be2e7dce100dc376fafb4efa2f4b948b21f75da6d5. Result JSON SHA256 84bfc54c7326903f8bfe69a4a737b6681f6bfee90364d7a0fb9fbe089b0b2bc6. No empirical parameters, raw fish tracks, or estimated social interactions are used. CI reproduction [45583894086](https://github.com/zuizui0223/boids/actions/runs/45583894086).

Eight fixed sampling sites in two four-member patches, observed scalar velocity V_i=A+Z_patch+E_i. A, both Z, and all E_i are independent stationary Gaussian AR(1) processes. There is no interindividual edge. Nearest three other sites share the focal patch; global mean uses all seven other sites. Conditional local share is 100*(MSE_BG−MSE_BGN)/(MSE_B−MSE_BGN). Here B uses focal velocity at t and t−1 only (static geometry is constant); exact population least squares, not the empirical finite-sample 14D Ridge. Time step .2s, target t+1 vs t+4. All 81 cases admitted (positive joint gains). This is an algebraic counterexample, not an integrated position/velocity fish simulation or estimate of a fish sensory range.

| Persistence regime | Cases | Decrease | Increase | Practically unchanged | Mean change pp | Min/max pp |
|---|---:|---:|---:|---:|---:|---|
| global longer-lived | 27 | 27 | 0 | 0 | -10.2699548665 | -40.88999847 / -.49159013 |
| equal | 27 | 0 | 0 | 27 | -1.06149e-11 | -1.10604e-9 / 9.02844e-10 |
| local longer-lived | 27 | 7 | 20 | 0 | +7.5002015322 | -9.48169566 / 46.11155106 |

The frozen code counts signs with tolerance 1e-10 pp; for equal persistence it reports 5 negative, 3 positive, 19 unchanged, all within 1.11e-9 pp. The table above explicitly interprets differences below 1e-8 pp as floating-point numerical error, not biological differences; no change to stored raw results. The reverse regime need not reverse for every variance combination.

Central prespecified example rho_global=.9, rho_patch=.3, rho_individual=.2, each variance 1. Short B=2.3116477273, BG=2.2015794133, BGN=2.1996853244, local gain=.0018940888, total=.1119624029, share=1.6917186323%. Delayed B=2.8182204155, BG=2.7207566971, BGN=2.7207566399, local gain=5.72262e-8, total=.0974637755, share=.00005871534%. Delta=-1.6916599170 pp. When true present A and focal Z are included in the oracle base, own current velocity identifies current E; future innovations are independent of neighbors. Maximum absolute additional oracle improvement across 162 horizon/case combinations: 4.44089e-16. The synthetic exact check shows common-field timescale differences suffice for a direction of change resembling the observed hierarchy. It does NOT imply that real fish have no interactions or that environment caused the empirical result.

## New-source independent-study admissions (no forecast scores yet)

- Lecheval et al. (2018) article DOI 10.1098/rspb.2018.0251, archive DOI 10.5061/dryad.9m6d2: original 50 Hz ring-tank recordings, frozen 8.zip (179.56 MB listed), metadata.txt, README.txt. Random draw from 70 fish, reuse across days possible, no group-level independence claim until author metadata reviewed.
- Watts et al. (2017) article DOI 10.1098/rsos.160804, archive DOI 10.5061/dryad.j0226: six randomly assigned 10-fish shoals, 32Hz 3D records, human walk-by stimulus at 20s, reconstructed frame 600–1600. The 1.44 MB original archive is a separate source with a distinct temporal grid and intervention context. Not exact .2s replication. Dataset source schema must be verified before new prediction models.
- Local runtime cannot reach the Dryad API (DNS resolution failure); GitHub Actions source-only gate initiated. Exact provider version, file links, byte/digest and structural metadata must pass; no new real-fish results yet. Do not conflate new independent published studies with independently identified biological shoals.

The next empirical contrast should condition on genuinely measured or fixed exogenous geometry/stimulus features without learning from future targets, and compare matched predictions against a source-appropriate common-driver null. Geometry-only adjustment is not sufficient to rule out arbitrary latent fields. The fixed-site Gaussian counterexample is deliberately a minimal identifiability argument, not the empirical null distribution. Draft PR #255, main unchanged.
