# v45 — USFWS recovered nightly-count workbook: source observational grain & effort-field support

**Frozen 2026-11-19 JST, after v44 CRC32/header-only PASS but BEFORE any original numeric bat species-pass counts or per-night activity values are read.** This is an independently labeled source audit, not a behavioral result.

## Exact original source

USFWS ServCat Reference 112151, DownloadFile 165800, archive fixed total **495,216,105 bytes**. v43a verified original 65KB terminal ZIP tail SHA256 \`69f4410f8b868849e6e17160b377e6f34fc65068e62f2590e31b598bc5f0fa59\`; directory contains 11 XLSX files. v44 original selected files fully passed central ZIP CRC32 and byte size:
- Nightly Pass Counts workbook, compressed **1,773,269**, reconstructed XLSX **2,171,863** bytes, original outer ZIP CRC32 **3666e794**; two worksheet XML members, first row 17 cells.
- Metadata workbook, compressed **34,955**, reconstructed XLSX **46,292** bytes, original ZIP CRC32 **19f9b7c8**; two worksheet XML members, one sheet's first row 23 cells.
- No published whole-archive SHA256; original v42 whole-source size cap and original v43 second-range transport stops remain unchanged.

## Fixed v45 pre-outcome questions

1. Reverify exact original 65KB tail SHA and both selected original XLSX ZIP-member CRC32 through the v44 fixed **12MB compressed / 30MB uncompressed per-member** gate; never download whole archive or nine large pass-list workbooks.
2. Count original worksheet rows **without interpreting numeric bat pass counts**. Inspect only first row text headers, or if the first row contains a prose title, report safe generic keyword categories from up to first 3 rows but never output full prose or original station/site names. Report exact field names only when plausible generic labels and no coordinates/person/place values; sanitize/protect sensitive source tokens.
3. Identify \`site\`, \`detector\`, \`year\`, \`date/night\`, \`WAC files\` or operating-hours columns by **literal original header meaning**. Report if the field exists, not its numeric values.
4. Source observation-grain test: if an unambiguous original row-level site token and night/date/year key exist, count unique site-night groups, rows per group, groups with duplicate keys, number of original recorder categories. Decode **only those grouping identifiers**, never acoustic counts, species columns, weather, GPS or raw site names in artifacts.
5. Identify whether XLSX has a column for original qualifying \`# WAC files\` or operating hours, versus a documentation note only. Count **presence/absence** of the source cell under that column, but do not open the numerical number of WAC files yet.
6. A source table that includes only detector-night rows meeting the published \`>=8 WAC\` / >=2h nominal operation filter is **effort-qualified for included rows** but does not automatically include all attempted zero-activity nights, partial failed nights or a common full-night exposure. The existence of an explicit zero-number in a bat species-count column would require opening a numerical bat outcome, which is explicitly prohibited until the future v46 predictive model and source zero-audit are frozen.
7. **Eligibility for a future independently preregistered study** requires >=3 distinct years, >=10 distinct site tokens and >=100 uniquely identified detector-night rows with an explicit valid recording-duration/WAC field, and a clear site-night key with no ambiguous duplicated aggregation rows. If the original document has 2 sheets with different grains, NEVER merge without verifying the intended original layout.

## Inference boundaries

- Metadata categories, source file inclusion and count of original rows are **not** evidence that silence means bat absence. No occupancy/intensity/temperature model, prey selection or cross-country transfer may be fitted in v45.
- The USFWS original species automatic classifier was not individually manually validated; a future study must either account for misclassification, use guild sums with quality control, or retain this as observational weakness.
- Original 2010–18 / 276-site catalog claims are source context; actual original row/site/year support must be reported from the workbook, not invented.
- Original Finland v39 6/7 years mean gain +.017943 was **nonconfirmatory** by exact sign p=.0625 and regions −.038835; Italy/Belgium v41 missing effort denominator, morphology v37 and Carollia v30 negatives remain frozen.
