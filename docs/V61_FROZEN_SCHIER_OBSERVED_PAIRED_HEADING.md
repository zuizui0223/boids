# v61 frozen: same paired-observed tidal heading endpoint on Schiermonnikoog

Frozen on 2026-11-07 after **source-only** v59 Schiermonnikoog passed (211 disjoint opposite-phase observed 2011 B-trip pairs; 7 birds with >=10 pairs; 45 ISO weeks; 12 calendar months) and **before inspecting any matched observed-heading v60/v61 numerical effect**. This is a spatial companion site in the same Wadden Sea and species, not an independent new taxon or an independent untouched ecological cohort.

**DO NOT use the Ameland observed primary v60 directional result to select, alter or reweight the Schier test.** Reuse literally the identical v60 projected-direction primary, bird/ISO-week bootstrap estimands, exact bird sign-flip sensitivity, controls and zero-gradient policy.

## Frozen source and admission

- Schiermonnikoog 2010 original wild GPS 7,911 3-fix training trips / 21 birds; 2011 source 4,948 3-fix test trips / 13 birds. Retain native site coordinates (no inter-island centroid translation).
- Original publisher-MD5 and fixed SHA256 Zenodo GPS, and genuine measured `schiermonnikoog.waddenzee` RWS WATHTE NAP 2009–2011, exactly 52,561 records per gauge-year; same official authenticated source loader and 2010->2011 old heading replay as v43.
- Reproduce v59 fixed pairing **without looking at future B→C headings**: same native 1km grid, same source bird, original rising/falling, real h diff <=0.15m, >=24h apart, day-of-year <=30d, clock <=3h, preceding heading <=45deg, preceding log1p speed <=0.4, deterministic one-to-one greedy and no tuning. Reconstructed source-only counts must match the archived v59 original field log and independent artifact: 211 pairs, 7 birds with >=10, 45 weeks, 12 months; original 2011 rows 4,948, original birds 13; sequential eligibility counts [1784,1294,1276,969,572,277,248] (source B location, +h, +separate day, +season, +clock, +prior heading, +prior speed). Failure is SOURCE_STOP, not a biological zero.
- Train only the unchanged v41 ridge lambda=10 2D east/north next-direction model on **Schier 2010**, never 2011 target headings or source-match selections; bird identities can persist across years. No coefficient updates or newly tuned tide offset.

## Frozen primary: exactly v60, no new definition

For each source-verified genuine rising B+ and genuine falling B- episode, compare **observed** next B→C unit-vector heading `y+` versus `y-`. Derive one 2010-fitted model phase-switch unit-heading difference at each of their actual starting B covariate states without changing other fields, then average the two contrasts to `g`. Score `T=dot(y+ - y-,g)/4` within [-1,1], including T=0 when g is zero. No normalizing by the size of g or censoring unfavorable cases.

Primary equal-bird mean T; 10,000 whole-bird resamples (seed=20261107), count positive birds and exact enumerated one-sided bird-level sign-flip sensitivity. Separate week-then-bird point estimate and 4,000 week bootstraps (rising original B week assignment), never substitute its confidence interval. Supported observational concordance only if primary mean >0 and bird-bootstrap 95% lower >0. Reproduce v60 secondary matched-phase true-versus-flip cosine gain, observed actual pair angle difference and orthogonal score without model selection; report any negative or null. Retain equal bird weights despite unequal episodes.

Source-only v59 and synthetic Boids results are not evidence for a Schier ecological phase effect. A positive v61 would indicate **two neighboring sites in one species** supporting directional concordance under historical observational matching, not causal waterline tracking, weather/resource-front effects, Reynolds neighbor alignment, 3D flight control or universal niche differentiation. Original IDs, timestamps, coordinates, pair mappings, per-bird outcomes, RWS measurements and raw tracks must never enter any committed artifacts.
