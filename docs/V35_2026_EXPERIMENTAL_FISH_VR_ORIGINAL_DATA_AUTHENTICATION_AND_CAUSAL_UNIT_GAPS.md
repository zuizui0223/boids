# v34–v35 verified original 2026 VR fish source discovery and the missing causal-unit schema

**2026-11-24 JST. Important: this is ORIGINAL AUTHOR SOURCE DATA-ADMISSION progress, not a new measured experimental fish social effect.** PRX/PLOS original small ZIP/code/README source and all PLOS large 2R/C1/C2/C3 DAT files have now been checked against original provider MD5 and byte sizes, including a controlled Figshare 1-hop source URL process. **No experiment-level intervention effect fitted by our code.**

## Why this matters for the Boids v33 study

The genuine EIDC MacGregor–Ioannou 2021 84-trial/12-original-shoal study established that present velocity of correctly assigned nearest three fish has source-conditional predictive benefit over current whole-group movement and one fixed neighbor-velocity permutation, yet an exact spatial common-driver analytic model with **zero causal fish-to-fish arrows** can produce the same positive comparisons. To move beyond retrospective correlation, we need a controlled manipulation of another entity's response to a real fish. Two 2026 original experiments provide possible independent source families.

## Source family A: Kang et al 2026 PRX Life closed-loop 1 real + 4 virtual fish

Published DOI **10.1103/18qw-sfyd**. Original provider Figshare [DATA 31378621](https://doi.org/10.6084/m9.figshare.31378621), [CODE 31386349](https://doi.org/10.6084/m9.figshare.31386349). Both original author ZIP files were retrieved from unchanged official Figshare URLs via an independently verified **single official 302 redirect** to exact original Cloudflare R2 hostname, and **published original file size / MD5 match**:
- Original Figs.zip **1,863,466 bytes**, original MD5 **4514391ae74d0715969159b9eda9c11a**, recomputed SHA256 **626b8e88e4df6de2ec95fdc0dd1066d1e979a5a199515133d7556a306b4973dd**; source-only archive central directory lists **70 original members**. The member Figs/Fig2/traj_exp.dat is a **1,572,996-byte candidate experimental trajectory**. The member Figs/FigS3/traj_sim.dat is **2,359,851-byte SIMULATION**, not independent fish evidence. We DID NOT extract either data member.
- Original Model code.zip **181,872 bytes**, original MD5 **4e6cf4d167c6204d4f557ae456ed5ba1**, SHA256 **920ad8a9f89d32cfc4ec9adf9a1311185f5700050e419b532f424637cc904111**; **37 archived members**, not executed.
- Subsequently source-safe v34e inspected **16 original author FIGURE README small documents + 2 CODE README documents**, each under the source caps, and indexed source descriptors for k_V, real/virtual, time and column formats. Some original README documents describe k_V and fish measurements. **None proved a full per-trial k assignment, repeated real fish subject/session identity, source physical clock AND real/virtual track fields joined for all experimental trials.** Therefore exact published trial-level reanalysis status remains **SOURCE_TRIAL_INTERVENTION_IDENTITY_NOT_ADMITTED**.
- Checksums/manifest [v34d](v34_verification/AUTHENTICATED_2026_ORIGINAL_AUTHOR_FOUR_SMALL_SOURCE_FILES_ZIP_TOC.json), original README audit [v34e](v34_verification/PRX_2026_AUTHOR_ZIP_18_READMES_SOURCE_SCHEMA_NO_TRIAL_IDENTITY.json), all original authors' source no-effect Actions [#45368792758](https://github.com/zuizui0223/boids/actions/runs/45368792758), [#45369497172](https://github.com/zuizui0223/boids/actions/runs/45369497172).

## Source family B: Escobedo et al 2026 PLOS Computational Biology 3D closed-loop VR fish

Published **2026-08-03**, DOI [10.1371/journal.pcbi.1014544](https://doi.org/10.1371/journal.pcbi.1014544), original provider [Figshare 30539666](https://doi.org/10.6084/m9.figshare.30539666). Authors describe four separately recorded regimes:
- **2R:** two real fish, published 16 one-hour replicates;
- **C1:** natural-speed virtual companion that reciprocally responds, 8 one-hour replicates;
- **C2:** faster virtual companion **reciprocally responds** to real fish, 12 replicates;
- **C3:** same faster virtual companion but its **social response DISABLED**; real fish may follow one-way, 8 replicates.
**C2 vs C3** manipulates the virtual controller's reciprocity at the same approximate speed, unlike C1 vs C2 which changes virtual speed. The existence of original author conclusion on persistent directional coordination despite nonreciprocal virtual fish must be credited to the authors; it is NOT a result we newly measured.

### Exact original experimental files and what was actually authenticated

[Full publisher source MD5/schema audit](v35_verification/PLOS_2026_ALL_FOUR_ORIGINAL_FIGSHARE_DAT_MD5_SOURCE_FORMAT_ONLY.json), [all 4 original original-source CI jobs #45370055482](https://github.com/zuizui0223/boids/actions/runs/45370055482) SUCCESS. Total original source **194,350,605 bytes**, not redistributed; each full original file streamed from original Figshare+one allowed original source CDN redirect through provider MD5, original exact declared bytes and new SHA256. Only the number/form of source tokens in the first 12 rows was checked; original source coordinate/numeric values NOT logged.

| Original filename/experimental arm | Original source bytes | Verified original SHA256 | Original newline count |
|---|---:|---|---:|
| 2R-TwoRealFish.dat | 34,978,800 | 8d55d2b5a03ab5193111b21081074fac2214c2afbf4bd3ba1286c73a0b524f9c | 437,235 |
| C1-OneReal+OneVirtual.dat | 37,289,920 | 6b3dc238750d085285c9c4d21690e87a71e3d63ea72ec81cd7fd7cf54ec7ca37 | 466,124 |
| C2-OneReal+OneVirtual.dat | 65,786,880 | 23a0ea8ff2cb6112e64cff5ea4cc0dc201f844b9ea02f28962ac51fc3c829745 | 822,336 |
| C3-OneReal+OneVirtual.dat | 56,295,005 | 5137c1aa90ebed10edfcaf6f4d791a823f290caccfe06a47e8e2e93d8ba2e5d1 | 712,595 |

**Critical source result**: All four original DAT files appear to be ASCII numeric data, and each of their first 12 complete text rows has **exactly nine numeric fields**, **zero text header fields**. Thus we cannot yet know the actual field meanings, source sample clock, trial boundaries or individual real/virtual identity from the data file itself. The original paper describes a 9-variable instantaneous behavioral state (horizontal speed, vertical speed, wall distance and incidence, depth, interindividual distances/angle and heading difference), but **9 data columns are not proof that they correspond to these nine states in that exact order**. Could be derived observables rather than raw 3D XY tracking; do not infer.

**Major prospective causal lag issue**: original paper describes original trajectory preprocessing with filtering, interpolation for gaps under 1 second, and a **symmetric Gaussian smoothing kernel width h=0.5 second**, used with support about **±2 seconds**. If published original DAT values reflect that preprocessing, values at t can incorporate positions from later source frames. The source file's preprocessed/raw status is unknown. Applying our prior v30/v33 0.2-second motion-age prediction to these data without authenticating their processing would conflate source smoother support with biological cue latency. The paper also describes real-time VR position exchange ~30–90Hz; that **does not** identify the frequency of these published DAT rows. Need original sample clock from source documentation.

### Missing experimental source gate before novel reanalysis

This independent published study offers the scientifically relevant **reciprocal C2 vs unilateral C3** comparison. But the dataset's nine numeric fields have no header, no explicit session/subject ID, and no verified real/virtual orientation, so a future causal experiment-side reanalysis cannot pool numeric rows as independent replicates or assume 12 vs 8 original sessions can be reconstructed from row counts. Before any new behavior model:
1. Obtain author-authenticated original DAT schema/code reader mapping each column, its coordinate/time units and original preprocessing state.
2. Recover explicit source session boundaries, original biological fish IDs and any cross-condition subject repetition.
3. Freeze original session-level outcomes and the *specific* controller-reciprocity effect prior to examining any original C2/C3 behavioral values; split/cluster by true original experiment unit.
4. Preserve a negative or inaccessible source audit rather than turning 9 unlabeled columns into invented raw fish position time series.

Original PLOS code Model3D-VR.py and Parameters-Input.txt were already MD5 and SHA256 authenticated as original small files in v34d, but author code itself is a simulation/model module, not yet a verified loader/crosswalk for all four original DAT recordings. It has not been executed. No new measured effect, causal Boids force or fish acoustic sender data exists in this source-only audit.

## Next mechanism-oriented Boids hypothesis

**Hypothesis (future, not an observed finding):** A nonreciprocal but predictable virtual neighbor can preserve *directional alignment* while weakening *pairwise cohesion*, so movement predictability and local attraction cannot be summarized as one Boids interaction coefficient. The original PLOS authors already describe consistent behavioral patterns; a novel contribution would be to quantify **the same source-physical-time predictive strength × temporal persistence** as v32–v33 using intervention arm C2 vs C3 **only if original time-series and trial identity are source verified**, with all of the above confounds and two studies' distinct designs explicitly separated. No animal vocalization hypothesis is tested.

Separate 2026 robot-preprint original Figshare 33086195 API returned 404; no original files or data admitted. Original v33 real schooling 12-group results unaffected. [Draft PR #248](https://github.com/zuizui0223/boids/pull/248) stays unmerged, main untouched.
