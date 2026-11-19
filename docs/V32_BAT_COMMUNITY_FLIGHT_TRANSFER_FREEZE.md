# v32 — Cross-site and cross-species transfer of bat community-context flight rules

**Freeze:** 2026-11-19 JST, BEFORE opening any numerical mean flight-speed / feeding-buzz outcomes.  
**Evidence class:** independent published observational data, *new analysis of existing 2025 source*, not independent replication of that article's own mechanism.  
**Repo:** \`zuizui0223/boids\` on a new research branch, separate from active sensory-gaze PR #213 and frozen \`batter\`.

## 1. Motivation and prior art

Delmotte et al. (2025), *Behavioral Ecology*, DOI 10.1093/beheco/araf090, already reported that bat speed–foraging coupling changes in the presence of intra-guild heterospecifics and that activity can increase with others. Merely reestimating this coefficient is **not a novel ecological result**.

The new, falsifiable question is whether a **community-conditioned speed–foraging association** learned in one species/site predicts feeding activity in **previously unobserved sites and species**, beyond source-specific baseline speed, habitat, species/guild and effort.

**Prior published authors' Dryad:** [10.5061/dryad.6q573n6b0](https://doi.org/10.5061/dryad.6q573n6b0), published 2025-08-27, CC0. Author README states \`data.csv\` is **one row per detected flight trajectory**, not per identifiable bat. Dataset from **one geographic area**, Rhône Valley, France, September 21–30, 2022. Published authors' R code \`R_file.R\` available. Original data.csv source file ID 4258753 according to official landing page. File size displayed 235.74 KB.

## 2. Evidence boundaries

- Dataset records are trajectory **summaries**, not synchronized 3-D turn-by-turn raw GPS, independent individual histories, experimental manipulations, or measured prey abundance.
- \`meanBuzz\` is the trajectory-average feeding-buzz score, **not a measured capture success, intake or energy balance**.
- \`meanVfinal\` is trajectory-average flight speed contemporaneous with \`meanBuzz\`; the intended task is **cross-sectional transfer of a statistical relationship**, **NOT forward-time prediction**.
- Co-occurrence of species is observational and may reflect resource density, detection, habitat, time or spatial colocation; not causally randomized. Verify how flags are defined. Do not claim direct aggression/cooperation, competition or facilitation.
- Five focal species and 16 sites are not five independent phylogenetic radiations or 16 independent geographical regions. Intra-site rows are pseudoreplicates for site generality. Source author analyses are prior art.
- Absence of individual bat IDs means individual-based crossfold and memory/learning cannot be tested.

## 3. Original source structural admission gate — without outcomes

Freeze before reading numerical \`meanBuzz\` or \`meanVfinal\`:
1. Read only official Dryad version/page metadata and source file headers. Download via the official pinned file endpoint when public, checksum and record source byte count. Never silently switch datasets or version.
2. Parse CSV delimiter/decimal locale by a fixed rule: semicolon if header includes \`;\`, otherwise comma if header includes \`,\`, otherwise tab; numeric value parser converts French comma decimals only *after* the model protocol is fixed.
3. Count full rows, distinct \`IdTraj\`, \`id_site\`, \`Species_corrected\`, \`guild\`, categorical co-occurrence columns, missing/nonmissing structural fields, and site×species / species×context support. Do not read/log numeric speed or buzz values in this step.
4. Confirm that co-occurrence labels include \`Conspecific_sp\`, \`Heterospecific_intraMRE\`, \`Heterospecific_inter_nonMRE\`. Confirm habitat columns \`dist_Eau\`, \`dist_Lisiere\`, \`foret_500\`, effort \`traj_length\`, and response \`meanBuzz\`, \`meanVfinal\`.
5. No duplicates under \`id_site\`×\`IdTraj\` in the original dataset. If duplicates, stop pending declared observational grain (do not silently drop).
6. Structural admission for a site-transfer primary requires at least **8 sites**, **4 focal species**, **300 usable trajectory rows**, **6 sites with >=10 usable rows**, and both 0/1 values for at least one co-occurrence category on the pooled sample. A usable row has nonmissing model and target fields, with *only missingness* opened in structural gate.
7. Stop as \`SOURCE_ACCESS_STOP\`, \`SCHEMA_STOP\`, \`GRAIN_STOP\`, or \`SUPPORT_STOP\` without fitting if source/structure fails. Record complete coverage; do not lower gates after looking at outcomes.

## 4. Competing predictions for held-out sites

**M0 (baseline):** pooled global intercept + log1p source-supplied trajectory duration, continuous source habitat fields (\`dist_Eau\`, \`dist_Lisiere\`, \`foret_500\`), species one-hot (ignore unseen), guild one-hot (ignore unseen), and mean flight speed; training-only imputation and scaling. Source-specific \`id_site\` is never a feature because entire sites are withheld.

**M1 (community rules):** M0 + \`Conspecific_sp\`, \`Heterospecific_intraMRE\`, \`Heterospecific_inter_nonMRE\`, and their three **predefined interactions with mean speed** (centered using training-only mean). No arbitrary species-specific interaction search.

**Primary endpoint:** \`meanBuzz\` (original trajectory-averaged score). Report equal-site MSE(M0)-MSE(M1) using **leave-one-site-out** fully held-out predictions, for identical rows/folds and fixed \`Ridge(alpha=10)\` with train-only median imputation, continuous standardization, and category one-hot. No feature selection or hyperparameter search.

**Decision:** retain signed per-site gains, equal-site mean gain, 10,000 deterministic whole-site bootstrap 95% interval, and exact positive-site sign test. A positive generalizable site-transfer effect requires mean gain >0, site-bootstrap lower 95% >0 and one-sided site-sign p<=0.05. If any fail: primary NOT_SUPPORTED. One source region remains the inference ceiling even if all pass.

**Secondary:** leave-one-focal-species-out transfer to remaining source species using identical model pipeline (species unknown level ignored), equal-species estimates and uncertainty clearly labelled as low-power exploratory; conditional \`meanBuzz\`–speed slope by context estimated strictly in training folds, not as a causal effect. Predefine but do not retool primary based on species results.

## 5. Interpretability and leakage

- Co-occurrence indicators may be assigned from the *same detection period* as the flight and might depend on future recording windows; no prospective behavioral forecasting or causal response claim.
- Buzz and flight-speed averages derive from the same acoustic data stream, not independent instruments; correlated observation errors are possible.
- Do not use \`maxBuzz\`, \`minBuzz\`, any postprocessed \`meanBuzz\` derivative or other source target-derived feature to predict \`meanBuzz\`.
- Train-only fill/scale/encode, **no** all-data normalization, split by original site before transformation; source and site labels are not independent species populations.
- If a site/species category is absent from training, holdout receives the declared unknown-category representation; do not drop difficult holdouts.
- A result that only reproduces the original authors' association, without held-out site gain, is not a new universal rule. Before any universal claim seek an independent **non–Rhône region** and a stronger comparable observational design.
- Contrasts are prediction scores, not an inference of social-information sharing, resource causality or learned flight motor policy.

## 6. Prior-result separation

- \`batter\` observational vertical individual-shape findings are unchanged.
- \`boids\` v30 original \`Carollia\` acoustic-increment result remains negative, with no reinterpretation.
- No combination of incompatible original azimuth, future-heading and trajectory-mean buzz endpoints into one pooled effect size.

**Current state at freeze:** proposed prediction and admission rules; numerical meanBuzz and meanVfinal unopened in this programme.
