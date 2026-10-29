# v24-A — Independent USGS brood wetland used–available source admission

Registered 2026-10-29 JST, before opening any v24 wetland use outcome or fitting any habitat-history prediction. Older v13–v23 original results, positive and negative, stay frozen.

## New original biological source

Peterson & Ackerman (2026), Dabbling Duckling Habitat Use and Movements, USGS original data release DOI 10.5066/P13NYGAI; original sciencebase item ID 68631b39d4be025653d31f22, resolved independently from USGS data catalog. USGS page published February 27, 2026 and marks release as CC0. Original 2016–2019 study in Suisun Marsh, California, radio-tagged Mallard and Gadwall ducklings/broods.

USGS public source description says original used wetland observations and GENERATED available locations in flooded wetlands for each brood, with year-dependent wetland habitat type, dominant vegetation, percent cover, salinity and flooded area. Source claims must be checked in actual file(s), including whether both chosen and available rows are at brood × date × alternative grain, rather than assuming that two tables with wetlands permit a proper future choice-set forecast.

This is a genuinely new field population compared with Bangladesh v23 dabbling ducks and Kenyan v20/v22 guineafowl. Distinguish sample independence at brood, nest, hen, wetland and observation date. Sibling ducklings are NOT independent social groups.

## A1 official manifest and original source handling, NO outcome values

1. Request exact USGS ScienceBase JSON item ID 68631b39d4be025653d31f22, official item DOI/title/provenance, file list, sizes, checksums, license, and child item identifiers when relevant. Search fallback only under official USGS ScienceBase API. Never invent file names or download URLs. Report API access failures as source STOP.
2. List attachment names/types/provider file sizes. For candidate original tabular archives <=250,000,000 bytes EACH (total <=300,000,000), download only official ScienceBase-provided file URLs. Check exact original size, provider digest if supplied, compute SHA256, reject unexpected redirects to untrusted origin, duplicate filenames, zip bombs and unsafe nested paths.
3. Inspect original tabular file column names and non-outcome structure only: file/member counts, original identifier grain, date field presence, use/available label columns, original brood IDs and original generated availability unit IDs. Do not inspect location coordinates, used values, salinity/vegetation/area response numerical values or published model fitted effects at source-only admission.
4. Independent scientific unit requires source-declared brood/hen ID, not inferred from geographic clustering. For a conditional future choice set, require a source-declared BEFORE-outcome choice-set ID or a documented brood × observation date scheme with one used option and >=1 alternative that was genuinely available at the same decision time. A pooled availability sample per brood or year is NOT automatically a date-specific alternative.
5. Minimum preregistered target gate: >=8 independent original broods with >=3 chronologically ordered observed use dates each, >=200 actual future-date choice events with at least one measured available alternative per event, at least two year-defined wetland environments. If not met, freeze NOT_ADMITTED and do not select a convenient subset.
6. Any published used/available construction based on future brood paths or buffers must be labeled retrospective conditional availability, not known pre-choice environment. Original habitat covariates must be measured at corresponding wetland/year, not imputed from the chosen outcome.
7. No raw bird locations redistributed. No automatic assumption of calibrated GPS (source is radio telemetry), 3D niche, measured diet, social motor force or food intake. CC0 source license does not eliminate need to protect sensitive nest/brood locations.

## B1 prospective test design — only after outcome-blind original source audit passes

Primary scientific target: conditional log loss on held-out original brood × future-use-date matched choice sets, comparing:
- Environment-only M0: original wetland type/vegetation cover/salinity/flooded area and availability structure, plus year and species, with model fitted entirely from other original broods' earlier choice sets.
- Individual/brood historical wetland-use MI: past visits to original wetland IDs strictly before target date, no future use.
- MEI: environmental model plus fixed historical shrinkage w=n/(n+2), imported without refitting from v23; note this is a predictive weighting rule, not the best biological learning parameter.
- Distance-to-nest/prior-position baseline and chance/availability control, fixed with original source metadata, to prevent trivial spatial autocorrelation being mistaken for a resource-specific individual niche.

Use identical original choice sets for all models; no future use or outcome-derived negatives in training. Whole-brood holdouts, year/site blocking and cluster uncertainty. One available wetland generated multiple times is NOT independent biological replication. No inferences about cognition/competition without direct study.

If source only provides selected locations with no source-verifiable matched generated alternatives, do not fit a pretend choice model; report source NOT_ADMITTED and seek a legitimately independent source. The positive v23 individual daily spread result neither demands nor predicts a positive habitat-choice result.

## References

- USGS DOI: https://doi.org/10.5066/P13NYGAI
- USGS ScienceBase API: https://www.sciencebase.gov/catalog/item/68631b39d4be025653d31f22?format=json
- Original published paper: https://doi.org/10.1093/ornithapp/duag014
- Site is Suisun Marsh, California, not Bangladesh or Kenya.
