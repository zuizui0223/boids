# v47–v48 original USGS 2026 NABat continental acoustic source audit — public metadata accessible, manifest header blocked

**Completed 2026-11-19 JST.** New separate project-specific source candidate, original official USGS publication DOI \`10.5066/P1HDZNY9\`, ScienceBase item ID \`6ace802b1ba49b69a5819e47\`, published 2026-10-15. Do not equate public acoustic file release to a full behavioral telemetry/true zero-detector-night data release.

## v47 official original item JSON: PASS

[Actions 44528911035](https://github.com/zuizui0223/boids/actions/runs/44528911035), five known-truth source-admission tests passed. Public ScienceBase original item returned **HTTP 200 JSON**, verified the item ID and eight published file entries, comprising:
- **3 CSV**, **3 Parquet**, **1 README.md**, **1 XML**;
- **4 files** smaller than 1MB and **4 files >=100MB**;
- filename categories indicate two \`manifest\` mentions across file types, no original bat/audio recordings or per-record species labels accessed.
- Exact source file identities, URLs or source locality names were not emitted.

This is only original publication/fileset availability, not data-driven bat ecology.

## v48 original README and bounded original CSV header gate: mixed result

[Actions 44529541733](https://github.com/zuizui0223/boids/actions/runs/44529541733), five synthetic source/header/effort tests passed. Exact official provider metadata contained one \`README.md\` and one CSV manifest candidate.
- **README obtained**: exact **18,336 bytes**, 274 lines, original downloaded SHA256 **d51e63365cee6fcc19303e84366f3719652e89582ca1972a7b0fc44b8d3f7855**, HTTP 200 Markdown.
- README text-documentation keyword screen includes \`recording, detector, survey, date/time, labels, manual, metadata, start/end\` but did **not** find literal \`effort\`, \`duration\` or \`hours\` strings. Keyword absence does **not** prove the fields are absent in original manifests or survey tables; no workbook schema or per-detector-night schedule was reconstructed.
- Official CSV manifest provider-reported original file length **9,463,684,696 bytes (~9.46GB)**.
- Strict v48 bounded \`bytes=0-16383\` request returned **HTTP 206 but only 4,255 bytes of HTML (\`text/html\`)**, not a verifiable CSV prefix or the required Content-Range. **\`MANIFEST_RANGE_UNVERIFIED_STOP\`**, and overall **\`README_OR_MANIFEST_SOURCE_FILE_ACCESS_STOP\`**. Not an ecological negative or proof original manifest lacks records.
- No partner account, private NABat portal, unverified mirror, entire multi-GB source or biological acoustic event rows accessed.

## Scientific conclusion and remaining evidence gap

The original release supports **public existence of a large continental acoustic recording corpus and its metadata documentation**, but does not yet establish:
1. a complete list of all attempted site-night recorder windows (including true no-detection nights);
2. independent per-night original recording duration and detector failure validation;
3. overlap/duplication with the separate 2010–2018 USFWS original source analyzed in \`boids\` v46;
4. consistent species labels and methods across independent providers;
5. a comparable resource/prey or habitat stimulus at the original acoustic recording-event unit.

Do **not** claim continental or all-bat law, causal learned flight decisions, space partition, source independent replication or direct negative bat ecology from this access-only result.

Original USFWS v46 site-year seasonal-composition *simple sinusoidal model* primary remains **negative**: 23,018 classified-positive site-nights, 236 whole-site groups, gain **−0.171152 nats/night**, CI **[−0.194166,−0.145439]**, 15/236 positive, and 9-year holdout gain −0.191168, 0/9 positive. The corresponding v45 no-per-night-WAC-effort audit remains source STOP. None of these results was changed or rescued.

**Next substantive step requires a new independent original source with explicit recorder-on schedules, valid negative bins, stable project/site/year IDs and climate/resource covariates.** NABat README and massive original manifest by themselves do not fulfill that requirement. Keep this PR Draft and \`main\` unchanged.
