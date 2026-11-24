# v31b frozen author-controlled Zenodo 2021 84-trial group crosswalk source review

**2026-11-24 JST. Frozen BEFORE opening original Zenodo CSV rows and original R code contents.** The prior v31 source-only GitHub Actions #45341383890 confirmed: original EIDC 84-file index and Dryad original metadata were valid; Dryad direct original 2021 file_stream downloads 936892/936894 returned HTTP403. However, both **original author-linked Zenodo record APIs** were accessible and returned exact published filenames:

- official Zenodo record 5490572: `MacGregorIoannou_Data.csv` and `Readme.csv` (this is original 2021 dataset mirrored to Zenodo)
- official Zenodo record 5458081: `MacGregorIoannou_Code_Final.R` (the original 2021 author source code)
- official EIDC dataset DOI 10.5285/08305a43-79b5-432f-ad20-2ddffe0d1077 original raw 84 numbered 25fps track TXT files.
- published paper DOI 10.1098/rsos.210655 reports 12 shoals of eight fish with repeated trials, 84 total trials.
- original source-only protocol at [v31](V31_STICKLEBACK_AUTHOR_GROUP_TRIAL_CROSSWALK_FREEZE.md) predates all v31 group code/CSV parsing and remains scientifically controlling.

## v31b frozen retrieval rules

1. Obtain exactly the two trusted published original Zenodo record metadata endpoints `https://zenodo.org/api/records/5490572` and `https://zenodo.org/api/records/5458081`, each capped at 2MB JSON.
2. Derive the **unmodified exact original published same-host file link** for only the three expected author files listed above. Never invent an external URL or rely on a current Zenodo file guessed from a name. Verify original source field `checksum: md5:<hash>` (or original provider-declared MD5 format), size >0 and <=300KB CSV, <=30KB Readme, <=3MB R code, then independently verify the entire original download MD5 and byte size, followed by a SHA256 digest. The resulting receipt may include file names/sizes/hashes but **never the original CSV raw biological response rows**.
3. Header-only and column-statistics original CSV: report original header strings, row count, source grouping/trial/video/file candidate ID columns and unique/count/missing tokens; extract just those ID string values, not the full outcome content. Ignore original response columns entirely for output. The original code file is inspected for **source path / group / trial ID relationship**, output only a small bounded number of context snippets that include group/file/video/read.csv joins or string patterns, with line numbers. No original R source file or complete CSV redistributed to GitHub.
4. Apply the exact same [v31 strict identity join](../validation_fish_school_v31/original_author_crosswalk.py): the 84 actual EIDC TXT file stems must all match explicit original author source trial/video/recording identifiers and one original group/shoal ID each, with no contradictory groups and at most 12 distinct groups. If R code has an alternate **explicit join** it must be audited in a separate future source-only protocol before admission; do not silently override the CSV gate or infer original groups from numeric file order, trial rank or number of days.
5. If no author-controlled group mapping exists in CSV or code, output `SOURCE_IDENTITY_NOT_ADMITTED` even if original file retrieval is successful. No current v26/v30 3-file ecological result is upgraded. Preserve all error receipts.
6. Synthetic fixture tests must include bad MD5, ambiguous group mapping, error HTML, other-host URLs and lack of trial ID. No original animal positions, MSE, trajectories, video or fish calling scored in v31b.

Scientific next step **only if explicit 84-to-12 original join admitted**: a new freeze for source-level 12-shoal leave-whole-shoal-out with fixed 200ms model. It must check all original 84 SHA/size and never treat original numbered recordings as separate fish schools. No acausal group-force or fish sound attribution without further experimental evidence. PR #248 Draft, main untouched.
