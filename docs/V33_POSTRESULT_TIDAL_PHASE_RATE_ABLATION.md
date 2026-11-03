# v33 POST-v32 explicitly exploratory tidal phase versus slope ablation

Date 2026-11-02 JST. This protocol is fixed **after** v32 cross-year positive results were opened. All v33 results MUST be reported as post-result explanatory analyses, not preregistered confirmation of the earlier hypothesis.

## Motivation and distinction
v32 external-year M1 contained 20-minute water-level **rate**, discrete ebb/flood **phase** and phase×height. Thus v32's positive predictive increment cannot by itself be uniquely assigned to the ebb-vs-flood indicator. Test whether phase or continuous rate contributes beyond observed gauge height and fixed spatiotemporal controls.

## Immutable field cohorts and comparison
Use the original provider-MD5-verified Zenodo 2009, 2010, 2011 GPS annual files and RWS original measured 10-minute NAP water at `schiermonnikoog.waddenzee` exactly as v32. Hourly-first original GPS fix/ID, 0.5-2h step, response log1p(horizontal km/h), same geographic gate, slack exclusion, tide at start, original GPS timestamp provisionally UTC and -15s sensitivity; NO source/time filtering based on outcomes.

Retain frozen external-year directions: **primary 2010→2011**, secondary 2009→2010. One unchanged per-year frozen training sample, one completely withheld year, same predictors and ridge regularization as v32 (λ=10, train-only standardization, equal source-bird training weights and equal test-bird scoring).

Compare strictly nested fixed variants:
- `M0`: intercept + measured water height and its square, latitude and longitude, diel sin/cos and year sin/cos.
- `Mphase`: M0 + phase (-1/+1) and phase×height, **no rate**.
- `Mrate`: M0 + measured 20-minute trailing water-height rate, **no discrete phase**.
- `Mboth`: M0 + phase + phase×height + trailing rate, identically reproducing v32 M1.

Signed predictive gain = M0 equal-bird MSE − variant equal-bird MSE. Also report incremental `Mrate−Mboth` and `Mphase−Mboth` using the actual mean bird-level MSE and whole-week 95% bootstrap, with 4,000 fixed-seed whole-week resamples. Report all four model scores, positive-bird counts, positive-week counts. If both phase and rate model gains positive, it does not assign causality due to collinearity.

Prespecified technical check: `Mboth` predictions and M0 predictions must agree with v32 original code on the identical training/test rows to numerical floating-point tolerance.

The GPS timestamp is labeled UTC **or GPS time** in the original metadata and source station may lag locally; M2 actual exposed habitat/prey and M3 social neighbor response remain **NOT_ADMITTED**. No raw GPS, individual IDs, coordinates, or water level time series is to be committed.
