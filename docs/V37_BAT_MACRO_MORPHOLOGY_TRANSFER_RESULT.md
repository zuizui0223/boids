# v37 result — morphology-only prediction did NOT transport across published bat telemetry studies

**Completed:** 2026-11-19 JST. **Original workflow:** [GitHub Actions 44456589820](https://github.com/zuizui0223/boids/actions/runs/44456589820), all six preregistered synthetic group/leakage regression tests PASS. The original 2022 Zenodo meta CSV was re-downloaded and exact MD5 verified before all scores. Frozen model contract: [v37](V37_BAT_MACRO_MORPHOLOGY_TRANSFER_FREEZE.md). Original paper by Laforge et al. already established in-sample morphology/habitat associations.

## Source and independence

- Original published dataset DOI \`10.5061/dryad.qnk98sfhh\`, Zenodo 5794471; verified original \`Meta_data_bat_home_ranges.csv\` 2,043 rows.
- \`Authors×Year_pub×Journal\` candidate keys — NOT 166 independently verified canonical paper identifiers — were grouped entirely in each primary holdout.
- The v36 landscape site join remains STOP (82 of 122 parseable rows uniquely mapped, below predeclared 80%; 40 ambiguous; too few matched paper keys). No habitat/landscape features used.
- Published paper sample is 166 studies / 3,129 tagged individuals / 49 curated species / 22 countries; evaluated original-file support **differs** from those counts.

## Frozen primary: distance (source \`Dist\`)

Original complete target: **370 rows**, **54 candidate publication groups**, **13 raw country labels**, **36 raw species labels**; 1,673 excluded target rows because distance was missing, nonfinite or negative. Morphology observed in 122 target rows for positive Mass, 59 for positive Forearm. Both variables were train-only imputed and labelled missing when absent.

| Study-equal predictive comparison | MSE on log1p-source-distance | Improvement |
| --- | ---: | ---: |
| M0 — training-only paper-weighted population mean | **1.983131** | reference |
| M1 — M0 + log mass, log forearm, missing indicators, frozen Ridge(10) | **2.010143** | **−0.027012** |

- Whole-paper bootstrap (10,000): **95% [−0.090615,+0.036450]**.
- Positive paper groups **28/54**, exact one-sided positive sign p = **0.445962**.
- Predeclared positive gate **FAIL**.
- This is **no evidence of a portable morphology-only forecast increment** over pooled mean across original study summaries; it is NOT proof morphology has no ecological effects.

### Independently heldout geographic and taxon boundaries (secondary)

| Holdout | Independent evaluation groups | Signed morphology gain | 95% group bootstrap | Positive groups | Positive-direction sign p |
| --- | ---: | ---: | --- | ---: | ---: |
| Country | 7 qualifying raw country labels | −0.031349 | [−0.084479,+0.020244] | 2/7 | 0.9375 |
| Raw species label | 11 qualifying labels | −0.142060 | [−0.294657,−0.010603] | 3/11 | 0.967285 |

In these secondary tests, **any publication containing the withheld country/species label was removed from the training sample**, preventing same-paper identity leakage. The raw species labels are not phylogenetically harmonized. Although the species-group bootstrap interval is negative, this is a declared **secondary** contrast; no new negative scientific universal law is established from this one heterogeneous compilation.

## Frozen secondary endpoint: home-range area MCP

- Original positive target support: **785 rows**, 83 candidate paper groups, 16 country labels, 45 raw species labels. Morphological positive support: Mass 202, Forearm 120.
- M0 MSE **5.953034**; M1 MSE **5.768259**; apparent improvement **+0.184776**.
- Whole-paper bootstrap **95% [−0.169057,+0.584489]**, positive groups **32/83**; one-sided positive sign p **0.986233**.
- **Not supported** under frozen rules, even though the mean metric is positive.
- Country secondary: 11 groups, improvement −0.136078 [−0.331572,+0.037132], 5/11 positive.
- Species secondary: 24 raw labels, improvement −0.013084 [−0.197396,+0.219743], 4/24 positive.

## Interpretation and strict limitations

1. **Model transportability is a stronger question than an in-sample ecological association.** A stable positive regression coefficient within an original analysis does not guarantee prediction in a new independent paper/country/species.
2. This compiled source is strongly **missingness-constrained**: only 59/370 distance-record rows contain usable Forearm, and 122/370 usable Mass. The failed forecast must not be generalized to the proposition that morphology can never predict behavior in a richer, calibrated source.
3. Distance \`Dist\` and MCP are published literature summary variables, not new per-fix flight observations. Candidate paper labels may merge multiple real publications or split bibliographically inconsistent citations. Source countries/species within the 370-row primary represent temperate regions only; not global bat fauna. Target units, measurement methodology and covariate definitions remain heterogeneous.
4. The tested body mass+forearm representation is not wing loading/aspect ratio. It is not a rigorous test of all flight morphology, a resource-mediated mechanism, social interaction or individual memory.
5. No exploration/sit-and-wait action switch, sensory input, 3-D niche or animal-level causal response was measured by this source. **No universal behavior law is established.**

## Prospective next discriminating data design

The scientifically valuable next test requires at least two **independent public datasets with consistent target definitions and measured habitat** plus trait variation, such that whole-study/site holdouts retain adequate morphologic coverage. A new source cannot simply reuse another summary of these 166 studies.

Do **not** rescue v37 by retuning Ridge alpha, choosing favorable taxa/years, changing target transformation, relaxing frozen geographic join radius or filtering to observed winners. Any diagnostic on this source must be labelled post-outcome exploratory and should not overwrite the frozen primary.

**Freeze:** one true new macro-data prediction was executed, no positive universality or motor rule claimed, all prior \`batter\`/\`boids\` results untouched.
