# v134 Multi-taxon Screen and IPD Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert the broad source inventory into explicit full-text decisions and exact effects, and execute a source-audited exploratory analysis when original data allow it.

**Architecture:** Keep source acquisition/identity checks separate from full-text judgments and numerical models. Preserve all prior versions and original study identities. The report consumes saved JSON/CSV outputs; independent reviewers inspect original evidence and numerical claims.

**Tech Stack:** Python standard library for source audit and unittest; NumPy/SciPy/pandas/scikit-learn and Matplotlib only where actual numerical analysis requires them.

**Spec:** `docs/V134_MULTITAXON_SCREEN_AND_IPD_SPEC.md`, with a prefit addendum required before any new outcome model.

## Global Constraints

No fabricated observations or covariance; no access-control bypass; no TinyFish or eBird; no third-party messages. Existing v131–v133 files remain unchanged. Original data remain original; no missing intervals become zero behavior. Published additive effects, interactions, and disparate endpoint families remain distinguishable. A short exploratory series does not pass the frozen eight-week confirmatory gate.

## Review Focus

- A valid DOI with no XML body must not become a completed full-text eligibility decision.
- A no-DOI PMID record must be verified against the focal article, not its references.
- Hour zero and naive animal timestamps must not produce an unnoticed one-hour or timezone shift.
- Gaps, all-zero current grid nodes and out-of-range ghost times must not become invented observations or valid slack water.
- Repeated minutes, animals, outcomes and species sharing a coast must not become independent studies or pseudo-precise uncertainty.

## Task 1: Expand and reconcile original-source decisions

**Files:** `validation_v134/source_screen.py`, `validation_v134/test_source_screen.py`, versioned source and full-text ledgers.

**Interfaces:** `select_rescue(corpus) -> list[dict]`; `verify_article(raw, doi=None, pmid=None) -> dict`; CLI consumes the frozen v132 corpus and source cache and writes an access ledger. Curated screen records retain DOI, source SHA256, exact source section/table locators and explicit inclusion reason.

- [x] Write and run failing tests for outcome-independent rescue selection, DOI/PMID mismatch, reference-only identity and empty-body detection.
- [x] Implement minimal source resolution, retained failures and the 46-record rescue pass.
- [x] Integrate the two non-overlapping 43-record full-text screens and verify complete 86-record coverage, no duplicate articles and explicit uncertain decisions.
- [x] Verify newly extracted coefficient/SE/unit records against original tables and distinguish previously audited papers from newly assessed sources.

## Task 2: Audit and analyze accessible original time series

**Files:** `validation_v134/penguin_source.py`, `validation_v134/penguin_analysis.py`, focused tests, source receipts and aggregate results; `docs/V134_PENGUIN_PREFIT_ANALYSIS.md`.

**Interfaces:** Source audit returns original file hashes, schema, coverage and time/cadence evidence. The prefit addendum fixes the numerical interface and units before fitting; an analysis must expose matched rows, held-out units, loss aggregation and all prespecified sensitivities.

- [x] Independently verify complete source files and audit time/effort/current-grid mapping; retain the source-defined UTC mapping qualification.
- [x] Freeze endpoint, sample rules, interpolation, solar terms, ghost shifts and holdouts using source structure only.
- [x] Write failing tests for hour origin, no extrapolation, missing observation support, whole-week separation and animal/week aggregation; implement and verify.
- [x] Run the frozen analysis and sensitivities; report effect sizes, coverage and uncertainty at the actual independent unit. If minimum source gates fail, save the exact failure and do not fit an unsupported model.

## Task 3: Scientific review and delivery

**Files:** `docs/V134_MULTITAXON_FULLTEXT_AND_CURRENT_RESULT_JA.md`, result figure where useful, scoped CI workflow.

- [x] Recompute consequential counts/effects independently and inspect any figure at its rendered size.
- [x] Request a fresh whole-branch scientific and code review; resolve material findings.
- [x] Run focused v131–v134 regression suites and source/analysis replay checks warranted by actual risks.
- [ ] Publish the authorized isolated draft branch/PR stacked on v133, verifying remote tree and CI. Deliver the research result with source citations and limitations.

## Publication checkpoint

This checked-in plan records the verified pre-publication snapshot. The final remote-tree and CI outcome is recorded in the draft PR and execution ledger after publication; the final delivery checkbox remains open in this preparation snapshot.
