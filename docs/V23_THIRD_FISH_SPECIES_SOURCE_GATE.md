# v23 third independent fish-source admission: frozen metadata-only contract

**2026-11-24 JST. Before any v23 original fish movement values are accessed.** This is source discovery and access verification, not a movement result or a third independent replication.

## Publication and exact source

Zheng et al. (2026), *Nested interaction network enhances responsiveness in collective behavior*, Communications Physics, DOI https://doi.org/10.1038/s42005-026-02510-0. This paper reports schooling *Hemigrammus rhodostomus* 5-fish, 10-fish and 15-fish groups with **186, 267, and 181 reported motion recordings**. Original raw fish trajectories/video are **available from authors upon request**, while two curated extreme-maneuverability examples and derived summary files are in the authors' public GitHub. It is not 634 fully public fish trajectories.

Upstream: https://github.com/DerekZhengEvosil/Nested-Interaction-Network-Enhances-Responsiveness-in-Collective-Behavior ; exact original commit 5a2a834580c3212b3f69f33517869add934513b5.

Original public files (path, byte size, Git blob SHA1):
- data/biological_data/high_maneuverability.mat — 128481 — f438dc0a87cd8c4bcf9c516720d0e552559938c1
- data/biological_data/low_maneuverability.mat — 55133 — 52feee019a0f11125c23c59a8c6ab264db427937
- data/biological_data/NODF_curvature_polarization.mat — 12669 — b46b03d22238c4a164a409cad049ebac72fb550b

The published biological_analysis scripts label the high/low variable names as high_maneuverability_example and low_maneuverability_example. MATLAB examples plot 15 fish and use 0.01-s nominal frame step, but trial identities, source chronology, complete groups and track interpolation are **not** verified from this metadata.

## Exactly registered before v23 access

1. Download *only* these three files at the exact pinned upstream commit with a max 512KiB response size each. Independently verify original Git blob SHA and byte size before scipy.io.loadmat. Log SHA256, provider SHA, size, expected variable name and matrix **shapes only**. No original animal coordinates or movement outcomes in GitHub/JSON.
2. For each high/low file require at least two same-shaped numeric matrices in the expected MATLAB cell object (the first two are position x/y per published code). If missing, stop scientific admission. Derived NODF aggregate file only gets top-level variable names/dimensions, no effect estimates.
3. Include independent synthetic known-truth fixtures testing correct Git object SHA, changed byte, nonnumeric xy, and missing cell arrays. Fail-closed: status only TWO_CURATED_EXEMPLARS_METADATA_ADMITTED or SOURCE_ACCESS_OR_SCHEMA_STOP.
4. A successful source status authorizes **no third-species heldout predictions** because exactly two high/low examples were selected by the authors, not randomly sampled independent schools. The full groups' raw data need separate source access and release before v23 empirical evaluation.

## Next scientific admission threshold

Require full original 5/10/15 fish trials (not just two examples), individual IDs, all time-stamped XY, stable recording/session identifiers, original source checksums, clocks and sensors, permitted reuse, and a fixed cohort definition. Freeze whole-recording holdout with current versus 2-second-old neighbor fields before predicting fish motion. No fish calls are documented for this source. PR #248 remains Draft; no main merge or fish chorus claim.
