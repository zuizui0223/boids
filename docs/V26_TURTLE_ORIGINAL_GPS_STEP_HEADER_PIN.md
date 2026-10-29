# v26-B1 pinned original marine turtle CSV: checksum, headers and physical rows before step outcomes

**Registered 2026-10-29 JST after provider metadata-only audit and BEFORE reading any sea turtle individual time/step identities, movement results, protected-status, chlorophyll or depth numeric values.**

Original independent USGS source [DOI 10.5066/P9UZU4GG](https://doi.org/10.5066/P9UZU4GG), ScienceBase ID `5faab074d34eb413d5df1f41`. Official original file manifest from successful source-only CI contains:

| Original USGS file | Published exact bytes | Published MD5 | Purpose |
|---|---:|---|---|
| `Hart et al_iSSA.csv` | **45,669,515** | `5c5f25398720a663ae332097b49bf740` | original observed and random step environmental data |
| `iSSA data release V3.xml` | **22,606** | `bb23daf440cb8ee6932f60a8fc7293a5` | original FGDC dictionary |

No original binary was downloaded or independently hashed in stage A. [Official source manifest CI](https://github.com/zuizui0223/boids/actions/runs/40848377952).

## B1 test

- Download only the exact provider-listed **45,669,515-byte CSV** from the official ScienceBase file URL, bounded 80MB. Require full byte length and published MD5, compute new independent SHA256. A mismatch means hard `NOT_ADMITTED`.
- Parse **ONLY** CSV original header field names and physical row count. Do not inspect any PIT identifiers, exact dates, step outcomes, step alternatives, coordinates, protected status, depth or chlorophyll numbers yet; retain only field names, source byte SHA and row count.
- Original `.xml` dictionary is optional next-source step with separate checksum; do not call it verified until bytes independently match official published checksum. Earlier unrelated v25 USGS XML MD5 mismatch shows why metadata declarations alone are insufficient.
- This original file is independent marine turtles rather than prior pigeons, ducks or guineafowl. A title or provider description naming PIT IDs and start/end times does not establish that the exact CSV physically contains these fields. Source schema must be checked.
- A later separate `v26-B2` may check source PIT×start time×step ID categorical grain, strictly without numerical depth/chlorophyll/used endpoint values, and `v26-C` must freeze all prediction conditions before any ecology.
- Attribution: Hart et al. 2020 USGS public-domain data release. Raw turtle locations and original exact PIT IDs will not be redistributed.

Stage B1 makes **no ecological prediction** and preserves v13–v25 positive, negative and source-invalid findings.
