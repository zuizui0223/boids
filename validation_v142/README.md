# v142 Public Dryad acquisition integrity

Source URLs:
- California 9 recorder sites / 60 fish chorus XLS deployments: https://doi.org/10.5061/dryad.q2bvq83sw
- Kashima 5 hydrophones / one system: https://doi.org/10.5061/dryad.zkh1893qn

The v141 original individual file API returned HTTP 401 Unauthorized in GitHub Actions. This checks **only documented public download routes** and the official public file download link published by Dryad, without using an API key or bypassing access restrictions. Each original is independently hashed and validated as a true XLS/XLSX/ZIP, or the access gate explicitly FAILS. California dataset latest-version bundle is ~2.69MB. Kashima full archive is 842MB and deliberately not downloaded.

An original dataset might supply chorus event onset/offset and deployed time but **not necessarily complete active recording / audibility**. Even if retrieved, no biological tide×solar effect is calculated without verified local tide exposure, night/solar definitions, observation effort, and non-event recording time. Original binaries are NOT redistributed in PR.
