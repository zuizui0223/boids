# v17-B independent original mate-ledger gate — registered before association analysis

**Date 2026-10-28 JST. Stage: public source-only provenance/graph audit; zero GPS turning or weather×partner prediction outcomes read.**

## Independent source and controls

From Taylor et al. (2019), *Birds invest wingbeats to keep a steady head and reap the ultimate benefits of flying together*, PLOS Biology DOI `10.1371/journal.pbio.3000299`, its **S3 Table: Bird and pairing information** is linked directly as `10.1371/journal.pbio.3000299.s008` (original XLSX). The authors describe two distinct assigned partner phases: similar size (phase 2) and different size (phase 3). These partner assignments, not GPS coincidence or forecast outcome, define the **exogenous interaction-network edges**. The article identifies bird B01 as paired with B82 in the similar-size phase and B07 in the different-size phase, an informative published source crosscheck.

Other independently archived original files from v17-A remain pinned, not downloaded for numerical GPS outcomes here:

- GPS ZIP SHA256 `030e70082b107a353dd4f0afb0cd54868438273a416efac135120a6bdf9c2b29`.
- Weather CSV SHA256 `45885ce19954fd99397b92847421d3e11a6ea2c8d22d1a1d6220ea4940fa2917`.
- Prior original v17-A GPS source inventory: exactly **20 source bird IDs**, 458 tracks in four phases. No raw positions or heading outcomes previously read.

## Independent partner graph procedure

1. Download original S3 XLSX from the exact published PLOS supplementary DOI or official NCBI PMC mirror only, max **5 MB**, record HTTP provenance, content length, SHA256, ZIP member list. A 403/404 is **source unavailable**, not proof that pairings are absent. Do not guess bird partnerships from track overlaps.
2. Extract workbook table headings and identifier-bearing string cells only. Numeric tarsus/body-mass/airspeed cells must not be included in any report; no animal telemetry data is involved.
3. If source table contains recognizable bird, similar-sized partner and different-sized partner columns, map all original subject IDs and two phase-specific undirected pair sets. Check source-specific reciprocals: A→B must agree with B→A *for the same phase* if both listed; no self-pairs. Duplicates of the same phase and bird must agree.
4. **Predefined graph:** all distinct original bird IDs are vertices; edges are the union of **phase-2 and phase-3 assigned pairs**, irrespective of whether two birds separated during a particular flight. Compute connected components of this **full experiment-level graph**. Do **not** define fold groups from observed GPS distance or date/route/turning target.
5. Primary independent social forecast eligibility requires **≥8 components** each with at least 2 birds and at least 2 distinct source flight sessions. If fewer than 8, report `NOT_ADMITTED_INDEPENDENT_COMPONENT_COUNT`. Do not split a connected component at phase boundaries, arbitrarily leave out a single bird with its assigned partners in training, or treat 458 recordings as independent flocks.
6. If S3 only contains columns that cannot be mapped unambiguously to phase assignment, report `STOP_AMBIGUOUS_LEDGER` with original masked header and counts; do **not** choose apparent pairings by matched filename/time.
7. A structural graph gate pass does **not** imply the weather clock UTC offset is solved. Cumulus v1.9.4 standard logs are locally time-stamped; original public MATLAB serial-day weather export can have an unknown postprocessing conversion. Even 100% GPS/weather *coverage* at 0h is not validation. Wind × neighbor forecast remains blocked until an external source confirms export time zone and wind-from / wind-to semantics.

## Source-bound inferential distinction

The published experiment may establish improved homing or visual stability, but v17 wants a *new* independent out-of-sample **predictive information gain** for next-turn angle conditional on wind. Neither S3 table, pair network connectivity, nor original Cumulus software documentation alone establishes that gain.

**No previously opened v6/v8/v15/v16 experimental results are modified or re-scored.** Inability to attain 8 independent social components is a scientific design constraint, not a reason to refit existing data post hoc.
