# v135 — field interaction casebook and habitat-response contrast

A bounded, source-linked continuation of v133–v134. Reads frozen `validation_v134/results/normalized_study_decisions.json`, `validation_v134/results/reported_numeric_records.csv` and `validation_v133/source_evidence_index.json`. The six-coast interaction casebook is a **curated evidence map, not a systematic representative or meta-admissible subset**. There is no across-coast pooled estimator.

The new calculation is a within-site ratio of Poisson expected counts across beach and mudflat, from Jech & Forys 2023 Table 1, at standardized mean wind. It uses the Cauchy covariance upper bound, ±0.005 printed rounding for each beta and SE, and three-comparison Bonferroni normal critical value. This calculation does not repair original serial dependence/overdispersion or infer actual marked-animal transitions.

Run `python -m unittest discover -s validation_v135 -p 'test_*.py' -v`, then `python validation_v135/source_consistency.py --check`. To regenerate without overwriting frozen inputs, use `python validation_v135/source_consistency.py`; inspect diffs before committing. The checked output `results/meta_feasibility_and_habitat_contrasts.json` is derived from original source-linked ledgers.
