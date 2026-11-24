# v31/31b — 原著者データで84録画と12群の対応を確定

**2026-11-24 JST｜元の魚位置データや新しい未来運動の予測を用いず、公開原著メタデータだけから確認。**

## 独立した原著資料と認証記録

Original EIDC 84 numbered fish source TXT files: [MacGregor & Ioannou 2021, EIDC DOI](https://doi.org/10.5285/08305a43-79b5-432f-ad20-2ddffe0d1077), original directory SHA256 270ae039d690ca4dc315416a5390b3cd3cbfa14e9dcbc1e456ec8e8302158ddc. Native tracking clock 25 fps, eight fish per published shoal, original source missing coordinates NA.

Original author data: [Zenodo 5490572](https://zenodo.org/records/5490572), MacGregorIoannou_Data.csv (41,146 bytes, original provider MD5 PASS, SHA256 f642200bfcd0741e80969981b0a7358462f63ac816bd93dba1b95983855ea3f3) and Readme.csv (1,459 bytes, original provider MD5 PASS, SHA256 ac1c7e0ffb78e06157f2e9e1344d830399ae71f71eab072157222de49b64dde0). Original author's R code: [Zenodo 5458081](https://zenodo.org/records/5458081), MacGregorIoannou_Code_Final.R (25,231 bytes, original provider MD5 PASS, SHA256 c7095571b67376d382164bda000d40f90d737837577d272531f983a049c7e3e0). The R code references the author's original CSV; the strict file-to-group join itself was obtained from that CSV, not from guessing filenames or reading response values.

The original data CSV has 416 presentation/interval rows, with a field Trial giving **exactly the 84 numeric EIDC TXT filename stems** and Group giving exactly **12 unique original group IDs**. Each original trial ID maps to a single, uncontradicted original group ID even if multiple rows occur within a trial. Author original data are available from Zenodo despite direct Dryad file_stream returning HTTP 403. The README is Windows-1252 text, decoded solely for metadata without changing provider original bytes/hashes. The source-identity check was frozen before opening any original summary values.

[Original 2021 author source-only GitHub Actions #45341859409](https://github.com/zuizui0223/boids/actions/runs/45341859409) PASS. [All 84 IDs and 12 original shoal IDs are preserved in a source-verified JSON file](v31_verification/EIDC_84_ORIGINAL_FILES_TO_12_AUTHOR_SHOALS_VERIFIED.json), Git blob SHA1 57ea77c604414cb484f4abd1dd6637eecb2fdf90.

## Original trial file count by independent experimental Group

| Original Group ID | Original trials |
| --- | ---: |
| 1 | 5 |
| 2 | 11 |
| 3 | 7 |
| 4 | 3 |
| 5 | 5 |
| 6 | 12 |
| 7 | 3 |
| 8 | 8 |
| 9 | 8 |
| 10 | 8 |
| 11 | 10 |
| 12 | 4 |
| **Total** | **84** |

Previously preselected file examples have author Group 4 (01.txt), Group 2 (02.txt) and Group 11 (105.txt), so those three were from **distinct original experimental groups**. This does NOT make them representative of all 12 shoals. The authors report early replacement of some fish in three groups, so a stable Group ID denotes the experimental group, not necessarily all the exact same eight individual fish across the study.

The original file-to-group identity dependency in [Issue #249](https://github.com/zuizui0223/boids/issues/249) is now resolved and closed. The new [pre-result v32 protocol](V32_TWELVE_SHOAL_FULL_84_TRIAL_FORECAST_FREEZE.md) uses **leave an original whole Group ID out**, pooling no original fish frames from any video of that group into its training model.

**Scientific ceiling:** This is confirmed original sample provenance, NOT an ecological effect. It does not imply 84 independent fish groups, social interaction causality, neural memory, or acoustic source attribution. No synchronous caller-origin data are present in these sources. [PR #248](https://github.com/zuizui0223/boids/pull/248) stays Draft; main untouched.
