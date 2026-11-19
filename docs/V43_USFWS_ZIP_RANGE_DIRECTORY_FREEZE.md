# v43 — USFWS original ZIP byte-range central-directory audit (after v42 size-cap STOP)

**Freeze 2026-11-19 JST, BEFORE requesting ZIP central-directory bytes or inspecting source archive members.** The original v42 bounded whole-ZIP admission remains **SOURCE_HTTP_OR_SIZE_CAP_STOP** (official HTTP 200, Content-Length **495,216,105 bytes** against fixed 100,000,000-byte whole-source cap). Do **not** increase the v42 cap and do **not** reinterpret v42 as PASS.

## Distinct bounded protocol

Source remains **the same exact USFWS official DownloadFile/165800?Reference=112151**, no mirrors, headless browser, credentials, or indirect archives.

1. Issue one HTTP Range request for the **last 65,536 bytes** of the original published ZIP (expected Content-Length 495,216,105 from v42). Accept **only** status 206 with exact Content-Range and original total; if ignored (200), read at most 1 MB then stop; never download whole 495MB file.
2. Identify standard ZIP end-of-central-directory signature and expected central directory offset/size and declared member count. STOP if missing/ambiguous ZIP64/multi-disk or out-of-range offsets. A later server version/total-size difference also STOPs.
3. Request only the exact central-directory HTTP Range, with **at most 4 MB compressed directory bytes**. Require correct 206 Content-Range and expected length. Parse ZIP central-directory metadata (header, filename bytes, member compressed/uncompressed size, local offset) and compare declared entry count. No per-member compressed payload/animal data is fetched.
4. Export **only** extension/category counts and relevant title-keyword counts (\`night\`, \`pass\`, \`counts\`, \`metadata\`, \`survey\`, \`effort\`, \`recorder\`, \`WAC\`). Do not export original site/roost/member filenames or coordinates.
5. Whether member names suggest \`Nightly Pass Counts\` does NOT prove a complete detector-night sampling denominator or true zero detections. Qualified source-night effort remains false until a separate predeclared workbook-header and instrument-validity review.

## Scientific interpretation ceiling

USFWS catalogs a multi-site 2010–2018 source and states source \`Nightly Pass Counts\` only includes nights with >=8 15-min WAC files, roughly >=2 recorded hours, with damaged/short nights omitted. Even if files are listed, this is not equal monitoring of an entire night. All earlier Finland v39 primary FAIL, three-region negative transfer, v41 Italy/Belgium incomplete effort and prior boids/batter results stay frozen.

The v43 result is **remote metadata feasibility only**, no biological finding, and no official provider checksum available for complete original archive. Partial range bytes cannot establish full original bitstream integrity.
