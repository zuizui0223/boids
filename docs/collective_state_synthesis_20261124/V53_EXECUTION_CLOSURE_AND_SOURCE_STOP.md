# v53 execution closure: exact dynamic null reproduced; empirical source admission stopped

2026-11-25 JST. Original run [45583894086](https://github.com/zuizui0223/boids/actions/runs/45583894086). Frozen source-only/dynamic-null protocol at 2590e68a5500e36bcb50bdf1045dd0bc96589b87.

## Completed numerical reproduction
Dynamic-null job 139100464944 SUCCESS. Original artifact 15008425337 downloaded and independently checked. ZIP SHA256 e80944943277b776370d605b999525d7759ed605843bbef202f483d2a24c701d; member dynamic_null.json SHA256 84bfc54c7326903f8bfe69a4a737b6681f6bfee90364d7a0fb9fbe089b0b2bc6, byte-identical to the local execution result. All 81 case changes exactly reproduced; maximum additional oracle gain magnitude 4.440892098500626e-16. See V53_DYNAMIC_COMMON_FIELD_NULL_RESULT.md.

## Dryad source inventory verified, source bytes not admitted
Both published dataset/version and file manifests retrieved via official Dryad API; download requests returned HTTP 401 Unauthorized. No new fish trajectories or forecast scores were obtained. Dryad's current API accounts documentation specifies authentication for file download; do not attempt to circumvent authentication. User can obtain the original public files via the provider interface and supply them, or authorize access via a supported credential workflow. No credentials in the repository.

| Dataset | Official version | File | Bytes | Provider MD5 | API file ID |
|---|---|---|---:|---|---:|
| 10.5061/dryad.9m6d2 | 265 | metadata.txt | 6274 | 619c3ff7ff3dbad8826911db256b1f05 | 1091 |
| 10.5061/dryad.9m6d2 | 265 | README.txt | 2336 | d0d2164d5f01bd2a95b7b510d8703039 | 1090 |
| 10.5061/dryad.9m6d2 | 265 | 8.zip | 179559645 | d3fb45face96a3ad993dd53f8c32b7fd | 1096 |
| 10.5061/dryad.j0226 | 21089 | Data Dryad.zip | 1438254 | b535c5cc64832f259da672c84ea3a0e9 | 72001 |

Ring job 139100464644 FAILURE (source admission STOP); artifact 15008150798, ZIP SHA256 1d7b20c2e7f6b24aacdf4c38468fdcee4086cf6a280761421e9db4febe96f3ca. Banded3d job 139100464303 FAILURE (source admission STOP); artifact 15007377610, ZIP SHA256 1989c8938785c9ff7c452b53e0d35adc157eedd4a87d598b1c326cee3af74d22. Artifact digest values are from GitHub's manifest; unlike the dynamic-null artifact these two STOP ZIPs were not independently downloaded. Manifest MD5s are provider declarations, not verified file bytes.

Provider landing pages:
- https://doi.org/10.5061/dryad.9m6d2
- https://doi.org/10.5061/dryad.j0226

Next priority: authenticated 3D archive (small, six separately assigned shoals; clock and stimulus limitations), then the 8-fish ring archive with original README and metadata. Validate actual archive byte sizes/MD5s and document identity/clock/cohort before fitting. The v53 synthetic calculation demonstrates non-identifiability; it does not replace those empirical tests. Draft PR #255, main and previous results unchanged.
