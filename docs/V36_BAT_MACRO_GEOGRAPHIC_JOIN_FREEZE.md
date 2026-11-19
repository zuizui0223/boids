# v36 — Outcome-blind Laforge bat landscape join and replication audit

**Freeze:** 2026-11-19 JST, before accessing any numeric MCP (home range), Dist (roost–foraging distance), Max_Dist, Mass, wing dimensions, roads or habitat variable values. Source input: two **exact-MD5 verified** originals from Zenodo 5794471 / Dryad 10.5061/dryad.qnk98sfhh. The previous v35 source-only audit establishes metadata file 2,043 rows, landscape file 140 rows, and NO common column names.

## Core integrity question

Can the movement source's \`Lat\`/\`Long\` (latitude/longitude) be mapped to site-level \`X\`/\`Y\` without falsely joining multiple ecological observations? Candidate mappings must be frozen **before** coordinate values:

- Candidate A: \`X=longitude, Y=latitude\` (geographical convention)
- Candidate B: \`X=latitude, Y=longitude\` (possible swapped export)
- Both candidates require latitude [-90,90], longitude [-180,180], original movement lat/long in valid geography, and reported positions **not** user location or animal movement path observations.
- For each original movement record, compute nearest and second-nearest landscape-site coordinates as haversine distance in km.
- A matched record requires nearest <=**1.0 km** and second nearest >=**3.0 km**; no match if a duplicate landscape coordinate, unknown CRS, distance tie or ambiguous candidates. These fixed gates prioritize false-match avoidance over record recovery.
- The preferred orientation is accepted only when >=**80% of parseable movement records** match uniquely and the alternative orientation matches <=**10%**. Else \`SOURCE_JOIN_AMBIGUOUS_STOP\`, not outcome effect. Do NOT change radii/thresholds after seeing results. In particular do not silently map UTM positions to degrees.
- Independently report coordinate-parseable row count, longitude/latitude axis range validity flags, candidate-A/B match counts and rates, unique landscape point count, first-/second-nearest ambiguity count; never export site coordinates or GPS paths.

## Independent ecological units, before target values

- \`Authors\` alone has 113 labels and cannot stand in for the article's 166 studies. First count unique \`Authors×Year_pub×Journal\` publication-key combinations, regions/countries (\`Pays\`) and raw \`Species\` label counts. These are *metadata-defined candidates*, not proof of 166 unique source datasets, bat biological individuals or canonical taxa.
- Count missingness only for \`MCP\` and \`Dist\` at the publication-key, location-key and species level; do not decode numerical endpoints or wing/habitat covariates.
- Maximal independent landscape units <= 140 source rows (often repeated across species/colonies). Do not multiply area rows through join or treat 2,043 metadata records as 2,043 independent landscapes.
- Expected future targets: home range MCP and daily roost–foraging distance **separately** with paper-level grouping; no source out-of-sample claim until outcome model freeze. DO NOT claim a memory, action-selection, flight-transition or individual-level predictor from these published aggregated telemetry outcomes.

## Decision

Stage passes to a separately frozen quantitative experiment only if (i) a unique published-source orientation satisfies the predeclared match checks, (ii) >=10 publication groups, >=4 countries, >=10 distinct raw species labels, and >=100 nonmissing records for at least one target exist in uniquely joined rows, and (iii) no full-track observational unit is double counted. Otherwise status \`JOIN_OR_GRAIN_STOP\` and retain signed counters.

A passing join would still establish **only** the ability to test macro-study portability. No published source coordinates, detailed roost locations or original animal movement data should be redistributed in outputs, logs or GitHub commits.
