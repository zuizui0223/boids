# v26 source-backed ecology eligibility: original marine turtle has 23 PITs but no verified used case; mammal and vole archives exceed cap

**2026-10-29 JST.** This is a **new, fully reproducible independent original-source quality and scientific identifiability result**, NOT a new observed ecological effect. Source-only originals are separate from previous pigeon, bat/duck, guineafowl and California brood projects. All v13–v25 frozen endpoints including v25-F corrected private-history non-support remain unchanged.

## 1. Independent USGS marine turtle original source: actual raw-file authenticity PASS

Hart, Smith, Burkholder & Roberts (2020), *Integrated step selection analysis of turtle tracking data in the Florida Keys National Marine Sanctuary, 2008–2019*, USGS [DOI 10.5066/P9UZU4GG](https://doi.org/10.5066/P9UZU4GG), ScienceBase `5faab074d34eb413d5df1f41`, publicly available USGS source.

The original `Hart et al_iSSA.csv` was **actually downloaded and full-file provider MD5 verified**:
- Exact provider bytes: **45,669,515**
- Provider original MD5: **`5c5f25398720a663ae332097b49bf740`** independently matched
- Independent SHA256 computed: **`eef4d2dd16c97cd0d8722ed1cac8a031cf3dd336404b2e8e4c085cb2fadd4ec0`**
- Physical CSV data lines: **420,365**
- Exactly 11 original named fields: `orgnl_pit,step_id,step_length,log_step_length,turn_angle,cos_turn_angle,start_time,end_time,protected_status,water_depth,chlorophyll`.

[Original full-source MD5+header CI 40848688649](https://github.com/zuizui0223/boids/actions/runs/40848688649), 4/4 synthetic source/no-leakage tests and full original data source pass. [Original-source receipt](../validation_v26/results/turtle_original_header_v26.json).

### 2. Actual individual × step × time independence: source structure verified, ecological choice **NOT ADMITTED**

A separate [registered PIT/step/time contract](V26_TURTLE_PIT_STEP_TIME_SOURCE_CONTRACT.md) and [passing original source audit CI 40849441133](https://github.com/zuizui0223/boids/actions/runs/40849441133) read ONLY original source `orgnl_pit,step_id,start_time,end_time` categoricals, not animal direction, movement length, numerical water depth, chlorophyll or protected-region ecology.

| Original source structural unit | Actual measured source structure |
|---|---:|
| Distinct PIT identity tokens | **23** |
| PITs with ≥3 different calendar days | **23** |
| Original PIT × step-ID keys | **26,997** |
| PIT × recorded start/end time keys | **26,451** |
| Rows with both dates parsed | **420,365** |
| Most common number of rows per PIT × step-ID | **16** (23,949 keys) |
| Largest original PIT identity's rows | **382,560 / 420,365** (~91%) |
| Explicit source `used/case/available` field | **absent** |
| Author-verified chosen-vs-random step label | **unavailable** |

The source has many repeated individual and generated-step observations, but one PIT token accounts for roughly 91% of all rows. **Do not treat all 420,365 observations as independent animals or environmental replicates**, or assume that 23 PIT tokens imply 23 equally informative moving individuals. The source has no original latitude/longitude fields to recover absolute turtle paths. The observed `water_depth` column is an environmental depth, not direct measured swimming altitude.

**Scientifically necessary decision:** `SOURCE_TURTLE_GRAIN_VERIFIED_CHOICE_NOT_ADMITTED_NO_VERIFIED_LABEL`. The original source's 11 columns lack explicit observed/available case labels. `step_id` values are numeric tokens without documented source semantics to identify which one of typically 16 associated rows was chosen. Reconstructing the "used" case from first/last row order, the shortest length, the most favorable habitat or an assumed 1:15 pattern would **invent a response definition**. Thus no sound new observed used-vs-available ecological choice model has been fitted. This is a source-identifiability stop, **not** evidence that turtles ignore depth/chlorophyll or that individual memory does not operate.

[Full aggregate PIT/group distribution (no original IDs or times)](../validation_v26/results/turtle_pit_step_time_v26.json).

### 3. Independent full-byte source dictionary integrity failure, not biological negative

The official original FGDC `iSSA data release V3.xml` was listed as **22,606 bytes**, MD5 `bb23daf440cb8ee6932f60a8fc7293a5`. The independently downloaded 22,606-byte response computed MD5 `a6e135a664c32c76d2e957bfbb793fb4`, **different from the provider declaration**. It was **not accepted as verified original metadata**, and no case-label convention was inferred from it. This is a separate source-integrity boundary. [Dictionary CI 40849036359](https://github.com/zuizui0223/boids/actions/runs/40849036359). The original turtle *CSV* itself passed its own independent full MD5 and is not invalidated by this XML discrepancy.

## 4. Global mammal and social bank vole source sizes — metadata verified, data excluded

| Independent published dataset | Provider original main file | Declared bytes | Decision |
|---|---|---:|---|
| Franke et al. 2026, terrestrial mammals 48 species / 1,344 GPS tracks, Zenodo `15756163` | `Data_locallandscapelevelconditions_stepselection.zip` | **1,788,505,978** | Exceeds precommitted 250-MB/file cap; not downloaded |
| Pohle et al. 2024, simultaneously tracked bank voles, Zenodo `10101651` | `Pohle_et_al_2023_BehavioralStates_iSSA_Data.zip` | **662,165,095** | Exceeds cap; not downloaded |

These are **provider-listed files** and the author-published study sizes, **NOT new independent original-animal sample counts verified by this project's ingestion**. The original Zenodo 48-mammal source is CC BY 4.0. Its separate 3,580-byte `README.txt` **was** downloaded and publisher MD5 `b03a51664b620a2cdd3cc38bb20b4215` independently matched; new SHA256 `233d27e610bf52b8ab3cfaed90b913f6ea1f27c1ff24483cc4e0e237904e3b82`. The README establishes original nested RDS lists, **19 iSSA fields with explicit `case_` TRUE used/FALSE available**, and NDVI, terrain ruggedness, human population density and road distance source covariates. It explicitly says the distributed data are **processed annotated steps without raw GPS coordinates**. This source could support better macroecological conditional habitat selection if it becomes feasible to ingest under a separately registered large-data workflow, but no endpoint exists now.

The bank vole source has a 28,397-byte original code ZIP (not yet downloaded) and author data archive of 662 MB. The PeerJ publication concerns latent behavioral states and **simultaneously tracked bank vole contacts**, potentially relevant to movement and social information. However its original case-control animal records were not downloaded, so no true social-neighbor, memory, or habitat-choice contrast was tested. [Original vole source manifest CI 40849841604](https://github.com/zuizui0223/boids/actions/runs/40849841604).

[Original combined USGS/Zenodo source manifest CI 40848377952](https://github.com/zuizui0223/boids/actions/runs/40848377952). Full source/README dictionary receipts and original archive sizes are in `validation_v26/results/`.

## 5. Implication for a defensible Boids ecological theory

These source results expose an information-layer boundary: **physical movement steps, statistical choice labels, environmental availability and synchronized social contact are different observations**. Having numerical step length/angle + environmental fields alone does not identify which route was chosen relative to a verifiable alternative, or whether another individual caused a turn.

The previously frozen evidence remains:
- **v23** raw Bangladesh dabbling-duck GPS + previous-day ERA5: individual own past daily spatial spread improves next-day spread prediction in 44/49 original ducks; weather-bin alone and fixed shrinkage increment not robust.
- **v24** USGS Suisun brood source: five environmental habitat attributes predict static used vs generated nest-accessible alternative points for 185 heldout broods, but genuine dated individual wetland history not recorded.
- **v25-F** corrected California four-waterfowl source habitat profile: common habitat source ranking surrogate positive, birdyear-private history increment **not supported**; v25-D original "100% accuracy" was an identified case-specific source scale artifact, not ecological evidence.
- **v26** marine turtle source structure verified but used-case identification absent, 48-mammal and bank vole original sources exceed safe data size limits. **No new biological predictive effect is reported.**

A useful next genuinely independent validation dataset needs original source `individual ID, timestamp, observed case, generated alternatives, choice-set ID, start position/time, environment for ALL alternatives`, paired with accurate origin of the movement kernel and an independent year/animal holdout. If these are missing, record NOT_ADMITTED, do not reconstruct from predicted outcomes. Never claim recovered Reynolds alignment/attraction/separation forces, resource competition or 3D foraging niches without direct measurements.

## 6. Source reproducibility

Code and tests under `validation_v26/`; all five new independently executed GitHub Actions pipelines passed:

1. [Provider-only turtle+global mammal manifests](https://github.com/zuizui0223/boids/actions/runs/40848377952)
2. [Actual original turtle CSV full MD5/SHA and 11-column header](https://github.com/zuizui0223/boids/actions/runs/40848688649)
3. [Turtle FGDC MD5 mismatch and authentic mammal README](https://github.com/zuizui0223/boids/actions/runs/40849036359)
4. [Actual original turtle PIT × step × time structural proof](https://github.com/zuizui0223/boids/actions/runs/40849441133)
5. [Original bank vole social-case-control Zenodo source metadata](https://github.com/zuizui0223/boids/actions/runs/40849841604)

Original USGS/Zenodo raw animal location data, individual PIT identities, environmental response rows or other researchers' untransformed files were not committed. All earlier v13–v25 original results remain frozen.
