# v131 — Global tidal × solar temporal-niche ecology: systematic review and multi-cohort meta-analysis

**Frozen design version: 2026-11-14 JST.** Scope explicitly expanded from one Vlieland species/year to multiple species, multiple coastal landscapes and independent studies. Protocol frozen before v131 literature source census and any v131 pooled biological effects. Prior v127/v129/v130 Vlieland results have already been observed; they are **hypothesis-generating pilot data** and can never become blinded independent confirmation. This is a structured evidence-building effort; **no quantitative global effect has been estimated yet**.

## Core nontrivial question

**When does tidal timing provide unique information about biological temporal niche organization beyond time-of-day, solar cycle, environment, and sampling schedules — and why do organisms differ in the strength and direction of that response?**

Distinct claims:
1. **Diel association**: behavior differs day/night. Not by itself causal solar entrainment.
2. **Tide-specific *prediction***: correct local measured/reliable tide uniquely improves out-of-source temporal prediction beyond clock+sun+sampling controls and matched wrong-tide shifts.
3. **Physical resource gating**: true GPS-local `access(x,t)=1{z(x)>h(x,t)}` (or verified aquatic-depth/current exposure analog), independently observed ground/bed morphology and water level with compatible vertical datum, mediates tide response.
4. **Temporal niche partition**: within a community or co-occurring species individuals differ in conditional time utilization beyond shifts in habitat composition, source coverage and pooled taxon turnover.
5. **Causal endogenous circatidal clock**: never inferred from field observational tide association; requires controlled cue-removal/free-running experiments.

## Two linked, NON-INTERCHANGEABLE evidence arms

**A. Systematic published-study evidence extraction (PRISMA 2020).** Search title/abstract/full text from Crossref/OpenAlex/Europe PMC and links in major circatidal reviews for marine/estuarine/coastal activity, diel + tide. Distinct paper IDs, article versions, and article–dataset linkage retained. Screen in two stages: metadata candidates vs full text independently assessed; only full-text reports with explicitly reported effects and compatible standard errors/covariances enter quantitative meta. Individual effects measured as e.g. Hedges g for prespecified exposure contrasts, Fisher z for valid correlation partials, or GLM effect with reported SE. **No conversion of arbitrary log-score, MSE, odds ratio and standardized mean difference into one uncalibrated global pooled number.** Multi-outcome correlated estimates nested inside study/site. Negative, zero, inaccessible data counted and documented. No effect invented from abstract direction. Search strings and query date versioned.

**B. Individual-participant/raw-time-series ecological meta-analysis (IPD).** Independent genuine source raw animal GPS, ACC, acoustic, camera, field density/behaviour series with original UTC, site geometry and sampling effort. Refit matched clock/solar/tide predictors separately within **endpoint families**:
- observed/ACC-inferred behavior class share; preserve classifier-specific false positives/accuracy and sampling duty cycles;
- speed/movement or habitat occupancy, with coordinates/temporal sampling;
- acoustic/photographic detection probability, explicitly model detection and seasonal effort;
- independent manipulative circatidal laboratory experiments kept separate from field observational endpoints.

Per dataset, compare **same records** and exactly matched holdouts: M0 clock+season+bird/group+effort; M1 + astronomical solar geometry; M2 + actual true local tide height/phase (+ relevant interaction); Mwrong tide phase aligned to other valid observed tide clocks, 8–24 matched wrong shifts if possible (fixed before each dataset's Y). Hold out **entire local calendar weeks** first, then whole sites/coasts when possible. Head-to-head source-matched `ΔL = L(M1)−L(M2)` and `Δphase=L(best wrong tide)−L(real tide)` separately per endpoint and site. Score per true animal within week, then weeks within independent site; no millions of GPS or ACC events falsely counted as independent studies. For skewed outcomes use appropriate distribution, prespecified likelihood, and ideally log-score on the *same response family*; do not pool unlike units.

## Gating before an effect claim

Minimum source eligibility (for raw IPD test) **known true original time and site**, >=3 separated tide cycles and day/night covered, observation effort recorded, original taxon IDs/individual IDs when applicable, source original provenance+license, reference tide measured or documented modeled-source with uncertainty, source geometry verifies tide vs local time overlap, at least two distinct weeks, valid field endpoint. For confirmatory real-vs-ghost temporal CV require stronger site-specific fixed gates frozen before source behavior: 8 independent original animals if animals are the unit, >=1000 eligible source 15min windows or appropriate endpoint-specific target and >=8 weeks (alternative monitoring without individual animal structure predefine plot/week as unit); field study with no sufficient source gets NOT_ESTIMATED, never 'no tide effect'.

A single single-site study may contribute to research synthesis but **global moderator inference requires >=3 geographically independent coast-study units, >=3 distinct species and >=2 functional groups** with usable effect and uncertainty; ecological generality across ocean basins requires >=3 independent ocean regions with balance sensitivity. These are minimum *guardrails*, not statistical power guarantees. Cohorts within one site/study/colony never become independent merely because years/species/birds differ.

## Biological moderators / falsifiable hypotheses

- H1 **Access-gated tide effect**: tide-specific behavior/prediction strength increases with the amount of time the locally used habitat transitions through availability, a function of terrain elevation distribution and relative local tide range. Predict weak effect on permanently submerged or permanently emergent microhabitats, unless tidal current/prey supply is a separate confirmed mechanism.
- H2 **Solar–tide conflict**: as tide advance shifts exploitable windows across day and night, some organisms preserve spatial/functional specialization while changing activity timing. Daily 24h solar clock and 12.42h semidiurnal tide are *not* the same rhythm. Diagnose aliasing and time-of-day effects; no universal sign asserted.
- H3 **Functional and trophic stratification**: shorebirds, gulls, fish, crustaceans, intertidal molluscs and arthropods show different responses according to mobility, prey/food, predator risk, exposure and internal/external zeitgeber mechanisms. Literature lab 'free-running' clocks must be kept in mechanistic evidence layer.
- H4 **Anthropogenic lighting and predator regime** as moderators, not as post-hoc covariate rescues. ALAN exposure, predator presence, latitude/daylength, tidal form factor, amplitude, hydrogeomorphology and season where available; no unvalidated ALAN–response claim.
- H5 **Species and individual-level time-niche partition** requires paired species or guilds at a co-occurring site and comparable monitoring opportunity, with detection/habitat composition controls. An activity rhythm within one species is NOT niche partition.

## Independent unit, meta structure, and validation

ID hierarchy: **paper/dataset -> study -> colony/site/coast -> taxon -> genuine individual -> year -> week -> observations**. For correlated studies, use multilevel meta-regression with covariance/shared-site random effects or RVE at independent sites where sampling supports it. Distinct behaviors and species use outcome family strata; no pooling 2 years of same tagged individuals as independent. Model selection and feature support no later than raw outcomes; full case ledger includes not-admitted sources and expected wrong-phase effects.

Summary model within one compatible endpoint family: `y_j ~ Normal(theta_j, s_j^2)`, `theta_j=alpha_family + beta*X_site + u_coast + u_taxon + u_study`; keep known repeated-tag covariance where available, weakly regularizing random effects, estimate tau and heterogeneity with wide uncertainty. If sources too few for a random effect, report descriptive side-by-side results only; no made-up variance estimate. Cohort/paper small-study and publication selection diagnostic only when sufficiently many independent studies (>10 per family), explicitly not guaranteed.

Use cross-coast and cross-taxon leave-one-out; model source version changes; daylight duty-cycle and timestamp localization; measured gauge vs offsite modeled stage; phase-preserving ghost controls; 3/7/11d from v130 alone cannot be universal because tidal regime and sampling differ. Physical source fallback: [GESLA-4](https://gesla787883612.wordpress.com/) hourly/higher-frequency, 6474 sites in global inventory (not 6474 biological cohorts); other national gauges incl RWS/NOAA; [FES2022](https://www.aviso.altimetry.fr/en/data/products/auxiliary-products/global-tide-fes/release-fes22.html) registration/license needed and not necessarily reliable in enclosed/estuarine waters; [TICON-4](https://doi.org/10.17882/109129) for global tidal characteristics. No tidal amplitude from raw site name alone.

## Search and extraction reproducibility

For initial bounded **discovery**, reproducible queries:
- `"tidal" "diel" animal activity`, `"tidal" "solar" animal behaviour`,
- `"intertidal" "nocturnal" feeding`, `"circatidal" "circadian" movement`,
- `"tide" "acoustic telemetry" fish`, `"tidal" crab activity`, `"lunar" tide behavior`, `"shorebird" tide tracking`.
Expand synonyms British/US spellings and taxa, run dedup by DOI plus normalized title. Metadata-search hits are **not** eligible samples and not scientific outcomes. Full-text two-rater eligibility and full reference chasing required for a complete PRISMA review. Source registry in `validation_v131/source_registry.json` is **curated seed** for source inventory, not an exhaustive PRISMA search. Candidates explicitly label `metadata_only` / `source_known` / `field_effect_observed`.

For each included effect report: citation and original study, longitude latitude or non-sensitive region, species/taxon, habitat, year/season, actual observation endpoint, original timed sampling/effort, measured tide vs model, solar basis, number of independent sites/animals/weeks, raw/summary access, effect + SE/CI, sharing of animals or sources, source gate, and exclusion reason. Keep exact tested time windows and preregistration. Record zero and negative studies. Publish harmonized aggregate only unless raw-data redistribution license allows.

## Critical limitations & publication criteria

As of this v131 protocol, the **one source-backed field positive** v130 is 2018 Vlieland oystercatcher **single study/site**: genuine measured tide beats 3 shifted clocks on 193,088 matched ACC class proportion windows, 35 birds, 17 heldout weeks. This is post-v129 in-sample study and not yet independent confirmation. v127/v129 daylight association is not causal light. The resulting work is currently **NOT a completed global meta-analysis**, and MUST NOT claim global positive effect, worldwide coverage, cross-taxon niche partition or causal zeitgeber. Review and candidate acquisition must expand outside the Netherlands/Belgium, across independent source ecologies.

Versioned literature references:
- van der Kolk et al. 2022 ZooKeys GPS & accelerometer data six oystercatcher studies [DOI](https://doi.org/10.3897/zookeys.1123.90623)
- Rock et al. 2022 Towards an Understanding of Circatidal Clocks [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8914038)
- Rhythms and Clocks in Marine Organisms (2023) [DOI](https://doi.org/10.1146/annurev-marine-030422-113038)
- Hart-Davis et al. 2026 global tidal characteristics [DOI](https://doi.org/10.5194/os-22-1681-2026).
