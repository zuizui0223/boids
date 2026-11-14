# v134 — Multi-taxon full-text screen and source-matched IPD

Design recorded on 2026-11-14, before v134 outcome models. Parent: v133 commit `0710acd9aa30c1308f9139210d5c688f2d27f8b4`. This continues the user's authorized global tide–solar temporal-niche project; it does not replace the frozen v131 protocol.

## Question and deliverable

Establish which independent field studies can quantify tidal information beyond solar/diel timing, and carry genuinely accessible original data through a reproducible matched analysis when their source audit permits it. Deliver a complete decision ledger for the 86 DOI-verified XML records acquired in v133, a reproducible sensitivity pass through previously uncertain metadata, exact new published coefficients, and a Japanese research report. An exploratory IPD result must retain its original study/coast identity and never stand in for a global meta-analysis.

## Literature scope fixed before new extraction

1. Read all 86 v133 DOI-verified XML records, including apparent exclusions. XML retrieval is not substantive full-text availability: an absent or empty article body remains unresolved.
2. From the 405 v132 `uncertain_relevance` records, rescue every record with both original `tide` and `behavior` flags, or a title matching `\b(?:tidal|tides?|intertidal|circatidal)\b` (case insensitive). This yields 46 candidates in the frozen input; selection does not use effect direction, significance or repository availability. This is a sensitivity expansion, not a complete review of all 1,061 records.
3. Verify original article DOI, or original PMID when a DOI is absent. A DOI in the reference list cannot verify the focal article. Record retrieval failures, bodyless records and uncertain decisions explicitly.
4. Distinguish field behavior, occupancy, detection, community composition, physiological endpoints, laboratory rhythms and non-behavioral ecology. Separately record diel phase, seasonal daylength, semilunar phase, tide height and current velocity. Joint additive effects are not interactions; unestimated interactions are not zero effects.
5. Retain exact coefficient, reported SE, link, exposure contrast/unit, covariate adjustment, outcome, original table locator and within-study dependence. Do not invent covariance, effect sizes from omnibus tests, or comparability between different outcomes. Existing v133 effects remain available without being counted as newly discovered studies.

## Raw source audit and analysis boundary

The Magellanic penguin deposit `10.6084/m9.figshare.28517873.v1` provides pressure depth, original animal ID/time/position and independent ROMS current fields. Verify complete-file hashes, time origin, timezone provenance, cadence/gaps, weeks, day/night overlap and coordinate-to-current joins before fitting. The actual `Timestamp` column is naive; mapping it to UTC is an explicit interpretation of the author's metadata, not a timestamp encoded with an offset. Published time rounding and released workflow flooring differ and must not be silently equated. A separate prefit addendum will fix the endpoint, interpolation, temporal holdouts, ghost shifts and sensitivity analyses after source audit and before fitting any outcome relationships.

The Helgoland oyster paper describes a 540-day field series, but PANGAEA publicly states a moratorium until 2027-07-10. Record the access limitation and date discrepancy; do not bypass access controls or claim raw reanalysis. Other original fish or animal files may improve the source map; their acquisition alone does not authorize an unregistered outcome model.

Confirmatory raw IPD gates remain those of v131: at least 8 animals when animals are the unit, at least 1,000 appropriate eligible windows, and at least 8 weeks. A short series can provide a clearly labeled exploratory analysis if minimum source gates are met, but cannot establish confirmatory tide specificity. Millions of time samples, multiple species at one barrier and multiple effects in one paper are not independent coast studies.

## Implementation and validation

New code and outputs live in `validation_v134/`; v131–v133 remain unchanged. Original large files remain in scratch and are redownloadable from versioned original URLs with hash checks. Publish aggregate outputs and appropriately licensed derived data only. Tests focus on consequential identity, missingness, temporal alignment, interpolation, leakage and aggregation errors. Independent review checks the actual sources and scientific claims as well as code. Do not use TinyFish, eBird, fabricated data, or access-control workarounds. Do not contact authors or other people.
