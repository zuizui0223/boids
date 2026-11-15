# v142 Public Dryad acquisition integrity

Source URLs:
- California 9 recorder sites / 60 fish chorus XLS deployments: https://doi.org/10.5061/dryad.q2bvq83sw
- Kashima 5 hydrophones / one system: https://doi.org/10.5061/dryad.zkh1893qn

The v141 original individual file API returned HTTP 401 Unauthorized in GitHub Actions. This checks **only documented public download routes** and the official public file download link published by Dryad, without using an API key or bypassing access restrictions. Each original is independently hashed and validated as a true XLS/XLSX/ZIP, or the access gate explicitly FAILS. California dataset latest-version bundle is ~2.69MB. Kashima full archive is 842MB and deliberately not downloaded.

An original dataset might supply chorus event onset/offset and deployed time but **not necessarily complete active recording / audibility**. Even if retrieved, no biological tide×solar effect is calculated without verified local tide exposure, night/solar definitions, observation effort, and non-event recording time. Original binaries are NOT redistributed in PR.


## v142 verified source breakthrough

The documented public version download `https://datadryad.org/api/v2/versions/376573/download` (NOT the unauthorized dataset or per-file endpoint) returned an authentic 2,698,238-byte ZIP, SHA256 `c9e2a221955eedc76b9b1927d9cbd1c07fc99875bb661316c5cb516ee297a33e`. It includes exactly 60 Excel deployment logs and README. The source audit script reads every workbook, validates detection start/end, original metadata UTC effort interval, calendar time, site code, chorus type and duplicate recording hours. **All no-detection hours are NOMINAL DEPLOYMENT-COVERED hours, not proof of acoustic audibility or animal absence.** No original user source files are rehosted, no synthetic fish detections, no unverified local tide used. Original fish chorus source is independently cited as Kim et al. 2025, DOI 10.3354/meps14910.
