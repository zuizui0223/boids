# v34: ebb-versus-flood movement asymmetry at comparable tide height

**Exploratory follow-up, 2026-10-31 JST.** Already known: v33-D recorded negative high-minus-low astronomical tide effects on wild GPS step speed in 36 birds, and v33-E showed similar directions in the original 5–30/30–90-minute observation classes; v33-C did not show incremental next-day daily-spread prediction. This distinct analysis is not a new independent population, preregistered multi-source confirmation or causal tide manipulation. This document and all analysis code are committed **before opening the new ebb/flood-conditioned joint speed scores**.

## Ecological prediction

At the *same approximate water height*, the intertidal exposure front is **moving seaward during ebb (falling)** but landward during flood (rising). Daan & Koene (1981, doi:10.1016/0077-7579(81)90002-8) reported that foraging-flight schedules respond to when mussel banks become exposed; contemporary studies describe low-water foraging and high-water roosting, though behavior differs across settings. Hence a state transition tied to shoreline accessibility could yield hysteresis: the current water height alone might be insufficient.

**Single fixed primary estimand:** mean **ebb-minus-flood** original GPS step displacement speed on a log1p(km/h) scale **within matched (bird × original UTC year-month × UTC clock hour × 0.5-m astronomical height band × original GPS-step duration band)**. A positive value would be consistent with higher observed displacement speed while water is falling; a negative value may reflect movement to roost as water rises. Report an exact **one-sided sign probability for positive ebb-minus-flood** together with the **two-sided 95% whole-bird bootstrap CI** regardless of direction. Do not change the orientation after seeing outcomes.

## Frozen sources and reproducibility gates

Use precisely the source-verified v33-D data and preprocessing: original Zenodo 10053970 version v4 Schiermonnikoog oystercatcher GPS, **all seven 2008–2014 CSV.gz files** with the previously pinned original MD5 and SHA256; accept visible original GPS fixes, exclude original manually marked outliers, exclude *all* duplicate bird×UTC records. All step pairs are consecutive observed fixes from the same bird with elapsed original UTC **5–180 minutes inclusive**, both endpoints at most 25 km from the official gauge, with haversine displacement/elapsed-hours → log1p(km/h). **No GPS interpolation, smoothed altitude, tag- or outcome-based cohort search**.

Environmental series: exactly Rijkswaterstaat official gauge `schiermonnikoog.waddenzee`, verified WATHTE **astronomisch**, cm above NAP, **2008–2014 at 10-minute support**, original returned fixed Dutch offset +01:00 converted to UTC. All seven annual series must still pass v33's source gate. For each GPS-pair midpoint t, select the closest 10-minute original tide observation (≤5 min, exact tie earlier). Require original astronomical heights also at **t−30min and t+30min**. Classify `ebb` if H(t+30)<H(t−30), `flood` if H(t+30)>H(t−30), and exclude equal extrema (no post-outcome derivative threshold). This uses an astronomical time series and is a retrospective **association**, not a next-day predictor.

**Height control:** 0.5-m intervals relative to NAP, bin code `floor(H(t)/0.5)`, with boundaries fixed before observing results; no learned thresholds, phase-based selection or calendar-shift tuning. Duration bins: short [5,30), medium [30,90), long [90,180] min, exactly the v33-E boundaries. Within each original bird × year × month × UTC clock hour × 0.5-m water-height bin × duration bin, require at least **2 valid original GPS steps in each ebb and flood category**. Compute unweighted mean log1p speed within ebb and flood, subtract to form one paired stratum; then equally weight paired strata within each bird and equally weight original birds. No GPS fixes or stratum pseudo-replications in variance.

**Admission gate:** a whole bird needs at least **8 paired strata**. Primary effect/CI can be released only if **≥20 whole birds and ≥200 paired strata**. Otherwise `NOT_ADMITTED` with only QC/support, no score, no more permissive year/duration/height strata. Do not replace unadmitted birds. Track total matched pairs by phase, empty height cells, temporal pairs discarded, within-stratum differences in observation interval (minutes) and mean actual tide height (meters) to expose residual confounding within height bands. Report per-duration and per-height-bin signed gains as **descriptive only** on the fixed admitted cohort, even when opposite or zero.

**Inference:** 10,000 paired whole-bird bootstrap resamples, RNG seed `20261031`. The 36 original birds experience one local coastal study and shared weather/landscape/measurement processes; their bootstrap is not 36 independent sites. Source tides from astronomical harmonics do not include storm surge, sediment microtopography or local foraging-site waterlines. GPS-derived displacement is not tagged feeding, direct ecological resource use, learned memory, high-water roost identity or interspecific/Boids force.

## Mandatory original D replay before any new result

Before releasing ebb/flood scores, recompute original v33-D using identical source and require **all anonymous per-bird mean effects, 36-bird sample, 5,422 strata, 10k bootstrap values, source QA and overall mean** to match the frozen `validation_v33/results/oystercatcher_tide_speed_v33.json` to absolute tolerance **1e−12**. The original v33-C day-ahead tide-range negative and v33-D/E high-low positives must remain unchanged. If the receipt changes, STOP before new inference.

## Scientific reading

- **Positive ebb>flood after water-height/time/duty matching:** supports an *observational tidal hysteresis of movement*, consistent with a moving foraging-accessibility boundary. No proof of actual feeding because original GPS contains no prey uptake/behavior classifications.
- **Negative or null:** also useful; high-low water gating can arise without a distinct asymmetry between flood and ebb at the same height, and cannot be replaced by a more favorable post-outcome tide derivative threshold.
- Unchanged high-low water result is not counted as an independent replication of this phase test.
- No eBird, no TinyFish, no changing main, no merge. Separate draft PR stacked on v33.

## Deliverables

Standalone `validation_v34/ebb_flood_height_matched.py`, invented-fixture tests, source-read-only GitHub Actions, anonymous aggregate JSON, complete signed result note and original-digest provenance. Fix only demonstrated code/test errors before real source scores. No raw original bird IDs, animal UTC fixes, GPS coordinates or original 10-minute water-height series committed.
