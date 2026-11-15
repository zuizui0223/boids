# Source-grammar-only amendment v6e (2026-11-15) — before ecological effects

This is a separate *prospectively recorded source-format amendment* of original v6c; do not revise or relabel the immutable v6c `SOURCE_DOMAIN_STOP` result.

## What failed in v6c, and exactly why v6e is permitted

- Native `BirdUseCWHP.csv` (provider MD5 `48965f5cefa6364a34b6e92894b76a9b`) contains 240 rows. The v6c script explicitly required `Study year` values `2022`/`2023`; **all 240 records were rejected before any ecological model or prediction score**. Original receipt `SOURCE_DOMAIN_STOP`, no field effect.
- A distinct *non-ecological* checksum-pinned v6d audit, using ONLY `Study year`, `Date` and site IDs, returned native labels `Year1` (136 rows) and `Year2` (104 rows), each mapping unambiguously to actual date years 2022 and 2023 respectively; all 240 dates parsed as `%m/%d/%Y`. Source keys comprise **36 distinct properties** and **118 distinct compound wetland identifiers**, vs the paper's descriptive 117 wetlands. No attempt to merge unidentified site aliases.
- Thus the only authorized v6e change is a verified `Year1 → 2022; Year2 → 2023` parsing normalization *prior* to passing the source rows to the **unchanged v6c parser and prediction routine**. Require the exact same one-to-one source-grammar mapping and original checksum in the v6e execution; otherwise STOP. All response definitions, 240-row starting source, column roster, mean-vs-CV M0/M1 predictors, alpha, missingness/invalidity handling, property group splits, 15-group minimum, 20k bootstrap and fixed primary directional gates remain byte-identical to v6c.

## Clarification of originality

Hartman et al. 2025 (DOI 10.1002/ece3.72032) **already analysed water-depth CV** as a predictor of waterbird counts. v6e does not claim discovering the association; it is a separate independent-*property*-heldout prediction transfer. It cannot demonstrate individual environmental-state buffering, state options reachable by animals, learning, habitat selection causality, or a universal cross-taxon principle.

## Decision

If parser/source domain remains invalid: retain `SOURCE_DOMAIN_STOP` or `SOURCE_SCHEMA_STOP`, no ecological outcome. Otherwise report the prespecified unchanged primary `log1p(shorebirds)−log1p(dabbling ducks)` equal-property heldout mean MSE improvement, site-bootstrap 95% CI and positive group fraction, plus all six secondary negative or positive results. No threshold or model rescue after original scoring.
