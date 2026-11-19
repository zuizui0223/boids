# v44 original USFWS Nightly Counts and Metadata XLSX header audit — PASSED

**Completed 2026-11-19 JST.** [Original Actions run 44524697417](https://github.com/zuizui0223/boids/actions/runs/44524697417): **6 synthetic integrity/non-leakage tests PASS**, exact original USFWS ServCat Reference 112151 / DownloadFile 165800 subset source verified.

## Original byte provenance, without the 495 MB full archive

- Original 495,216,105-byte ZIP, **11 XLSX members**, central directory size 1099 bytes from pinned final 65KB original tail. Provider-tail SHA256 **69f4410f8b868849e6e17160b377e6f34fc65068e62f2590e31b598bc5f0fa59** reverified.
- Selected **one** filename containing \`Night\`, \`Pass\`, \`Count\`, and **one** filename containing \`Metadata\` before reading workbook bytes.
- Original **Nightly Pass Counts.xlsx** ZIP member: compressed **1,773,269 bytes**, uncompressed XLSX **2,171,863 bytes**, CRC32 **3666e794** verified on decompressed original member. This archive is NOT the full 495MB USFWS source checksum.
- Original **Metadata.xlsx** ZIP member: compressed **34,955 bytes**, uncompressed XLSX **46,292 bytes**, CRC32 **19f9b7c8** verified.
- Server returned HTTP 206 with a Content-Range ending at original file EOF rather than requested prefix endpoint. New v44 predeclared method safely consumed only requested prefixes, verified original outer ZIP local filename/method/size and CRC32; no >12MB member or whole archive was read.
- Neither member contains original bat outcome numbers parsed in this stage. Site IDs/coordinates or original ZIP member strings were not exported.

## Workbook structure (source first-row text only)

| Verified XLSX | Source sheet XML members | Structural header summary |
| --- | ---: | --- |
| Nightly Pass Counts | **2** | first sheet **17** header cells with \`night\` / \`site\` keyword categories. Second sheet has one first-row explanation cell containing \`count\`, \`detector\`, \`file\`, \`hours\`, \`night\`, \`operation\`, \`record\`, \`WAC\` |
| Metadata | **2** | first sheet one title cell with \`region\` / \`site\`; second sheet **23** header cells containing \`detector\`, \`night\`, \`species\` keyword categories |

**v44 verdict:** \`ORIGINAL_WORKBOOK_HEADERS_VERIFIED_SOURCE_ONLY\`.

## Scientific status and strict limits

This is **genuine original-data-source acquisition and CRC32 integrity**, not a positive behavioral effect. Source file existence and authors' published \`>=8 WAC\` (>=2 nominal recorder-hours) inclusion condition **do not prove 100% nighttime detection coverage**, absence of unsurveyed zero nights or species classification accuracy. The numeric pass counts and per-night file counts have **not** been opened, so it is not yet proven which records have valid effort denominators.

**Next source-only test:** the separately frozen [v45 original site-night/effort-grain contract](V45_USFWS_NIGHTLY_SOURCE_GRAIN_EFFORT_FREEZE.md) will count source rows, original site/night ID and effort field presence without reading numerical bat outcomes. All prior v42/v43 stops remain unchanged.
