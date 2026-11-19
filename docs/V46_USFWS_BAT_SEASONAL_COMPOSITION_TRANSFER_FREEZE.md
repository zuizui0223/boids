# v46 frozen new primary — cross-site transport of bat acoustic seasonal community composition

**Pre-outcome freeze 2026-11-19 JST.** No numerical original USFWS species count or ALL response was opened under v42–v45. This is a **new source-backed acoustic-community prediction**, not a test of full-night acoustic activity rate, individual flight, bat co-operation, ecology mechanisms or animal GPS.

## Verified original source and ceiling

USFWS Great Lakes and Upper Midwest Acoustic Bat Dataset, ServCat Reference \`112151\`, original ZIP DownloadFile \`165800\`, 495,216,105 bytes. v43a original ZIP directory 11 Excel members verified with pinned final-65KB SHA256 \`69f4410f8b868849e6e17160b377e6f34fc65068e62f2590e31b598bc5f0fa59\`; v44 Nightly Pass Counts.xlsx original member 2,171,863 bytes, ZIP CRC32 \`3666e794\` independently verified. v45 source-only XLSX inspection confirmed **33,168 unique AcousticSite×NightOf rows**, no duplicates, and **17 columns**: \`AcousticSite, NightOf, ALL,\` plus **14 original automated species labels**
\`EPTFUS,LASBOR,LASCIN,LASNOC,MYOLUC,MYOSEP,PERSUB,MYOLEI,MYOSOD,NYCHUM,CORRAF,ANTPAL,LASINT,TADBRA\`. Original site metadata sheet has 277 rows but lacks proof of detector-hours per site-night. The original agency requires >=8 WAC 15-minute files to include a night in this table, **but no comparable full-night effort denominator**. This limits every result to **conditional relative acoustic classifier composition among included records**.

**Important:** USFWS automatic classifications were not individually vetted. True species identity, individual bat count, prey and social activity are NOT validated by these columns. This is a within-one-regional-survey analysis (not independent studies, global species-general law or direct physiological rule). The v45 missing per-night WAC effort is NOT repaired.

## Outcome, covariates, and fixed models

- Each source row is exactly one \`AcousticSite×NightOf\` detector-night, never treated as multiple individual bats. Parse Excel serial date using base 1899-12-30 (including standard 1900 leap-year correction), or explicit \`YYYY-MM-DD\`, \`MM/DD/YYYY\`, \`YYYY/MM/DD\` or \`YYYY-MM-DD HH:MM:SS\` text. No other date guessing. Source labels may be shared-string indexes and must be decoded for the dates only.
- For each original 14 species-count column require finite **nonnegative integer** value; zero allowed, no imputation. Negative/non-integer/nonfinite/missing => exclude row and report full reason count.
- Require source \`ALL\` nonnegative integer but never use it as model predictor or as denominator. Report missing/invalid and count as exclusion. Do not require \`sum(14 species) == ALL\` (classifier conventions may differ); report count of differences only, avoid silent filtering.
- Conditional target on each source detector-night with \`sum(14 labelled counts)>0\`: vector \`p_{j}=count_j/sum_{k=1}^{14}count_k\`. Exclude all-zero classified nights from composition with explicit counts (this does NOT mark the site as true bat absence).
- Primary baseline \`M0\`: training-only mean of nightly compositions, fixed Laplace prior \`+0.25\` for each of 14 categories, divided by \`Ntrain+14×0.25\`.
- Primary seasonality model \`M1\`: training-only standardized two inputs \`sin(2π DOY/365.2425), cos(2π DOY/365.2425)\`, with **Ridge alpha=10**, multioutput 13 logits trained from \`log((count_i+0.5)/(count_last+0.5))\`; predict via softmax of 13 outputs + reference zero. Models predict 14-class conditional proportions; zero pseudo-counts are fixed in advance. No site/country/animal ID input, no year feature, no post-outcome filtering or tuning.
- Same eligible source rows for M0 and M1. Loss per detector-night is cross entropy \(-Σ_j p_{obs,j} log(max(p_pred,j,1e−10))\) in nats. M0−M1 positive = calendar seasonality improves **relative acoustic species-label composition**, not true bat counts. Reject any claim about absolute detector effort/intensity.
- **Primary independent-group holdout**: leave each complete \`AcousticSite\` out of fitting. For final score first average within test site then **equal-weight sites**, rather than pooling 33,168 dependent nights. Exact original site names never exported. Site-level per-group gains and limits may be saved under *anonymized sequential labels*.
- **Secondary** whole-year holdout: every row of a complete original recording year withheld; equal-year mean and interval, no tuning based on primary.
- No climatic/habitat predictors; day-of-year is a seasonal proxy, not direct temperature, prey resource, sensory or environmental causality.

## Frozen support gate before model fitting

After reading original numeric source counts, eligibility is checked **before fitting the model**, with no threshold changes:
- ≥1,000 detector-nights with nonzero sum of 14 classified counts and valid \`NightOf\`.
- ≥30 \`AcousticSite\` categories with ≥20 eligible nights each; ≥5 source recording years with ≥50 eligible nights each; ≥10 total species labels with at least one positive detection over admitted nights.
- Each leave-site-out fold must retain at least 500 training nights. If gate fails, report \`SOURCE_RESPONSE_SUPPORT_STOP\` and do not fit.
- Selected year/site heldout test groups with fewer than minimum eligible records are reported and not counted as successful forecast. No after-outcome rescue.

## Inference and uncertainty

- Per-site equal-group **10,000 bootstrap** resamples (seed \`20261119\`) of site-level losses, 95% percentile interval; exact one-sided positive-site sign test. Positive primary requires mean gain >0, bootstrap lower CI >0 and sign p<=0.05 simultaneously.
- Secondary year-level 10,000 bootstrap and exact positive-year sign p. With fewer than 5 eligible years, secondary STOP; never claim year universal from a single year.
- Source screening is observational retrospective external-site prediction **within one USFWS survey**. A positive relative composition effect could reflect shared life-history seasonality, classifier prior/range-mask rules, detector settings or season-dependent availability rather than bat cognitive action policies. Entirely independent other agencies/regions are required to establish cross-study universality.
- All original v42 whole-archive size STOP, v43 second-range STOP, v43a/v44 source-pass, and v45 effort STOP remain unchanged. \`batter\`, \`boids\` v30/v37 negatives and v39 nonconfirmatory Finnish thermal transfer remain unchanged.

## Irreversible decision

**Do not change these models, metrics, source rows, species columns, validation groups, thresholds, pseudocounts or loss after scores are opened.** Even if the result is positive, title it *transferrable seasonal relative acoustic composition* rather than *universal bat flight law*.
