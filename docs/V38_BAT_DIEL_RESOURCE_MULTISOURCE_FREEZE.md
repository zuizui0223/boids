# v38 — Independent bat activity and resource-context archive preflight

**Frozen 2026-11-19 JST BEFORE reading numerical acoustic event counts / activity, prey abundance, flight speed, movement, or forecast outcomes.** Branch \`research/bat-diel-resource-transport-v38-20261119\`. \`boids\` v37 negative whole-study morphology prediction, v30 negative Carollia sensor prediction, v32–v36 structural source STOPs and frozen \`batter\` results remain unchanged.

## General question

Do bat activity-timing rules learned under one ecological context transfer to a **different year, recording site or climatic/structural setting**, or does functional-guild/ecological opportunity change the rule? Original studies already associate temperature, night length, habitat management and species activity with acoustic detections. New contribution would be **rigorous held-out forecasting of detection-conditioned diel activity** with effort and site-night replication correctly handled, not rediscovery of in-sample slopes.

Do not confuse detection intensity with actual feeding, bat cognitive choice, social co-presence, 3D tracks, or foraging success.

## Independent original public sources and exact published file checksums

A. **Finland high-latitude thermal-window data** — Lilley et al. 2026; Zenodo \`18298435\`, DOI 10.5281/zenodo.18298435; \`Data.xlsx\`, MD5 \`444c510bcb154bf9272d620f1ce0ec5a\`, ~7.6MB. Article describes >9,000 monitoring nights over 7 years of northern bat *Eptesicus nilssonii*, 60°–66°N. Published night-time temperature × night-length activity patterns are **prior art**. Worksheet columns, actual record grain, effort/no-detection coverage and site/year group structure must be audited before outcomes.

B. **Italy managed-forest acoustic detections** — Castiello et al. 2026; Zenodo \`21808015\`, DOI 10.5281/zenodo.21808015; \`Databats_Cansiglio.csv\`, MD5 \`76b954fd896ad182aa5a9b97516b6535\`, ~7.3MB. Detection records contain site, management treatment, date/time, taxon label and call parameters, 2022–2025. Acoustic detection records alone are *not* automatically an effort-complete time series; zero-call bins need recording-window logs.

C. **Belgian tree-row agricultural bioacoustics with co-sampled invertebrates** — DIGITAF, Vandendriessche et al. 2026; Zenodo \`20137204\`, source DOI \`10.15468/cm9c76\`, 64 plots across 27 cereal fields; files:
- \`metadata_loc.csv\`, MD5 \`9672cb0e7dec4d0811540458375229b1\` (~38.5kB), plot/site/treatment context.
- \`Obs.AudioMoths-bats_activity.csv\`, MD5 \`d0588f30bf4ed86a168c5438373e6019\` (~799.7kB), bat activity evidence.
- \`Obs.AudioMoths-bats.csv\`, MD5 \`e048b351a5300e9cd30c7e4500a9259a\` (~23.8kB), source bat detections.
- \`Obs.Pitfalls.csv\`, MD5 \`fd45668086cc38fbfa9a4c682607d7fe\` (~548.8kB), arthropod community (sampled on different protocol).
- \`Obs.Transects.csv\`, MD5 \`82a80234186bdeaeeace7d9859dd7e7e\` (~146kB), other taxon transects.
Published sampling includes 48 h acoustic deployments: **1 minute per 15 minutes**, plus date/clock windows; pitfall 14 days and transects different dates. **Do not** interpret sample richness/abundance as instantaneous bat prey or contemporaneous independent sensor input without an explicit join/time-lag audit. The Belgium source is independent of Finland/Italy, but habitats differ radically.

D. **Israel urban–rural bat detection dataset (secondary source-screen only)** — Ding et al. 2026; Zenodo \`19216373\`. Source script states 27 monitored sites, with nights without detections explicitly absent from the call-level table and needing a separate monitoring effort ledger. NOT admitted to a cross-region denominator unless those zero nights and record-clock data can be reconstructed from published *original* effort, not publication summary estimates. Do not silently treat a detection-only table as a fully sampled grid.

## Original source audit protocol, ahead of any response model

1. Download **only the exact named source files from the public, original Zenodo record**; compute complete-file MD5 and SHA256; reject HTTP access denial, HTML challenges, malformed CSV/XLSX, size cap or provider-hash mismatch. No alternate version/silent mirror substitution.
2. CSV source gate: read headers, row counts, distinct **nominal site labels / treatment labels / taxon labels / date/year/time strings**, field missingness and unique identifiers. Never read or log numerical activity, prey counts, wing/flight metrics, species abundance or any original restricted micro-location coordinates.
3. Finland workbook gate: inspect ZIP/XLSX container safely, original sheet names, first-row text/header and sheet row dimensions **without decoding numeric cell values**. No formulas evaluated and no original workbook redistributed.
4. Identify the actual observational unit separately for each source. Record if bat occurrence rows are individual pulses, 1-minute bins, site nights, or aggregate nightly/group responses. Explicitly assess *recording effort on zero-detection nights*. If unmeasured, do not claim absence, occupancy or comparable intensity.
5. Belgium join: separately inspect metadata/bat/invertebrate source ID **column names and label support**, but do not join and interpret prey effects before a declared common plot/date grain is verified. Pitfall, transect and acoustic sampling windows differ.
6. Eligibility for a common site-night activity model: at least 2 independent public sources with verifiable local date/time and site IDs **and** complete observation schedules (including no-detection intervals) or explicitly measured effort denominators. A lower-standard *detection-conditioned timing distribution* is allowed only as a distinct exploratory question, not as a surrogate for true bat activity intensity.
7. After passing this source gate, freeze one primary whole-site/whole-year held-out model (if same response and weather/effort support are real), then evaluate. A positive within-site score is insufficient for cross-country generality. **Never pool incompatible sampling schedules, guild-only vs species detections or prey proxies without a harmonization report.**

## Scientific outcomes and preregistration boundary

- Supported prior paper claims are NOT original findings of this programme. 
- Full causal forest→insect→bat mediation cannot be identified from observational temporal co-detection alone.
- Two to three regions are neither a random sample of all bats nor globally representative. 
- The result of this v38 stage is source-integrity and exact observational-support evidence only. Any missing source, effort denominator or independent ecological co-record becomes a **structural stop**, not a negative behavioral finding.
- Raw bat site coordinates / sensitive roost locations / source CSV/Excel original animal record dumps are not to be committed in GitHub. Store counts and digests only.
