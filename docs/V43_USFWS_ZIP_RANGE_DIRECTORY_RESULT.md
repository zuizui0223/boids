# v43 original USFWS bounded ZIP byte-range result — second range STOP

**Executed on 2026-11-19 JST.** Original official source: USFWS ServCat Reference \`112151\`, DownloadFile \`165800\`; full archive reports **495,216,105 bytes**. Source-only original workflow [44522009560](https://github.com/zuizui0223/boids/actions/runs/44522009560) PASS with five known-truth ZIP/range tests. Workflow success means source handling/stop logic succeeded, **not** source-night coverage or bat biology.

## Exact frozen v43 observations

- Original last 65,536-byte HTTP Range \`bytes 495150569-495216104/495216105\`: **206 and exact Content-Range**, 65,536 bytes; SHA256 \`69f4410f8b868849e6e17160b377e6f34fc65068e62f2590e31b598bc5f0fa59\`.
- Standard ZIP EOCD at end of verified original tail: **11 declared ZIP members**, central directory at byte **495214984**, length **1099 bytes**; no ZIP comment, no ZIP64/multi-disk indication in EOCD.
- Frozen second request specified \`bytes 495214984-495216082\` (1099 bytes). Original server instead returned HTTP 206 with **Content-Range \`bytes 495214984-495216104/495216105\`** (over-broad to the end of the file). Reader was capped at 1100 bytes. The exact-range transport contract correctly rejected the response.
- **v43 verdict: \`CENTRAL_DIRECTORY_RANGE_SOURCE_STOP\`**. Not an original archive corruption verdict, no member filenames or payloads parsed, no animal observations, no inference of full detector-night effort.

The v42 cap-100MB whole-ZIP result remains STOP and is not retroactively changed.

## Separately frozen successor v43a

The entire ZIP central directory offset range (495214984–495216082) lies inside the exact final 65,536-byte interval already proved genuine. A separate [v43a frozen contract](V43A_USFWS_ZIP_INTAIL_DIRECTORY_FREEZE.md) therefore authorizes **one** re-verified original final-tail request with the **same pinned 65KB SHA**, in-memory extraction of only the central directory, and no second HTTP request. It must not inspect file payloads or infer bat-night zero sampling.

Any v43a source-index result is **metadata only**, not a field ecological effect, instrument-effort confirmation, independent across-species behavioral rule, or proof of downloadable full source integrity. A subsequent bounded workbook-header/source-effort plan is needed if directory metadata permits.
