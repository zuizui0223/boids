# Independent Boids v15 post-run review

**Final verdict: the saved local results, final Japanese report, and numerical reproduction in the CI receipt pass independent verification.** All Critical, Important and Minor findings are closed. The final reviewed Japanese report has SHA-256 `2cca47fa3682512da883b3ecf86af6ee519211b1767613ab45e650c038ed8b39`.

The independent script was run with the complete results directory and an explicit repository root. It exited 0 and produced `independent_result_receipt.json`. The verified NPZ contains 48,311,954 bytes, SHA-256 `ff50dbf071df55e53e8391c84373802b848ec43fa4a08ed3c4864ebbd935c420`.

### Coverage

- Verified the raw 96-seed manifest in order, twelve continuation corners, separate source histories, trace offsets, array shapes and dtypes, finite values, integer calling grid, cue schedules, donor snapshots and their fish order, hull/call snapshot consistency, and first-call velocity invariance. Direct sequential PCG64 draws matched both stored random states for every seed. The 96 exact natural-history replay pairs matched the recorded worker validation metadata. The reviewed runner performs those trajectory comparisons before admission.
- Matched the five computational source checksums against the frozen bytes and both JSON files against each other. Recomputed all three windows, all twelve arm means, nine contrasts for each metric, each cohort, all seven Möbius terms by inclusion-exclusion, and all three Shapley allocations by averaging marginal contributions across all six orders. Integer Möbius and Shapley closure held in every row. Verified bootstrap percentile intervals, signed positive/negative/zero tallies, concentration, cohort membership, restricted latency summaries and every saved statistical field.
- Independently calculated 200-update arrival totals by integer convolution and validated the observed, censored and restricted-latency records at 0.80, 0.90 and 0.95. Checked every row of each table by its named seed/arm/window/metric or threshold. All 6,912 window rows, 1,920 effect rows and 3,456 arrival rows agreed, including their complete key sets.
- The verifier imports no production analysis or simulation modules and launches no trajectories. CSV numeric fields were checked by exact float round trip. JSON estimates and interval endpoints used a relative numerical tolerance of 5×10⁻¹³ and zero absolute tolerance. Integer counts, keys, nulls, booleans and source/trace digests were checked directly.

### Scientific readout

The all-96 primary contrast (intact 111 minus 000, mean call fraction over updates [1040,4040)) was +0.001897243923611111, with paired percentile interval [+0.0000341796875, +0.004570765516493055]. Its median was zero. There were 33 positive, 28 negative and 35 exactly zero seeds. Seeds 2062 and 2048 supplied 90.0643% of the positive mass.

The fixed baseline-low cohort comprised seeds 2029, 2041, 2048, 2057, 2062, 2064, 2068 and 2085. Its mean primary-window contrast was +0.02279948, interval [+0.00182161, +0.04888766]. At arrival threshold 0.90, mean restricted-latency contrast was −18.75 updates for all 96 and −225 updates for the eight low-baseline seeds. Event counts were 95/96 in each natural arm and 7/8 in each low-baseline natural arm.

The all-seed signed allocations were X +0.00032735, V +0.00124542 and C +0.00032447. The paired X-minus-C contrast was +0.00000288, interval [−0.00009533, +0.00011431]. The all-seed motor-cut minus intact difference in the X insertion contrast was −0.00066580, interval [−0.00159766, −0.00013758]. These secondary quantities concern the specified finite model and fixed exchange of state coordinates.

### Japanese scientific claim review

Reviewed `docs/V15_STATE_TRANSPLANT_RESULT.md`, SHA-256 `61af365a345d88a090e6fbcc41e0a01012d1247cfbaa1f932f507bc90e4d310c`, with the CI paragraph still pending. Compared every numerical table against the independently verified JSON/CSV or raw baseline traces. All reported values, the thresholds and all eight seed-specific rows agreed at their displayed precision. The report correctly distinguishes absolute percentages, changes in percentage points, hull area and model-update units.

The executive summary retains the all-96 primary endpoint, describes the eight baseline-low seeds as a fixed secondary subgroup and properly uses positive mass for the 90.0643% primary concentration. The late 99.4390% concentration in seed 2029 and the 76.1788% share of positive V allocation in 2062 were both verified. V has the largest average allocation under the stated convention. The report acknowledges that V superiority was not tested, X-minus-C intervals include zero, and large natural contrasts in 2048 and 2062 have different component allocations.

The three motor contrasts retain their signs and cut-minus-intact definitions. The report recognizes the four-anchor limitation. The low-seed arrival table correctly distinguishes observations and censoring, with the earliest completed confirmation at step 1240. Seed 2064 is censored in 000 and 111, but confirms at 4577 in 010 and 4422 in 011. This supports the stated example of a nonmonotone response to adding playback-derived components. The bounds on biological extrapolation, stationary behavior, mediation and positive effects at finite horizon are appropriate.

**Minor wording:** In the reviewed draft, line 187 grammatically attached exclusion of self-hearing to C. C stores all individual binary calls. The hearing matrix excludes the focal individual's own call. Suggested: 「Cは各個体の直前の二値発声を並べたベクトルです。各個体の受音量を計算するときは、その個体自身の発声を除きます。」 The numerical results and claims are unaffected.

### Targeted Japanese text recheck

The pre-final-CI text (SHA-256 `c645d8d3410d661c3431e467a756fc97319b09307e6d0d0b61b4be7865c6c6b0`) incorporates the C/self-hearing correction. The added §4 paragraph correctly identifies the old absolute positions and previous calls as the inputs to perceived sound in the post-split zero-cue updates. A velocity-only exchange at fixed X,C and RNG therefore leaves the first resumed binary calls identical. Later updates can see the geometry produced by changed velocities. The targeted test freshly passed across all four fixed X,C backgrounds and checked the full per-fish call vector. The equations support the stated pathway without a claim that every velocity swap changes later calls.

The stated numerical tolerance agrees with the JSON estimate and interval checks (relative 5×10⁻¹³, absolute zero). The CSV round-trip check is stricter and requires equality of the parsed floating values. Integer counts, flags and SHA-256 digests require exact matches. The final CI paragraph remains to be reviewed against its receipt.

### Final CI and Japanese report signoff

Checked final run **44976865455**, job **137068600382**, tested commit `24e3b99f50e0a69b341a3f35c5bac1359d457dce` and artifact **14736701409** against the supplied CI receipt. The receipt records success on 2026-11-22 at 02:54:08 UTC, with 5 + 34 + 44 + 82 = 165 passing tests. The final Japanese paragraph identifies that tested commit and links to the matching run and artifact.

Independently mapped the six fields in the extracted final CI output to their local JSON counterparts. Object keys, array ordering, and all **1,451 scalar values** agreed exactly. This is numeric equality without a tolerance. The extracted CI JSON serializes 43 whole-valued numbers as integers where the local JSON uses a decimal form, such as `0` and `0.0`. These are identical numeric values. The raw receipt matched the independently verified local byte count and SHA-256, and each of the five listed digests matched its local source file.

The final report correctly states the comparison's scope: both cohort manifests, both primary-window metrics with the reported contrasts and calling decomposition, and threshold-0.90 arrival summaries. The other windows and thresholds were independently checked from the matching raw archive. No claim of bit-identical PDF/PNG files or whole-artifact byte equality is required. This check used the supplied final CI output and receipt; it did not redownload the artifact. No additional simulation or test suite was run.
