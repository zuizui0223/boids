# v134 independent original-source effect review

Read-only review of six requested effect papers plus the Arcachon oyster classification. All numerical values below are transcriptions from the cached focal article XML; no effect was fitted, missing uncertainty was not imputed, and no new source was downloaded. Source hashes and automated row comparisons are in `source_verification_receipt.json`; XML section/table IDs below are exact source locators. Local extracted reading copies are retained alongside this report.

## Decision-relevant findings

The six effect papers contain recoverable coefficients and reported standard errors, but they do **not** supply one compatible common effect family. Gull habitat choice, lemon-shark headshake occurrence, sevengill acoustic detection, oyster valve opening, plover counts, and bream log acceleration remain distinct outcomes. Exposure contrasts and conditioning also differ. Missing covariance blocks specified derived contrasts; it does not invalidate every directly reported scalar coefficient.

The important classification correction is Arcachon: its one-year measurements belong in a **constrained-field valve-activity stratum under natural forcing**, matching the Helgoland design stratum. A bag/chamber restriction is insufficient to label one laboratory evidence while accepting the other as field evidence. `FIELD_TIDE_DIEL_SEPARATE` plus an explicit constrained-field design attribute is a consistent available classification. This change does not make Arcachon quantitatively poolable.

## 1. Herring gull — DOI 10.1002/ece3.4167

**Original:** `PMC6106178.xml`, Table 3 `ece34167-tbl-0003`; methods `ece34167-sec-0007`; results `ece34167-sec-0012`.

| Term | β | Reported SE | Reported OR |
|---|---:|---:|---:|
| Water level | −0.40 | 0.04 | 0.67 |
| Night versus day | 0.59 | 0.08 | 1.80 |

The response is mudflat rather than terrestrial habitat use among retained non-flight fixes on foraging trips. This is an additive binomial-logit model conditioning on colony, sex and day/night; it is not a tide-by-diel interaction. Water level comes from the nearest of five gauges, measured each minute. The main XML does **not** state the water-level unit or any scaling convention, so “per metre” would be unsupported from this source alone.

The analysis uses 37 birds and 1,115 trips from three nearby colonies in the same study. Trips and bird IDs enter as random intercepts, with temporal dependence addressed through thinning/autoregression. Crucially, the reported β and SE are **averages across 14 fits**, each starting at a different offset while retaining every fifteenth record. These offset series have distinct retained rows but share animals/trips and temporal dependence. The arithmetic mean of their SEs is not demonstrated to be the sampling SE of their averaged coefficient. Retain “reported mean SE”; resolve the estimator and covariance before inverse-variance harmonization. Do not divide this SE by √14 or count 14 studies. Minor ledger wording correction: “overlapping offsets” should mean shared study dependence, not literal overlapping retained rows.

## 2. Lemon shark — DOI 10.1007/s00227-018-3318-y

**Original:** `PMC5842499.xml`, Table 8 `Tab8`; methods `Sec9`/`Par28–29`, Tables 2 and 4; results `Sec13`/`Par35`.

| Tide factor, with ebb as reference | β | SE |
|---|---:|---:|
| Flood | 0.012 | 0.132 |
| High | −0.600 | 0.149 |
| Low | 0.028 | 0.144 |

The response is hourly presence of classifier-inferred headshaking, a prey-capture proxy. The binomial GAMM includes a cyclic hour-of-day smoother, wet/dry season and a shark random effect; these are additive terms. High/low are each ±1 hour around their event, with intervening ebb/flood, using NOAA predictions adjusted by the documented approximately one-hour local lag. The paper names a binomial distribution but does not explicitly name its link; a logit interpretation is conventional, not code-verified here.

Table 2 independently yields **20 five-day deployments on 18 distinct PIT-tagged wild sharks**: two sharks appear in both seasons. Four semi-captive classifier-training sharks are a separate part of the design. Table 4's “Shark ID 1–20” requires code verification before assuming retagged animals were correctly grouped across deployments. The 2,400 hours are repeated observations, not biological replication. Classifier uncertainty is not propagated by simply quoting the GAMM SE.

The high-minus-low point difference is −0.628, but its SE requires `Var(βHigh)+Var(βLow)−2Cov(βHigh,βLow)`. The published marginal SEs alone cannot recover this. The three ebb-reference contrasts also cannot be counted as three independent studies.

## 3. Sevengill shark — DOI 10.1098/rsos.230667

**Original:** `PMC10565395.xml`, Table 2 `RSOS230667TB2`; methods `s2f2`; results `s3` and `s3b`; Table 1 `RSOS230667TB1`.

| Hourly-detection term | β | SE |
|---|---:|---:|
| Intermediate versus high tide, female reference | −0.074 | 0.034 |
| Low versus high tide, female reference | −0.149 | 0.041 |
| Male × intermediate tide | −0.523 | 0.051 |
| Male × low tide | −1.042 | 0.062 |

Tide height categories use the lower/upper quartiles of hourly predicted height. They are not the lemon-shark ±1-hour tide-event categories. The GAMM includes cyclic hour and sex-specific hour terms, tide height/direction and sex interactions, plus tag random effects. Its response is hourly acoustic detection **only on days when that shark was detected in the array**. It is not full-calendar presence or directly observed foraging. There are 18 retained adults (11 female, 7 male), five surviving receivers and one inlet; receiver losses restrict inference to the upper half of the inlet.

Two source presentation issues remain: Table 1 uses smooth notation for height despite categorical methods/Table 2, and direction remains in the stated final model although its coefficients are absent from Table 2. “Binomial link” does not explicitly verify logit coding. Keep these unresolved until original code is inspected.

The male low-versus-high point is −1.191, the sum of −0.149 and −1.042. Its SE requires the covariance of the main and interaction coefficients; `sqrt(0.041²+0.062²)` would assume an unreported zero covariance. The female directly reported scalar retains its reported SE, conditional on the documented model and coding caveats. Seasonal tide-amplitude smooth F=16.9, edf=2.6 is a test summary, not another signed scalar effect.

## 4. Helgoland field oyster — DOI 10.1038/s41598-026-63105-x

**Original:** `PMC13408198.xml`, Table 1 `Tab1`; methods `Sec5`/`Par13`, `Sec6`/`Par15`, `Sec12`/`Par22–29`; results `Sec17` and `Sec19`.

| Response and water-level term | β | SE |
|---|---:|---:|
| Valve opening amplitude (VOA) | 3.26 | 0.72 |
| Valve opening duration (VOD) | −4.47 | 1.10 |

Methods define both responses as percentages, water pressure converted to metres (1 bar=10 m), and an untransformed linear mixed model. Thus percentage points per metre is the method-supported interpretation; original analysis code was not available to confirm any unreported scaling. VOA is normalized to each individual's empirically updated maximum; VOD is percentage of the hour above the 5% VOA threshold. They are distinct but dependent responses.

The global additive model conditions on daylength, direction of daylength change, temperature, sound, chlorophyll a, salinity and turbidity, with an individual random intercept. **Daylength is not clock phase or day/night.** The reported water slopes are not uniquely diel-adjusted tidal effects, and the later top-three interaction models omit tide. `FIELD_TIDE_DIEL_SEPARATE` is appropriate. No residual serial-correlation structure is specified; a random intercept alone does not establish independence of hourly residuals. Sound is missing after 28 February 2024 and the exact handling/sample used by the model is not described precisely.

Sixteen oysters were deployed in protective individual chambers in one field basket; 15 survived beyond the first day. Technical losses reduce observed individuals to 14 and then 8. One lander/site and 12,960 nominal hours do not create independent coasts or studies. VOA/VOD require joint covariance if a common summary is constructed. Shell growth and gene expression were not reviewed as activity effects here.

## 5. Florida plovers — DOI 10.3390/ani13223548

**Original:** `PMC10668691.xml`, methods `sec2-animals-13-03548`; Table 1 `animals-13-03548-t001`; Table 2 `animals-13-03548-t002`.

| Species | Mudflat tide β (SE) | Beach tide β (SE) |
|---|---:|---:|
| Piping plover | −0.40 (0.15) | 0.89 (0.06) |
| Snowy plover | −0.45 (0.07) | 0.17 (0.07) |
| Wilson's plover | −0.11 (0.03) | 0.71 (0.05) |

These are Poisson abundance coefficients conditional on standardized wind and tide×wind. They represent the tide slope at the wind reference value; under conventional z-scoring that is mean wind and the coefficient is per one tide SD. The source reports standardized predictors and tide SD 0.19 m, but does not document the exact code/convention; “per 1 SD” and the conventional log link should be labeled method-derived rather than explicitly code-verified.

There are 38 shared morning surveys (07:30–10:30) on one island, with tides assigned at 07:00. The study does not fit tide×diel. Species/habitat rows share survey dates and potentially redistribute the same birds, so six rows are not six independent coast-study units. The six tide×wind coefficients, in the same row order as this table, are 0.35, −0.06, −0.01, 0.18, 0.09, 0.03 (SEs 0.16, 0.05, 0.07, 0.07, 0.03, 0.04). A tide effect at another wind value needs covariance with this interaction; covariance is not reported.

Table 2 preserves null-compatible peck-rate tide slopes: piping −0.01 (SE 0.08; p=.942), snowy −0.17 (SE 0.10; p=.088). Methods describe a GLMM with date random effect and “lmer,” while Table 2 says GLM and reports z statistics. The response link/transformation is unresolved, so these are source-scale coefficients, not compatible log-count effects by assumption. A source-table anomaly is piping intercept 3.24, SE0.84, z38.49: the printed numbers are arithmetically inconsistent. Do not silently repair that SE. Wilson's plovers were never observed foraging; that is not a fitted zero-effect model.

## 6. Yellowfin bream rescue — DOI 10.1371/journal.pone.0080962

**Original:** `PMC3832432.xml`, Table 4 `pone-0080962-t004`; methods `s2c–s2d`; Tables 1–3; results `s3`.

| Printed Table 4 label | Methods-defined predictor | β | SE |
|---|---|---:|---:|
| Diel period | Standardized continuous PAR | 0.1651113 | 0.019 |
| Tidal period | Standardized continuous tide height | 0.1785145 | 0.035 |
| Depth | Standardized depth | −0.0972872 | 0.029 |
| Diel·Tide | PAR×tide | 0.1120134 | 0.039 |

The response is log-transformed bi-axial acceleration; the underlying sensor units are m/s². The source does not specify log base or the exact standardization equation. These are not binary day/night and high/low coefficients despite the table's labels and the separate categorized display figure. The tide main term is conditional on PAR's model reference (normally zero after standardization); a different light level requires the interaction and its covariance.

The model is GLS with first-order serial autocorrelation, final φ=.34. It includes PAR, tide, depth and their PAR×tide interaction; temperature, turbidity and lunar phase were removed. The published XML does not specify an animal random intercept or the grouping/time formula for its correlation structure, so six-animal clustering cannot be assumed to have been solved. The interaction's own SE is directly reported and can be retained as an interaction coefficient without inventing a day-night contrast.

Six fish at three nearby receivers form one Georges River study. Table 1 sums independently to 37,070 activity readings and 37,066 depth readings; the first three fish provide 97.09% of activity readings. The results give 15,014 activity bins and 15,091 depth bins, not that many animals. Methods `s2a` identifies the broader array as also reported in Payne et al. 2013, DOI 10.1098/rspb.2012.2363. This is a potential shared-cohort linkage to preserve if that paper is added; exact animal overlap was not checked because its focal XML was not present.

## Arcachon classification against frozen v131

**Original:** `PMC5636115.xml`, methods `sec003`, `sec006`, `sec008`; results `sec020`. **Protocol:** `boids/docs/V131_FROZEN_GLOBAL_TIDE_SOLAR_META_PROTOCOL.md`, “Two linked, NON-INTERCHANGEABLE evidence arms,” “Biological moderators,” and “Independent unit.”

At Eyrac Pier, oysters were in a permanently submerged field bag on a table, near wild oysters, at minimum approximately 1 m water depth with natural semidiurnal tides and current. Valvometry followed eight diploids and eight triploids from 20 March 2014 to 19 March 2015, with 11-day and 9-day electrical gaps. The farm-origin and triploid characteristics should remain explicit moderators. Helgoland uses hatchery-origin oysters, prior tank acclimation and individual field chambers protected by mesh, also under natural forcing. Both are constrained field activity studies; neither tests unconstrained habitat movement.

The frozen protocol separates laboratory manipulations/free-running clocks from field observational endpoints and explicitly includes molluscs. It does not exclude all restrained sessile animals. Consequently, retaining Arcachon only as `LAB_OR_SEMINATURAL` because of the oyster bag creates an inconsistent field count when Helgoland is accepted.

Arcachon analyzes cosinor tidal/daily rhythmicity over 25 consecutive approximately 15-day segments, with ploidy, daylength and season comparisons. The source says the year is divided into segments; the current B67 description “overlapping 15-day windows” is unsupported. Nonsignificant percent-rhythm values are set to zero by the authors: those zeros are thresholded summaries, not observed zero biological effects. No directly comparable signed tidal slope and SE were recovered. The classification correction therefore changes the evidence stratum, not the compatible-effect pool.

## Pooling gate

For a directly reported scalar, retain its reported uncertainty and clearly label the source's model. For a derived contrast `cᵀβ`, use `cᵀVc`; off-diagonal covariance cannot be assumed zero. This specifically affects lemon high-minus-low, sevengill male tide effects, bream light-specific tide slopes, and plover wind-specific tide slopes. Dependent outcomes/species from one coast require shared-study handling, not numerical row counts. No reviewed set meets a common endpoint/exposure/conditioning definition with verified uncertainty across the frozen minimum three independent coast-study units.
