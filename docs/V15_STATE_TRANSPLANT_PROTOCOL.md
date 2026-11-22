# v15 — Independent-seed state-transplant audit

Frozen before new outcomes, 2026-11-22 JST. **SYNTHETIC_ONLY_NOT_FIELD_RESULT.**

## Question and design choice

v14 found finite-horizon arrival differences in a minority of its original seeds, with a negligible late calling contrast. This follow-up asks whether a pulse leaves dynamically consequential information in positions X, velocities V, or previous binary calling C. It is an independent-seed computational follow-up, not an independent model, animal experiment, natural-mediation analysis, or test of stationary uniqueness.

We considered longer unmodified trajectories, a two-component motion/calling swap, and a full three-component swap. We choose eight X/V/C corners because otherwise velocity can be mistaken for positional memory. Four additional post-pulse motor-cut anchors test two positional contrasts without claiming a complete second factorial. These are implementation choices under the user's continuation authorization. An independent design review was completed without running new seeds.

## Fixed cohort and histories

- Authoritative predecessor: `7295d885b587d808cb74fbae11163819ed8cf22d`; preserve v12–v14 sources and outcomes.
- New seeds: **2000–2095, all 96**. No added or removed seeds based on baseline state or later outcomes.
- N=32; dt=0.06; original v14 initialization, equations, update order, and weights (5,3).
- Paired histories: no playback versus amplitude0.8 at updates **[1000,1040)**.
- Split after **1040 completed updates**, immediately before update t=1040.
- Preserve fish index, absolute positions, vector orientations, and the origin-dependent wall. No recentering, rotation, matching, or identity permutation.
- Same initialization draws in original order: normal positions, uniform headings, binomial initial calls; then one `rng.random(N)` per update in every arm.
- Both source histories must have identical RNG state at1040. Copy that state for each continuation; never reseed at the split.

For bit label `xvc`, 0 selects a component from the no-playback history and 1 selects it from the playback history. Code mask bits are X=4, V=2, C=1. Copy arrays independently to avoid in-place mutation of a source or another corner.

Intact continuations use all eight labels `000,001,010,011,100,101,110,111`, weights(5,3). Motor-cut continuations use only `000,100,011,111`, weights(0,3). The cut is applied starting at update1040, after both source histories have been generated with intact weights. Cue is zero in every continuation. Stop at **6000 completed updates**, giving4960 continuation samples and **1152 continuations** across the96 seeds.

Hybrid states generally occurred in neither unmodified history. Save the two original prefixes separately from continuations, which have global offset1040. Never attach a fabricated prefix to a hybrid.

## Primary endpoint and prespecified secondary analyses

The single primary endpoint is mean call fraction over **[1040,4040)**; the primary contrast is intact **111−000 averaged over all96 seeds**.

Secondary windows are immediate [1040,1240) and late [5000,6000). Report call fraction and convex-hull area for all12 continuations in all three windows. Late is a finite-window diagnostic, not a claim about long-run maintenance.

For the primary-window endpoint, calculate the full intact factorial separately within each seed. Let f(S) denote the endpoint for the corner whose components in S come from playback. For every nonempty S⊆{X,V,C},

`m(S) = sum_{T subset S} (-1)^(|S|-|T|) f(T)`.

Report all seven terms X,V,C,XV,XC,VC,XVC. They must sum to f(XVC)−f(empty). Also report Shapley allocations, for example

`phi_X = m_X + (m_XV+m_XC)/2 + m_XVC/3`,

and analogously for V and C. Their sum must equal the same total for every seed. Shapley is an allocation convention for interactions; it is not a unique physical decomposition. Report signed call-fraction units, not percentages of a possibly small or cancelling total. Report the paired difference phi_X−phi_C descriptively if comparing their magnitudes.

For each of the intact and motor-cut panels, define X insertion as100−000, X deletion as111−011, and total as111−000. Report each cut-minus-intact difference. Four cut anchors do not identify cut-panel Shapley values, all factorial interactions, or the average X effect across all VC backgrounds. Insertion/deletion are not automatically sufficiency/necessity claims. A positional effect under motor cut can reflect hearing and ordinary Boids movement in inherited geometry.

## Baseline state and arrival

Define the prespecified baseline-low subset by the shared **[800,1000)** mean call fraction **<0.90**. Keep all its members regardless of later response or censoring. The all96 primary result remains primary; the conditional subset is secondary. Sample size96 is an exploratory precision choice, not a demonstrated power calculation or a guarantee of enough low-state seeds.

For all12 continuations, find the first completed200-update window with mean call fraction≥0.90, with window starts1040 through5800. Confirmation is start+200; earliest1240. If no window qualifies, event time is null, event=false, censored=true, restricted latency=4960. Confirmation exactly at6000 is an observed event with the same restricted latency, not a censoring event.

Compute window totals as integer calling counts (fraction×32), validating the 1/32 grid, to avoid floating threshold ties. Repeat fixed thresholds0.80 and0.95 as sensitivity checks. Report all arm event counts, per-seed records, and the natural111−000 restricted-latency contrast; also report it in the fixed baseline-low subset. No adaptive horizon or threshold selection. Already-high states have a200-step measurement floor; confirmation is not an absorbing transition.

## Uncertainty and concentration

Use10000 paired whole-seed percentile bootstrap replicates, RNG seed **2026112205**. Within each cohort, the same index matrix is used for every arm and derived contrast. Calculate factorial terms and allocations within seeds before resampling. For the fixed low subset, resample its members; do not select them anew by post-treatment outcomes. Empty cohorts yield null estimates/intervals, singleton cohorts yield their point estimate but a null interval. Small subsets must be labelled descriptive and shown per seed.

Intervals are unadjusted descriptive simulator-seed intervals, not fish-population estimates or simultaneous confidence statements across secondary endpoints. Report means, medians, signs, and positive-effect concentration with denominator sum(max(delta_i,0)); no ratio to a near-zero net sum.

## Validation, storage, and interpretation

Preserve state snapshots at completed counts1000/1040 for source histories and1040/1240/4040/6000 for continuations. Record positions, velocities, binary calls, and RNG states at the split/end; save full call-fraction and area traces, cue information, seed/corner identity, and the offset.

Before saving, validate exact keys/shapes, finite values, binary calls, call grid, snapshot/trace consistency, and positive nondegenerate hulls. Validate each worker result before assigning it to a fixed output array. Capture computational source hashes before execution and verify them after analysis before writing outputs atomically.

For every new seed, intact000 and111 must replay the corresponding unmodified v14 6000-step history exactly, including trace values and recorded states. Unit fixtures additionally verify: split/no-split RNG replay; first resumed calls independent of V provenance at fixed X,C (perceived sound is computed before movement); and motor-cut motion independent of C at fixed X,V. Unit fixtures use other seeds; do not preview the96-seed outcomes before freezing this protocol.

There is no separate latent internal-memory variable in this model. C is a collective binary calling pattern; self-hearing is excluded. The interventions identify consequences of exchanging state components in the specified equations, not biological memory, natural causal mediation, or a universal ecological mechanism. Previous conclusions from unrelated fish locomotion and acoustic sources remain separate.

Deliver raw arrays, per-seed tables, aggregate results, static figures, a Japanese report, and source/provenance receipts. Obtain fresh independent code and result review. Reproduce the fixed calculation in GitHub Actions. Update Draft PR#248 with expected-head guards; keep main unchanged and do not merge.
