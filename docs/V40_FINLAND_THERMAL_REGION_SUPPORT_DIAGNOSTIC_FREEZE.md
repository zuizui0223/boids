# v40 diagnostic-only: climate exposure overlap for the three heldout Finnish regions

**Explicitly post-outcome exploratory diagnostic, frozen 2026-11-19 JST after v39 scores were opened.** Do not promote to new independent confirmation or rescue a failed primary. V39 primary: out-of-year mean +0.017943 nats/night but exact sign p=0.0625, positive gate FAIL; out-of-region −0.038835 nats/night, 1/3 positive.

## Question
Before invoking behavioral specialization, is the failed extrapolation to two Finnish regions accompanied by **measured out-of-training climate covariate support**? Or were temperature/night-length combinations within training support, leaving habitat, insects, recording or other factors plausible?

## No new prediction
Use exact provider-MD5 source 18298435/Data.xlsx and the **same 4,208 original valid Q1–Q4 detector nights** selected in frozen v39. Read already-opened environmental predictors \`mean_temp,night_length,sum_rain,mean_wind\` and structural fields \`region,year,period\`; do not recompute any bat activity forecasts, gains, thresholds or subset scores.

For each complete heldout region: use all *other-region nights* as train. For each of the four predictors record training 5th–95th percentile envelope, median in train/heldout, fraction of test nights outside that frozen training envelope. As a two-dimensional joint thermal/solar support diagnostic, record fraction of test nights outside **either** training temperature or night-length 5th–95th percentile envelopes. These 5–95% quantiles are a **descriptive** convention, not a physiological threshold. Record count of unseen \`period\` category labels in the test region and year support overlap.

Group indices must follow original v39 sorted region labels, relabelled only region_group_1..3. Output no original latitude/longitude/site/recording data, nor original per-night predictor values.

This diagnostic does not establish the cause of v39 region prediction failures. Additional observational predictors (prey, canopy, detector processing) and a new independent region must be tested prospectively before ecological mechanism or all-bat generality claims.
