# v17-B completed: true independent pigeon pairing structure is five four-bird networks, not twenty birds or ten dyads

**2026-10-28 JST — FINAL SOURCE TOPOLOGY ENDPOINT. Observed partner assignments from a third-party published supplementary table; NO GPS behavior, turning forecast or wind × social coefficient was fitted.** This is **not** a finding that the birds exchange navigational information, follow partner motion, or have ecological niches.

## Original citation, data provenance and reproduction

Taylor et al. (2019), *Birds invest wingbeats to keep a steady head and reap the ultimate benefits of flying together*, PLOS Biology 17:e3000299, [article](https://doi.org/10.1371/journal.pbio.3000299) and **[S3 Table, original bird and pairing XLSX](https://doi.org/10.1371/journal.pbio.3000299.s008)**.

The published original S3 table was successfully fetched directly from the publisher:
- `https://journals.plos.org/plosbiology/article/file?id=10.1371/journal.pbio.3000299.s008&type=supplementary`
- XLSX **12,200 bytes**, recorded original SHA256 `f06a89cdb0bb4df338337c1d2f459d7eee545289ede06904bc76114653981e84`.
- One worksheet, exact headings: `A:Bird ID`, `E:Partner ID` under *Similar-sized pairs*, `I:Partner ID` under *Different-sized pairs*, **20 original bird records**.
- All 20 identifiers are reciprocal and exactly matched the subjects in the supplementary table. `B01–B82` in phase 2 and `B01–B07` in phase 3 reproduce the named examples in the original paper.
- [Source-only acquisition run 40623881771](https://github.com/zuizui0223/boids/actions/runs/40623881771): 4/4 source/no-telemetry tests passed. [Independent full S3 graph run 40624071037](https://github.com/zuizui0223/boids/actions/runs/40624071037): all 8 source/graph tests passed, complete SHA/reciprocity/connectivity checks and a **fail-closed eight-cluster gate**.
- Executable parsing code: `validation_v17/published_S3_pair_source.py`, `published_S3_graph.py`; read-only verified summary: `validation_v17/results/original_s3_pair_graph_v17.json`. Neither raw GPS nor body-mass/tarsus/airspeed numerical source traits was examined for model prediction or distributed.

## Exact original **experiment-wide** graph

Define `V` as original 20 pigeon IDs, `E_2` as the undirected similar-sized phase-2 assigned pairs, and `E_3` as different-sized phase-3 pairs. The full experiment contact-opportunity topology is `G=(V,E_2 ∪ E_3)`, **not** the graph of GPS-derived proximities.

| Original connected group | All 4 bird identifiers | Phase 2 paired dyads | Phase 3 paired dyads |
|---|---|---|---|
| C1 | B01, B07, B82, B87 | B01–B82; B07–B87 | B01–B07; B82–B87 |
| C2 | B61, B84, S25, S87 | B61–S25; B84–S87 | B61–S87; B84–S25 |
| C3 | B65, S13, S27, S84 | B65–S84; S13–S27 | B65–S13; S27–S84 |
| C4 | B67, B80, S05, S12 | B67–B80; S05–S12 | B67–S05; B80–S12 |
| C5 | B75, S03, S06, S30 | B75–S06; S03–S30 | B75–S30; S03–S06 |

**Computed exact structure:**
- `|V|=20`, `|E_2|=|E_3|=10`, no repeated pair between two experimental phases, all reciprocal.
- Each source bird has exactly two distinct original partners across phases, one per assigned paired phase (`degree=2`); 20 unique graph edges total.
- `G` has **exactly five disconnected components**, all consisting of four bird IDs and four edges. Every component is the cycle graph **C₄**.
- For each bird, two birds are direct assigned contacts across the two phases and the fourth component member is connected by two graph steps. **This describes only possible experimental information pathways; it does not measure actual transmission**.
- A single-phase comparison has 10 independent dyads **within that phase**, but these cannot be treated as 10 independent experimental units for a model that analyzes **both phases** or trains across different partners: the shared identities connect pairs into 5 four-bird clusters.

## Predeclared confirmatory admission: **FAILED, as required**

The preregistered v17-B contract in `docs/V17_PUBLISHED_PAIR_GRAPH_CONTRACT.md` required **at least 8 independent original bird-connected social-network components**. The actual experiment has **5**. Therefore `eligible_for_confirmatory_v17_wind_neighbor_forecast=false`. This decision was established before computing any GPS turning model, wind context effect, or forecast outcomes.

**Do not:** split same-component bird IDs across training and test, count 458 GPS files as 458 independent pairs, count 10 two-bird pairs as 10 independent units across both phases, change the threshold to 5 after inspecting the source, or call a future exploratory model a preregistered confirmatory test.

Five components are **an upper bound** for independent network replication in this single experimental setting; birds may additionally share the same loft and meteorological conditions, which further limit external generalization. For a five-component unanimous sign test the best one-sided exact p-value could be 0.03125, but that mathematical possibility does not override the **pre-fixed eight-component design requirement** or grant an unobserved prediction effect.

## Separate wind-clock identification limit remains

The v17-A3 raw weather data have 152,227 serial-day records interpreted as 2015; weather within 90 seconds of a GPS source timestamp is available under candidate shifts 0, −1 and +1 hours at 100%, 97.93% and 99.67%, respectively. **These coverage rates do not determine the correct weather clock offset.**

Independent Cumulus documentation explains that **Cumulus 1.9.4 standard logger records system-local time**, including summer-time behavior ([Cumulus Wiki Standard log files](https://cumuluswiki.org/a/Standard_log_files)). Original Taylor et al. weather data were additionally exported/processed into a **three-column MATLAB serial-day CSV**, not an unaltered Cumulus standard monthly log, so station-local time does **not** prove the exported serial days are BST without a documented source conversion. It remains `timezone_not_verified`; neither a particular wind-from/wind-to convention nor a selected UTC offset is authorized for behavior forecasting.

## Connection to v13 toy Boids and next falsifiable claim

The natural experiment's pairing transition is a precisely known change in contact opportunity: each C₄ changes between two disjoint **perfect matchings** of four birds while the full experiment's connected group membership stays fixed. This is conceptually related to how v13 separated physical steering from socially shared resource *choice*, but the real source measures no experimental reward history or long-term resource occupancy. The comparison is **structural**, not mechanistic confirmation.

The next valid field programme needs another independent GPS/wind/social-partner source with >=8 disconnected *pre-outcome defined* social groups or sufficient truly independent sampling units, verified weather station timezone and original synchronized pair fixes. Test a new frozen wind-by-partner predictive gain on entirely heldout groups. Do not refit v15/v16 observed primary endpoints or the v13 simulator receipts.

**Final status:** verified source topology and **necessary confirmatory STOP**. The failure to admit is a successful scientific data-integrity and inference check, not an empirical negative behavioral result.
