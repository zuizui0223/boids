# v31 finished: source-only structural STOP before GPS outcomes

**2026-10-31 JST. `NOT_ADMITTED_ORIGINAL_ID_UTC_SUPPORT_BEFORE_GPS_OUTCOMES`.** [Source-only original 10-file integrity run 41184502922](https://github.com/zuizui0223/boids/actions/runs/41184502922) and [frozen full 10-file ID/UTC eligibility run 41184698257](https://github.com/zuizui0223/boids/actions/runs/41184698257) completed successfully, with all published MD5 and pinned SHA256 and source-only synthetic tests passing. The two explicitly chosen original records were 10053970 (Schiermonnikoog) and 10053702 (Westerschelde), totaling 675,443 rows in 10 GPS-year archives. The original GPS lat/lon, altitude, physical movement and daily prediction responses were **never read** during this experiment.

The exact prior protocol [v31](V31_OYSTERCATCHER_CROSS_SOURCE_PROTOCOL.md) required **both** original studies to each supply at least 8 eligible birds and 80 future days, with 20 birds / 300 days combined. The source-only structural ceiling below is calculated from original bird IDs and UTC times only and can only shrink after GPS observation-quality filters:

| Frozen original study | Distinct original bird IDs | Future-predictable bird IDs upper bound | Future original bird-day targets upper bound |
|---|---:|---:|---:|
| Schiermonnikoog | 39 | 36 | 7,086 |
| Westerschelde | **7** | **1** | 121 |

The second source fundamentally fails the **≥8 eligible birds** requirement: it only has seven distinct original IDs across the entire three-year GPS archive, and time-only history/other-bird admissibility leaves one potentially scorable ID. No alternative year, model, GPS quality cutoff, threshold or geographic replacement was selected after this finding; no pooled comparison M0/MP/MI/MH or ecological score was computed. The 7,086 and 121 numbers are **upper bounds on opportunities from ID/date**, not actual GPS-valued forecasts.

**Scientific result:** this is a negative *data fitness/admission* outcome, **not** evidence against the efficacy of private memory, same-day state prediction, Reynolds/Boids social forces, or anything about the species' ecology. The outcome-preserving registration had a useful structural falsification gate. The frozen v23/v29/v30 positives and negatives are untouched.

Full machine-readable original support [here](../validation_v31/results/oystercatcher_source_support_v31.json). The run was based entirely on the exact provider-pinned original files in [the earlier source-only SHA receipt](../validation_v31/results/oystercatcher_source_only_v31.json).

A different protocol may be designed around another ORIGINAL source before opening any new GPS movement outcome, preserving this irrecoverable v31 STOP. Do not relabel this as a completed two-study forecast or retroactively lower the v31 study threshold.
