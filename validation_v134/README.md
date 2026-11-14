# v134 — Multi-taxon evidence screen and exploratory penguin analysis

This directory contains a bounded expansion of the Boids tide–solar evidence base, source-level numerical extractions, and one reproducible individual-data analysis of Magellanic penguins. **No global pooled effect is estimated.** The evidence ledger, published numerical records, and penguin predictive scores are different deliverables and must retain their original study identities.

## Scope and accounting

The authoritative counts are in [`results/evidence_summary.json`](results/evidence_summary.json), generated from the three saved screening ledgers.

| Quantity | Saved v134 count | Interpretation |
|---|---:|---|
| Distinct article decisions | 118 | 86 articles acquired in v133, plus 32 accessible rescue articles |
| Substantive article bodies available | 117 | One acquired XML lacks a substantive body and remains unresolved |
| Documented substantive fulltext reads | 115 | Body availability and an actual fulltext read are counted separately |
| `FIELD_JOINT_TIDE_DIEL` | 20 | Broad joint-field design/candidate-model evidence category; **not 20 retained joint regression models** |
| `FIELD_TIDE_DIEL_SEPARATE` | 13 | Tide and solar/diel evidence assessed separately, including descriptive comparisons |
| Reported numerical records | 311 | Extracted from 60 articles; includes coefficients, means, intervals and test statistics |
| Global meta-analytic effect | Not estimated | Numerical rows are not independent coast-study units or automatically compatible effects |

The joint category includes spectral classifications, candidate joint models whose selected model is tide-only, and joint temporal filters without a fitted coefficient. Read each record's `joint_model_status`, endpoint, exposure definition and original ledger pointer before counting a fitted joint model or admitting an effect. Joint additive effects are also distinct from tide-by-diel interactions; an unestimated interaction is not a zero interaction.

The frozen metadata corpus contains 1,061 records. The 150 prior field-triage access checks were extended by a prespecified rescue of 46 uncertain records: the original tide and behavior flags were both present, or the title contained a tide/intertidal/circatidal word. Of those 46, 32 yielded identity- and body-verified XML, 11 lacked a PMC XML identifier, and three returned HTTP errors. The resulting 196 targeted access checks leave 865 corpus records outside this bounded pass. This is not an exhaustive completed global systematic review, and independent human two-rater screening/adjudication is not claimed.

## Deliverable map

Paths below are relative to this directory unless they start with `../`.

| Files | Purpose |
|---|---|
| [`fulltext_screen_a.json`](fulltext_screen_a.json), [`fulltext_screen_b.json`](fulltext_screen_b.json), [`rescue_fulltext_screen.json`](rescue_fulltext_screen.json) | Article-level biological decisions, designs, endpoints, tidal and solar definitions, dependence, source locators and uncertainty |
| [`results/normalized_study_decisions.json`](results/normalized_study_decisions.json) | Common decision schema, source-ledger JSON pointers, and explicit non-admission to a pooled effect |
| [`results/reported_numeric_records.csv`](results/reported_numeric_records.csv) | Numerical extraction index; consult the linked ledger for all contrast details and caveats |
| [`results/rescue_access_audit.json`](results/rescue_access_audit.json), [`additional_source_receipts.json`](additional_source_receipts.json), [`rescue_validation_receipt.json`](rescue_validation_receipt.json) | Acquisition, identity, body availability and source receipt records |
| [`published_effect_verification.json`](published_effect_verification.json), [`INDEPENDENT_PUBLISHED_EFFECT_REVIEW.md`](INDEPENDENT_PUBLISHED_EFFECT_REVIEW.md) | Checks against focal original tables and review of effect scales, uncertainty, dependence and field-oyster classification |
| [`penguin_original_source_audit.json`](penguin_original_source_audit.json), [`results/penguin_analysis_source_audit.json`](results/penguin_analysis_source_audit.json) | Original data lineage, hashes, schema, clock qualifications, observed denominators and current joins |
| [`results/penguin_15min_matched_inputs.csv.gz`](results/penguin_15min_matched_inputs.csv.gz) | Redistributed, source-matched derived inputs for replay: 1,379,867 bytes, approximately 1.38 MB |
| [`results/penguin_analysis_results.json`](results/penguin_analysis_results.json), [`results/penguin_primary_animal_week_scores.csv`](results/penguin_primary_animal_week_scores.csv) | Complete exploratory scenarios, held-out scores and conditional animal-cluster intervals |
| [`penguin_independent_verification.json`](penguin_independent_verification.json), [`penguin_independent_refit.json`](penguin_independent_refit.json), [`penguin_independent_minute_verification.json`](penguin_independent_minute_verification.json) | Independent source aggregation, interpolation, scoring and optimizer checks; the reports state which implementation components were reused |
| [`penguin_conditional_solar_coverage.json`](penguin_conditional_solar_coverage.json), [`penguin_exposure_approximation.json`](penguin_exposure_approximation.json), [`INDEPENDENT_NUMERICAL_REVIEW.md`](INDEPENDENT_NUMERICAL_REVIEW.md) | Solar-coverage qualification, mean-location exposure approximation, shifted-speed similarity and scientific interpretation limits |
| [`fish_longterm_source_audit.json`](fish_longterm_source_audit.json), [`fish_longterm_data_profiles.json`](fish_longterm_data_profiles.json), [`fishway_raw_inventory.json`](fishway_raw_inventory.json), [`kelp_raw_inventory.json`](kelp_raw_inventory.json) | Further raw-data feasibility audits; acquisition does not imply an admissible new outcome model |
| [`figures/penguin_current_diel_validation.png`](figures/penguin_current_diel_validation.png), [`figures/penguin_current_diel_validation.svg`](figures/penguin_current_diel_validation.svg) | Exportable comparison of actual and shifted current models, simple baselines, and prespecified sensitivities |
| [`../docs/V134_MULTITAXON_SCREEN_AND_IPD_SPEC.md`](../docs/V134_MULTITAXON_SCREEN_AND_IPD_SPEC.md), [`../docs/V134_PENGUIN_PREFIT_ANALYSIS.md`](../docs/V134_PENGUIN_PREFIT_ANALYSIS.md), [`../docs/V134_POSTFIT_DIAGNOSTIC_LOG.md`](../docs/V134_POSTFIT_DIAGNOSTIC_LOG.md) | Frozen scope, prefit analysis choices and the explicitly postfit diagnostic/fix record |

The original v131 confirmation rules remain in [`../docs/V131_FROZEN_GLOBAL_TIDE_SOLAR_META_PROTOCOL.md`](../docs/V131_FROZEN_GLOBAL_TIDE_SOLAR_META_PROTOCOL.md). A source hash or a successful access check establishes provenance, not ecological eligibility or statistical compatibility.

## What the penguin result means

The primary response is the **share of actually observed seconds with pressure-derived depth greater than 2 m** in a 15-minute bin. It is submergence, not prey capture, foraging success, or energetic benefit. The analysis uses 27 animals from one colony/coast and one trip per animal. After observed-coverage, common-support and conservative current-grid masks, the primary sample has 3,334 bins and 3,000,423 observed seconds. Missing seconds are not filled with zero behavior.

The original animal `Timestamp` has no encoded timezone. UTC localization follows author metadata for a differently named `DateTime` field and is therefore a **conditional clock interpretation**, not an independently established timestamp fact. The current grid has an explicit GMT origin. Prespecified −3 h and +3 h animal-clock sensitivities are retained; an outcome-favored timezone is not selected.

Only two local calendar weeks are available. Each entire week is held out and predicted from the other, with five animals shared between folds. This is an exploratory mixture of temporal and animal generalization, not leave-animal-out validation. The frozen **at-least-eight-weeks confirmation gate is unmet** despite the animal and window counts. Conditional animal-cluster intervals hold these two weeks and fitted models fixed; they are not refit-bootstrap intervals, independent-week uncertainty, or meta-analysis standard errors.

The saved primary cross-entropies illustrate why relative model improvement must not be described as useful tide-specific prediction:

| Model or diagnostic | Held-out cross-entropy, nats; lower is better |
|---|---:|
| Fixed probability 0.5, postfit diagnostic | 0.693147 |
| Training-only animal-balanced prevalence, postfit diagnostic | 0.706177 |
| M0: clock, animal, space and other controls | 0.804310 |
| M1: M0 plus solar variables | 0.808294 |
| M2: M1 plus actual modeled current speed | 0.771751 |
| Best shifted-current comparator, −12 h | 0.770989 |

Actual current improves on M1 by about 0.036543 nats, but ranks third among nine clocks and performs slightly worse than the best shifted comparator. **All primary fitted models perform worse than both simple postfit baselines.** The baselines were added to diagnose calibration after the first fit; they did not change the prefit models, settings or holdouts.

The “ghost” controls use the same recorded positions and original current field at prespecified time shifts. Scalar current speeds at −6/+6 h correlate approximately 0.991 with real speed, and at −12/+12 h approximately 0.966–0.968. They are near-equivalent speed exposures, not independent datasets. Failure to distinguish their clocks cannot establish absence of tidal influence; selecting the best shift on held-out scores is not a randomization test or an unbiased selected-model performance estimate. The analysis concerns scalar-speed prediction and does not reproduce the paper's directional navigation analysis.

## Reproduce from the repository root

Use Python with the versions allowed by [`requirements.txt`](requirements.txt). All commands below run from the **repository root**, not from `validation_v134/`. Replace `/path/to/...` placeholders with your own external caches/output directories. Historical receipts may contain acquisition-machine paths; those paths are provenance, not required runtime locations.

```bash
python -m pip install -r validation_v134/requirements.txt
python -m unittest discover -s validation_v134 -p 'test_*.py' -v
```

### 1. Compile the saved evidence ledgers

```bash
python -m validation_v134.compile_evidence
python -m validation_v134.verify_saved_results
```

The compiler regenerates the three canonical evidence outputs in `validation_v134/results/`: `evidence_summary.json`, `normalized_study_decisions.json`, and `reported_numeric_records.csv`. It reconciles saved judgments and rejects duplicate DOI inflation; it does not repeat the substantive reading or create compatible meta-analytic effects. The saved-results verifier checks the packaged outputs and their internal consistency; it is distinct from checking external original XML.

### 2. Replay the penguin analysis from packaged derived inputs

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m validation_v134.penguin_analysis \
  --prepared validation_v134/results/penguin_15min_matched_inputs.csv.gz \
  --output-directory /path/to/v134-replay

python -m validation_v134.verify_saved_results \
  --replay-directory /path/to/v134-replay
```

This reruns the primary model, all prespecified sensitivities, postfit baseline diagnostics, and conditional intervals from the exact serialized matched inputs. It writes results and animal/week scores to the selected output directory. It does not rebuild the source joins or independently verify the approximately 932 MB of original observations and current data. Small numerical differences may arise across numerical-library versions; use the verifier's stated comparisons rather than requiring text-identical JSON.

### 3. Rebuild from the two complete original penguin files

Obtain the exact versions below, keeping their original filenames in one directory. The versioned deposit is [Figshare 10.6084/m9.figshare.28517873.v1](https://doi.org/10.6084/m9.figshare.28517873.v1).

```bash
V134_ORIGINALS="/path/to/penguin-originals"
mkdir -p "$V134_ORIGINALS"

curl --fail --location \
  https://ndownloader.figshare.com/files/52709456 \
  --output "$V134_ORIGINALS/Penguins.csv"

curl --fail --location \
  https://ndownloader.figshare.com/files/52709309 \
  --output "$V134_ORIGINALS/Ocean_Currents.csv"

OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m validation_v134.penguin_analysis \
  --source-directory "$V134_ORIGINALS" \
  --output-directory /path/to/v134-full-rebuild

python -m validation_v134.verify_saved_results \
  --replay-directory /path/to/v134-full-rebuild
```

`penguin_source.py` is the source-processing module invoked by this command, not a separate acquisition CLI. Before processing, it checks byte count, MD5 and SHA256 against the frozen original-file receipts. It then removes only verified exact duplicate rows, rejects conflicting animal/time duplicates, aggregates observed seconds, reconstructs source-matched current exposures, serializes the derived inputs and analyzes those serialized inputs. A rebuild also writes `penguin_analysis_source_audit.json`. Complete downloads and more memory than the compressed replay requires are necessary; truncated previews or similarly named replacement datasets are not acceptable inputs.

### 4. Check published effects against original XML

Use a cache containing the v133 original XML and a separate cache containing the v134 rescue XML, each named by PMCID.

```bash
python -m validation_v134.verify_published_sources \
  --fulltext-cache /path/to/v133-fulltexts \
  --rescue-cache /path/to/v134-rescue \
  --output /path/to/published-source-verification.json

python -m validation_v134.verify_saved_results \
  --fulltext-cache /path/to/v133-fulltexts \
  --rescue-cache /path/to/v134-rescue
```

`verify_published_sources.py` replays the specified comparisons against seven focal original articles. Its optional `--download` mode requires **empty or absent cache directories** and retrieves only those seven official Europe PMC XML sources; it does not fetch raw animal data. Use fresh directories for that mode:

```bash
python -m validation_v134.verify_published_sources \
  --fulltext-cache /path/to/new-empty/fulltexts \
  --rescue-cache /path/to/new-empty/rescue \
  --output /path/to/fresh-published-source-verification.json \
  --download
```

The saved-results verifier never downloads sources. These checks do not turn all 311 numerical records into independently adjudicated, compatible effect sizes. Preserve disclosed source-hash changes, numerical discrepancies and acquisition failures instead of replacing the frozen evidence silently.

### 5. Repeat the fixed-rule rescue access check

Supply the archived frozen v132 corpus JSON whose hash is recorded in `results/rescue_access_audit.json`:

```bash
python -m validation_v134.source_screen \
  --corpus /path/to/frozen-v132-corpus.json \
  --cache /path/to/v134-rescue \
  --output /path/to/rescue-access-audit.json \
  --workers 4
```

This selects candidates without using effect direction/significance or access success, and checks focal article identity and body availability. It does **not** regenerate manual ecological decisions. A new network run can differ in availability; retain its retrieval date and compare it with the saved audit instead of treating live access as the frozen result.

### 6. Render the saved comparison figure

```bash
python -m validation_v134.plot_results
```

The plotter reads the canonical `validation_v134/results/penguin_analysis_results.json` and writes the PNG/SVG in `validation_v134/figures/`. It has no replay-directory argument; running a replay into an external directory does not automatically change the plotted canonical results.

## Licenses, attribution and source boundaries

The penguin source is **Gunner et al. (2025), “Penguins exploit tidal currents for efficient navigation and opportunistic foraging,” [DOI 10.1371/journal.pbio.3002981](https://doi.org/10.1371/journal.pbio.3002981)**, with original data at **[Figshare 10.6084/m9.figshare.28517873.v1](https://doi.org/10.6084/m9.figshare.28517873.v1)** under **[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)**. Preserve this attribution and license when redistributing the supplied derived penguin inputs. Boids modifications include duplicate handling, observed-second aggregation, clock interpretation, current interpolation and masking, derived solar/current features, and the new exploratory predictive analysis. These outputs are not the authors' original navigation-effect estimates.

The approximately **1.38 MB derived 15-minute input** is included for reproducibility. The two complete original CSVs total 931,713,396 bytes, approximately **932 MB**, and are **not tracked in this repository**. Their public URLs and integrity hashes are retained so a complete source rebuild remains possible.

The audited 4TU fish archive is **CC BY-NC-ND**; its originals are **not redistributed here**. This directory preserves source/provenance and feasibility summaries. Its missing receiver uptime/zero-observation history blocks an aggregate count model: silent intervals must not be fabricated as observed zeros. The fishway audit separately records explicit observed zeros but also two pairs of identical full-day tide columns across years; that discrepancy remains unresolved. Other raw-data leads and supplements retain their individual source licenses and access restrictions; they are not covered by a blanket penguin-data license.

Finally, no published SE is invented from an omitted interaction or omnibus p-value, no unavailable covariance is assumed zero for a derived contrast, and multiple species, endpoints, bins or clock settings are not counted as independent coast studies. These constraints explain why a larger, traceable evidence base is delivered without a global pooled result.
