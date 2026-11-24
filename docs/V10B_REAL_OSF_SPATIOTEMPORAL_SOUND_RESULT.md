# v10b original wild acoustic source position-order test — positive diagnostic with major resolution warning

Date: 2026-11-21 JST. This is an **exploratory source-level temporal-order test**, not a real individual fish schooling or direct school-to-chorus result.

Authentic source: Mouy et al. 2023 *Methods in Ecology and Evolution* DOI 10.1111/2041-210X.14095. All six author-original [OSF q8dz4](https://osf.io/q8dz4) `localization_results.csv` original SHA256 values were reverified against previously committed source-only receipt v6, BEFORE opening event x/y/z or UTC time fields. New original field test [Actions #44769141245](https://github.com/zuizui0223/boids/actions/runs/44769141245) PASS, six synthetic fixtures PASS, [complete no-raw-event source receipt](https://github.com/zuizui0223/boids/actions/runs/44769141245/artifacts/14646498933).

Original six CSV source rows: 17+2+6+6+23+12 = **66**; complete UTC time and finite x/y/z retained **5+2+6+6+19+12=50** (large OGD missing xyz in 12 of 17, mobile C missing xyz in 4 of 23). All 50 analyzable records have blank `label_class` in original CSV; do not assume acoustic species or fish individual identity. Other source fields include `label_subclass` but no validated recurrent individual tracker ID.

Frozen statistic: per-array median 3D distance between *consecutive* localized events with time gap 0.001–120s. Require at least 6 eligible events and ≥5 such adjacent pairs. Within each array, fixed-seed 1,999 random reassignments of spatial positions to fixed source event times (labels originally blank). The same-source shuffles preserve the exact locations, time schedule and source N, but are only a conditional descriptive temporal association null; permutations are not independent fish/replicates. Coordinate units from source are meters.

| Original array | Eligible events | 120s pairs | Actual median successive event 3D distance (m) | Mean shuffled median (m) | O/E | one-sided model-conditional p |
|---|---:|---:|---:|---:|---:|---:|
| large OGD | 5 | 4 | — | — | — | SOURCE_SUPPORT_STOP |
| mini | 2 | 1 | — | — | — | SOURCE_SUPPORT_STOP |
| mobile A | 6 | 5 | 0.08944 | 0.08180 | 1.093 | 0.5965 |
| mobile B | 6 | 5 | 0.04472 | 0.03556 | 1.258 | 0.9370 |
| mobile C | 19 | 18 | 1.67965 | 2.04924 | 0.820 | 0.1670 |
| large HI | 12 | 11 | **0.07903** | **0.27667** | **0.2856** | **0.0005** |

The predeclared `label_class`-stratified shuffle is not independent here because all original classes are blank. Predeclared strict 3D original uncertainty ≤1m all three axes remains evaluable for mobile A/B and large HI; all mobile C measurements fail strict support.

The **one** strong large-HI signal is an authentic localized source event time ordering, not evidence that fish move or coordinate via social steering. Critically, median Euclidean combined original xyz localization uncertainty-span at large HI is **0.70712m**, nearly **9× larger** than 0.07903m nominal successive localization distance. Its apparent temporal clustering can reflect multiple sounds at one static acoustic hotspot, an unobserved persistent vocal fish, inhomogeneous detection, localization algorithm rounding/error dependence, different animals or a moving school. No fish source identity can be linked across sounds.

An explicitly post-v10b sensitivity experiment using all available original per-axis `x_err_span,y_err_span,z_err_span` is independently frozen in `docs/V10C_ORIGINAL_OSF_UNCERTAINTY_FREEZE.md`. It simulates arbitrary *independent Uniform(center±span/2)* positional error scenarios, not an acoustic posterior. A source significance check without this caveat would be scientifically misleading.

## Same-site paired scatters still not admitted
New 2026 Dryad Kim et al dataset DOI 10.5061/dryad.qz612jmx0 explicitly contains same-site South_T 20min UF440 sound + depth-resolved 70kHz biological scatter for up to four deployments. Original companion author R script already fits a GAMM relating nightly SPL and backscatter; rediscovering that correlation is prior art. GitHub Actions [v10 source-only gate #44768532962](https://github.com/zuizui0223/boids/actions/runs/44768532962) successfully fetched nine official original file metadata records but **actual file bytes returned HTTP 401**, a source access STOP. Current Dryad Files API requires a bearer token for file-download endpoints, as per [Dryad API docs](https://github.com/datadryad/dryad-app/blob/main/documentation/apis/api_accounts.md). Do not invent a paired biological result from metadata, and do not bypass access controls.

## Need for real school × chorus
- A continuous fish school *including silent fish* tracked with individual IDs and velocities.
- Audio/video time synchronization, acoustic source localization uncertainty and individual call attribution over the same observation times, with environmental/time-based common-cause controls.
- Independent school-level recorder/date holdouts and counterfactual group-only vs call-response generative predictions.
No validated causal Reynolds forces, direct schooling→chorus effect or multi-region meta-effect yet.

Keep draft [PR #248](https://github.com/zuizui0223/boids/pull/248), main unchanged. Do not merge.

