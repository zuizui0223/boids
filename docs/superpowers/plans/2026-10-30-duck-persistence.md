# Duck persistence comparator implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add one exact-yesterday predictor to the unchanged v23 duck forecast and determine whether its multi-day history advantage survives that comparator.

**Architecture:** Import the frozen v23 parser, original sources and prequential predictions. Enrich the existing records with one new squared error and chronology diagnostics; verify the full saved v23 per-bird receipt before releasing any new scores.

**Tech Stack:** Python standard library and existing NumPy; no new dependencies.

**Spec:** `docs/V29_HISTORY_VERSUS_PERSISTENCE_PROTOCOL.md`.

## Global Constraints

- Same-source exploratory extension, not independent replication; previous results were known when this comparator was specified.
- Do not edit any pre-v29 code, result, source gate or protocol.
- MP uses the raw complete day at exactly t−1; never the last eligible event.
- All five predictors score identical original v23 records. Match original counts and per-bird M0/ME/MI/MEI errors at absolute tolerance `1e-12` or stop.
- The primary is MP−MEI; MP−MI is secondary. Report all absolute errors and all declared contrasts, regardless of direction.
- Use 10,000 whole-bird bootstrap draws, seed `20261030`, equal-bird weighting, no tuning.
- Export source hashes and anonymized aggregate errors only; no raw animal coordinates, timestamps, daily target values or original IDs.

## Review Focus

- Gaps in eligibility must not turn t−1 into an earlier event day.
- Same-date values must never enter a history audit or MP predictor.
- Sites with changes must retain the original v23 record and site definition.
- Unequal record counts must not change equal-bird weighting.
- A source or cohort mismatch must stop new reporting, not silently continue.

### Task 1: Exact persistence extension with executable source and receipt gates

**Files:**
- Create `validation_v29/persistence_benchmark.py`.
- Create `validation_v29/test_persistence_benchmark.py`.
- Create `.github/workflows/duck-persistence-v29.yml`.

**Interfaces:**
- Consume v23 `parse_original_gps`, `eligible_daily_events`, `prequential_predictions`, `evaluate`, the original source gates and saved `validation_v23/results/independent_duck_daily_ERA5_forecast_v23.json`.
- Produce `add_persistence(records, events, daily) -> (records, chronology_audit)`, `verify_v23_receipt(records, expected) -> dict`, `summarize(records) -> dict`, and `run() -> dict` plus CLI `--out` (default `validation_v29/results/duck_persistence_v29.json`).
- Optional CLI `--gps-file` may read a locally downloaded original file only after enforcing original byte count, MD5 and SHA256; network default must use the existing v23 download/gates. No custom cohorts or model parameters.

- [ ] Write failing known-truth tests for exact calendar t−1 despite a gap in eligible events; missing raw t−1 raises; input record errors remain identical; current/future events excluded from audit; equal-bird weighting with unequal days; original receipt mismatch raises before new export; aggregate output contains no raw IDs/dates/target values.
- [ ] Observe failures before implementation. Do not assert source-code text or merely mock the numerical routines.
- [ ] Implement the enrichment and audit without reproducing v23 predictor logic. Reuse v23 predictions and evaluation for all four original errors. Audit a date-batched 14-item same-site/bird deque, adding events only after each date is evaluated.
- [ ] Match original `original_independent_ducks`, `original_future_duck_day_targets` and every entry in the saved `per_original_individual_anonymized` representation (inspect the actual receipt key); verify four mean errors and daily counts, and record its SHA256. Fail clearly on a mismatch.
- [ ] Summarize five errors in order M0/ME/MI/MEI/MP per anonymous bird and equal-bird aggregate. Compute primary MP−MEI, secondary MP−MI, descriptive MP−ME and MP−M0 with paired 10,000 resamples, percentile CI, positive count, nonzero count and exact sign-tail probability. Handle zero gains and no records explicitly. Do not multiply independent samples by days or sites.
- [ ] Make the CLI download/reverify original GPS and ERA5 through v23, rerun unchanged original predictions, verify the frozen receipt, then compute/save new aggregates. Include protocol path, source hashes, code base SHA, source QA, support counts, chronology audit, known-source limitation and preservation status. Atomic output write after successful gates.
- [ ] Add a workflow on pull requests touching v29/protocol/workflow plus workflow_dispatch, permissions contents:read, timeout 15 minutes; install NumPy, run v23 and v29 tests separately to avoid generic module-name collisions, run real-source CLI and archive only aggregate JSON. No push-trigger needed because protocol push must not open outcomes.
- [ ] Run `PYTHONPATH=validation_v23:validation_v29 python -m unittest discover -s validation_v29 -p 'test_*.py' -v` and the original v23 suite, then commit only these three code/workflow files. Do not run real-source outcomes or push remotely; the controller handles the observed run after independent review.

## Controller work after Task 1

- Verify the task against this plan and spec with a fresh reviewer, then execute the original-source comparison.
- Save original-source hashes and new anonymous aggregate results, inspect the full declared contrasts, and write `docs/V29_OBSERVED_DUCK_PERSISTENCE_RESULT.md`.
- Consolidate all positive empirical and synthetic results in a source-linked Japanese evidence note, explicitly distinguishing v16/v23/v24/v28 endpoints and preserving failed primary controls.
- Add README links, open a draft PR on the research branch and report the actual verification and observed conclusion. Do not merge without existing explicit authorization.
