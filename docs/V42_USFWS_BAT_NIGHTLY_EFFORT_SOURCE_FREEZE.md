# v42 — Independent USFWS 2010–2018 bat nightly-pass monitoring source gate

**Frozen 2026-11-19 JST BEFORE opening source numeric bat activity, detected species, ecological effects or site-night zero values.** New independent branch, not a modification of the completed v38–v41 Finnish/Italian/Belgian source or nonconfirmatory thermal forecast.

## Official original source and established prior metadata

Original US Fish and Wildlife Service **Great Lakes and Upper Midwest Acoustic Bat Dataset**, public Data.gov catalog [USFWS acoustic monitoring](https://catalog.data.gov/dataset/usfws-great-lakes-and-upper-midwest-acoustic-bat-dataset), archival original **USFWS_Bat_Acoustic_Data.zip**:
\`https://iris.fws.gov/APPS/ServCat/DownloadFile/165800?Reference=112151\` (USFWS ServCat Reference 112151, DownloadFile 165800). Catalog lists **276 survey sites during 2010–2018** across the Great Lakes region/Upper Midwest, multiple bat species and repeated stationary acoustic monitoring.

Original method reports Wildlife Acoustics SM2Bat+ trigger recording to **15-minute WAC files**, with \`Nightly Pass Counts\` restricted to nights with **>=8 WAC files (>=2 nominal hours of detector operation)**; nights with fewer files or known detector failure removed from that summary, though some may remain in \`Pass Lists\`. Original automatic species labels were **not individually manually vetted**. These facts are official source metadata, not findings of this new analysis.

Published USFWS zip is an archived series of XLSX files and a metadata document, not necessarily a ready-to-model uniform detector-night table. Public link does NOT imply source bytes are obtainable from all cloud runners. No numerical per-night counts, recorder uptime or species data have yet been read.

## Why this is promising, and why gate is necessary

The completed v41 Italy/Belgium source gate found valid site keys (Belgium 27/27 plots match environmental metadata) but **no independently verified complete denominator of zero/nonzero acoustic recording windows**. The USFWS source explicitly reports an instrument-operation criterion for its *Nightly Pass Counts*, potentially allowing effort-gated nocturnal activity across a larger spatial and temporal domain.

However, **8 WAC files = at least 2 nominal hours** does *not* mean an entire night was observed, absence of a species is true absence, or all-night monitoring opportunities are comparable. Any future model must use the correct original denominator, actual recording windows, and account for species-classification errors.

## Frozen source-only steps, in order

1. Attempt only the exact official USFWS download URL. Record HTTP result, Content-Type, Content-Length, real received size and computed SHA256 of the **exact obtained original ZIP**. Stop safely if >100 MB or source HTTP 401/403/404/other error, HTML, invalid ZIP or transport error. Never invent a provider MD5 where none was published.
2. Inspect ZIP central-directory metadata only: number of entries, extension counts, member size ranges, file-name **category patterns** (not per-site names). Do not export original detector/site filenames or GPS/roost coordinates.
3. For at most 20 original ZIP members with small safe byte size and format XLSX, inspect nested worksheet sheet-name and *first header row text* only (not numeric species pass counts). Record whether workbook/sheet titles indicate \`Nightly Pass Counts\`, \`Pass Lists\`, \`Metadata\` or \`Recorder Effort\`, without assuming category name guarantees complete effort.
4. If original ZIP is huge, source website requires login, member format is not supported, or full nightly instrument-duration schedule cannot be demonstrated, record structural STOP. No retuning file cap or switching unverified mirrors after seeing source results.
5. Do not open numeric pass count, acoustic calls, named species, latitude/longitude, activity rate or site-night series in v42. Actual independent site-year/survey replicate and the zero/count denominator must be verified in separately predeclared model-source audit.

## Future falsifiable question, conditional on full source success

**Can a time-and-weather conditioned bat activity model trained in some monitoring regions/years predict other independent regions/years better than a period/night-effort baseline?** The 2010–2018 USFWS source can be a separate, independent North American panel, but cannot be pooled quantitatively with 2026 Finnish one-species night-quartile **compositions** unless effort and source response are harmonized with a distinct pre-outcome protocol.

Original Finnish v39 year mean gain +0.017943 nats/night was **not confirmed** under preregistered sign p=.0625; spatial mean gain −0.038835. No change to these results or to original \`batter\`, \`boids\` v30/v37 negative findings.

**Stage v42 output only:** official original-source integrity and schema receipts, NO biological effect or out-of-source predictive claim. This is a meaningful independent new source programme; its start cannot be treated as a new affirmative biological result.
