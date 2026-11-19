# v37 pre-outcome contract — macro bat morphology-to-movement transportability

**Frozen 2026-11-19 JST before any original numeric \`Dist\`, \`MCP\`, \`Mass\`, \`Forearm\` or habitat effects are opened for modeling.**

Source: Laforge et al. 2021/22 original Zenodo 5794471 / Dryad 10.5061/dryad.qnk98sfhh, exact MD5-verified \`Meta_data_bat_home_ranges.csv\`. v35 source shows 2,043 metadata rows; v36 pre-outcome audit finds 138 \`Authors×Year_pub×Journal\` candidate publication groups, 20 raw country labels, 53 raw species labels. Only 122 source rows have valid lat/long, so the source landscape table **cannot be joined under the fixed 1 km/second-nearest 3 km test**. No landscape variables may be introduced.

## New predictive question, beyond the published original effects

Does a **morphological scaling representation** of bat movement (\`Mass\`, \`Forearm\`) fitted to other publications improve prediction of a *new entire publication*, a *new country*, or a *new raw species label*, relative to a fixed global-population baseline?

The original article already estimated mass, morphology and habitat effects in in-sample mixed models; those effects are **prior art**, not discoveries of v37. The new object is *out-of-source predictive transfer*. The source measures reported summary movement metrics, **not** individual action switching, lifetime memory, actual 3D flypath, or cognitive foraging choice.

## One primary endpoint, fixed before outcome

Primary response: source numeric \`Dist\` (published roost-to-foraging-distance summary in source units), transformed \`y=log1p(Dist)\`. Drop target rows only when missing/nonfinite/negative, and report every exclusion. No imputation or transformation of \`Dist\` from other endpoints. \`MCP\` home-range is an independently predeclared **secondary only** with the *same* models/heldout approach; report failure as failure.

Study publication group: all rows with the same original \`Authors\`, \`Year_pub\`, \`Journal\` are held out together. This is a *candidate conservative paper key*, not proof every underlying study has a unique key. The 2,043 records are **not 2,043 biological individuals**.

## Frozen predictors and models

- Identical target rows across M0 and M1.
- **M0:** all-training-source mean of \`log1p(Dist)\`, using weight = 1 / number of eligible records per candidate publication (so one large paper does not dominate). This is an intercept-only model.
- **M1:** M0 + two prespecified morphology variables \`log1p(Mass)\` and \`log1p(Forearm)\` (strictly positive finite original source values). Missing morphology is represented by train-only median imputation **plus two missingness indicators**. Train-only standardization, fixed Ridge L2 alpha=10, and **the same paper-equal training weights** as M0. No country, species, author, publication year, roost, landscape or outcome-derived features are allowed in M1.
- Future value prediction is inverse-target-transformable to source distance units, but signed primary scoring is MSE on log1p-source-distance scale.
- **Primary holdout:** leave-entire-candidate-publication-key-out (each test publication gets equal weight in final average; score within paper first, then average across papers). This is out-of-publication retrospective transfer, **not forward chronology**.
- **Secondary holdout 1:** leave-one-country-label-out, equal-country score (requires >=5 countries with >=10 eligible test records). Any candidate publication containing a withheld-country record is entirely removed from training, even if some of its rows belong to another country; this prevents publication overlap in a country holdout.
- **Secondary holdout 2:** leave-one-raw-species-label-out, equal-label score (requires >=10 labels with >=10 test records). Any candidate publication containing the withheld raw species label is entirely excluded from training even when it also reports other taxa. Raw labels are not canonical species; taxonomy and phylogenetic independence are not resolved.
- **No tuning:** no hyperparameter search, degree changes, filter sweeps or post-outcome favorable species/country selection. Two morphologic fields are the complete candidate mechanism family.

## Source-only eligibility before model fitting

For primary \`Dist\`, require at least **100 eligible target rows**, **20 independent candidate paper keys**, **5 raw country labels**, and **8 raw species labels**. If not, stop before fitting and record \`STRUCTURAL_SUPPORT_STOP\`. If \`Mass\` and \`Forearm\` each have fewer than **20 positive values** among eligible rows, stop with \`MORPHOLOGY_UNOBSERVABLE_STOP\` rather than fabricate a scale. A secondary MCP fit requires the *same* gate; it may fail without invalidating the Dist primary.

## Predictions and interpretation

**H1, transferable allometry:** M1 outperforms M0 across whole-paper holdouts, and signs are concordant on country and raw species holdouts (these latter are only secondary). The counter-hypothesis is that morphology has little transferable information once source heterogeneity and study clustering are respected.

Report per-paper signed gain, equal-paper MSE delta (MSE_M0 - MSE_M1), 10,000 deterministic **whole-paper** bootstrap 95% interval (seed 20261119), number of positive paper groups, exact one-sided sign-test p (numerical underflow-safe), plus secondary country/species outcomes regardless of sign. Primary positive confirmation requires gain >0, lower bootstrap >0, and sign p<=0.05. **Do not** claim universality from the mean effect alone.

Any discovery is restricted to compiled North American/European temperate bat telemetry and source publication grain. It cannot establish social learning, individual route re-use, or 3D niche stratification. No bat home locations/coordinates or original individual records may be exported in public results.

**Source outcome values opened only by the exact frozen script + CI after this contract.** Preserve negative primary without retuning; the v34 failed source join and v30 negative Carollia outcome remain unchanged.
