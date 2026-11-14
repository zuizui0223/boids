# v131 targeted global study audit — genuine evidence categories beyond the Netherlands pilot

**Date 2026-11-14 JST.** This is a targeted **non-exhaustive** selection of primary scientific articles, source-researched separately from the first 197 Europe PMC bibliographic candidates. Source: `validation_v131/targeted_paper_triage.json` has 10 exactly named records. This document is not a PRISMA 2020 flow chart; individual samples and effect SE are not harmonized. The prior v131 original-source census (8 actual Zenodo publisher catalog passes) and zero eligible primary meta effects remain unchanged.

## Six independent *source-context examples*, different ecological endpoints

| Original study/region, DOI | Taxa & ecological process | Observed relevance | Eligibility boundary |
|---|---|---|---|
| Ware et al. 2023, British Columbia, Canada [10.1002/ece3.9957](https://doi.org/10.1002/ece3.9957) | 20 black oystercatchers `Haematopus bachmani` tracked across **4 nested BC regions**, coastal habitat choice | Coastal high-intertidal foraging areas preferred specifically at low tide; predation-refuge and light also considered | Original GPS deposited in Movebank study **696824680**, yet GPS source rows/unbiased site effects not source-audited; four regions nested under one paper/cohort |
| Keirsebelik et al. 2025, Scheldt Belgium–Netherlands [10.1186/s40462-025-00548-3](https://doi.org/10.1186/s40462-025-00548-3) | `Eriocheir sinensis`, **34 tagged, 33 detected**, 90,107 original acoustic detections, 6 sensors with accelerometers; downstream spawning migration | In non-tidal river primarily **night-associated**, in tidal estuary downstream transport preferentially on **ebb** | Source data [European Tracking Network DOI 10.14284/726](https://doi.org/10.14284/726), no native source QA done; river turbidity, current, receiver effort and location confounded; all one watershed |
| Goldsborough et al. 2023, Jicarón Island **Panama** [10.1098/rsos.230355](https://doi.org/10.1098/rsos.230355) | Coastal white-faced capuchins `Cebus capucinus imitator`, >5 years camera surveys | Coastal activity of tool-using groups more consistently tied to tide than non-tool users; candidate **resource access and tool-use moderator** | Camera detection ≠ ingestion; original tide reference at **~90 km away**; one island. Supplemental [Figshare DOI 10.6084/m9.figshare.c.6837151](https://doi.org/10.6084/m9.figshare.c.6837151) |
| Ethève et al. 2026, European kelp forest [10.1186/s12862-026-02521-z](https://doi.org/10.1186/s12862-026-02521-z) | Fish soundscape community, environmental tide, underwater visual census | Fish **acoustic activity** higher at **low water**, visually seen fish **abundance** higher at high water — *observation endpoint matters* | 26 sound categories not 26 taxa; original supplement contains 3 analysis datasets (acoustic/environment/UVC); hydrophone current masking and detection require source gating |
| Ekrem et al. 2025, Roscoff, Brittany, France [10.1111/ele.70139](https://doi.org/10.1111/ele.70139) | Intertidal insect `Clunio marinus` two sympatric lunar timing strains; genotype-by-elevation + theoretical coexistence | Full-moon vs shifted new-moon low tide emergence determines **spawning waterline** and larval **spatial separation**; *time-to-space mechanism*, not just synchrony | Data/code [EDMOND DOI 10.17617/3.LNP6DC](https://doi.org/10.17617/3.LNP6DC). Coexistence mechanism modelled; same system as Jacobsen 2026 theory, not a second independent field cohort |
| Florida 2023 [10.3390/ani13223548](https://doi.org/10.3390/ani13223548) | 3 plover species, mudflat vs beach, **38 same island** surveys | Standardized tide coefficient for mudflat count negative in each species, beach count positive, but mean observed **peck rate did not differ clearly with tide** | **Only 07:30–10:30** sampled => CAN contribute to tide-only habitat use, **CANNOT identify solar day/night or tide×solar**; 3 species all same coast, strong correlated effect dependence |

Additional mechanism/control sources:
- Japan Goda et al. 2006 [10.5179/benthos.61.26](https://doi.org/10.5179/benthos.61.26): two sympatric mud crabs in **two Ehime estuaries** show species-specific diel and feeding-habitat use but actual tidal phase and compatible SE are not established. Field *solar/feeding niche* candidate, not automatically tide-specific.
- Underwood et al. 2025 [10.1371/journal.pone.0329449](https://doi.org/10.1371/journal.pone.0329449): marine `Marinogammarus marinus` vs freshwater `Gammarus pulex` **laboratory ALAN light** experimental manipulations; confirms light responses can differ functionally, but has **no wild field tide×light effect**. Raw laboratory records available as [University of Southampton 10.5258/SOTON/D3024](https://doi.org/10.5258/SOTON/D3024).
- Jacobsen et al. 2026 [10.1371/journal.pcbi.1014235](https://doi.org/10.1371/journal.pcbi.1014235): simulations of `Clunio` competition and allochronic divergence. **Theoretical** extension of same Roscoff field system, exclude from wild-field replication count.
- China Leizhou shorebirds [Dryad 10.5061/dryad.51c59zwm3](https://doi.org/10.5061/dryad.51c59zwm3): promising extra-European candidate, but timed original GPS and stage/solar / endpoint still **not** source verified.

## One *real paper-level* secondary tide-only effect family: Florida plovers

From published Table 1 Poisson GLM with standardized tide and wind and tide×wind interaction, the **mudflat abundance** tide coefficient conditional on mean standardized wind is:

| Species | Tide `beta` | Original paper `SE` | Same study/coast |
|---|---:|---:|---|
| Piping Plover, `Charadrius melodus` | −0.40 | 0.15 | Outback Key, Florida |
| Snowy Plover, `Charadrius nivosus` | −0.45 | 0.07 | Outback Key, Florida |
| Wilson's Plover, `Charadrius wilsonia` | −0.11 | 0.03 | Outback Key, Florida |

These are **original report estimates, not new raw analysis and not a cross-species global meta**. The tide predictor was standardized; species GLMs are based on **the same 38 morning survey dates/one island**, and tide×wind interactions mean the tide coefficient is conditional, not an average unadjusted tide effect. They are in `validation_v131/targeted_paper_triage.json` **only as secondary published data**, NOT the primary effect ledger. No spurious three-site meta from three plover taxa.

## Deepening the ecological mechanism: from periodic signals to niche organization

The previous v130 only establishes **within-source predictive information** of measured tide on ACC classifier share. The cross-taxonomic evidence suggests at least **three different causal channels**: 
1. **Substrate access gating:** the part of shoreline exposed at local tide varies, so terrestrial birds, mammals and intertidal insect oviposition change space use. This predicts tide coupling only where habitat actually switches accessibility, not all sites with large astronomical tide.
2. **Current-mediated transport:** moving aquatic organisms can use flood/ebb current vectors and depth, with optimal *tide phase opposite* to that of low-tide terrestrial access; the mitten crab exemplifies use of ebb migration rather than exposed flats.
3. **Predation/light/behavioral detectability:** nighttime predation risk and visual vs acoustic detection change which cycle dominates the observed *endpoint*. Do not interpret fish sound counts as fish counts or GPS activity-class shares as feeding minutes.

**Stronger prediction:** Not every species needs a strong intrinsic tide clock. Organisms should show tide-specific out-of-source predictive information **only when their experienced payoff gradients depend on the tide**, via substrate availability, current transport, prey/predator access, or locomotor constraints. The sign of a simple tide-height/phase coefficient can legitimately reverse across functional groups. An interesting emergent mechanism is **temporal → spatial niche translation**, not mere day-night separation. Clunio field+model shows niche partition can aid coexistence when timing changes where descendants live; temporal staggering alone need **not** stabilize coexistence.

Formalizable two-level program:
- Cohort-specific *predictive* `\Delta L_{g,c} = L(M_{clock+solar}) - L(M_{clock+solar+tide})`, and correct tide vs **matched-support** phase ghosts; compare only **same score family** and same pre-outcome sourced records.
- Cohort/site **access switching amplitude** `G_c = mean_x Var_t 1[z_c(x)>h_c(x,t)]` (or analogous validated flow-opportunity metric); test whether `G_c` and direct field prey/behavior channel predict `\Delta L`, after adjusting for tide measurement quality, environment, sampling, taxon and detection. `G_c` is **proposed**, NOT yet computed or empirically validated globally.
- Verified **time-niche partition** separate from plain response: community/strain overlap in *joint time×space* utilization conditional on equal sampling and shared habitat composition. Test stabilizing ecological coexistence only if population outcomes or mechanism data are present.

The macroscale causal question becomes **“Under which ecological opportunity channels do solar and tidal cycles create behavior synchronization, resource partition, and ultimately coexistence?”**, not the trivial “Do tides correlate with animal behavior?”

## Critical data quality / next acquisition

First-priority native raw/IPD candidates: Canadian black oystercatcher Movebank study 696824680, European Tracking Network mitten crab original, Panamanian capuchin Figshare research collection, French kelp fish supplementary environmental+acoustic+UVC 3 datasets, Clunio EDMOND genetic-elevation field and coexisting chronotypes. These cover birds, crustaceans, mammals, fish and marine insects but **do not share one common behavior response**; each is a **different meta-analysis endpoint family** requiring a common effect definition/SE, a documented independent coast unit and original time/effort checks. Expand more ocean regions before global moderator inference. PR v131 remains DRAFT with zero primary compatible pooled effects.
