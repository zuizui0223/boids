# Source-authoritative bat sonar / Boids model audit — 2026-11-07

**Source audit, not an original independent ecological experiment, and no new measurements.**

## Verified accessible prior-art model

Mazar & Yovel (2026), *eLife* DOI `10.7554/eLife.105571`, source GitHub repository `omermazar/Colony-Exit-Bat-Simulation` (public MIT `LICENSE`), pinned original main commit `a74fb61a8efb57ca37693893c3bd7b35fa94fa89` on 2026-02-12. Original code models two simulated species (`Pipistrellus kuhlii`, `Rhinopoma microphyllum`), no new bat tracking in our project. The paper ALREADY demonstrated the benefit of short inter-pulse intervals, multi-call echo integration, multi-call clustering and immediate obstacle avoidance under acoustic masking. **It would be false to claim that those mechanisms were newly discovered here.**

Unlike our previous source-blocked 2025 `Goldshtein et al.` movement+onboard audio dataset (Mendeley raw Data.zip unavailable), the eLife **simulation source code, parameter XLSX and prior source MAT files ARE public and source-identifiable**. However, original MATLAB GUI scripts contain absolute Windows filesystem paths, `uigetfile/uigetdir`, table/GUI and signal processing constructs; Python or GNU Octave cannot automatically be called an exact replication.

## Three scientific source gates, BEFORE opening or running source numerical model outputs

1. Pin exact original Git blob hashes of MIT source `CaveExit_Experiment_Confusion.m`, `BatFlightForGui.m`, `BatManueverDecision.m`, `BatSonarDecision.m`, `DATA/DefaultParamsTable_CaveExit_FInal_PK.xlsx`, `DATA/DefaultParamsTable_CaveExit_FInal_Rhino.xlsx`, and the original `Swarm_200bats_New_1.mat`. Verify against GitHub original blob metadata and compute independent SHA256. Inspect only function names, source parameter identifiers, MATLAB-specific dependencies, and MAT variable names/shapes. No original .mat numeric arrays read or source code rehosted.
2. Distinguish source **perception** and source **action**:
   - `ConfusionObs` / `MaskingByConsps` govern acoustic sensory interference;
   - `ObsMemorySize` and `ObsRepeationsFlag` / `ObsEchoesRatioTH` govern multi-call echo aggregation and outlier rejection;
   - `BatManueverDecision` contains immediate obstacle / bat separation response to current sensor output, at a different timescale from memorized wall/path integration.
   These are original prior-art architecture claims, not our predictions.
3. Compare with *our* `boids3d_empirical_v4/boids3d_research` model: it uses explicit geometric separation/alignment/cohesion and persistent vertical response gains but **does not implement a source-calibrated sonar receiver, acoustic false returns, or multi-call memory**. Therefore a synthetic collision-avoidance success is not source-faithful bat sonar behavior. Treat exact source code as a source benchmark, not a new biological outcome.

## Candidate new source-controlled question (not yet tested)

**Is the separation between fast reflexive collision avoidance and slower multi-call spatial memory sufficient to predict when a group can navigate an acoustic bottleneck, under common signal physics and independently held-out geometries?**

A *new contribution* would require original model numerical replay (or a formally tested, source-equivalent port) plus a **new untouched obstacle topology, detection/latency manipulation**, and an externally valid observable outcome (exit success, collisions, completion time). Merely redoing the authors' confusion vs memory ablations is their prior paper. No fresh biological model fitting or attempt to improve a desired sign without predeclared controls.

## Explicit hard stops and claims

- If original GitHub blob SHA or downloadable original parameter file differs, SOURCE STOP, not silent code substitution.
- MATLAB-specific or hard-coded environment dependencies discovered => do not say full original solver ran or original eLife figures were recreated. A source architecture inventory is the valid outcome.
- `Swarm_200bats_New_1.mat` could be a sample simulation output, not observed 200-bat telemetry; inspect variable metadata before interpreting it. Do not claim 200 measured bats.
- Original source repository and third-party software may have separate LICENSE files; use original MIT attribution and avoid rehosting original code or files.
- Keep `boids` PR #36 Draft and `batter` frozen JAE/BE manuscript branches unchanged. The 2024 `Molossus` within-bat crowding association remains original authors' prior art and separate from this cave emergence model.
