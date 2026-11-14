# v132 — 潮汐×太陽周期の全球・複数分類群メタ解析：年代補正後の実測文献探索と独立コホート比較

**2026-11-14 JST。** Genuine original [Actions #43585881986](https://github.com/zuizui0223/boids/actions/runs/43585881986) SUCCESS, 6/6 source known-truth tests. Source-only artifact ID **14110556853**, ZIP SHA256 **f89d423ec0f242e7b9038794a1d430d4c8232fca415d136fd7f696b669507963**. All 36 period×taxon Europe PMC queries completed, 0 failures, full query strings/responses pinned in `validation_v132/period_stratified_literature_screen.py` and the original workflow artifact. This is **bibliographic expansion, not yet a completed PRISMA review or meta-effect estimate**.

## 1. First nontrivial gain: correct the 2026 recency bias

Previous v131 7 capped search queries yielded 197 DOI/title-unique records, **121 publications (61.4%) in 2026**. New six time periods 1970–1999; 2000–09; 2010–14; 2015–19; 2020–24; 2025–26, crossed with six functional taxon terms, fixed max 40 Europe PMC original metadata results each.

- New original query rows **1,225**; matched records across queries/initial seed **361**; DOI-or-same-title/year aggregate **1,061 candidate bibliographic records**.
- Period distribution **140 / 144 / 165 / 169 / 189 / 254** (these are **max-result-censored search outputs**, NOT full literature production counts).
- Title/abstract **automatic high-sensitivity** triage: **93 possible true field tide×solar**, **57 possible tide-only field**, **24 possible clock/lab**, **19 review/theory**, **405 uncertain**, **463 unrelated**. There is no double-screen, no manually verified number of eligible studies and **no global pooled empirical effect**.
- The automatic screen is deliberately imperfect: e.g. 93 includes gene-expression studies, review items and publisher corrections; 405 uncertain may contain relevant true studies. Neither automated exclusion nor hit count can be published as systematic-review inclusion statistics. Manuscript grade requires genuine source/candidate full text and explicit exclusion ledger; v132 has advanced **discovery**, not already completed screening.
- Source quality: prior v131 eight true Zenodo metadata catalogs remain validated, but **four ACC classifier collections all from the Netherlands**. Global physical tide stations do not solve this biological sampling bias.

## 2. Original published field evidence across oceans — 15 curated distinct source records

The machine candidates led to independently sourced fulltext and publisher-abstract checks. The **15 original source records**, including one Boids field pilot, are in `validation_v132/curated_primary_ecological_evidence.json`. **15 records ≠ 15 statistically independent effect estimates**: Wadden Netherlands sources share a coast, some papers compare multiple nested sites/taxa, and endpoint families differ.

| Geographic source, original DOI | Direct source observations | What the result actually supports |
|---|---|---|
| **Portugal** Tagus vs Ria Formosa [Rodrigues 2025](https://doi.org/10.1007/s12237-025-01598-x) | **35 analyzed juveniles, same species, two wetlands**, feeding ACC classifier | Tagus wetland includes alternative rice-field feeding, diel stronger; Ria Formosa more intertidal feeding, tidal×diel interaction most supported. Tide×diel *model* AICc contrasts: Tagus additive better than interaction by 10.28; Ria interaction better than additive by 373.92. **Not a standardized effect difference**; Tagus 10 birds vs Ria 25 and tag schedules have strong daylight duty-cycle differences |
| **Australia** Port Stephens [Hewitt 2023](https://doi.org/10.1186/s40462-023-00384-3) | **18 original tagged giant mud crabs**, HMM inferred inactive/foraging | Forage more likely at **low/incoming** tide; inactivity ~79%, and hour-of-day not in selected model: tidal *water access/current + risk* channel can dominate solar time |
| **Colombia** Bahía Málaga [Pülmanns 2018](https://doi.org/10.1111/jfb.13788) | Juvenile armed snook, **one year macrotidal mangrove creeks** | Intertidal fish abundance highest **neap-night**, lowest **spring-day**; stomach fullness also depends on tidal×diel category. A separate *fish predation and prey* access channel |
| **Antarctica** Humble Island [Oliver 2013](https://doi.org/10.1371/journal.pone.0055163) | Adélie penguin foraging **10 seasons**, satellite GPS/2011 dive monitoring | Foraging sites change with **weekly diurnal vs semidiurnal tide-current regime switching**, not ordinary instantaneous low/high tide; the *relevant period* can change by channel |
| **USA** Florida Indian River microtidal lagoon [Heres 2024](https://doi.org/10.1371/journal.pone.0302433) | Spring spawning horseshoe crab volunteer survey, two within-lagoon stations | **NEGATIVE/NULL tide:** global model native tide beta +1.978, **SE 1.776**, CI [−1.503,+5.459]; wind/onshore direction more predictive. In weak astronomical tide, wind surge may dominate biological opportunity |
| **USA** Alaska [Coutré 2017](https://doi.org/10.1080/19425120.2017.1285377) | **6 analyzed juvenile sablefish**, 40-day acoustic vertical excursion | Group best AIC model = date+diel, tide adding worse ΔAIC **+2.2** and interaction +4.2; **3/6** individual top models include tide or interaction. Individual differences not captured by population-level cycle |
| **USA** 400km marsh coast [Kimbro 2012](https://doi.org/10.1890/11-0596.1) | Predator treatments + field marsh landscape tidal-regime gradient | Snail grazing **predator-mediated indirect effects reverse** between diurnal/mixed semidiurnal regimes; plant biomass consequences. Tide organizes **interaction networks and ecosystem function**, not merely animal timing |
| **Panama** Culebra [Yong & Lim 2022](https://doi.org/10.6620/ZS.2022.61-08) | **46** juvenile/adult ghost crabs, zonation and emergence | Juveniles use higher intertidal elevation and emerge more at night, indicating **ontogenetic time×space partition**; does **not** independently estimate tide-phase effect or prove stable coexistence |
| **France** Roscoff [Ekrem 2025](https://doi.org/10.1111/ele.70139) | `Clunio` FM vs NM timing genotypes and larval elevations + coexistence model | Reproductive timing changes egg waterline and **larval spatial niche**; simulated competition supports coexistence from time→space conversion, not from temporal separation alone |
| **Netherlands** Wadden [Bulla 2017](https://doi.org/10.1098/rstb.2016.0253) | **42 red knots**, >50h each | 88% birds tide periodic, 57% daily periodic, 52% both; these are periodicity detection fractions, **not pooled tide-response regression effect sizes** |
| **Canada** BC [Ware 2023](https://doi.org/10.1002/ece3.9957) | **20 black oystercatchers** across four nested regions | Space choice depends on tide and diel, but regions are nested under one published study rather than four independent cross-coast samples |
| **Panama** Jicarón [Goldsborough 2023](https://doi.org/10.1098/rsos.230355) | Coastal capuchin cameras, multiple years | Tool-using group more tide-associated; tide measured approx 90km away, camera detection and group behavior can confound |
| **USA** Florida plovers [2023](https://doi.org/10.3390/ani13223548) | 3 species with original tide-beta/SE **from 38 same-morning surveys** | All three mudflat count tide slopes negative [−0.40(0.15), −0.45(0.07), −0.11(0.03)] but **no night**, same coast and no tide×diel |
| **Netherlands** Wadden [Beardsworth 2026](https://doi.org/10.1111/ibi.70126) | 2018–2022 radio-ATLAS red knots conditional on low tides | Low tide night vs day changes patch residence, roost-distance and asymmetric home range overlap (20% vs41%). **Only low-tide subset** cannot isolate real tide vs no tide; bird-year duplicates/longitudinal sharing need checking |
| **Netherlands** Vlieland [v130 2018 genuine study](https://github.com/zuizui0223/boids/actions/runs/43581975420) | Original **35** tagged oystercatchers, **193,088** linked ACC source bins, 17 held-out weeks | On same 2018 record set real RWS tide MSE 0.128819 vs best wrong-tide 0.148567, but post-v129 exploratory model and single coast. Not an independent global effect |

**Do not pool these 15 records.** The table mixes predictive MSE, AICc, movement counts, field abundance, predator grazing, reproductive timing, and computational coexistence models. Even common p-value or odds-ratio transformation would be scientifically invalid without a source-verified comparable endpoint, valid independent observational unit and variance.

## 3. Mechanistic structure now supported as a cross-study *hypothesis*, not a pooled law

The most explanatory frame is **channel-gated temporal niche organization**.

Let the environment supply solar time `S(t)` and tide water height/flow `H(x,t),F(x,t)`. Biological tidal responsiveness is not simply a function of tidal amplitude: it depends on whether local payoffs change with tide.

\[
 U_i(x,t) = R_i(x)\,A_i(x,t) + C_i[F(x,t)] - P_i(x,t) + B_i(x,t),
\quad
 A_i(x,t)=\mathbf1\{z(x)>H(x,t)\}
\]

For terrestrial intertidal foraging, **dry exposed area** can gate access; for aquatic foragers, *inundation depth* and **flow direction** can gate access (different or opposite sign); for fish/penguins, tide may move prey or change currents; for marsh predator chains, tides gate predator access and risk; for `Clunio`, tide-lunar timing positions descendants in **different microhabitats**.

Therefore:
1. High tidal amplitude **does not necessarily** entail high biological tide dependence. If birds forage in rice fields or physical stages are tiny compared with wind surges, relevant behavior may be dominated by diel/light or wind.
2. Strong tide dependence **need not synchronize all taxa to low tide**: giant mud crabs forage in shallow incoming waters, snook neap-night inundation, seabird foraging may follow weekly current regime switching. Direction and biological temporal scale depend on *opportunity channel*.
3. Temporal rhythms do not automatically constitute **temporal niche partition**. To establish partition, need concurrent co-occurring individuals/species, same observable opportunity, differentiation beyond habitat composition and detection. To establish coexistence, a demographic feedback or test of competition is needed. Time→space conversion is a more discriminating mechanism than simple night/day non-overlap.
4. **Detection and source duty-cycle can imitate clocks.** Portugal juvenile tags mostly fix at 05–21h with one 01h fix, 2022 tags changed nocturnal schedule. Original ACC/GPS classifiers, acoustic detectability, fish sound counts and wind/tide proxy distances must be audited independently.

### Main quantitative moderator proposed

Within one **compatible endpoint family**, raw dataset/source-corrected held-out loss:
\[
  \Delta_i = \frac{L_i(M_{clock+sun}) - L_i(M_{clock+sun+tide})}{L_i(M_{clock+sun})}.
\]
Test real tide vs multiple *source-matched, physically reasonable phase ghosts* in every cohort; preserve negative gains. Define a **physically calculated local opportunity-switching index** (for terrestrial access),
\[
 G_c=\mathbb E_{x\in{\cal H}_c}\left[\operatorname{Var}_{t\in T_c}\bigl(\mathbf1\{z_c(x)>H_c(x,t)\}\bigr)\right],
\]
using actual source-verified ground elevations and stage reference. For aquatic current or depth channels, create separate corresponding environment effect rather than treating `G=0` as absence of tide effect.

Then fit independent-site, grouped-endpoint, taxon/phylogeny-aware meta-regression `\Delta_i \sim G_i + current_i + predator_i + ALAN_i + effort_i + random(coast,study,taxon)`, only after actual original source-stable `\Delta_i` and uncertainty in **several independent coasts and ecological channels**. Earlier minimum >=3 site clusters, >=3 taxa, >=2 functional groups for any tentative cross-taxon synthesis remains a *minimal source gate*, not proof of power.

## 4. Next original data priorities — genuine macroanalysis, not endless bibliographic listing

**P1 cross-site same original behavior:** native GPS×ACC year overlap source QA for 2026 original Texel/Schiermonnikoog gull classifiers, with real independently matched gauges and source function labels. Distinct classifier species and site accuracy must be proven before comparing tide response across oystercatcher and gull.

**P2 genuinely outside Europe raw response:** Australia 2023 `Scylla` acoustic HMM [public code](https://github.com/DEHewitt/gmc_vps_hmm) and IMOS ATF source; Antarctica Adélie publisher raw GPS/dive; Panama shore/mammal cameras; Colombia fish original tidal×diel stomach data; USA USGS and government field count source. For shared primary effect families, reanalyse only if raw original timestamps, sampling effort and tide local are reliably available. **No raw source ⇒ STOP**, not a false negative.

**P3 1,061 human-screened bibliographies:** Prioritize 93 automated dual-cycle suggestions and 405 uncertain citations (not just 93 positives), source-verify independent taxa/coasts, full PRISMA exclusion + publisher data code. Independent paper duplicates and nested Wadden/Portugal/Florida samples must be accounted for.

**Status:** searchable global bibliography expanded and 15 source-backed examples curated across seven broad marine regions, but **global pooled biological meta-effect remains NOT ESTIMATED**. The new substantive insight is a set of precise *positive and negative mechanism discriminators* for the coming quantitative test, not a claim that every coast follows the same tide clock.
