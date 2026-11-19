# Carollia v30: one frozen bat-label-held-out sonar-to-next-call turn forecast

**Freeze date:** 2026-11-19 JST. **No source numerical future-heading targets opened when this protocol was written.**  
**Evidence:** exploratory reanalysis of already-published 2026 Carollia data, **not a new independent confirmation** of published acoustic gaze anticipation. Preceded by the v29 source-only integrity, HDF5 metadata and pipeline-leakage audits.

## Scientific question and contrast

Does **absolute microphone-fitted acoustic beam azimuth measured at a call** predict the next raw call-to-call heading change *beyond strictly earlier call-position kinematics*, when every biological bat label is withheld? This is a restricted prospective-prediction benchmark, **not** a universal sensory-margin law.

The full physical sensing-margin q=v*IPI/(d_free*p_usable) is **structurally NOT ADMITTED** here; independent distance-to-obstacle and echo reliability are absent. We must not silently relabel the v30 proxy as q.

## Immutable original source
- Original public repository: 00keveland/Tunnel_2026, exact commit 59928a71887d521fec143080b0b187736c046a0e, all 30 trial blobs verified at v29.
- Eight original source labels C1–C8, with 30 trials and only **two sampling dates**; trial points must NOT be considered independent animal replicates.
- Original HDF5 datasets: RESULTS/calls/tSec (K time stamps); RESULTS/calls/XYZ_raw (3 x K raw-call-localized coordinates); RESULTS/beam/az_rad (K original global acoustic directions); RESULTS/beam/fitR (K fit diagnostics).
- NEVER use RESULTS/beam/rel_deg, derived from heading_from_track on smoothed and interpolated track with symmetric future-point differencing. NEVER use RESULTS/track/pos_sm as independent observed trajectory or authors' turn labels.
- Source metadata and source HDF5 fields are assessed as documented before outcome scoring; no source animal data are redistributed.

## Fixed pre-event design

For every trial with calls indexed in time, predict from call k (zero-based) with **k>=4, k+1<K**:
- Previous displacements: u0=XY[k-2]-XY[k-3]; u1=XY[k-1]-XY[k-2]; u2=XY[k]-XY[k-1]. Thus prior heading and its prior change are made *strictly before* the target next displacement.
- Timing predictors: dt0=t[k-1]-t[k-2], dt1=t[k]-t[k-1]. (Older dt is used only for validity of u0 if necessary.)
- Prior heading theta_pre=atan2(u2_y,u2_x). Prior heading change dtheta_pre=wrap(theta_pre-atan2(u1_y,u1_x)).
- Source absolute beam b_k=RESULTS/beam/az_rad[k], with fitR[k]>=0.30. Use sin(b_k),cos(b_k) as additional predictors; never construct a relative beam using a smoothed or future point.
- Primary outcome: dtheta_next=wrap(atan2((XY[k+1]-XY[k])_y,(XY[k+1]-XY[k])_x)-theta_pre), measured using the **next original call-coordinate** only.

Fixed validity rule: finite required numbers; all temporal increments strictly >0; previous and next XY displacements length >=0.05 m; previous speed >=0.1 and <=30 m/s; fitR[k]>=0.30; any source anomaly is reported as an exclusion, no threshold adaptation. No future outcome enters predictors, imputation, scaling or model choice.

## One model family, one primary contrast

**M0** train-only standardized ridge regression alpha=1.0 on [XY[k], previous speed, dt1, sin(theta_pre), cos(theta_pre), dtheta_pre].  
**M1** M0 plus [sin(b_k),cos(b_k)].  
Both fit in scikit-learn Ridge with fixed parameters and training-only StandardScaler. Predicted signed angular change is scored by the squared **wrapped** angle error in radians squared on exactly the same withheld rows. The target is bounded [-pi,pi], not fitted as a species-specific circular model.

**Primary score:** equal-bat-label mean MSE(M0)-MSE(M1) from leave-one-C-label-out forecasts across the 8 original labels. Bat-label bootstrap: 10,000 deterministic resamples, seed 20261119; two-sided percentile 95% interval. An exact one-sided binomial sign p across 8 labels is also reported. Predeclared directional success requires positive mean gain, bootstrap lower limit >0, and one-sided exact sign p<=0.05. A failure stays a failure; no post-hoc subset/tuning rescue.

**Structural STOP before fitting:** >=6 original labels with >=20 valid candidates each, >=300 candidates pooled; if not met, no predictor fit, record eligibility stop. Target validity may remove rows; do not change gate after viewing results.

**Fixed secondary diagnostics:** (a) matched-set model using azimuth 3 calls earlier (k-3), keeping exactly the same target rows; (b) train on all labels from day 1 and test all day 2 labels, and converse, with no refit after results. These are **not** primary confirmations and have only two independent dates.

## Scientific boundaries

Even a positive M1-M0 would be *a held-out predictive contrast in one processed Carollia archive*. It would not identify auditory causality because both beam and call XY derive from microphone arrays, the published paper already describes acoustic look-ahead, and physical obstruction/echo rate are not independently calibrated. A negative gain does not falsify active sensing. Any cross-species or broad ecological law requires independent sources with matching inputs and source/site/species holdouts.

Do not change frozen earlier boids v6/v8/v15/v16/v28 or batter analyses. Do not merge this exploratory finding into a causal manuscript claim until independently replicated.
