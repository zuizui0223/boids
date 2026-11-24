# v26d frozen prospective exploratory third-taxon fish movement prediction

**2026-11-24 JST; frozen before any source numerical movement outcomes.** The same three EIDC source originals 01.txt, 02.txt and 105.txt were chosen and SHA-authenticated for v26/v26b/v26c *schema only*. This is an **exploratory third-species recording-heldout** test, NOT independent shoal-heldout and NOT a formal cross-taxonomic meta-analysis.

Source MacGregor & Ioannou (2021) *Gasterosteus aculeatus*, EIDC DOI 10.5285/08305a43-79b5-432f-ad20-2ddffe0d1077, original 25fps, 8 fish. Exactly pinned original SHA256/byte sizes:
- 01.txt 9422363 bytes 657872348cdf31b90e01c9f087df64937cb435f14d92eb1b1b9c3bc59a4b314a
- 02.txt 8144030 bytes 552f766d2a72926d041df8316caf8a0e2454aee64746ca837ad60e83973d10ed
- 105.txt 8734098 bytes 541617d6458a07c22bedeca43636c76e59e4dc30cfb12eedfa038d168cec0336

Source header exact order: x.1,x.9,x.2,x.10,x.3,x.11,x.4,x.12,x.5,x.13,x.6,x.14,x.7,x.15,x.8,x.16,frame. These encode alternating XY for fish IDs 1–8, with a final native integer frame counter. The frame must increment by exactly +1 in each of these original source files; a source mismatch is scientific STOP. Native missing coordinates are literal NA. Never invent or interpolate missing XY or use unknown source school IDs.

## Frozen chronological task, identical rows for all models

- Source 25 Hz. Every fifth original frame beginning t=55, stop no later than T-21 (exclusive). Source predictor time points are **t−55, t−50, t−30, t−25, t−15, t−10, t−5, t** (corresponding to all age-0, 0.2, 0.4, 1, 2 second other-fish velocity supports and focal own 0.2/0.4s history). The common exact original fish×frame evaluation cohort is the set where **all eight fish at every source predictor time** and in **t+5, t+15, t+20** target frames have finite unaltered XY. Do not rescue near gaps by source interpolation. Require ≥200 complete source frames per file after filtering.
- Own/geometry G fixed for every age: focal current XY, focal current 0.2s velocity (t−5→t), earlier 0.2s velocity (t−10→t−5), finite difference acceleration proxy, focal speed, school-centroid XY displacement, topological three-nearest neighbor mean displacement and mean distance measured at **t**. Geometry-only panel G never contains neighbor speed.
- Five aged social vectors `R_i(t;ell) = mean_{j != i} v_j(t-ell) - v_i(t)` for age ell = **0, 0.2, 0.4, 1, 2 seconds** (= 0,5,10,25,50 native frames); each v_j(t-ell) uses 5 native source frame difference [t-ell-5, t-ell]. **Focal term is always CURRENT v_i(t)** even in old-age arms. Same XY geometry, same focal motion, same prospective Y and source frames in every model.
- Responses: 2D future mean focal velocity for 0→0.2 seconds ([t,t+5]) and delayed 0.6→0.8s ([t+15,t+20]), in original **pixels per second**. Never compare absolute MSE units to 2024 Puy centimeter/s or Niizato unknown coordinate/s.
- Training-only StandardScaler plus sklearn Ridge(alpha=10), fixed no retune, leave exactly one of **three original recording files** out for the heldout test. Cannot claim independent biological shoals because original file IDs are not mapped to school/day/trial.
- Primary source-specific signed comparison: mean over 3 heldout FILES of MSE(age=0.2)−MSE(age=0), separately short and delayed, signs per file; report negative/zero unchanged. Secondary age=0.4,1,2 and normalized predictive retention I(ell)=[MSE(G)-MSE(age ell)]/[MSE(G)-MSE(age0)] iff denominator>0; otherwise not defined. No test/adaptive age threshold after seeing outcomes, no hypothesis that every species has exact 0.2s biological half-life. With 3 files, do not use a nominal population p-value or extrapolate population-level confidence.
- Source curation and missing-value counts from v26c [source](V26_EIDC_STICKLEBACK_ORIGINAL_SOURCE_RESULT.md) frozen independently of this v26d effect. Do not select files by level of forecast performance or remove negative recordings.
- No original fish coordinates, prey events, call sounds, or source animal time-series to repository. Save only per-recording MSE, source SHA, model definition, source eligibility counts and result/STOP receipt.

## Falsification and claim hierarchy

If age0 is not best, or age0.2 is not worse in some files, report adverse signs without changing outcome, feature set or cohort. The expected v24 cross-species decaying pattern may fail in sticklebacks due to different foraging context, age, sensing, or source processing. Since school identity is unknown, **a positive three-recording source result would be third taxon exploratory only; the registered cross-source claim remains two strong fish studies plus exploratory third**. Social causality and fish vocal-chorus feedback are not measured. PR #248 Draft, main unchanged.

This protocol was authored before the first v26d original movement forecast.
