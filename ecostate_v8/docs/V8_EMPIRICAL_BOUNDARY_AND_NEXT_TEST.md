# v8 scientific boundary and next decisive test (2026-11-16)

## Questions and observed versus non-observed evidence

Primary hypothesis: in source-defined used-versus-available movement choices, does an *origin-state retention* feature improve held-out animal likelihood beyond distance, turn angle, and destination state alone? This is a direct discriminating test of conditional movement organization, not proof of memory, adaptation, or resource-state portfolio exhaustion.

## Original-source outcomes

1. White-spectacled bulbul / Handel et al. 2025. Dryad dataset DOI 10.5061/dryad.wwpzgmsxg, provider file ID 4155360, `Field_Margins_Bulbul.zip`, 204,844,719 bytes, official sha256 `bfcd6aee40791a741cd8e8f490a8dc8ead826338592ec2e9a6bb24f23e9eb09b`. Dataset and file metadata retrieved and verified. HEAD requests to /api/v2/files/4155360/download -> HTTP401 and /downloads/file_stream/4155360 -> HTTP403 in the GitHub Actions environment. **Original bytes NOT obtained, source schema/matched alternatives NOT admitted, zero ecological effects computed.** Synthetic numerical benchmark passes; that cannot stand in for an animal-field result.
2. USGS 2022 waterfowl GPS DOI 10.5066/P9XBZKZ8. Original source metadata, full CSV byte count 30,403,945 and MD5 `3e5a91b2d5176cce43101ffcb6a60f25` verified; 224,888 records, 131 distinct deployment ID strings, native GPS time, coordinates, MNDWI, wet-or-dry, annotated Status. **No per-step matched available alternatives** in its 12-column original CSV, no field effect computed.
3. Strict original source crosswalk, USGS 2022 versus 2023 step-selection source DOI 10.5066/P9ELSUHN. The second original CSV 27,997,528 bytes MD5 `78eb6064eca992225d6907d6e46f5bef`, 380,578 rows, 493 birdyear tokens. Exact matching of original `Xdeployment ID` or `Concat` with 2023 `birdyear`: **zero matching ID strings, zero matching ID+minute keys**. **No source-verified identity crosswalk**: can't transfer 2022 beginning-of-step habitat status onto 2023 generated candidates or claim independent replication. Timezone/fuzzy coercion was deliberately not attempted. Zero overlap is not proof of distinct real birds.

## Scientific consequence

This iteration improves *falsifiability and source provenance*, not the number of positive animal effects. Existing source-specific positive observations (Serengeti timing, bat identity, King Rail hydrological buffering, California waterfowl diel sequences) remain valid within their original inferential limits but cannot be pooled into one causal effect. The `boids` PR #146 negative predictive endpoints and `louis` PR #7 exploratory manuscript are unchanged. No defensible original cross-taxon niche-organization law follows yet.

## Next admissible empirical work

- **First choice**: get original bulbul source directly from its maintainers, or obtain an authorized, provider-checksummed distribution. Verify the original RData schema, source origin state and one used plus ≥2 available candidates per exact individual × burst × step/time. Only then run the *already-frozen* whole-animal out-of-sample M0 (destination) versus M1 (destination + origin retention). This is a source-access prerequisite; do not evade 401/403 access controls.
- **Alternatively**: discover a wholly separate open-source GPS/step-selection release with true per-event origin and matched alternatives, check DOI and original SHA before scoring any response, and preserve all zero/negative outcomes. No eBird.
- **Do not** treat the USGS 2022 observational GPS exposure time series as matched choice data, or use unsupported ID/time joins to fill 2023 step origin fields. With the current data, a descriptive within-animal wet/dry exposure analysis could be separate, but would not establish reachable-state causal tracking or validate the ecological bridge.

## Exact reproducibility

`python -m unittest discover -s ecostate_v8/tests -p 'test_*.py' -v`: 19/19 known-truth and source-guard tests passed locally on 2026-11-16. GitHub Actions v8 original-source gate #43877792036 and known-truth #43877792021 passed; 2022 USGS source header #43878741912 passed; cross-source identity run #43879373482 passed. These pass source/test integrity *not the biological endpoint*. Original source receipts preserved as JSON under results; no raw animal GPS or subject identifiers are redistributed.

