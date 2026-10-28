# v18 observed-source endpoint — predeclared fourteen-pair GPS route-memory test **NOT ADMITTED**

**2026-10-28 JST; frozen structural result, no future-memory predictive effect measured.**

## Source and experimental design

Morford et al. (2026) *Collective route memories emerge through differential forgetting of navigational information in homing pigeons*, DOI [10.1038/s41598-026-39898-2](https://doi.org/10.1038/s41598-026-39898-2), original author GitHub commit `8e4f7e48abfa57212c5207c28580003f0ef14210`.

The source membership ledger records **14 independent non-overlapping pigeon pairs, 28 birds**, and the original GPS ZIP contains **426 track CSV files**. All source bytes and exact Git blob SHA1/SHA256 integrity were checked in [v17-D](V17D_INDEPENDENT_14_PAIR_MEMORY_SOURCE_RESULT.md). No raw bird trajectories or numeric source rows were redistributed.

The [frozen v18 prediction protocol](V18_FROZEN_14PAIR_MEMORY_FORECAST_CONTRACT.md) required **all 14 assigned pairs**, both geographical release sites `LH` and `SH`, historical training `TR` flights at each site, and at least one later memory-test `CM` flight at each site *before opening any future CM trajectory*. It fixed source-site-specific population/own-pair/own-bird circular route-bearing forecasts at eight radial shells 250–2000m; whole-pair independent scores, no post-hoc parameter changes.

## Original-source parsing audit and result

A first-run filename parser rejected **19** original files containing `Checked` status or `pair*` (planned solo joined a real partner). The pre-outcome *source-format-only* [filename run 40626226608](https://github.com/zuizui0223/boids/actions/runs/40626226608) identified all 19 file names **without reading GPS contents**. Original author R code explicitly reclassifies actual `pair*` flights as `pair`. The resulting [source-format amendment](V18_ORIGINAL_FILENAME_AMENDMENT.md) included **all 426 original GPS CSVs** with both `Checked` and `Nocheck` status—no favorable trajectories selected and no scoring criteria altered.

The [frozen v18 result run 40626313864](https://github.com/zuizui0223/boids/actions/runs/40626313864) passed **10/10 known-truth tests**, verified exact source files and all 426 original file names. The outcome was:

> **`NOT_ADMITTED_ORIGINAL_FILENAME_STAGE_SITE_GATE`** — original pair **O19** has **10 LH training TR files + 14 SH training TR files, but 0 LH CM and 0 SH CM files**.

The other 13 assigned pairs have CM files at both sites, but original v18's preregistration required *all 14*. **No GPS position, bearing, future route or predictive error was opened or scored.** The source absence is not biological evidence of weak or strong memory.

[Machine-readable original 14-pair structural stop receipt](../validation_v18/results/frozen_14pair_source_stop_v18.json) records all 14 pairs' training and memory-test file counts by site and the explicit three frozen rule failures.

## What a legitimate next study can do — separate hypothesis, not a rescue

A **new, explicitly exploratory**, *structurally eligible* complete-case cohort of **13 originally assigned pair components** can be declared based only on the independent stage/file existence check (not route outcomes) before opening any bird's `CM` trajectory.

The next study may reuse the frozen v18 methodology and all unchanged radial shells/sites while explicitly publishing the earlier all-14 **NOT ADMITTED** result and marking its results **post-source-availability-conditioned exploratory**, not a confirmatory verification of 14-pair memory superiority. Exclude O19 **only from the testing cohort because no CM target exists**, not from the source population's historical `TR` reference unless the design is independently declared. Continue to report site × solo/pair cell coverage, all 13 pair contrasts and source-quality limitations. A new observational prediction test cannot prove causality or neural memory.

**No historical v6/v8/v15/v16 observed endpoint, v17-B five-network stop, or v13 synthetic model was modified.**
