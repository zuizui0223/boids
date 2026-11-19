# v43a — USFWS ZIP directory exclusively from already bounded tail range

**Freeze 2026-11-19 JST. Separately prespecified correction to v43 source TRANSPORT STOP. No bat activity or sensor outcomes read.**

## Immutable result from v43

The official USFWS \`ServCat/DownloadFile/165800?Reference=112151\` 495,216,105-byte original archive answered the exact final 65,536-byte HTTP 206 range \`bytes 495150569-495216104/495216105\` (SHA256 \`69f4410f8b868849e6e17160b377e6f34fc65068e62f2590e31b598bc5f0fa59\`).

The ZIP EOCD metadata, found entirely inside that verified tail, reports **11 entries** and central directory **offset 495214984**, **size 1,099 bytes**. These numbers also place the ENTIRE central directory within the already retrieved 65,536-byte tail: relative bytes 64,415–65,513, followed by 22-byte ZIP end-record at the end of file.

The second v43 Range request specified those 1,099 bytes but the server returned a Content-Range that extended to EOF, with an oversized body. **v43's exact second-range transport rule consequently FAILED and remains FAILED**. This is not a biological or archive-corruption verdict.

## New v43a source-only protocol

1. Issue **only one** original official 206 Range request for final 65,536 bytes, with **the exact original total** \`495216105\`. For a Range-ignoring server, read at most 1 MB and STOP, as in v43.
2. Require SHA256 of the returned 65,536 bytes to equal the previously verified original tail checksum \`69f4410f8b868849e6e17160b377e6f34fc65068e62f2590e31b598bc5f0fa59\`. If source changed, STOP; do not re-pin after contents have been inspected.
3. Recompute ZIP EOCD and reject ZIP64/multi-disk/ambiguous metadata as in v43. Proceed ONLY if the entire central directory byte interval is contained in the exact verified tail.
4. Slice the central-directory bytes **in memory from the same verified tail**. Validate central-file count, sizes, offsets and names with the already tested v43 pure parser. No second HTTP request, no member payload access, no unbounded source download.
5. Export only extension counts, summary keyword counts and central-directory structural integrity; **never** original archive member filenames, site names, coordinates, source bat species or activity measurements. Do not claim complete original ZIP SHA256.
6. This is **source-directory visibility** only. Nightly count presence, complete detector operating windows, genuine sampled zeroes and independent ecological units remain unverified and require separate source-only workbook admission before any biological effect model.

## Stop rules and scientific boundary

If the 206 tail request fails, its SHA changes, EOCD does not match, directory extends outside tail, or ZIP central parser fails, return explicit structural STOP and do not rescue by new ranges/caps. The initial v42 100 MB whole-source cap STOP, v43 second-range failure, Finnish v39 non-confirmatory positive mean / 3-region negative transfer and Italian/Belgian v41 effort STOP are unchanged. No inference of a universal bat movement or activity law arises from this audit.
