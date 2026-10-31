# v44 — Balanced NEAR versus FAR previous-heading forecast on identical original GPS episodes

**2026-10-31 JST, expressly AFTER viewing v43 outcomes.** Known previous result: original Schiermonnikoog 20 wild birds/171,013 heldout NEAR≤200m future 2D GPS episodes; near-heading MSE gain +0.000082414, bird-bootstrap 95% interval crossed 0, far-heading gain +0.000184189. FAR direction was measured for only 68,232 of those original NEAR episodes. The v43 *descriptive* near−far gain (−0.000101775) was therefore confounded by different environmental/bird/month **availability opportunities**. This v44 is a **post-outcome diagnostic**, NOT an independent test of social forces, even if a new model ranking emerges.

## Single fixed ecological question

**On exactly the SAME future original GPS step episodes, where NEAR≤200m and FAR≥1km other-bird PAST headings are BOTH available**, is the conditional additional directional information from local bird past movement stronger than the regional far-bird past direction? This removes *gross differential heading availability* only; it does NOT match near/far habitat, distances, source bird composition, measurement duration or unmeasured shared wind/patch conditions.

## Source, metric and immutable replay (must pass BEFORE calculating v44 effects)

Use precisely original Zenodo 10053970 v4 O_SCHIERMONNIKOOG seven GPS-year original MD5 and SHA-gated files and seven full RWS original astronomical WATHTE 10-minute year files in NAP/UTC, same already-observed v43 study. NO newly substituted source, no raw animal locations/IDs/UTC published.

1. Run `validation_v43/near_heading.py` source gate from its frozen source: v41 exact ID×UTC original full receipt (39 birds/602,380 fixes), v42 source real-space exact 21 focal birds / 171,041 NEAR prior-other eligible starts 2010–12, v33-D, v39 and v40 original per-bird/time/method numerical receipt match at abs 1e−12, and original 328,323 source four-fix source candidate steps.
2. Recompute **the ENTIRE original v43 four-model 2D vector AND angular outcome**, including all bird-balanced absolute MSE, signed contrasts, 2010–2012 year/month breakdown, source QA, and per-bird numbers. Compare to the saved `validation_v43/results/original_near_bird_heading_forecast_v43.json` with recursive numeric abs tolerance 1e−12. STOP if any drift.
3. The source's original v43 model predictions are produced in a strict **UTC-month prequential 7-day embargo** ridge (α=25) with all source training episodes, including missing-neighbor zero-coded availability, held out next month. **Do not refit/tune/change ANY model coefficients or features after the previously observed v43 effect**, and do not normalize using future test data. v44 ONLY re-estimates the loss on the below FIXED equal-cohort source subset using exactly these four preserved forecasts. Prediction target and transformation exactly as v40/v43, sum squared errors of asinh-east and asinh-north km/h; no future GPS time interval as a predictor. No source GPS pair shared between own prior and next target.
4. Select test episodes ONLY if (i) original v43 all-model errors finite (already forward-held-out), (ii) a real original near-other bird preceding GPS pair is available `near_mask=True`, and (iii) a real original far-other bird preceding GPS pair is available `far_mask=True`. Both other-bird latest 5–30min past GPS pairs must have ended in [t−5min,t], never after t. Both near and far same original focal bird/episode/calendar time, so availability is identically TRUE for all S0,S1,S2,S3.
5. All original available source matched birds with ≥**30** future true four-fix step episodes remain, without selecting positive effects. **Gate to release any new score:** ≥**15** original focus birds, ≥**25,000** future matched episodes, ≥**8** source UTC calendar months and ≥**2** original source years (all thresholds fixed before opening new matched-cohort v44 model scores); otherwise `NOT_ADMITTED_BALANCED_NEAR_FAR`, aggregate support only, NO model MSE, no cutoff rescue. This lower than v43 20 birds source gate reflects smaller fixed BOTH-available cohort and is NOT evidence from independent birds.

## Fixed SAME TARGET comparisons and uncertainty

Original models from v43:
- S0: original v40 V1 with prior self speed+heading, current astronomical tide H/dH with nonlinearity, clock/season, GPS source known position and bird, observational cadence, **known near+far other-bird presence/count/distance/age/speed and near-closest bearing** (not other heading).
- S1 = S0 + near≤200m other-bird mean PAST heading (east,north unit).
- S2 = S0 + far≥1km other-bird mean PAST heading (east,north unit).
- S3 = S0 + both previous near and far other headings.

**Registered PRIMARY signed comparison:** `[MSE(S0)−MSE(S1)] − [MSE(S0)−MSE(S2)] = MSE(S2)−MSE(S1)` on the exact same episode per bird. Positive favors NEAR over FAR; zero/no robust mean fails to establish local specificity; negative favors FAR. This tests relative predictive information, **not causal social alignment**. There is no pre-result choice to switch the sign.

**SECONDARY** in stated order: S0−S1 (NEAR gain), S0−S2 (FAR gain), S2−S3 (NEAR after FAR), S1−S3 (FAR after NEAR). Report all four source-same-cohort absolute model MSE and all signed contrasts even unfavorable. For each original bird, average ALL its matched heldout original episode errors first; then mean the bird means equally, 10,000 **paired whole-bird** bootstrap RNG seed 20261031, exact positive one-sided bird sign; 95% percentile two-sided intervals. Report source-bird positive/negative, near/far source availability opportunity fraction and the difference of model MSE **within original year and calendar month**, no year/month cherry-picking. Equal-month 10k bootstrap is descriptive (months share same birds and original environmental conditions).

**Preset directional-only secondary:** original next recorded GPS displacement ≥0.05km; compare `1−cos` direction loss using v43's fixed neutral loss=1 for predicted vector speed <0.05km/h, same future target angular episodes for all S models. Admit only if ≥15 whole source bird IDs each with ≥20 original moving target episodes and ≥8,000 moving episodes total, else angular STOP with no angle effects. This subset does NOT redefine primary whole-vector MSE target (all matched future episodes).

## Critical limits and falsifiability

- Already-known v43 unbalanced outcome is not independent of v44 matched-cohort analysis. Even if near wins, observed closeness is not randomized: location selection, stage of tide, local route, wind, food, and social grouping can create a near-specific correlation without causal Reynolds interaction.
- If FAR wins or no robust localization, do NOT rescue by changing 200m to 100m/500m/1km, changing time interval from 5min, rescaling ridge, selecting only positive years, or maximizing model complexity after outcome.
- Same 2008–2014 source (with heldout support mainly 2010 and 2011), only ONE coastal study. We do not infer 3D altitude, food niche, true social ties or Reynolds alignment/cohesion/separation coefficient.
- All previous PRs draft and unchanged; create a new v44 draft PR stacked on original v43, never merge without authorization. No eBird/TinyFish. Publish aggregate numeric JSON, all group signs, test and GitHub Actions provenance; no raw GPS ID, coordinates, original times, RWS original series or per-episode bird movement.

**Interpretation:** this directly checks whether v43's near-vs-far ranking can be explained by differential sample support. It does not adjudicate causality or identify field social steering.
