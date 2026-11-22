# Acoustic maintenance audit implementation plan

> **For agentic workers:** Use superpowers:executing-plans for root integration and a fresh final review. Independent simulation and mathematical modules may be delegated with their fixed interfaces.

**Goal:** Distinguish finite-horizon playback delay from post-pulse acoustic maintenance in the existing synthetic Boids model.

**Architecture:** A separate v14 simulator preserves the literal v13 update loop and adds timed weight removal and state snapshots. A fixed runner collects paired outcomes and a separate monotone probability closure diagnoses frozen geometries; plots and the Japanese report use saved results.

**Tech Stack:** Python 3.12, numpy 2.3.5, scipy 1.17.0, matplotlib 3.10.8, unittest, GitHub Actions.

**Spec:** `docs/V14_ACOUSTIC_MAINTENANCE_PROTOCOL.md`

## Global constraints

- Keep v12/v13 immutable and main unchanged; retain Draft PR #248.
- Seeds 1000–1023, 16000 steps, 32 individuals, pulse [1000,1040), post-pulse cut at1040.
- Four continuations × pulse/no-pulse =192 trajectories; primary window [12000,16000).
- All outcomes synthetic-only; same-seed follow-up is not an independent replication.
- Freeze the protocol in a separate commit before running new outcomes.

## Review focus

- Off-by-one intervention and snapshot times must match the completed-update convention.
- Shared random streams must preserve counterfactual pairing and exact old prefixes.
- Right-censored high-window confirmations must never be counted as observed arrivals.
- A frozen-geometry closure must never be labeled the exact stochastic expectation or moving-system attractor.
- A wrong-shape or stale archive must not overwrite valid output or masquerade as this experiment.

## Task 1: exact timed-intervention simulator

Files: `validation_fish_boids_v14/simulation.py`, `test_simulation.py`.

Produces `simulate(seed, steps=16000, pulse_start=1000, pulse_duration=40, intervention_step=None, audio_weight_after=5., heard_weight_after=3., n=32, snapshot_steps=(1000,1040,4000,16000))` with call_fraction/hull_area/cue and snapshot_steps/pos/velocity/calling arrays.

- [x] Write and observe failing tests for v13 replay, prefixes, intervention boundaries, snapshots, constant-Bernoulli calling after hearing removal, and invalid arguments.
- [x] Preserve the v13 loop; add only timed weights and snapshot collection.
- [x] Run `python -m unittest discover -s validation_fish_boids_v14 -p test_simulation.py -v`; all tests must pass.

## Task 2: frozen-geometry closure

Files: `geometry.py`, `test_geometry.py` in the v14 directory.

Produces `geometry_diagnostic(pos, heard_weight=3., theta=-2.8, tol=1e-12, max_iter=10000)` returning JSON-safe endpoint vectors, means, gap, residuals, convergence/classification, stability radii and weighted-degree summaries.

- [x] Test far-separated uniqueness, zero hearing, a coincident-four-node L=6 bistable fixture, unresolved finite iteration and invalid inputs; observe RED.
- [x] Implement monotone lower/upper iterations and Jacobian diagnostics; observe GREEN.
- [x] Include closure-versus-stochastic and finite-chain limitations in the module and report.

## Task 3: fixed paired analysis and runner

Files: `analysis.py`, `test_analysis.py`, `run_audit.py`, `test_runner.py`.

Consumes the simulator arrays and geometry diagnostics. Produces `full_traces.npz`, `audit_result.json`, `summary.json`, `per_seed_windows.csv`, `arrival_records.csv`, `geometry_diagnostics.json`, and receipts.

- [x] Test paired difference-in-differences, fixed-window summaries, confirmation/censor boundary cases, and exact key/shape validation before implementation.
- [x] Implement fixed seed resampling, window and arrival summaries without adaptive selection.
- [x] Run the 192 fixed trajectories; require exact v13 prefixes and preserved-source hashes.
- [x] Compare local intact prefixes against the archived v13 NPZ.

## Task 4: delivery and independent review

Files: `plot_audit.py`, `README.md`, `requirements.txt`, `.github/workflows/fish-school-v14-maintenance-audit.yml`, `docs/V14_ACOUSTIC_MAINTENANCE_RESULT.md`.

- [x] Generate publication-style static plots from saved values and visually inspect them.
- [x] Obtain a fresh review of code, estimands, raw numeric summaries and claim boundaries; fix material findings with meaningful tests.
- [ ] Run the v12/v13/v14 scoped suites and the fixed experiment in GitHub Actions at the final commit.
- [ ] Package the Japanese report, outputs and pinned code links; verify ZIP hashes and save the result bundle.

## Execution ledger

- Base: f558b7f5de63e3b3e712b92a0b2239a08663264f; remote main 47cf12b51553c865027961ae5c162f1b479f5c8c.
- Ruling: use a focused immutable source snapshot and GitHub Git-data API, because the ephemeral checkout was gone; preserve exact fetched blob hashes and use expected-head leases for all branch updates.
- Ruling: proceed under the user's repeated continuation instruction; design choices are ours, not represented as user-specified. No merge, messaging or external data access escalation is authorized.
- Pre-flight: simulator snapshots are after s completed updates; geometry consumes positions only; analysis uses (seed,time) arrays and whole paired seeds. Interfaces checked before execution.

## Local completion evidence at the result commit

- Protocol frozen at d56e0de00d2a1bc11da434aedda00251049f0418 before new results; initial implementation at 9a3336d79015ac0eb3df04cf458579b999c97c8d.
- Fixed 192-trajectory sweep completed twice. The second run followed review fixes to source receipts, worker/array admission, and positive-effect concentration; raw NPZ bytes were unchanged.
- Trace SHA256: 573955d60dfb8e0099f0efd1df6d127f72e549d87073336d91105c4a37612e7c. All 48 intact prefixes match v13 replay; the 48 call/area prefixes also match the archived v13 data.
- Fresh root verification: v12 5 tests, v13 34 tests, v14 44 tests all PASS. All three figures visually inspected, PNG and PDF provided.
- Independent reviewer recomputed all 32 window/arm/metric summaries, 24 cut contrasts, 2 factorials, 768 CSV rows, 144 arrival records, and 192 geometry records. Material source-receipt and plot-input findings resolved with failing-then-passing regression tests; no computational issues remain.
- Japanese report distinguishes finite-horizon delay, the 3/24 arrival changes, structural null controls, numerical closure diagnostics, and the untested moving-system invariant measure. Archive comparison explicitly excludes cue, which is absent from the archived v13 NPZ.
- Delivery tasks above are recorded at commit time. This commit's CI completion and the final bundle checksum will be recorded in the PR update and bundle PROVENANCE.json after those operations complete, avoiding claims about future results in this ledger.
