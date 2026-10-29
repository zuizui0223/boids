# v28 source-first: independent Doñana ungulates GPS use/availability vs camera-trap detection

**Registered 2026-10-29 JST before opening original animal habitat outcomes or camera-detection values.** All v13–v27 results remain frozen; v25's invalid perfect profile separation remains invalid, v25-F private-history not supported, v26 turtle label missing, v27 tit Dryad blocked.

## Independent source and biological question

Ferrer-Ferrando et al. (2023), *The method matters. A comparative study of biologging and camera traps as data sources with which to describe wildlife habitat selection*, *Science of the Total Environment*, [DOI 10.1016/j.scitotenv.2023.166053](https://doi.org/10.1016/j.scitotenv.2023.166053). Author original source [Zenodo DOI 10.5281/zenodo.7766936](https://doi.org/10.5281/zenodo.7766936). The publication compares biologging/GPS resource selection functions against imperfect-detection models from camera traps in Doñana National Park, southern Spain. The study reports **17 GPS-tracked ungulates (7 red deer, 6 fallow deer, 4 wild boars)** and **60 camera sampling sites**; these published counts are prior authors' reported source design, not yet independently verified by this project's original CSVs.

Original Zenodo page describes under ~16 MB total:
- `RSFapproach_data.csv` ~2.2MB: GPS/available use-selection analysis source input;
- `IDMapproach_data.csv` ~38.5KB: camera trapping, detection observation source;
- `RSFapproach_code.R`, `IDMapproach_code.R`, `PredictionAgreement_code.R`: published source computation;
- `DNP_covariates.*` spatial polygon/covariate layers (~13MB total).

**Do not equate camera detections with true absence or GPS used locations with selected biological resource intake.** Models observe different processes; one condition may appear more informative because of detection/sampling/availability biases.

## Stage A exact original source authenticity (no animal rows)

1. Request original Zenodo API record `7766936`, verify exact DOI/record ID, source license, file names, byte lengths, publisher MD5 and official content URI. Do not invent URLs. Cap 50MB per original file and 100MB aggregate.
2. Original file source-only download candidates: the two exact source `.csv` and original RSF/IDM R scripts (plus code for source variable definitions). Download exact published bytes and original MD5, compute SHA256, **do not read original numeric habitat effects/animal GPS fixes/camera detections**. If only some accessible, clearly report which were verified; no partial dataset ecological inference.
3. Inspect source column headers, original individual/animal ID fields, timestamp/month, used/available source case labels, availability sampling ID, camera station/trap effort and observed detection counts only in a **separate A2 source-grain audit before any outcome modelling**. Source label schema must be derived from original code/metadata, never from the sign of observed habitat effects.
4. To support a properly heldout **individual history and environment** test: ≥8 source-identified individuals with ≥3 ordered original observation dates and ≥100 matched true used/available sets with independent availability drawn from prior/decision-time information. If only static RSF used/available and camera detections exist, restrict to static GPS-vs-camera source-model comparison; do not call it private memory or exact animal choice.
5. Species-level independence: published GPS sample is 7+6+4 original marked animals in ONE shared park, not three independent ecosystems; a single species may have fewer than 8 IDs. Camera 60 stations are monitoring units, not 60 individual ungulates and not confirmed true absences.
6. Camera detection and biologging selection are distinct observation processes; a common habitat preference should be tested with matched environmental/spatial supports and explicit trap effort/availability before claiming contradictory ecology.
7. All predictive models need a separate outcome-blind contract after source A2, animal-heldout and station/year holds, no data leakage from camera response to covariate availability, full positive/negative results. No original camera or GPS locations redistributed.

The project should pursue biological questions rather than merely count sources: *Does habitat choice inferred from individually followed animals survive comparison with detection-corrected camera observations when both share environmental context?* But a recorded source file's presence is not evidence it supports this test.
