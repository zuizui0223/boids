# v38 original-source pre-outcome: 2026 fish VR tracking platform and six-speed open-loop datasets

**2026-11-24 JST. Freeze BEFORE examining original Figshare collection contents or original newly identified article files.** Only original publisher pages have been read to locate SOURCE identifiers. No original source animal trajectory rows, treatment outcomes or group sessions read. Source-only discovery does not establish study independence or new experimental findings.

## Two already-published research families

1. **Sanchez et al. (2026), PLOS ONE**, DOI 10.1371/journal.pone.0339909 (original online 2026-01-21), published **correction 2026-02-20 DOI 10.1371/journal.pone.0343509** fixes a video caption speed unit from m/s to cm/s and affiliation. Original published author DATA DOI 10.6084/m9.figshare.29097605. Original authors explicitly give four software record IDs: **30188836** (3D tracking), **30188842** (trajectory simulator), **30188845** (3D rendering), **30188839** (calibration). Original method uses Intel RealSense D435 30–90fps capture, but source file sampling is NOT thereby verified. These original records may reveal true session/subject/clock metadata absent in v35 PLOS Computational Biology article, BUT studies and fish may overlap because of shared authors/platform.
2. **Reynaud et al. (2026), Proceedings of the Royal Society B**, DOI 10.1098/rspb.2026.0146 (published 2026-06-03). Authors conducted a **previously published** open-loop real fish versus one scripted VR fish rotating at six fixed virtual speeds: **5, 7.5, 10, 11.67, 13.33, 15 cm/s**, **7–9 one-hour trials per speed**. Authors have already reported the speed-dependence of social attraction/alignment and wall interaction strength. We must NOT claim speed manipulation or its results as new. Published supplemental/data Figshare COLLECTION DOI **10.6084/m9.figshare.c.8485282**, collection ID **8485282**; ORIGINAL article file IDs have **not** been retrieved yet.

## Frozen original metadata-only requests

Only these seven original Figshare REST targets allowed:
- Public exact original article metadata for **29097605, 30188836, 30188842, 30188845, 30188839** via `GET https://api.figshare.com/v2/articles/{id}`.
- Published collection metadata `GET https://api.figshare.com/v2/collections/8485282`.
- Published original collection member article list `GET https://api.figshare.com/v2/collections/8485282/articles?page_size=50`; cap 50 records and STOP on more than 50 rather than assuming exhaustiveness, do not infer source ID from titles.

Verify HTTPS host exact `api.figshare.com`, response <= 3MB, original numeric ID equals requested, published DOI matches official original `10.6084/m9.figshare.ID` for articles or `10.6084/m9.figshare.c.8485282` for collection (including version suffix) and is public. For member article LIST, report original article ID/DOI/title and published date only, not guess article file manifests. If collection members have genuine unique article IDs and <=50, a separate metadata verification may fetch those original author article manifests only after this protocol reports the permitted exact IDs. We do **not** download any original file contents, videos, Python code, zip archives or fish position rows in v38.

For each permitted original article metadata, report exact provider file name, supplied/computed MD5 if present, byte size, URL host only, and whether file name **suggests** trajectory or subject/session data, but never claim a data schema from filename. Multiple records from a methodological article may be code only; simulated fish trajectories must never be counted as independent real-animal data.

Explicit source limits: no data overlap/outcome, subject identity, source native clock, original DAT variable order, real/virtual fish IDs or original fish trials inferred. Existing v35 2026 PLOS Computational Biology 9 numeric original DAT values remain **NOT ADMITTED** to new C2/C3 response analysis, Issue #250 open. v33 real EIDC 84 trial/12 genuine shoal result unaffected; v37 one-way speed/spacing analytic example unaffected and not claimed as experimental replication.

Synthetic known-truth fixtures for bad article ID/DOI, collection mismatch, API error envelope, empty/malformed member list, >50 records, redirect host/HTTP authentication. Status SOURCE_METADATA_STOP on any untrusted source; preserve partial independent accessible records. [PR #248](https://github.com/zuizui0223/boids/pull/248) Draft and main untouched.
