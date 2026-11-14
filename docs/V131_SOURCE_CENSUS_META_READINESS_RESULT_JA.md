# v131 source inventory outcome — GLOBAL META IS NOT YET ESTIMATED

**First-party real original metadata census completed** on 2026-11-14 JST: [GitHub Actions #43584015155](https://github.com/zuizui0223/boids/actions/runs/43584015155) **SUCCESS**, 14/14 synthetic/pure source-and-effect-known-truth unit tests passed; original anonymous metadata-only result artifact ID **14109403141**, zip SHA256 **1725269ede5f04a3eb567fc00fe0124f731b229a8293e27cb0741e58ba72ec7c**. Complete reproducible query/source script in `validation_v131/run_source_metadata_and_literature.py` and fixed candidate source ledger in `validation_v131/source_registry.json`. A conservative meta effect gate in `validation_v131/meta_effect_gate.py` ran with an **empty** verified independent-effects ledger.

## True reproducible source inventory

| Result | Value | Scientific meaning |
|---|---:|---|
| Curated cross-taxon/data-source seed entries | **12** | A candidate source catalogue, **not 12 independent behavioral effect studies** |
| Genuine Zenodo first-party records checked | **8/8** | Metadata source file headers, original file names, publisher MD5 fields and positive sizes validated; **raw animal data not opened** |
| Native ACC-classified behavior source collections | **4** | O_VLIELAND, HG_TEXEL, LBBG_TEXEL, LBBG_SCHIERMONNIKOOG |
| Original GPS-only or raw acceleration without published classification | **4** | Zeebrugge, DELTATRACK, WesterSchelde, Ameland: GPS/raw ACC source, NOT comparable forage classifier |
| Source seed catalog other than Zenodo | **4** | China Leizhou field GPS/surveys; Japan crab two-species published paper; Japan fish acoustic research candidate; Canada Arctic freshwater solar-only control |
| Literature bounded metadata queries | **7** | Europe PMC public original metadata, 35 max returned/query, all query string/date preserved |
| Query hits before dedup (bounded) | **243** | Metadata hits only, many may be irrelevant or non-eligible |
| Distinct article metadata candidates | **197** | DOI/title-deduplicated; **zero fulltext screening and zero effect extraction completed** |
| Fully compatible independent cross-coast/meta effect studies | **0** | The primary global meta-analysis effect **NOT ESTIMATED** |

Each of the eight Zenodo records was checked via its **own first-party public /api/records/{record_id}** response. All eight passed *metadata* source gate. File year counts (GPS / ACC-classified behavior): O_VLIELAND **6 / 6**, HG_TEXEL **10 / 10**, LBBG_TEXEL **13 / 11**, LBBG_SCHIERMONNIKOOG **4 / 4**, LBBG_ZEEBRUGGE **11 / 0**, DELTATRACK **3 / 0**, O_WESTERSCHELDE **3 / 0**, O_AMELAND **4 / 0**. These are publisher catalog **file-year counts, not numbers of independently tested species, birds, or field effects**.

### New strong opportunity: published 2026 gull behavior classification

The newly updated [HG_TEXEL](https://zenodo.org/records/23923176), [LBBG_TEXEL](https://zenodo.org/records/23942209) and [LBBG_SCHIERMONNIKOOG](https://zenodo.org/records/23919012) collections contain published GPS plus ACC-inferred behavioral classification file years. Unlike older GPS-only gull analyses, these may permit cross-species and between-island tests of comparable (but GULLIVER-**not** oystercatcher native classifier) behavior. The new metadata validation **does not prove native file row counts, same bird GPS-time source match, behavior accuracy across taxa, environmental tide coverage, or any positive tidal effect**.

### Crucial geographic bias

All four currently source-confirmed behavior classifier collections are in the **Netherlands** (Vlieland, Texel, Schiermonnikoog). Other published biological sources in the candidate register include **Belgium, China and Japan**, but those have not passed effect eligibility for a common temporal behavior endpoint. The Canada Arctic lake data are intentionally **not an ocean tide study** and may only be a solar-clock negative-control family.

This means **the raw-behavior source audit is not yet global**. The global physical tide datasets (GESLA-4 / FES2022 / TICON-4) provide environmental coverage, **not automatically a global animal behavior sample**. Publication selection and regional opportunism remain large potential biases. Do not label this a completed global meta-analysis, even if one Netherlands species has 193k observations.

## Two linked analyses to deliver next

1. **Literature meta** — review full text of the 197 candidate metadata records plus backward/forward references, exclude unrelated findings without hiding them, extract compatible effect/variance values or stop. Taxa include coastal birds, fish, crustaceans, molluscs, insects; marine lab-clock effects held separate from field timing. Two independent screeners ideally; record PRISMA stage counts and exclusion reasons. No summary effect from title snippets.
2. **Source-backed raw time-series meta** — cohort-specific out-of-week clock/solar/tide phase tests across separately sourced species/sites (first gull ACC source records then China/Japan if valid original timed behavior). Site and source clusters, classifier calibration, phase-gauge error, latitude/daylength, coastal exposure and ALAN as moderators. For any endpoint family require >=3 geographically independent original sites, >=3 taxa and >=2 functional groups before pooling; separate ocean regions for an explicitly worldwide claim. Since none meet this today, the `effect_ledger.json` intentionally contains zero effects.

**Hypothesis prioritized:** **physical opportunity gating**: the larger the fraction of actually-used habitat switching accessibility across the local tidal cycle, the stronger the unique tide-dependent behavioral component *after conditioning on real solar time, sampling schedule and environmental history*. True local habitat elevation-water datum (`z(x)-h(x,t)`) is a separate mechanistic test; station stage alone is not proof. Test alternative tidal-current/prey and risk-mediated mechanisms and retain negative cohorts.

## Provenance
- Global tide: [Hart-Davis et al. 2026](https://doi.org/10.5194/os-22-1681-2026), GESLA4 sources and FES2022.
- Circadian–circatidal review: [Rock et al. 2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC8914038) and [marine rhythms review](https://doi.org/10.1146/annurev-marine-030422-113038).
- Independent behavior source start: [oystercatcher datasets](https://doi.org/10.3897/zookeys.1123.90623), [2026 gull native source](https://zenodo.org/records/23923176) and [China shorebird candidate](https://doi.org/10.5061/dryad.51c59zwm3).
- v130 single-site genuine field historical pilot: [previous Japanese result](V130_OBSERVED_2018_MATCHED_WEEK_HOLDOUT_TIDE_PHASE_RESULT_JA.md). **Never counted as worldwide independently replicated.**
