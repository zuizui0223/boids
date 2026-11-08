# Figure 2 original-output numerical analysis contract — 2026-10-31

**Design recorded after published results were known, but before this branch's first numerical extraction from the source Figure 2 CSVs.** It is a **reanalysis of existing Mazar & Yovel (2020) simulation output**, NOT a new bat observation, original MATLAB rerun, independent validation or randomized biological effect.

## Frozen source inputs / structural eligibility
- Correlation detector publisher file: `elife-55539-fig2-data1-v2.txt`, DOI 10.7554/eLife.55539; SHA256 `e36b0c461fc7aa448ecbd6d2fc8f724c0ac171f7ca972389f04a88cfe9c9c8b2`.
- Filter-bank publisher file: `elife-55539-fig2-data2-v2.txt`; SHA256 `285867a96b3fefd395bb998c1061496aca519cc167b18244f07b0632c50279ad`.
- Both are **240 published simulation-output rows**. Exposure = literal `ReceiverType`: `CorrelationDetector` versus `JAR_CorrelationDetector`, or `FilterBank` versus `JAR_FilterBank`.
- Six specified `NumberOfBats` levels = {2,3,5,7,10,20}; `NumOfPreys=20`, source power 110 and search pulse duration 7 held fixed.
- Only compare within the same `receiver family × NumberOfBats`. Do not make bat-group-level independence claims without original simulated-seed/deployment mapping.

## Fixed outcome families (all displayed; no new selection)
1. Original `NumberOfCatches` per output row = primary descriptive foraging proxy.
2. Original `NumberOfDetections`, and normalized `NumberOfDetections/NumberOfPulses` = proxy for sensor detection; distinct from captures and may contain repeated pulse events.
3. Source `NumberOfInterfernces`, `TotalInterferenceRatio` = acoustic masking proxies; they are not 2026 potential misdetections.
4. `fb_FA_rate` **only** in the filter bank table; no correlation detector false-alarm values are invented.
5. Group-size-specific JAR minus non-JAR row-balanced means and full raw mean on both arms, counts and finite n. Equal-six-group average difference reported descriptively. No significance tests or confidence bands from uncertain simulation-replicate dependencies.

## Mandatory STOP/inferential bounds
- Exact publisher SHA mismatch = STOP.
- Missing required treatment labels, 6 group levels, or fewer than 10 finite published output rows in a cell = STOP per cell; no grid/threshold rescue.
- Check the JAR/non-JAR **ExperimentName** batch support distribution but do not invent seed-pairings. Compare group means unpaired, with no causal attribution beyond the source's original simulation design.
- Do not compare 2020 group sizes {2,3,5,7,10,20} numerically as if identical to 2026 {4,8,16,32}. Their detectors, prey density, potential misdetection definition and independent simulated draws differ.
- No reanalysis of original animal responses here; all values arise from 2020 model output.
- 2020 receiver model full forward simulation is not rerun by this figure-data analysis.
