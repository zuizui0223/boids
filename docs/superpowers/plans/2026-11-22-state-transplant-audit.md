# State-transplant audit implementation plan

> **For agentic workers:** Use the frozen specification, meaningful RED→GREEN tests, isolated module ownership, and one fresh whole-change review. Root integrates and performs delivery.

**Goal:** Measure finite pulse consequences in96 new simulator seeds and locate their dependence on X,V,C state provenance.

**Architecture:** A restartable literal v14 update loop supplies copied states and RNG continuation. An independent algebra module computes paired factorial/arrival outcomes. A fixed runner validates and archives the12 arms, then static plots and a Japanese report use saved outputs.

**Tech Stack:** Python3.12, numpy2.3.5, scipy1.17.0, matplotlib3.10.8, unittest, GitHub Actions.

**Spec:** `docs/V15_STATE_TRANSPLANT_PROTOCOL.md`.

## Global constraints

- Preserve v12–v14 bytes; base7295d885b587d808cb74fbae11163819ed8cf22d, main47cf12b51553c865027961ae5c162f1b479f5c8c; PR248 remains Draft.
- New seeds2000–2095; split1040, horizon6000, N32; eight intact corners plus motor-cut000/100/011/111.
- Primary call mean[1040,4040), intact111−000, all96. Baseline-low[800,1000)<.90 is secondary and never changes enrollment.
- Protocol must be committed before new-seed outcomes; fixtures use old/unreserved seeds only.
- Maintain fish identity and absolute origin; copy arrays and RNG state; no fabricated hybrid prefix.
- All results synthetic only. No merge, author messaging, or new empirical fitting.

## Review focus

- A restart must continue the precise random stream after initialization and1040 updates, not reseed.
- Snapshot count s means after s updates, before update t=s; cues end before first continuation sample.
- Every factorial sign and X/V/C bit mapping must agree; Shapley and Möbius sums must close per seed.
- Empty/singleton low subsets and horizon-confirmed versus censored arrivals must remain distinguishable.
- Scalar broadcasting, changed source bytes, wrong seed manifests, or stale data must not be admitted or overwrite valid output.

## Task 1: restartable simulator

Create `validation_fish_boids_v15/simulation.py` and `test_simulation.py`.

Interfaces:
- `State(pos, velocity, calling, completed_steps, rng_state)` stores copied arrays and a copied PCG64 state dict.
- `initialize(seed, n=32) -> State` preserves original RNG draw order.
- `advance(state, stop_step, pulse_start=None, pulse_duration=40, audio_weight=5., heard_weight=3., snapshot_steps=()) -> dict` returns call_fraction/hull_area/cue, snapshot_steps/pos/velocity/calling, and `final_state: State`. All times are absolute completed-update counts; traces begin at input completed_steps. Do not mutate the input.
- `transplant(none_state, pulse_state, mask) -> State`, mask0..7 with X bit4,V bit2,C bit1; reject unequal times, shapes or RNG states.

- [x] Observe failing behavior tests for v14 exact replay, split/no-split replay, all component origins, no aliasing, first-call V invariance, motor-cut C invariance, invalid states/times/RNG, and boundary snapshots.
- [x] Implement the unchanged update equations plus state serialization/restart; no new model parameters.
- [x] Run the simulation fixture suite and record evidence.

## Task 2: independent factorial and arrival algebra

Create `validation_fish_boids_v15/analysis.py` and `test_analysis.py`.

Interfaces:
- `decompose(values)` accepts finite shape(n,8), including n=0; returns dict of per-seed vectors: `total`, `insertion_X`, `deletion_X`, `mobius` keyed X,V,C,XV,XC,VC,XVC; `shapley` keyed X,V,C; `shapley_X_minus_C`.
- `bootstrap_indices(n, replicates=10000, seed=2026112205)` returns paired indices or an empty index matrix for n0.
- `summarize(values, indices)` returns n, mean, median, ci95, positive/negative/zero counts, positive-concentration record; null mean for n0 and null interval for n<2. No per-seed vector duplication is required in aggregate JSON.
- `arrival_record(values, start_step=1040, window=200, threshold=.90, n=32)` validates the calling grid and computes integer-window confirmation, observed/censored flags and restricted_latency.

- [x] Observe RED using hand-derived additive, pairwise, three-way, cancellation, insertion/deletion and malformed factorial fixtures.
- [x] Observe RED for exact last-window event versus censoring, count-threshold boundaries, empty/singleton summaries and whole-seed resampling.
- [x] Implement minimal algebra; verify exact closure within floating precision and GREEN.

## Task 3: fixed runner and source/data admission

Create `validation_fish_boids_v15/run_audit.py` and `test_runner.py`.

- [x] Write failing tests for shape/key validation before assignment, snapshot physical consistency, seed/corner admission, atomic-save protection, and launch/end source guards.
- [x] Implement two source prefixes per seed, all12 continuations, and exact v14 reference replays for intact000/111.
- [x] Implement separate prefix and continuation arrays with offset1040, per-seed means/effects/arrivals, summaries and hashes. No adaptive enrollment/horizon.
- [x] Implement all96 and fixed baseline-low cohorts with common resampling within cohorts, all three windows, primary-window factorials, three motor DIDs, and all fixed arrival thresholds.
- [x] Pass scoped suites and independent code review before executing the fixed96-seed audit.
- [x] Run the fixed audit and verify its raw and aggregate receipts independently.

## Task 4: result delivery

Create `plot_audit.py`, minimal plot-input tests, README, pinned requirements, v15 workflow, and `docs/V15_STATE_TRANSPLANT_RESULT.md`.

- [x] Plot all-seed primary contrasts, all eight corner means with allocations/interactions, positional motor-cut comparisons, and low-state arrival/censoring. Use saved outputs; validate receipts before overwrite.
- [x] Obtain fresh independent numerical and claim review; resolve material findings.
- [x] Commit corrected implementation/results; run full scoped v12–v15 suites and fixed audit in CI; compare raw digest and printed aggregates with local execution.
- [ ] Package complete result/report/figures with pinned code links and verification receipts; save and verify delivery; update PR248 without merging.

## Execution ledger

- Ruling: use the existing Git-verified focused source snapshot and guarded Git-data API updates; this workspace has no checkout metadata. This preserves the existing research branch and unrelated files without fetching the whole repository.
- Ruling: proceed autonomously under repeated continuation authorization. Choices of96 seeds,6000 steps and12 corners are our prespecified design, not represented as user-specified.
- Ruling: independent simulation and algebra modules may be delegated in parallel with separate file ownership; developer-level delegation guidance governs. Root owns runner/integration and a fresh reviewer checks the full change before final claims.
- Design review:96 fixed seeds, continuous primary, full intact factorial, four cut anchors, integer arrival counts and explicit censoring accepted; no new outcomes were inspected.
- Pre-flight: Task1 emits absolute-time segment arrays and State; Task3 stores prefixes separately. Task2 consumes(n,8) corners in numeric mask order; Task3 creates that order explicitly. No interface conflicts remain.
- Before new-seed execution, independent review identified false signed interactions from subtracting rounded call means. A valid additive count fixture produced VC/XVC=-1.1102230246251565e-16. All call contrasts and factorial terms now use integer window totals; Shapley numerators share denominator6, and only final values are divided. The scientific estimands and frozen protocol are unchanged.
- Before new-seed execution, RNG admission was strengthened from valid-schema checks to full seed/time-bound PCG64 dictionaries. Independent initialization and jump-ahead expectations are checked against direct-draw fixtures; wrong-seed and split-for-end states are rejected before worker assignment.
- Before new-seed execution, plot admission was strengthened to require the exact current source hash map, predecessor, history count, replay count and validation flags. Per-seed points also use exact integer call numerators. Empty secondary cohorts now have null closure diagnostics.
- RED-to-GREEN evidence:24 simulator tests;30 algebra tests including6 new integer fixtures;15 runner tests including4 independent-review regressions;13 plot-input tests. Full-scope integration and focused review are recorded before any new-seed outcomes.
- Presweep gate: all82 v15 tests passed in22.479s; unchanged predecessor suites passed5/34/44 tests. Focused independent re-review passed15 regressions,257 exact six-permutation allocation comparisons and direct-draw RNG checks on four unreserved seeds. READY to commit implementation before executing the96 reserved trajectories.
- Execution scheduling: implementation was committed at91124e91b974c7fc7e0496bf87d7db8104b1a538 before the local sweep. Commit the workflow and pinned environment while that sweep runs so independent CI reproduction can proceed in parallel. Generated results and README-only changes are excluded from the workflow trigger; all computational inputs remain covered. The later report commit must preserve the same computational source hashes, and delivery will distinguish the CI-tested implementation/configuration commit from its result-document commit.
- Local fixed sweep completed with96 natural pairs exactly replaying v14; raw archive48,311,954 bytes, SHA256 ff50dbf071df55e53e8391c84373802b848ec43fa4a08ed3c4864ebbd935c420. The fixed baseline-low cohort contains8 seeds. The independent oracle reproduced all aggregates and12,288 CSV rows. Japanese numerical and inferential claims passed review; the definition of C was clarified to distinguish stored calls from self-exclusion during hearing.
- Actual-figure review found the primary-panel legend overlapped near-zero points. Only legend placement was changed; all96 points are now unobstructed and13 plotting tests passed again. Plot correction commit24e3b99f50e0a69b341a3f35c5bac1359d457dce triggers final CI run44976865455. All five computational input hashes remain identical to the presweep freeze and local outcome receipt.

- Final CI gate: run44976865455 at24e3b99f50e0a69b341a3f35c5bac1359d457dce completed successfully;165 tests and the full fixed audit/plots/artifact passed. Every printed field matched local exactly, including raw SHA256,5 source hashes, cohort identities, primary-window statistics and threshold0.90 arrival summaries. Final report/data additions preserve all tested computation, plotting and dependency bytes.
