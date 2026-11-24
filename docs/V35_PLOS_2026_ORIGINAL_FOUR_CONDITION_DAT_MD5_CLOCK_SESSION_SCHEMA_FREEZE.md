# v35 PRE-RESULT source admission freeze: PLOS 2026 four original 3D real/VR fish DAT files

2026-11-24 JST. FROZEN BEFORE any original .dat file has been downloaded/opened. Only original public Figshare file metadata and the small original code/parameters were MD5 authenticated in v34. This is SOURCE SCHEMA ONLY: no fish biological movement effects are fitted.

## Author-published experimental conditions
Escobedo et al (2026), PLOS Computational Biology DOI 10.1371/journal.pcbi.1014544, original Figshare source DOI 10.6084/m9.figshare.30539666.v1. Author paper defines 2R two real fish, C1 natural-speed reciprocally responding virtual clone, C2 faster reciprocally responding virtual clone, C3 same faster virtual clone but its reaction to real fish disabled (unidirectional). Paper reports 8 ~1h trials C1, 12 trials C2, 8 trials C3, but DOES NOT verify individual fish/session IDs, cross-condition reuse or randomized allocation from the source files. Author conclusions are already published; not newly measured here.

## Frozen original file names, publisher declared bytes and source MD5
- 2R-TwoRealFish.dat: 34,978,800 bytes, MD5 9221dd5d230b3db62143037b68dcd263.
- C1-OneReal+OneVirtual.dat: 37,289,920 bytes, MD5 1404f74726278aacddc0361abcd556c3.
- C2-OneReal+OneVirtual.dat: 65,786,880 bytes, MD5 9b727ba4bf64aa3aa1142d584a65cf2a.
- C3-OneReal+OneVirtual.dat: 56,295,005 bytes, MD5 6b3afe13c9e1be33d19fbd24be3997a8.

All four must first match original Figshare REST article ID 30539666 and exact published original DOI, file name, byte size, original computed/supplied MD5 and original unchanged download_url. The only authorized path is original HTTPS ndownloader.figshare.com with exactly one official source-directed HTTPS redirect to the separately v34c verified exact Cloudflare R2 host 44c1cec316ec56bca76dfd65d2882b20.r2.cloudflarestorage.com. Reject any other signed host, redirects, original byte mismatch or failed MD5. Signed URLs/tokens and raw original fish observations must NEVER be logged or uploaded.

## Frozen source-only schema check
1. Four GitHub Actions shards, ONE each per original published condition filename, are allowed to stream the entire authentic original source bytes in memory (maximum 70MB each), incrementally compute source SHA256, MD5, original byte count and line count. Reject mismatches. No original .dat artifact, coordinate row or per-time fish observations redistributed.
2. Buffer only up to 32KiB of source prefix to inspect original format after the full original MD5 and size pass. Report ASCII vs binary/NUL, number of separators, number of first <=12 physical text rows and numeric versus textual token counts; DO NOT print any real or virtual fish positional values, individual timestamps, speeds, treatment result or per-event rows.
3. Only explicitly nonnumeric original published COLUMN HEADER strings may be reported as source identifiers (max 25 tokens). If numeric-only rows, record ORIGINAL_SESSION_AND_REAL_VIRTUAL_AGENT_IDENTITY_NOT_VERIFIED even if the filename specifies C1/C2/C3. Do not infer the number of independent trials from number of lines or source file sizes.
4. No original PLOS Python model execution or additional outcome extraction, no per-condition animal predictor fit, no experimental effect or Boids causal attribution. A later separately frozen v36 can examine original session/subject mapping and the real/virtual coordinates with original source evidence before any causal model, and must account for within-subject trial reuse and source sampling clock.
5. Next scientific candidate once original schema is proven: C2 reciprocal fast VR partner versus C3 same fast partner unidirectional, while C1 and 2R remain contextual comparison. No claims of new mechanism already demonstrated by authors.

All four original source status receipts, positive or STOP, must be retained. PR #248 stays Draft, main not merged. No fish chorus sound source observed.
