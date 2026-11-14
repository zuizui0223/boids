# v133 Full-text and Effect Extraction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert the existing global bibliography into an auditable full-text/source ledger and actual compatible effect records.

**Architecture:** Preserve frozen v131/v132. A new source-audit program verifies DOI linkage and records original source status; a separate calculation program handles published odds ratios and uncertainty of dependent contrasts. The report consumes saved aggregate outputs.

**Tech Stack:** Python standard library for retrieval, XML/DOCX/JSON and tests; existing runtime plotting only if a figure improves interpretation.

**Spec:** `docs/V133_FULLTEXT_EXTRACTION_AND_ESTIMAND_SPEC.md`

## Global constraints

No invented original records, no outcome filling, no pooling different estimands, no counting repeated sites/contrasts as independent. Full-text acquisition is not eligibility or biological replication. Do not use TinyFish or bypass source protections. Existing source and result files remain unchanged.

## Task 1: Verify original literature and retrieve full-text sources

**Files:** Create `validation_v133/fulltext_audit.py`, `validation_v133/test_fulltext_audit.py`, and aggregate result JSON.

**Interfaces:** `select_candidates(corpus)` returns the original field-candidate rows; `summarize_xml(bytes, expected_doi)` verifies and summarizes a primary XML record. CLI accepts the original v132 corpus and a scratch cache.

- [ ] Write tests that catch accidental inclusion of unrelated candidates, mismatched DOI, and mistaking reference-only tide mentions for article evidence.
- [ ] Run the tests and observe failure before implementation.
- [ ] Implement metadata resolution, source-preserving retrieval and table/data locators; preserve transport failures as distinct statuses.
- [ ] Run tests and the actual 150-record source audit. Expected: one status per selected record, no pooled effect.
- [ ] Commit source audit and aggregate receipts.

## Task 2: Compute source-derived interaction and source fitness

**Files:** Create `validation_v133/effect_extraction.py`, `validation_v133/test_effect_extraction.py`, versioned ledgers and calculated result JSON.

**Interfaces:** `contrast_difference(a, b, covariance=None)` returns difference and exact or bounded SE; source-effects retain their metadata and dependence.

- [ ] Write tests for sign/orientation, covariance limits, independent versus unknown covariance, mixed estimands, and source-only camera counts.
- [ ] Run tests and observe failure before implementation.
- [ ] Integrate exact independently extracted supplement rows; reproduce selected values directly from DOCX XML and original source bytes.
- [ ] Run numerical calculations and original-data source summaries. Expected: source effects with traceable uncertainty, no manufactured global pooling.
- [ ] Commit calculations and receipts.

## Task 3: Review and deliver research result

**Files:** Create `docs/V133_FULLTEXT_AND_QUANTITATIVE_TIDE_DIEL_RESULT_JA.md` and scoped CI workflow.

- [ ] Review saved outputs against original sources and check key calculations independently.
- [ ] Request an independent review of the new source and effect code plus scientific claims; fix material issues.
- [ ] Run the v131, v132 and v133 suites and check the actual outputs.
- [ ] Publish the isolated draft branch/PR with exact scope and remaining evidence gaps.

## Review focus

Unknown covariance must not become independence; an additive-model interaction is not an observed zero; camera positivity is not monitoring effort; original sources and article/table metadata must match; numerical extraction rows are not independent study counts.
