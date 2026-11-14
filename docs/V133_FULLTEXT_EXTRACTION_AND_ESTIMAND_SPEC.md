# v133 — Full-text extraction and compatible tidal–diel estimands

Date: 2026-11-14 JST. Continuation of the authorized v131/v132 global meta-analysis. The v131 protocol and its historical outputs remain immutable. This extension is exploratory source extraction, not an independent prospective confirmation.

## Purpose and approach

Move from bibliography to inspectable quantitative effects. Retrieve the 93 tidal–solar and 57 tide-only candidate articles already identified by v132; retain unavailable, mismatched, review and laboratory records. This is a targeted full-text access audit, not completed two-rater eligibility screening or an exhaustive PRISMA review. The 405 uncertain and other v132 candidates remain unscreened.

The alternatives considered were another literature-discovery round, immediate pooling of published coefficients, and endpoint-specific full-text extraction. The last approach implements the current user direction: extraction can advance now, whereas arbitrary coefficients, model ranks and MSE cannot form a common effect.

## Numerical estimands

1. Preserve published estimates and standard errors with exact DOI, original supplement/table/row, outcome, contrast, model link, units, adjustment set and dependencies. P-values adjusted by Tukey are not Wald confidence intervals.
2. For the Portuguese spoonbill feeding model, record each reported conditional day-minus-night log-odds contrast separately. Derive the low-versus-high-tide change in that contrast. For a difference of two correlated estimates with unknown covariance, the point estimate is identified, while the sampling SE lies between the absolute difference and sum of the two marginal SEs. A normal interval using the upper bound is a conservative covariance sensitivity envelope, NOT an exact reported CI or an inverse-variance weight. Values are rounded in the source.
3. The selected additive Tagus model imposes zero interaction; it does not estimate a precise zero. Never use it as an observed null interaction.
4. A day–night association, a tide-only effect and a tidal–diel interaction are different estimands even if all are log odds. Keep habitat, behavioral and detection endpoints distinct. A harmonization key must include contrast, units, endpoint and uncertainty type.
5. No global pooling until compatible effects across independent coasts/studies satisfy the unchanged v131 scientific requirements. Multiple contrasts from one model are dependent observations, not additional studies.

## Raw-source audit

Check original bytes, metadata, schema, genuine timestamps and observation support. Positive-only camera sequences do not supply observed zero-effort intervals. A tide predictor inferred from the biological outcome process is not an independently observed physical tide. HMM behavior labels inferred using tide cannot be used as independent outcomes for testing the same predictor. Preserve inaccessible originals as unavailable, never as biological zero effects. Do not reconstruct missing biological observations with periodic gap filling.

Current candidate raw sources include the authentic capuchin Zenodo 8129505 archive, the Cobscook fish Dryad 438q3 record, and the Magellanic penguin Figshare 28517873 record. Acquisition of a source is not permission to claim that it meets an IPD analysis gate. Do not perform a new behavioral fit unless the source audit and an endpoint-specific pre-fit specification support it.

## Outputs and completion

Source access ledger for all 150 candidates; full-text metadata and table/repository locators (no republished full texts); exact feeding-effect ledger; derived interaction with uncertainty bounds; raw-source audit; Japanese findings report; tests of consequential conversions and scientific admission rules. Store in this existing GitHub-backed project. Publish an isolated draft branch/PR following the established project workflow; retain prior drafts and main.
