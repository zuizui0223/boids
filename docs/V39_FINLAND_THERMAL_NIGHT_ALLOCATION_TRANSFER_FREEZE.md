# v39 frozen: out-of-year thermal control of within-night acoustic activity allocation

**Commit before ANY source numerical n/weather/response values opened. Date 2026-11-19 JST.** This is a NEW outcome-blind programme after source-structure v38b four-bin STOP and distinct v38c six-label PASS. Neither historical stop is rewritten.

Original Lilley et al. 2026 Finnish Northern bat acoustic table \`Data.xlsx\` (Zenodo 18298435; provider MD5 \`444c510bcb154bf9272d620f1ce0ec5a\`). Original paper already demonstrates in-sample night-length × temperature effects, so this is a **new held-out transportability check**, not a novel original thermal mechanism.

## Why the original six labels are treated differently
v38c source-only shows each of **4,536 distinct active detector-nights** has exactly six labels: \`BSS,1,2,3,4,ASR\` with nonempty \`n\` and \`prop_activity\`. Independently checked published manuscript defines **BSS before sunset, 1–4 consecutive equal-duration 25%-of-night quartiles, ASR after sunrise**. The primary endpoint uses **only the four darkness quartiles** and excludes BSS/ASR from the denominator because their exposure intervals are not comparable to each 25%-of-night bin. This definition was selected **before** numerical n/prop_activity were opened by this programme.

Each row's source \`n\` measures the number of acoustic activity minutes in that period; the target per detector-night is \`p_k=n_k/(n_1+n_2+n_3+n_4)\`. Require original nonnegative finite \`n\` for all 4 bins and strictly positive 4-bin sum. Rows with missing/invalid \`n\` or weather are reported and not fitted; BSS/ASR are never modeled as nighttime quartiles.

**Independent statistical unit:** \`region×location×device×year×startdate\` detector-night, not the 4 original rows and not separate biological bats. Year is the main held-out grouping, regional groups secondary. The original v38c counted 7 years and 3 regions. Active-night selection (original paper ≥10 minutes all-period activity) means these scores measure **within-active-night composition only**, neither activity probability nor all-night effort.

## Models frozen before outcome
- M0: train-night-equal **period-specific four-quartile mean compositions**, Jeffreys smoothing (0.5 on summed fractional source-night values), using an overall training mean for unseen period. No outcome from target year/region enters.
- M1: M0's period one-hot covariates, plus train-standardized \`mean_temp\`, \`night_length\`, and their product (centered/scaled temperature × centered/scaled night length); fixed multiresponse linear Ridge **alpha=10**, trained on log-ratios \`log((n_k+0.5)/(n_4+0.5))\` for k=1,2,3. Reverse through stable softmax \`[z1,z2,z3,0]\`. Train nights weight equally. Source weather represents the **whole observed night**; this is retrospective context prediction, not a before-night weather forecast.
- M2 secondary only: M1 plus train-standardized \`sum_rain\` and \`mean_wind\`, same Ridge alpha and exact test observations; no choice or tuning after results.
- All features/test rows must be identical for M0, M1, M2. Require finite values for the four weather variables (to prevent differential-support advantages), for original four-bin n, plus nonmissing period and year/region key; no imputation is allowed. Report exclusion counts by cause.

**Primary loss:** out-of-year cross entropy \(-\sum_{k=1}^4 p_{k,\mathrm{observed}}\log p_{k,\mathrm{pred}}\) in nats per active detector-night. Positive M0−M1 means weather improves **activity allocation prediction**. Equal-night mean within each heldout year, then **equal-year mean over eligible years**. Train on all non-test years, using train-only period means and feature scaler; no random source rows split.

**Gates:** >=1000 valid detector nights, >=5 held-out years each with >=30 nights, >=2 regions with >=30 nights; each year must have >=300 training nights. If not, source stop before fitting, with no results. Regional holdout is a predeclared secondary, requiring >=2 eligible regions each with >=30 nights and >=300 training nights. No region/site with only a few nights is promoted post-hoc.

**Uncertainty:** 10,000 whole-year bootstrap resamples of yearly gains (seed 20261119), 95% percentile interval, positive-year count and exact one-sided sign p. Primary positive verdict requires equal-year gain >0, bootstrap lower bound >0 AND sign p<=0.05. A positive average with a nonsignificant sign gate remains NOT SUPPORTED. Region secondary scored similarly but 3 regions cannot independently achieve p<=0.05 with an exact sign test.

**Secondary outcomes (no rescue):** M1−M2 (extra wind/rain improvement) and region-left-out M0−M1. Report all even if negative. Do not scan alternative lag windows, weather thresholds, degree/interaction terms, seasonal subsets, ridge alpha, site-groups or favorable time bins after opening outcomes.

## Scientific boundary

This one-species northern Finnish passive-acoustic design cannot show a universal bat behavior law or independent cross-country transfer. Original ecological thermal/night-length **association** is prior art. Successful v39 out-of-year prediction would establish ecological *transportability within this source*, not memory, optimality, prey capture, social communication or causal microclimate reaction. Original Belgium/Italy datasets cannot be pooled as if they shared effort denominators. All original \`batter\`, \`boids\` v30 negative, v37 morphology negative, v38b FAIL, v38c source PASS remain unchanged.
