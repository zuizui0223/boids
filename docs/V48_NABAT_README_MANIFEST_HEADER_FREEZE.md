# v48 — NABat 2026 official README and recording-manifest header-only feasibility

**Freeze: 2026-11-19 JST, before fetching any original NABat README or manifest bytes.** Extends v47 public original *item-metadata* PASS without opening any biological data.

## Pinned provider and source inventory

USGS 2026 NABat acoustic release DOI \`10.5066/P1HDZNY9\`, ScienceBase public item \`6ace802b1ba49b69a5819e47\`, original URL \`https://www.sciencebase.gov/catalog/item/6ace802b1ba49b69a5819e47?format=json\`. Original v47 verified provider item JSON HTTP 200, 8 file metadata entries: **3 CSV, 3 Parquet, one README.md, one XML**; 4 original files <1MB and 4 >=100MB. USGS release description mentions a versioned \`nabat-acoustic-data-manifest-YYYYMMDD.csv\` but does not guarantee the manifest contains complete survey-event effort / no-detection windows.

## Fixed pre-outcome bounded source plan

1. Retrieve the exact same ScienceBase item JSON (1MB cap, original item ID check); only the actual provider \`files[]\` objects may authorize a download. No guessed file URL, no nonofficial mirror or implicit partner account.
2. Select **at most one** source \`README.md\` original file and all CSV file entries whose filename contains \`manifest\`, up to 2. If a file is absent/ambiguous, record structural STOP. No Parquet full download or large audio file request.
3. For the README, accept exact provider-issued HTTPS file URL with ScienceBase/USGS hostname and original declared size <=1MB. Read at most 1MB+1; record source SHA256/byte length; extract **only README line count and method-keyword categories** for \`effort, detector, survey, site, start, end, recording, acoustic, label, taxonomy, metadata, overlap, privacy, quality, validation\`. The original README narrative or named stations are not reprinted.
4. For each selected source CSV manifest, make **only a bounded Range request bytes=0-16383**. Accept **only** HTTP 206 with Content-Range that starts at zero, a fixed total, and at least 16,384 bytes. If the server ignores Range and returns 200, read at most 16,385 bytes then stop (no full 100MB original manifest). For a manifest smaller than 16KB, only if the original provider metadata size is trustworthy and <=16KB, request exactly that size. Inspect **only first line column headers**; do not decode or export any recording, species, timestamp, detector, site, row or GPS value.
5. Cap each manifest response to requested first-row header prefix, retain source original header SHA256 of just the returned header sample (NOT entire source CSV checksum). The original per-file hash remains unverified unless provider supplies a published hash; do not fabricate whole-file integrity or claim species counts.
6. Record only sanitized original **header column names and semantic categories** (survey start/end, detector, recording time, source project, species label, manual verification, site ID, coordinates, status). No source file names, URLs, GPS site locations, individual bat labels, or raw audio are exported in the receipt.
7. A \`recording timestamp\` in a detection-positive audio file does **not** mean a complete survey-night effort table is included. No true zero nights or source-independence from old USFWS 2010–18 can be asserted until verified raw survey schedule and project/event identifiers are accessible in an independent source.
8. If source download URLs require non-ScienceBase credentials/redirects, fail with \`SOURCE_FILE_ACCESS_STOP\`. Do not bypass controls or call the original source null.

## Scientific limits

This is original public metadata/README **schema only**, no bat ecology result. It cannot rescue the pre-registered original 236-site/9-year negative USFWS v46 shared annual acoustic-composition transfer. Any claim that independent NABat data permit cross-country behavioral laws requires a future outcome-blind **source overlap audit**, actual site-night denominator, harmonized species labels, and a new frozen predictive task.
