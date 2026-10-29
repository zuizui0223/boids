# v25-B2 source file pins — registered after official USGS manifest and BEFORE step/choice outcomes

**Date: 2026-10-29 JST.** Official ScienceBase 2023 source item `652edfe8d34edd15305a9ab0`, DOI `10.5066/P9ELSUHN`, showed two exactly named original attachments before any animal/source response data were read:

| Exact original file | Published byte length | Provider published MD5 |
|---|---:|---|
| `Data Release P9ELSUHN.csv` | **27,997,528** | `78eb6064eca992225d6907d6e46f5bef` |
| `Data Release P9ELSUHN.xml` | **26,316** | `170cf76948ef8604ae41f268bc3bf4f0` |

The attached CSV is under precommitted 250MB single-file cap. Its row/column and biological source structures have **NOT** yet been read.

## Immediate no-outcome B2

1. Fetch exact original two published attachments from the official ScienceBase URLs listed by item metadata; verify original full byte length/provider MD5, compute independently reproducible SHA256. Stop on mismatch.
2. For CSV, examine only ORIGINAL COLUMN NAMES and physical line count, no animal locations, GPS step start/end numeric coordinates, used/available outcomes, landcover/hunting predictor values or fitted scores. For XML, extract ONLY data-field labels and descriptions, not example raw telemetry coordinates or counts.
3. Classify whether original schema includes original bird IDs, used/available case labels, a stratum ID or paired start-position/destination identifiers and time. If required fields are absent, report a source-design `NOT_ADMITTED` rather than retrofitting an assumed 101-candidate choice set from a paper description.
4. In the published paper the availability kernel was estimated from observed movements across the full source, so even with step start origin in every row, this archived availability is a **retrospective** kernel-based source. It is NOT a wholly training-only generated future movement opportunity distribution. A future model may only be called conditional retrospective step-ranking unless it independently regenerates alternatives without heldout movement.
5. The source is within California Central Valley, where a separate 2026 brood source v24 Suisun Marsh exists. Same region/years do not by themselves imply or exclude shared individual IDs; do not assert independent animals without explicit original ID provenance.

All earlier v13–v24 results frozen. No observed v25 ecological effect at B2.
