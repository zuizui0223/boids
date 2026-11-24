# v25 frozen primary-source gate — independent 2026 lateral-line manipulation in 60-fish schools

**2026-11-24 JST, before opening any new v25 source numerical outcomes. SOURCE-ONLY discovery.**

Primary published source: Peterson, A. N., Zhou, J., Mittal, R. & McHenry, M. J. (2026), *The lateral line facilitates rapid responses in accelerating fish schools*, Integrative and Comparative Biology, DOI [10.1093/icb/icag151](https://doi.org/10.1093/icb/icag151), published August 18, 2026. The original paper studies schools of **60 rummy-nose tetra (*Petitella bleheri*)**, manipulating flow-sensing lateral line function. Published finding: fish with intact sensing exhibited an **approximately one-third lower inter-fish response latency** during acceleration than impairment groups; not the same contrast during deceleration. This is **already the authors' causal experimental observation**, not a newly observed v25 effect. Authors additionally report pairwise speed correlations/network structure and mutual information; re-estimating already-published outcomes is not enough for new novelty.

**Independent official Dryad link stated in the article:** https://doi.org/10.5061/dryad.gxd25482b. Dryad REST API documented as https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.gxd25482b. Original dataset content has not yet been admitted or downloaded in this project. Older Peterson/McHenry 2024 lateral-line data may overlap participants/recordings: exact trial provenance and independence MUST be determined before pooling.

## Pre-registered v25 source-only metadata workflow

1. Request the exact original official Dryad dataset REST metadata **once** (bounded ≤2 MiB UTF8 JSON). Record response status, DOI, title, original version links, license, size, version number and provider-assigned checksum *if supplied*; never claim a metadata-only SHA is a checksum of unseen raw animal files.
2. If official metadata includes a supported, same-host version ID or a verified versions link, fetch only the **official version's file listing**, max 200 entries and 3 MiB JSON. Record original filenames, byte sizes, provider SHA values and content types if provided. Do not request \`download\`, \`files/<id>/download\`, ZIPs, native MAT, CSV, trajectory rows, sound or video. No source numerical effects or responses may be opened in v25.
3. Fail closed for 401, 403, 404, API redirect error, schema mismatch, size limit, missing version or files, or metadata lacking observed animal/session/treatment identifiers. If exact files unavailable, report SOURCE_ACCESS_STOP, not a biological null. If metadata lists files, state **METADATA_ONLY_NOT_YET_TRAJECTORIES**.
4. Unit fixtures mock valid JSON + nested links, a missing DOI, 401, 403 and files-list truncation; verify no biological predictive scores and no source bytes redistributed.

## Strict subsequent empirical eligibility, only if source data are obtained

- Validate actual individual XY(time), frame clock, original recordings (school/session ID), baseline/treated lateral line assignment, and treated fish vs intact fish *at the recording level*; check whether sham treatment/control groups are separately identified.
- Require repeated independent schools per treatment and verifiable treatment timing, source smoothing/filtering, and common environmental hydrodynamic forcing. Create a fresh frozen heldout-school test of the 0.1/0.2/0.5/1/2-sec collective-state age curve conditional on **accelerating versus decelerating episodes** and treatment, followed by a study-level contrast, rather than conflating 60 fish within one school with 60 independent schools. This is the strongest mechanism-linked extension, but it remains a future **hypothesis**.
- The existing v24 Puy/Niizato 2-fish-study curves cannot show lateral-line function or acoustic feedback. Lateral-line flow detection is also **not itself** demonstrated conspecific vocal hearing/calling.
- No observed 3-species meta-effect until complete original time series of this or an independent third study pass source and cohort admission. Do not count the 2026 Zheng high/low clips as independent replicate schools.

Keep [Draft PR #248](https://github.com/zuizui0223/boids/pull/248) unmerged and main unchanged.
