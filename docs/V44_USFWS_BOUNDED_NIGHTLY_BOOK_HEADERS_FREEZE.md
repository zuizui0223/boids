# v44 — USFWS selective source-only workbook-header admission (distinct from v42/v43/v43a)

**Freeze: 2026-11-19 JST before requesting any original ZIP-member bytes.** Scope: USFWS original ServCat Reference 112151, DownloadFile 165800, archive reported exactly **495,216,105 bytes**. This extends the original source-only programme, not a movement or bat activity hypothesis test.

## Evidence already verified

- Original v42 whole-archive >100MB cap => STOP, unmodified.
- Original v43 strict second-range request => STOP when official server responded 206 to EOF rather than to exact requested endpoint, unmodified.
- v43a **single** 206 last-65,536-byte range, expected tail SHA256 \`69f4410f8b868849e6e17160b377e6f34fc65068e62f2590e31b598bc5f0fa59\`: parsed original central directory **11 XLSX members** (one title containing night + pass + count, nine pass lists, one metadata), without original member bytes. This is index verification, not an instrument-effort denominator.

## Preregistered selective member gate, before source workbook contents

1. Repeat only one official last-65KB HTTP 206 Range with exact published total and pinned original tail digest. Parse its ZIP central directory. Match **exactly one** member whose filename casefold contains all \`night\`, \`pass\` and \`count\`, and **exactly one** member whose filename contains \`metadata\`. If missing/ambiguous => SOURCE_SELECTION_STOP.
2. Record ONLY these two selected members' **compressed/uncompressed sizes, compression method and ZIP CRC32**, with no raw filenames or station names. Before downloading a selected member, hard cap the **compressed bytes to 12 MB per member** and uncompressed bytes to **30 MB**, each. Do not split a larger workbook, switch source or enlarge caps after seeing any outcome.
3. Request first **30 bytes** of each selected original ZIP local member header using official HTTP Range. The remote server has previously returned 206 with Content-Range extending to end-of-file. In this distinct v44 protocol accept a *matching start and total* with returned end **at least the requested end**, but consume at most the **requested prefix**. A 200 response or mismatched start/total => STOP. Verify member's local ZIP signature, filename bytes, method and flags against the previously verified central directory metadata.
4. Request the exact local-header+filename+extra+compressed payload prefix in a second bounded HTTP Range, with identical prefix checks; maximum read size <12.1 MB, never stream original 495 MB archive. Verify ZIP CRC32, output byte size and DEFLATE end-marker using the original member bytes; rejection is SOURCE_INTEGRITY_STOP. No original animal value is exported.
5. Open the **two selected recovered XLSX containers in memory only**. Read only workbook **sheet names and column headers on first worksheet row** (source text); do not parse numeric pass counts, species ID row values, geographic coordinates, bat movement, detector time-series or raw recordings. Protect against nested decompression >40 MB per XLSX and huge shared-string tables; stop if unsafe.
6. Report only anonymized per-book/worksheet **sheet-count**, **header keyword categories** and sanitized first-row field names if not sensitive. Any source member filename, station/roost name, coordinate or per-record value is NEVER in the output artifact.
7. Source acceptance is strictly \`ORIGINAL_WORKBOOK_HEADERS_VERIFIED_SOURCE_ONLY\` if both selected XLSX files satisfy checksum/header gates. **This is NOT a complete monitoring-effort admission**. A listing called \`Nightly Pass Counts\` and the original published \`>=8\` 15-min WAC inclusion rule are insufficient to prove continuous full-night detector operation, zeros across all attempted nights or comparable sample effort. Those require a separate outcome-blind instrument effort table audit.
8. Original source archive full SHA256 cannot be verified from selected ranges. We verify the exact pinned original 65KB tail and original selected members via central ZIP CRC32, not the full archive.

## Scientific boundary

No bat activity/behavior/zero night outcome model is permitted in v44. Published original site counts (276) / years (2010–18) are source context, not verified original workbook empirical sample counts. The previously frozen Finnish v39 year primary was **NOT SUPPORTED** (mean +.017943 nats/night, exact sign p=.0625), three-region transfer negative, and Italian/Belgian v41 effort denominator remains unverified. No cross-country universal bat activity rule follows from successfully opening these headers.
