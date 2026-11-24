# v25 2026 Peterson lateral-line intervention: original Dryad source-access outcome

**2026-11-24 JST. SOURCE_ACCESS_STOP — not a biological null, no 60-fish original individual trajectories or treatment effects fitted.**

## Primary published citation

Peterson A. N., Zhou J., Mittal R. & McHenry M. J. (2026), *The lateral line facilitates rapid responses in accelerating fish schools*, *Integrative and Comparative Biology* 66, article icag151, DOI [10.1093/icb/icag151](https://doi.org/10.1093/icb/icag151) (published 18 Aug 2026). In the published study, **60-fish schools of *Petitella bleheri*** underwent impaired lateral-line sensing; published authors report approximately one-third shorter response latency during acceleration for intact versus impaired schools, and no comparable latency effect during deceleration. These are **original authors' existing findings**, not reanalyzed results of Boids.

The journal's Data Availability statement refers to **Dryad DOI [10.5061/dryad.gxd25482b](https://doi.org/10.5061/dryad.gxd25482b)**.

## Actual access audit — all SOURCE-only

We froze a [source-only metadata and license/schema protocol](V25_LATERAL_LINE_2026_DRYAD_SOURCE_FREEZE.md) before original source outcomes. We did **not download original data files**, sensor streams or source fish positions; only official Dryad REST metadata URLs were requested. No fish model fitting was attempted.

| GitHub Actions technical status | Dataset REST source result | Scientific admission |
|---|---|---|
| [v25 first #45316984469](https://github.com/zuizui0223/boids/actions/runs/45316984469) SUCCESS | API returned JSON with DOI identifier but no file/version links | SOURCE_ACCESS_STOP; metadata response was not a complete public dataset record |
| [v25b schema #45317104625](https://github.com/zuizui0223/boids/actions/runs/45317104625) SUCCESS | Only top-level keys \`id\`, \`identifier\`, \`message\`. No \`_links\`, \`_embedded\`, title or file listing | SOURCE_ACCESS_STOP |
| [v25c error-envelope #45317246624](https://github.com/zuizui0223/boids/actions/runs/45317246624) SUCCESS | Official response \`id=184896\` and literal \`message="Identifier cannot be viewed. Either you lack permission to view it, or it is missing required elements."\` | **SOURCE_ACCESS_STOP: API_ERROR_ENVELOPE_NOT_PUBLISHED_DATASET_METADATA** |

Six offline source-aware original mock fixtures PASS in v25; the v25c revised version adds a seventh fixture against a JSON/HTTP200 logical **error-envelope** masquerading as dataset metadata, also PASS. Technical workflow success means expected 401/403/errors were correctly handled, **not source admission**.

Official API source tested: \`https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.gxd25482b\`. The source returned a limited public/error envelope, not the deposit contents. The dataset **may exist in another publication/incomplete/private state** and this access status does **not** establish data inexistence, permanent inaccessibility, embargo, or a biological null. No attempt to bypass publisher access constraints.

Frozen v24 short/delayed age-curve source results and original 2 taxa remain unchanged; the primary sensory-treatment-by-acceleration hypothesis remains untested by our independent reanalysis.

**Next legitimate step:** official released Dryad download / author-supplied files with original provider version and checksum, source treatment assignment, multiple independent school IDs, original raw current and past XYZ(t)/timestamps and interpolation metadata. No third-species meta-effect and no fish chorus feedback claim without actual admitted outcomes. Keep PR Draft, main unchanged.

Original frozen source-only artifact #45317246624 / #14886280670, ZIP SHA256 **15eab617619e341d64b2525cdc84709db028529e9cc4a25fec2c91b3328c1ada**.
