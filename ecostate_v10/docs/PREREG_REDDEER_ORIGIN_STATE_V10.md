# Ecological-state persistence in red deer: original-source independent validation v10

**Registered 2026-11-16 (before opening Dryad data_for_model.rds numeric responses).** Independent of earlier polar-bear v9 and the same historical boids/louis observational cohorts. Source: van Beeck Calkoen et al. (2026), Ecosphere DOI 10.1002/ecs2.70756, original Dryad DOI 10.5061/dryad.b8gtht7tf.

## Question and original novelty ceiling

A deer that begins a step in one understory/overstory cover state may select a destination resembling the starting state *more than expected given destination habitat selection, movement geometry and environmental risk*.

The original publication already reported day/hunting effects on understory, visitor avoidance and trail crossing; those are **not new**. The new test would quantify origin-conditioned retention on *whole-identity holdouts* while keeping each step's original available destinations. It is **NOT** a causal movement, learning, risk/perceived refugia, or niche-generalization claim.

## Input admission before outcome access

The original Dryad published dataset documents 2,041,891 candidate rows, 18 columns, a source `id`, `step_id_`, `case_` (used vs alternatives), `t1_`, `sl_`, `trail.cross`, `understory_start/end`, `overstory_start/end`, `dist_end`, `n.visitors_end`, `nohunting`, `tod_end_`, `dem`, `TRI` and other fields. The original paper reports **27 female deer and 178,698 steps** in its analyses, but do not equate those published counts with eligible candidate sets before inspecting original source structure.

Stop if original bytes cannot be obtained through standard public Dryad URLs, source hashes do not match provider, actual source has inconsistent step strata (other than fully documented exclusions), source IDs cannot be separated, or fewer than 15 deer have 50 complete strata each. One unique used alternative is required per complete `id` × `step_id_` and >=5 total alternatives including used; within-stratum fixed starting cover/time/zone must match exactly or within numerical tolerance specified before inspection (1e-6). Do not join rows by order or invent missing start covariates. Original step strata crossing deer IDs remain distinct. No post-effect model changes.

## Matched choice models (same response/steps)

M0 destination-preference model includes `log1p(sl_)`, `sl_`, `trail.cross`, understory_end, overstory_end, `log1p(dist_end)`, `log1p(n.visitors_end)`, `dem`, `TRI`, and a specified set of day/night and hunting interactions with end cover/risk terms (not main effects constant within strata). No arbitrary post-outcome transformations of endpoints. Train-only normalization, matching source alternatives per `id × step_id_` and equal-individual total training influence.

M1 adds exactly 2 continuous source-to-destination divergence terms:

- `abs(understory_end - understory_start)`
- `abs(overstory_end - overstory_start)`

Positive held-out log-score gain `M0 − M1` tests added information from **source-state similarity** beyond global destination selection. Negative coefficients on divergence may be interpreted as predictive state fidelity; nonnegative or inconsistent effects fail the stricter ecological sign gate. This does not establish optimizing habitat-condition stability or competition.

**Independence:** hold out entire original deer IDs in five source-ID-only hashed folds, maintaining source-defined time/strata. Fit fixed conditional softmax with L2 regularization, no tuning on test deer. Score one average log likelihood per deer; equal-weight deer means and 10,000 entire-deer bootstrap 95% intervals. Require CI lower >0 and >60% independent deer positive (primary effect), and within-model negative divergence direction for both added terms (strict biological gate). Report all failure states. Optional day-vs-night interactions are secondary and cannot rescue a negative primary.

**Crucial interpretation:** Even a successful M1 can reflect local spatial autocorrelation, different start-state neighborhoods, or missing destination-risk predictors—not proven behavioral desire to maintain state. Further independent spatial-block or directly measured reachable-state surfaces would be needed. Source random endpoints are not necessarily physically reachable alternatives after accounting for roads/trails; their kernel is an availability model, not measured capabilities.

## Source-only execution contract

Initial `source_gate_v10.py` checks official metadata, official version/file list and only `HEAD` public status of the exact named RDS. It does **not** read the RDS data or calculate a biological result. If Dryad presents HTTP401/403 or no listed downloadable file, record this as a source-access stop. Do not use unofficial mirrors to evade authorization. No source access status can be called a biological null.
