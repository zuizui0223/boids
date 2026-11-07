# Generality v1: phase of environmental change, accessible alternatives, and movement policy

**Frozen 2026-11-07 JST before any new generality-level aggregation/code outcome is computed.** This is an **inspectable, post-result synthesis and prospective cross-forcing hypothesis**, not a new external biological experiment. Preserve all prior positive original Wadden tide findings, and all source failures (WATLAS v64/v66, RSDS 48-source external solar radiation direction nonreplication, unknown/negative social Boids field results). Draft PR stacked on Boids #79; main unchanged.

## Larger ecological question

**When, across species and forcing mechanisms, does the *trajectory of an environment* carry movement/temporal-use information beyond its instantaneous value, and when can organisms buffer its change by switching among reachable alternatives?**

The candidate general principle is NOT "all animals turn the same way under rising tide", NOT "all species are nocturnal", and NOT "Boids neighbor alignment explains these examples." It has **three distinct, falsifiable layers**:

- **L1 / State ambiguity:** At equal environmental state (E_t) (same water level or near-identical daylength), rising and falling phases (operatorname{sgn}(dot E_t)) can correspond to different observed future actions. This is a **source-level phenomenon** only if the *outcome* is directly compared on the same scale with support and controls. Temporal patterning alone is not evidence of anticipation.
- **L2 / Predictive transport:** A frozen model augmented by a physical environmental trend/direction earns **positive proper-score gain on genuinely independent future periods, individuals and regions**, relative to state+movement-history+clock, and against a plausible time-shifted environment placebo. This is the same estimand **within each source and outcome**, never a pooled raw score across camera detections/GPS directions/hydrological use.
- **L3 / Accessible-state buffering:** The signed response and response mode (microtracking, longer relocation, temporal redistribution, persistence with spatial compression) depend on the reachable distribution of habitat states (mathcal A_i(t)), lag (	au_i), and sensory/mobility constraints. Individual history and social information enter **only if the original source measures them**.

### A mechanistic movement-policy hypothesis, not a claimed established law

For a candidate displacement (d) at observation (t), write

[
P_i(d\mid H_t)\propto K_i(d\mid v_{i,t})\exp\{\beta_i R(x_i+d,t)+
\gamma_i\tau_i\partial_t R(x_i+d,t)+
\delta_i Q_i(d,t)+\eta_i S_i(d,t)\}.
]

Here (K_i) is its own previous-movement kernel, (R) is independent environmental/resource state, (partial_t R) its physical rate, (Q) the set of *reachable* alternative states, and (S) optional measured nearby-conspecific information. **Without measured neighboring individuals, set (S=0) and do not fit a social force.**

The first-order environmental prediction (R(x,t+\tau)\approx R(x,t)+\tau\partial_t R(x,t)) shows *why* at equal current (R) two opposing phases can imply different future opportunity. If (	au=0), future opportunity is irrelevant, rate zero, or the rate brings no additional variation within the reachable step set, the dynamic-phase prediction may have **zero** incremental benefit. This is a conditional prediction, not proof of biological foresight; unmeasured habitat, season or observation effort can create the same association.

**Predicted three response modes at the same state (E_t):**
1. Many suitable states reachable: **local state buffering** (experienced (E) changes less than availability; louis is a field example of this separate response endpoint).
2. Alternative profitable states exist but relocate: **directional or temporal switching** (predictive environmental phase may matter; Wadden tide is a field example for direction; Serengeti is a descriptive recorded-camera-time analogue).
3. Limited accessible states or blocked dispersal: **contraction/concentration or reduced effective occupancy**, with local hazards carrying greater weight (mina penguin breeding-patch contraction is an ecological illustration, NOT validation of this movement-policy rate mechanism).

This formulation is related to established dynamic step-selection and habitat accessibility theory, so its novelty, if empirically supported, must be a **cross-forcing prospective predictive test and conditional response-mode boundary**, not simply including a time varying covariate in a movement model. References include Fieberg et al. 2021 (JAE, DOI 10.1111/1365-2656.13441), and the iSSA upscaling literature (DOI 10.1111/1365-2656.13832).

## Fixed evidence sources and their strictly distinct denominators

| Research source | Genuine observation and admitted result | Observation/replication unit | What it does NOT establish |
|---|---|---|---|
| **Boids v59–v63, wild Eurasian oystercatcher, Wadden Sea 2010–11** | Ameland 168 genuinely opposed-phase matched trip pairs / 5 birds, observed directional T +0.167687, bird CI [0.086181,0.249193]. Schier 211 pairs / 10 birds with matches (7 birds >=10), T +0.228679, bird CI [0.076369,0.425446]. Strictly disjoint 2010 training ids (8 train birds /1508 steps) to 2011 Schier yields +0.176419; a separate support-defined 7 birds /204 pairs yields +0.038154. 1,024 source-bird refits + test-bird resampling: joint interval all 211 [+0.033282,+0.304653], qualified 204 [+0.016655,+0.065092]. | 1 bird species, **two nearby local sites**, historically analyzed cohort. | tide causality, unseen region/taxon, prey-front, social interaction, general directional torque |
| **RSDS, original Movebank daytime/nighttime GPS survey** | 12 published original DOIs / 22 study×native-taxon rows (20 named species). Diel observed straight-line GPS movement proxy (q) estimable in 9/12 DOIs, 15/22 rows; signs 11 negative, 4 positive. DOI-equal mean +0.010262 with *descriptive* DOI bootstrap 95% [−0.04923,+0.07674]. Daylength-associated q slopes source-animal bootstrap positive 5, negative 2, include zero 8, unavailable 7. | DOI study is the original **independent field-study** unit; taxa within a DOI are nested. | a universal signed diel response, daylight causality, direct tide-style (dot E) GPS-turn forecast, globally random population |
| **RSDS, 4 matched original GPS study calendars** | 4/4 original DOI studies have ≥1 within-study species q rank difference, 3/4 with opposite nominal source-daylength slopes across taxa on shared eligible calendars. Illinois original DOI is **outside** the 12-study full dataset; three others **overlap**, never call this 16 independent studies. | DOI study / tagged animal; not calendar-day pseudoreplication | exact co-occurrence in a microhabitat, uniformly positive solar slope, independent replication of tide |
| **RSDS seasonal solar phase, Serengeti original camera records** | 186 original sites, 24,290 same-site same-astronomical-daylength paired site×dates; 38,792 detected photographs, 43 source taxon labels; 15 labels meet prespecified minimum photo-source counts; e.g. detected hyena night/day MH OR falling/rising 2.6284, Thomson's gazelle 0.7917. | ONE tropical landscape; physical camera site×season is nested. | *true animal activity rate*, effort-independent circadian entrainment, migratory steering, replicate ecosystems (camera uptime unverified) |
| **RSDS northern Ireland camera comparison** | Separate published geography but 13 same-site×year paired-source units, 353 original event-selected date pairs/988 camera rows, single site-year accounts for 51.56% of pairs; source literal taxon labels not merged. | Independent field project geography, **weak event-selected effort support**. | credible external biological replication of Serengeti photoperiod response |
| **louis, King Rail Lake Erie wetland** | 10/10 birds positive hydrological used-state retention; matched pseudo-use hydrological coupling slope 1.001 vs used 0.162, reduction 83.8%; original matched events, not 607 independent bird replicates. | 10 original birds / 1 regional wetland field project. | tide-phase movement direction; year/region independent recurrence; geographic migration mechanism (event-coordinate join unresolved) |
| **batter bat vertical space use** | 4/4 source panels support individual-specific vertical-use fidelity after topographic/horizontal control, separate older field cohort. | Source animal/session panels; **individual niche profile**, not environmental-phase model. | instantaneous Boids alignment or state-derivative response |
| **mina penguin breeding-space** | Palmer/Signy records show realized breeding locations contract with population decline (e.g., Palmer effective patches −19%/−51%/−83%), informative for slower opportunity/persistence boundary. | Spatial breeding-patch structure at colony/panel scale. | instantaneous step-turn movement or same animal tide-phase shift |

**Non-positive or unverified cases MUST remain visible**: v64 original WATLAS signed-tidaltime source-gate NOT_ADMITTED; v65 2018 sanderling 434 phase-slope-source triples/9 tideIDs feasible; v66 independently original RWS official-gauge **zero-shift** prescribed phase-sign gate NOT_ADMITTED because original-source **falling** agrees 151/201=75.12% <80%; −30min gauge-shift companion 431/433=99.54% agreement is **not** a replacement primary and NOT a next-heading prediction. Boids v6/v8 direct social-partner field primary comparisons not supported. Historical RSDS 48-source shortwave orientation negative external reproduction remains nonreplicated. No cherry-picked universal success.

## What this first synthesis is allowed to calculate

The frozen v1 script:
- Independently obtain **checksum-pinned aggregate result files** from *public* RSDS and document-supported original comparative studies. No private original GPS or raw camera individual IDs are downloaded/released.
- Recompute exact 12 DOI / 22 native rows / q/photoperiod sign support, within-study source-native contrasts, source/DOI-level descriptive interval and admitted/hold support from the **already published RSDS source JSON**; include all negative and HOLD outcomes.
- Recompute source overlap of the 4 shared-calendar studies, so 4 is not added to 12 as if four new independent studies.
- Verify the original Serengeti text receipt and louis hydrological state result under their fixed public Git blob SHA, but **do not convert their heterogeneous endpoints into the RSDS q metric**.
- Produce an **evidence-tier ledger** with fixed status `FIELD_PREDICTIVE`, `FIELD_DESCRIPTIVE`, `SOURCE_ONLY`, `SIMULATION_ONLY`, `HOLD` and `NOT_ESTIMATED`. Never rank countries by numbers of camera photos/GPS fixes or treat subsample size as an independent ecosystem count.
- Compute no pooled tide-vs-daylight-vs-hydrology effect size, no meta p-value and no biological confirmation of a universal phase rate advantage. If a pinned source changes, emit `SOURCE_STOP` rather than silently update positivity.

## Prospective cross-forcing test — separate future source admission

**Model hierarchy** for any original new field panel with *one agreed outcome and observation cadence*:

- M0: own previous movement/state, instantaneous local environmental level, habitat position/availability, clock/time season controls appropriate to the source.
- M1: M0 + prespecified **sign and size of independently measured local environmental rate** (dot E) and the interaction (E	imes dot E).
- M2: M1 + premeasured independently observable **reachable alternative-habitat state portfolio** and phase×portfolio interaction.
- Mghost: same parameter budget using shuffled/cycle-offset environmental phase preserving recorded autocorrelation and source calendar structure. Phase derivative must not be fully determined by an already included clock/calendar feature or else the incremental estimand is unidentified.
- Msocial: M2 + positions/velocities of actually simultaneous nearby animals; fit only if data resolve interaction radius, observation errors and times. Existing source-poor short-GPS data cannot support this.
- Endpoint (G_{k}=\overline{\log p_{\mathrm M1}(Y) -\log p_{\mathrm M0}(Y)}) (nats per observed outcome) on whole **held-out independent tideID, animal identities, landscape-year and eventually species**. Score current panel on the same (Y) across all models; do not compare a detection odds ratio with a next-heading cosine loss. Prefer positive proper-score increment with cluster/landscape CIs, sign against ghost, no parameter tuning on holdouts.
- A second, distinct endpoint (Delta\mathrm{Var}[E_{\mathrm{used}}]-\Delta\mathrm{Var}[E_{\mathrm{available}}]) may quantify environmental buffering, but its source-availability assumption must be explicitly matched like louis, not substituted for a movement forecast.

**Prospective predictions**:
P1: In at least two physically distinct forcing categories and at least two geographically independent field sources, phase improves held-out prediction beyond current state (not necessarily same *coefficient sign*).
P2: Where accessible suitable alternatives are dense, phase-linked movement primarily changes local/time use while experienced environmental-state variability can remain buffered.
P3: When alternative states are scarce, the same forcing should correlate with spatial relocation/concentration or failure of local buffering, conditional on detection; never infer this from penguin occupancy alone.
P4: Existing social Reynolds force cannot be claimed universal without direct simultaneous-neighbor source and a full-information M0/M1 baseline.

**Primary falsification for P1:** good support in multiple forcing classes but at least one out-of-source category fails to outperform clock+state baseline and ghost controls under source-cluster confidence intervals. **For P2/P3:** a well-supported field study where availability predicts no change in buffering/relocation or sign reverses with correct environmental geometry, even after controlling observation bias. Missing public raw data is NOT a biological falsification.

## Research target and journal path

This is a **multi-system macroecological predictive test design**, not a finished universal law. Publication if the prospective tests succeed: Ecology Letters / Global Ecology and Biogeography for general ecological conditionality; Journal of Animal Ecology if framed as field movement+resource-state policy. A theoretical paper would require an independent mathematical theorem and falsifiable field parameters, not merely renaming dynamic step selection as 'Boids universal law'. Separate the learned ecological policy from Reynolds social terms; **Boids proper** is tested only with measured conspecific interactions.
