# v47 — USGS 2026 NABat continental acoustic data source-only admission

**Frozen: 2026-11-19 JST, before accessing original source species labels, acoustic counts, timestamps or biological outcomes.** New programme, separate from the completed negative USFWS v46 source.

## Official source identity and prior findings

USGS *North American Bat Monitoring Program (NABat) acoustic data release*, published **2026-10-15**, DOI **10.5066/P1HDZNY9**, official ScienceBase item **6ace802b1ba49b69a5819e47**, CC0. The released collection is described as a multi-partner network spanning North America, with acoustic recordings and manifests including classifier- and sometimes reviewer-assigned labels. Official text warns that classifiers can misidentify species and that metadata in audio files may differ from the current manifest.

Public source endpoints to verify at item level (without login or browser bypass):
- \`https://www.sciencebase.gov/catalog/item/6ace802b1ba49b69a5819e47?format=json\`
- \`https://sciencebase.usgs.gov/catalog/item/6ace802b1ba49b69a5819e47?format=json\`
- official USGS source page \`https://www.usgs.gov/data/north-american-bat-monitoring-program-nabat-acoustic-data-release\`

The previous USFWS 2010–2018 Great Lakes bat acoustic source is an **entirely separate original publication** but recordings may overlap across contributing USFWS/USGS monitoring partners. Never call NABat records a fully independent biological replication until original project/station/recording date overlapping sources have been checked.

## Source-only work fixed before original outcome

1. Query only the two USGS ScienceBase item JSON endpoints, cap each response at 1 MB, record true HTTP status, response format, item ID, original file listing size/count if available. Reject HTML/JSON error pages as source access stops, not ecological failures.
2. Inspect only original metadata file entry names/sizes/content types for \`README\`, \`manifest\`, \`metadata\`, \`survey\`, \`effort\`, \`recording\`. Do not download acoustic recordings, coordinates, classifier outcomes or original detected-species rows. Report counts and keyword categories, never per-site filenames/paths/coordinates.
3. A public *manifest* is NOT equivalent to a full enumerated detector-hours and true zero-detection grid. To claim effort-complete bat-night analyses the source must separately expose original survey-event **start/end dates**, device deployment/validity, scheduled recording intervals and no-detection intervals. Those conditions remain unverified in this stage.
4. Explicitly distinguish public official data release from partner-owned NABat project portal access. A public release can still expose only individual audio-recording metadata and may not contain the original site-night survey effort. Do not obtain partner-private data or infer missing data from documented general NABat recommended metadata fields.
5. A future comparative test must avoid overlap with 2010–18 USFWS survey, use grouped holdouts by independent project/geographical region/country, harmonized classifier labeling and true effort denominators. If metadata not obtainable, record SOURCE_API_ACCESS_STOP and stop, without fabricating a country-specific ecological result.

## Scientific inferential ceiling

The 2026 USFWS v46 actual site-year predictor test (23,018 classified-positive detector nights; 236 site holdouts / 9 year holdouts) **did not support transferable simple annual sinusoidal relative species-composition prediction**: site gain −0.171152, year gain −0.191168 nats/night under fixed model. These are **not** physiological absence of bat phenology. Prior source-specific 2010–18 USFWS and Finnish/Italy/Belgium findings remain unchanged.

v47 is **a source-only access/effort-identifiability audit**, not a new behavior result or validation of any universal bat law. No source original animal values or downloadable acoustic files are exported by this programme.
