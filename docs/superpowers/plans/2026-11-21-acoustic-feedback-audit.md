# Acoustic Boids v13 audit implementation plan

> For agentic workers: execute the bounded tasks below, preserve v12, and finish with an independent review.

**Goal:** distinguish finite playback persistence from bistability and test the two programmed acoustic links.
**Architecture:** a compatibility-preserving simulator extension runs fixed matched seed comparisons; an independent mathematical module audits the mean-field model; a runner summarizes and plots saved arrays.
**Tech stack:** Python, NumPy, SciPy, Matplotlib, unittest; GitHub connector for guarded commits.
**Spec:** docs/V13_ACOUSTIC_FEEDBACK_AUDIT_PROTOCOL.md

## Global constraints

- Synthetic only; no parameter fitting or biological claims from simulator seeds.
- PR #248 remains Draft, main unchanged. No communication with study authors.
- Existing v12 code is unchanged.
- 24 new seeds 1000..1023; 4000 steps; mechanisms, windows and bootstrap exactly as the spec.
- This workspace contains a focused snapshot, not a full git checkout. Use the existing remote tree and expected-head guard for additive commits.

## Tasks

1. Freeze this protocol in the research branch before the new seed sweep.
2. Implement simulation.py and test_simulation.py. Test v12 equivalence and the causal invariants before the full run; preserve exact operation order.
3. Implement meanfield_audit.py and test_meanfield_audit.py independently. Check folds, tangent roots, critical root, stability and converged continuation.
4. Implement run_audit.py and test_summary.py. Validate seed-level aggregation, paired intervals and factorial contrast with hand-derived fixtures; save JSON, CSV and compressed full traces.
5. Replay v12, execute the fixed 216 trajectories, create plots from their output and inspect them.
6. Verify primary literature units and novelty; write docs/V13_ACOUSTIC_FEEDBACK_AUDIT_RESULT.md with explicit inference boundaries.
7. Independent code/result review, relevant v12/v13 tests, guarded commit, CI verification and durable artifact delivery.

## Review focus

- A shifted pulse must not shift the random number stream.
- A zero hearing link must erase call contrasts after stimulus ends, while motor memory may persist.
- Bootstrap rows must be seeds, never frames or fish.
- Near-degenerate root multiplicities must not become duplicate equilibria.
- Long-horizon numerical agreement does not establish stationarity or disprove all bistability.

## Execution ledger

- Design choices made by assistant under the user's continuation instruction: new seed set, horizon, warmup time and factorial ablations above; recorded before the new outcomes.
- Remote head verified 609dfac2fdf87fca8767c6836cdb1ce254b71f55, Draft true. Main 47cf12b51553c865027961ae5c162f1b479f5c8c.
- Personal-context retrieval included unrelated projects; the current PR and original v12 artifact define this task's scope.
